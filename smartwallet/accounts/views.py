
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .forms import (RegisterForm, LoginForm, PerfilForm, CambiarPasswordForm, BolsilloForm, MovimientoForm)
from .models import UserProfile, Banco, Bolsillo

import json
import logging
import os
import re
import time
from random import uniform
from time import sleep

import numpy as np
import openai
import requests
from openai import OpenAI, APIConnectionError, RateLimitError, APIError
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline


logger = logging.getLogger(__name__)

#############################################################################

ASISTENTE_CONFIG = {
    "personalidad": """Eres un asesor financiero profesional que responde en español con:
    - Explicaciones claras y sencillas
    - Ejemplos concretos
    - Pasos accionables
    - Uso moderado de emojis 💰📈
    - Precisión en cifras y porcentajes""",
    
    "respuestas_fallback": {
    "ahorro": """
    💰 Estrategias Inteligentes para Ahorrar 💰
    
    ✨ Acciones clave:
    ◦ Automatiza transferencias a tu cuenta de ahorros
    ◦ Reduce gastos pequeños (cafés, suscripciones no usadas)
    ◦ Establece metas SMART (específicas, medibles, alcanzables)
    
    📌 Tips adicionales:
    - Regla 50/30/20: 50% necesidades, 30% deseos, 20% ahorro
    - Usa apps de seguimiento de gastos
    - Revisa tus gastos mensuales para identificar áreas de mejora
    
    💬 Ejemplo práctico:
    Si ganas $2.000.000/mes, intenta ahorrar 400.000 (20%)
    """,
    
    "inversión": """
    📈 Guía Básica de Inversión 📈
    
    🔍 Distribución recomendada:
    ◦ 1) Fondo de emergencia (3-6 meses de gastos)
    ◦ 2) ETFs de bajo costo (60% de tu portafolio)
    ◦ 3) Bonos gubernamentales (30%)
    ◦ 4) Acciones individuales (10% máximo)
    
    ⚠️ Precauciones:
    - Diversifica siempre tus inversiones
    - Invierte solo lo que puedas permitirte perder
    - Considera tu perfil de riesgo
    
    💡 Para empezar:
    Con 1.000.000, podrías invertir 600.000 en ETFs, 300.000 en bonos y 100.000 en acciones
    """,
    
    "deuda": """
    🚨 Plan para Controlar Deudas 🚨
    
    ✅ Pasos prioritarios:
    1. Paga primero deudas con mayor interés (tarjetas crédito)
    2. Negocia tasas de interés con tus acreedores
    3. Detén el uso de créditos nuevos
    
    🛠 Herramientas útiles:
    - Método bola de nieve: enfócate en la deuda más pequeña primero
    - Consolidación de deudas (cuidado con las condiciones)
    - Apps para seguimiento de pagos
    
    📉 Ejemplo:
    Si debes 5.000.000 en tarjetas al 20% y 3.000.000 en préstamo al 10%, 
    enfócate primero en las tarjetas
    """,
    
    "presupuesto": """
    📊 Cómo Crear un Presupuesto Efectivo 📊
    
    1. 📝 Registra todos tus ingresos y gastos
    2. 🗂 Categoriza tus gastos (fijos/variables)
    3. 🎯 Establece límites realistas
    4. 🔄 Revisa y ajusta semanalmente
    
    💡 Consejo profesional:
    Usa la regla 50/30/20 como punto de partida
    """,
    
    "default": """
    🤖 No entendí completamente tu pregunta
    
    Por favor reformúlala incluyendo:
    ◦ El tema específico (ahorro, inversión, deudas)
    ◦ Cantidades aproximadas
    ◦ Tu objetivo principal
    
    💬 Ejemplos válidos:
    - ¿Cómo ahorrar $500 mensuales con un salario de 2.000.000?
    - ¿Qué inversión recomiendan para 1.000.000 a 1 año?
    - ¿Cómo reducir deudas de 5.000.000 en tarjetas?
    """
}
}

###########################################################################

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            logger.info(f'Usuario creado: {user.username}')
            UserProfile.objects.create(
                user=user,
                tipo_documento=form.cleaned_data['tipo_documento'],
                documento=form.cleaned_data['documento']
            )
            logger.info(f'Perfil creado para el usuario: {user.username}')
            login(request, user)
            return redirect('home')
        else:
            logger.error('El formulario no es válido')
            logger.error(form.errors)  
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

#################################################################################

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home') 
            else:
                form.add_error(None, "Usuario o contraseña incorrectos")
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

###################################################################################

@login_required
def home(request):
    return render(request, 'accounts/home.html')

#################################################################################

