from django.db.models import Prefetch
from django.shortcuts import render
from django.templatetags.static import static

from .models import Produto, ProdutoFoto


def home(request):
    # to_attr traz a lista de fotos direto no produto e evita uma
    # consulta por produto quando o template mostra a primeira foto.
    fotos = ProdutoFoto.objects.all()

    produtos = list(
        Produto.objects.prefetch_related(
            Prefetch('fotos', queryset=fotos, to_attr='lista_fotos')
        )
    )

    # Dados que o modal do produto usa. Vao para a pagina dentro de
    # uma tag <script type="application/json"> (filtro json_script),
    # que e a forma segura de levar dados ao JavaScript: o Django
    # escapa o conteudo, entao nao da para injetar HTML por cima.
    dados = {
        str(produto.id): {
            'id': produto.id,
            'nome': produto.nome,
            'descricao': produto.descricao,
            'preco': str(produto.preco),
            'estoque': produto.estoque,
            'fotos': [
                {
                    'src': static(foto.imagem),
                    'legenda': foto.legenda,
                }
                for foto in produto.lista_fotos
            ],
        }
        for produto in produtos
    }

    contexto = {
        'produtos': produtos,
        'dados_produtos': dados,
    }
    return render(request, 'home.html', contexto)