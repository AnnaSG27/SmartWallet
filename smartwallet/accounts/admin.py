from django.contrib import admin
from .models import UserProfile
from .models import Banco

admin.site.register(UserProfile)
admin.site.register(Banco)