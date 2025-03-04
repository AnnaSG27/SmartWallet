from django.db import models

# Create your models here.

class Reve(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=250)
    image = models.ImageField (upload_to= 'reve/images/')
    url = models.URLField(blank=True)