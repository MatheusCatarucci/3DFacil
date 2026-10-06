from django.shortcuts import render
from .models import Produto

# Create your views here.

def home(request):
    produtos = Produto.objects.all()
    contexto = {"produtos": produtos}
    return render(request, 'home.html', contexto)