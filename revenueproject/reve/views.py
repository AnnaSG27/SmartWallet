from django.shortcuts import render
from django.http import HttpResponse

from .models import Reve

def home(request):
    #return render (request, 'home.html')
    searchTerm = request. GET.get('searchReve')
    
    if searchTerm:
        reves = Reve.objects.filter(title__icontains = searchTerm)
    else:
        reves = Reve.objects.all()
    return render(request, 'home.html', {'searchTerm' : searchTerm, 'reves': reves} )
 

def about (request):
    return HttpResponse('<h1>Welcome to about home Page </h1>')


# Create your views here.
