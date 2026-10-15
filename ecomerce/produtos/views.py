from django.db.models import Prefetch
from django.shortcuts import render

from .models import Produto, ProdutoFoto


def home(request):
    # to_attr traz a lista de fotos direto no produto e evita uma
    # consulta por produto quando o template mostra a primeira foto.
    fotos = ProdutoFoto.objects.all()

    contexto = {
        'produtos': Produto.objects.prefetch_related(
            Prefetch('fotos', queryset=fotos, to_attr='lista_fotos')
        ),
    }
    return render(request, 'home.html', contexto)