def user_logout(request):
    logout(request)
    return redirect('login')

##################################################################################

@login_required
def perfil(request):
    usuario = request.user

    if not hasattr(usuario, 'perfil'):
        Perfil.objects.create(usuario=usuario)

    if request.method == 'POST':
        if 'actualizar_perfil' in request.POST:
            perfil_form = PerfilForm(request.POST, instance=usuario)
            if perfil_form.is_valid():
                perfil_form.save()
                messages.success(request, 'Tu perfil ha sido actualizado correctamente.')
                return redirect('perfil')
        elif 'cambiar_password' in request.POST:
            password_form = CambiarPasswordForm(user=usuario, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, 'Tu contraseña ha sido actualizada correctamente.')
                return redirect('perfil')
    else:
        perfil_form = PerfilForm(instance=usuario)
        password_form = CambiarPasswordForm(user=usuario)

    return render(request, 'accounts/perfil.html', {
        'perfil_form': perfil_form,
        'password_form': password_form,
    })

###########################################################################

def comparacion_bancos(request):
    bancos = Banco.objects.all()
    return render(request, 'accounts/comparacion_bancos.html', {'bancos': bancos})

#################################################################################

def educacion_financiera(request):
    return render(request, 'accounts/educacion_financiera.html')   

##################################################################################

@login_required
def bolsillos(request):
    bolsillos = Bolsillo.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    
    if request.method == 'POST':
        form = BolsilloForm(request.POST)
        if form.is_valid():
            bolsillo = form.save(commit=False)
            bolsillo.usuario = request.user
            bolsillo.save()
            messages.success(request, f'¡Bolsillo "{bolsillo.nombre}" creado exitosamente!')
            return redirect('bolsillos')
    else:
        form = BolsilloForm()
    
    return render(request, 'accounts/bolsillos.html', {
        'bolsillos': bolsillos,
        'form': form
    })

@login_required
def gestionar_bolsillo(request, bolsillo_id):
    bolsillo = get_object_or_404(Bolsillo, id=bolsillo_id, usuario=request.user)
    
    if request.method == 'POST':
        if 'eliminar' in request.POST:
            nombre = bolsillo.nombre
            bolsillo.delete()
            messages.success(request, f'¡Bolsillo "{nombre}" eliminado correctamente!')
            return redirect('bolsillos')
        
        form = MovimientoForm(request.POST)
        if form.is_valid():
            cantidad = form.cleaned_data['cantidad']
            descripcion = form.cleaned_data['descripcion']
            
            if form.cleaned_data['tipo'] == 'INGRESO':
                bolsillo.saldo += cantidad
                mensaje = f'¡Se agregaron ${cantidad:,.2f} al bolsillo "{bolsillo.nombre}"!'
            else:
                if bolsillo.saldo >= cantidad:
                    bolsillo.saldo -= cantidad
                    mensaje = f'¡Se retiraron ${cantidad:,.2f} del bolsillo "{bolsillo.nombre}"!'
                else:
                    messages.error(request, 'No tienes suficiente saldo para este retiro')
                    return redirect('gestionar_bolsillo', bolsillo_id=bolsillo.id)
            
            bolsillo.save()
            messages.success(request, mensaje)
            return redirect('bolsillos')
    else:
        form = MovimientoForm()
    
    return render(request, 'accounts/gestionar_bolsillo.html', {
        'bolsillo': bolsillo,
        'form': form
    })

##################################################################################

def iniciar_conversacion(request):
    """Inicia una nueva conversación con el asistente"""
    if 'conversacion' not in request.session:
        request.session['conversacion'] = {
            'historial': [
                {
                    "role": "system", 
                    "content": ASISTENTE_CONFIG["personalidad"]
                },
                {
                    "role": "assistant", 
                    "content": "¡Hola! 👋 Soy tu asesor financiero. ¿En qué puedo ayudarte hoy?\n\nPuedo ayudarte con:\n- Presupuestos 💰\n- Inversiones 📈\n- Deudas 🏦\n- Planificación 🗓️"
                }
            ]
        }
    return render(request, 'accounts/asistente.html')

