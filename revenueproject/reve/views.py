from django.shortcuts import render
from django.http import HttpResponse

from .models import Reve

def home(request):
    #return render (request, 'home.html')
    searchTerm = request. GET.get('searchReve')
    reves = Reve.objects.all()
    return render(request, 'home.html', {'searchTerm' : searchTerm, 'reves': reves} )
 




# Create your views here.
