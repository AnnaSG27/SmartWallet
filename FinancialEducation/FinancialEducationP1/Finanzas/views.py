from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('educacion')  # Redirige a la página de educación financiera
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'Finanzas/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def educacion_view(request):
    return render(request, 'Finanzas/educacion.html')