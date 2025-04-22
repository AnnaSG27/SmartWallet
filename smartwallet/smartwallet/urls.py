from django.contrib import admin
from django.urls import path
from accounts import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('home/', views.home, name='home'),
    path('comparacion-bancos/', views.comparacion_bancos, name='comparacion_bancos'),  
    path('', views.home, name='home'),  
    path('educacion-financiera/', views.educacion_financiera, name='educacion_financiera'),
    path('perfil/', views.perfil, name='perfil'), 
    path('asistente/', views.iniciar_conversacion, name='asistente'),
    path('manejar-mensaje/', views.manejar_mensaje, name='manejar_mensaje'),
    path('obtener-historial/', views.obtener_historial, name='obtener_historial'),
    path('imagen-concepto/', views.generar_imagen_concepto, name='imagen_concepto'),
    path('recomendaciones/', views.recomendaciones_ahorro, name='recomendaciones'),
    path('bolsillos/', views.bolsillos, name='bolsillos'),
    path('bolsillos/<int:bolsillo_id>/', views.gestionar_bolsillo, name='gestionar_bolsillo'),
]