@csrf_exempt
def manejar_mensaje(request):
    """Maneja los mensajes del usuario"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        mensaje = data.get('mensaje', '').strip()
        if not mensaje:
            return JsonResponse({'error': 'Mensaje vacío'}, status=400)

        cache_key = f"chat:{hash(mensaje)}"
        if cached := cache.get(cache_key):
            return JsonResponse({'respuesta': cached})

        client = OpenAI(api_key=settings.OPENAI_API_KEY, timeout=10)
        
        historial = request.session.get('conversacion', {}).get('historial', [
            {"role": "system", "content": ASISTENTE_CONFIG["personalidad"]}
        ])
        
        historial.append({"role": "user", "content": mensaje})
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=historial,
            temperature=0.7,
            max_tokens=300
        )
        
        respuesta = response.choices[0].message.content
        
        historial.append({"role": "assistant", "content": respuesta})
        request.session['conversacion'] = {'historial': historial}
        cache.set(cache_key, respuesta, 300)
        
        return JsonResponse({'respuesta': respuesta})

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        mensaje_lower = mensaje.lower()
        if 'ahorr' in mensaje_lower:
            respuesta = ASISTENTE_CONFIG["respuestas_fallback"]["ahorro"]
        elif 'invers' in mensaje_lower:
            respuesta = ASISTENTE_CONFIG["respuestas_fallback"]["inversión"]
        elif 'deud' in mensaje_lower:
            respuesta = ASISTENTE_CONFIG["respuestas_fallback"]["deuda"]
        else:
            respuesta = "⚠️ Estamos teniendo dificultades técnicas. Por favor intenta más tarde."
        
        return JsonResponse({'respuesta': respuesta})

def obtener_historial(request):
    """Devuelve el historial de conversación"""
    return JsonResponse({
        'historial': request.session.get('conversacion', {}).get('historial', [])[1:]
    })

##################################################################################################

def generar_imagen_concepto(request):
    if request.method == 'POST':
        try:
            concepto = request.POST.get('concepto', '').strip()
            
            if getattr(settings, 'HUGGINGFACE_API_KEY', None):
                try:
                    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
                    headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}
                    
                    prompt = (
                        f"Infografía minimalista abstracta sobre {concepto}, "
                        "estilo plano moderno, colores claros, sin texto, "
                        "ilustración vectorial simple"
                    )
                    
                    response = requests.post(
                        API_URL,
                        headers=headers,
                        json={"inputs": prompt},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        import base64
                        imagen_b64 = base64.b64encode(response.content).decode('utf-8')
                        return JsonResponse({
                            'imagen_url': f"data:image/png;base64,{imagen_b64}",
                            'service': 'huggingface'
                        })
                    else:
                        return JsonResponse({
                            'error': f"El servicio de imágenes está ocupado (código {response.status_code}). Intenta en 30 segundos."
                        }, status=503)
                        
                except requests.exceptions.Timeout:
                    return JsonResponse({
                        'error': 'El servicio está tardando demasiado. Intenta con un concepto más simple.'
                    }, status=504)
                    
            return JsonResponse({
                'error': 'Servicio no disponible temporalmente'
            }, status=503)

        except Exception as e:
            return JsonResponse({
                'error': 'Error inesperado. Por favor intenta con otro concepto.'
            }, status=500)

    return render(request, 'accounts/imagen_concepto.html')


##################################################################

RESPUESTAS_FALLBACK = {
    "creditos": [
        "• 💳 Paga más del mínimo en tus tarjetas de crédito",
        "• 📅 Establece un plan de pagos para reducir deudas",
        "• 🚫 Evita nuevos gastos con tarjetas hasta controlar tu situación"
    ],
    "ahorro": [
        "• 🏦 Abre una cuenta de ahorros separada de tu cuenta corriente",
        "• 🔄 Automatiza transferencias a ahorros con cada pago",
        "• 🎯 Establece metas de ahorro específicas y realistas"
    ],
    "inversiones": [
        "• 📊 Considera fondos indexados para empezar a invertir",
        "• ⏳ Recuerda que invertir es a largo plazo",
        "• 💼 Diversifica tus inversiones para reducir riesgo"
    ],
    "presupuesto": [
        "• 📝 Registra todos tus gastos por un mes para identificar patrones",
        "• 🧾 Categoriza tus gastos en esenciales y no esenciales",
        "• ✂️ Identifica áreas donde puedas reducir gastos"
    ],
    "general": [
        "• 💰 Revisa tus estados bancarios regularmente",
        "• 🛒 Compara precios antes de comprar",
        "• 📱 Usa apps de control financiero para monitorear tu progreso"
    ]
}

def recomendaciones_ahorro(request):
    if request.method == 'POST':
        consulta = request.POST.get('consulta', '').strip().lower()
        
        if len(consulta) < 4 or consulta.isdigit() or len(consulta.split()) < 2:
            return JsonResponse({
                'error': 'Por favor describe tu situación financiera con más detalle (mínimo 4 caracteres y 2 palabras)',
                'status': 'input_error'
            }, status=400)
        
        proveedores = [
            ('OpenAI', obtener_recomendaciones_openai),
            ('HuggingFace', obtener_recomendaciones_huggingface),
            ('DeepAI', obtener_recomendaciones_deepai)
        ]
        
        for nombre, funcion in proveedores:
            if getattr(settings, f'{nombre.upper()}_API_KEY', None):
                try:
                    recomendaciones = funcion(consulta)
                    if recomendaciones and len(recomendaciones) >= 3:
                        return responder_exitoso(recomendaciones, consulta, nombre)
                except Exception as e:
                    logger.warning(f"{nombre} falló: {str(e)}")
                    continue
        
        categoria = determinar_categoria_fallback(consulta)
        return responder_exitoso(RESPUESTAS_FALLBACK[categoria], consulta, "Sistema Experto")
    
    return render(request, 'accounts/recomendaciones.html')

def determinar_categoria_fallback(consulta):
    """Determina la categoría basada en palabras clave"""
    palabras_clave = {
        "creditos": ["tarjeta", "credito", "deuda", "pago", "interes", "cuota", "banco", "financiamiento"],
        "ahorro": ["ahorro", "guardar", "junta", "reserva", "emergencia", "alcancía", "economizar"],
        "inversiones": ["invertir", "bolsa", "acciones", "fondos", "rendimiento", "mercado", "dividendos"],
        "presupuesto": ["presupuesto", "gastos", "control", "mensual", "semanal", "administrar", "planificación"]
    }
    
    for categoria, palabras in palabras_clave.items():
        if any(palabra in consulta for palabra in palabras):
            return categoria
    return "general"

def procesar_respuesta_api(contenido):
    """Procesa la respuesta de las APIs para extraer recomendaciones"""
    if not contenido:
        return None
    
    if isinstance(contenido, list) and all(isinstance(item, str) for item in contenido):
        return contenido[:3]
    
    if isinstance(contenido, str):
        lineas = [line.strip() for line in contenido.split('\n') if line.strip()]
        recomendaciones = []
        
        for linea in lineas:
            if linea.startswith(('•', '-', '*', '>')) or (linea[:1].isdigit() and '.' in linea[:3]):
                recomendaciones.append(linea)
            elif len(recomendaciones) < 3:  
                recomendaciones.append(f"• {linea}")
        
        return recomendaciones[:3]
    
    if isinstance(contenido, dict):
        for campo in ['choices', 'output', 'generated_text', 'recommendations', 'response']:
            if campo in contenido:
                return procesar_respuesta_api(contenido[campo])
    
    return None

def obtener_recomendaciones_deepai(consulta):
    """Obtiene recomendaciones de DeepAI"""
    headers = {'api-key': settings.DEEPAI_API_KEY}
    response = requests.post(
        'https://api.deepai.org/api/text-generator',
        headers=headers,
        data={'text': f"Dame 3 recomendaciones financieras prácticas para: {consulta}. Formato: • [emoji] [texto]"},
        timeout=15
    )
    response.raise_for_status()
    contenido = response.json()
    return procesar_respuesta_api(contenido.get('output'))

def obtener_recomendaciones_huggingface(consulta):
    """Obtiene recomendaciones de HuggingFace"""
    headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}
    payload = {
        "inputs": f"Como experto financiero, dame 3 consejos prácticos para: {consulta}. Usa formato: • [emoji] [consejo]",
        "parameters": {"max_length": 200}
    }
    
    response = requests.post(
        "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill",
        headers=headers,
        json=payload,
        timeout=15
    )
    response.raise_for_status()
    contenido = response.json()
    return procesar_respuesta_api(contenido.get('generated_text'))

def obtener_recomendaciones_openai(consulta):
    """Obtiene recomendaciones de OpenAI"""
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "system",
            "content": "Eres un asesor financiero experto. Proporciona 3 recomendaciones prácticas con formato: • [emoji] [texto]"
        }, {
            "role": "user",
            "content": f"Para esta situación financiera: {consulta}, ¿qué 3 acciones concretas recomiendas?"
        }],
        temperature=0.7,
        max_tokens=150
    )
    contenido = response.choices[0].message.content
    return procesar_respuesta_api(contenido)

def responder_exitoso(recomendaciones, consulta, fuente):
    """Formatea la respuesta exitosa"""
    recomendaciones_formateadas = []
    for rec in recomendaciones:
        if not rec.startswith('•'):
            rec = f"• {rec}"
        recomendaciones_formateadas.append(rec)
    
    return JsonResponse({
        'recomendaciones': recomendaciones_formateadas[:3],
        'consulta': consulta,
        'fuente': fuente,
        'status': 'success'
    })