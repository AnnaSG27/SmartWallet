from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo_documento = models.CharField(max_length=2, choices=[('TI', 'Tarjeta de Identidad'), ('CC', 'Cédula de Ciudadanía')])
    documento = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.user.username

class Banco(models.Model):
    nombre = models.CharField(max_length=100)
    tasa_interes = models.DecimalField(max_digits=5, decimal_places=2)
    comisiones = models.CharField(max_length=100)
    requisitos = models.TextField()
    calificacion = models.DecimalField(max_digits=3, decimal_places=1)

    def __str__(self):
        return self.nombre

class Bolsillo(models.Model):
    TIPO_BOLSILLO = [
        ('AHORRO', 'Ahorro'),
        ('GASTOS', 'Gastos'),
        ('INVERSION', 'Inversión'),
        ('OTRO', 'Otro'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    saldo = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tipo = models.CharField(max_length=10, choices=TIPO_BOLSILLO, default='AHORRO')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    meta = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"{self.nombre} - ${self.saldo:,.2f}"
    
    @property
    def porcentaje_meta(self):
        if self.meta and self.meta > 0:
            return min(100, (self.saldo / self.meta) * 100)
        return 0
    
    @property
    def tiene_saldo(self):
        return self.saldo > 0

class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    celular = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.usuario.username}"


@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)

@receiver(post_save, sender=User)
def guardar_perfil(sender, instance, **kwargs):
    instance.perfil.save()