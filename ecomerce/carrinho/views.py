from decimal import Decimal
from urllib.parse import quote

from django.contrib import messages
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static

from produtos.models import Produto, ProdutoFoto

from . import sessao

WHATSAPP = 'https://wa.me/5519998742782'


def _eh_ajax(request):
    """A chamada veio do fetch do navegador, e nao de um form comum."""
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def _montar_itens(request):
    """
    Cruza os ids guardados na sessao com os produtos do banco.

    Devolve tambem o total. Produto removido do catalogo ou com
    estoque zerado e descartado do carrinho na hora, para nao
    sobrar item orfao.
    """
    quantidades = sessao.obter_itens(request)

    if not quantidades:
        return [], Decimal('0.00')

    # prefetch_related evita uma consulta de imagem por item na
    # hora de montar o card do carrinho.
    produtos = Produto.objects.filter(id__in=quantidades.keys()).prefetch_related(
        Prefetch(
            'fotos',
            queryset=ProdutoFoto.objects.all(),
            to_attr='lista_fotos',
        )
    )
    por_id = {produto.id: produto for produto in produtos}

    itens = []
    total = Decimal('0.00')
    orfaos = []

    for produto_id, quantidade in quantidades.items():
        produto = por_id.get(produto_id)

        # Some com o que nao existe mais ou ficou sem estoque.
        if produto is None or produto.estoque <= 0:
            orfaos.append(produto_id)
            continue

        # Garante que a quantidade nao passou do estoque atual.
        quantidade = min(quantidade, produto.estoque)

        subtotal = produto.preco * quantidade
        total += subtotal

        itens.append({
            'produto': produto,
            'quantidade': quantidade,
            'subtotal': subtotal,
            'foto': (
                static(produto.lista_fotos[0].imagem)
                if produto.lista_fotos
                else static('img/bulldog_cube.png')
            ),
        })

    if orfaos:
        restantes = {k: v for k, v in quantidades.items() if k not in orfaos}
        sessao.gravar_itens(request, restantes)

    return itens, total


def _link_whatsapp(itens, total):
    """Monta o texto do pedido para enviar pelo WhatsApp."""
    if not itens:
        return WHATSAPP

    linhas = [
        f'{item["quantidade"]}x {item["produto"].nome} - '
        f'R$ {item["subtotal"]:.2f}'
        for item in itens
    ]

    texto = '\n'.join(linhas + ['', f'Total: R$ {total:.2f}'])

    return f'{WHATSAPP}?text={quote(texto)}'


def index(request):
    itens, total = _montar_itens(request)

    contexto = {
        'itens': itens,
        'total': total,
        'total_itens': sessao.total_itens(request),
        'link_whatsapp': _link_whatsapp(itens, total),
    }
    return render(request, 'carrinho.html', contexto)


def adicionar(request, produto_id):
    """
    Recebe o POST do botao Comprar.

    Chamado por JavaScript devolve JSON e a pagina nao recarrega,
    com a notificacao aparecendo no lugar. Chamado por um form
    comum (sem JavaScript) continua redirecionando para o
    carrinho, entao o botao nunca fica sem funcao.
    """
    produto = get_object_or_404(Produto, pk=produto_id)

    # Aceita so POST: mudar o carrinho por GET permitiria que um
    # link malicioso adicionasse produtos So de ser clicado.
    if request.method != 'POST':
        return redirect('carrinho:index')

    ajax = _eh_ajax(request)

    if produto.estoque <= 0:
        texto = f'"{produto.nome}" está sem estoque.'

        if ajax:
            return JsonResponse(
                {'ok': False, 'mensagem': texto},
                status=400,
            )

        messages.error(request, texto)
        return redirect('carrinho:index')

    quantidade = sessao.adicionar(request, produto)

    if quantidade:
        texto = f'"{produto.nome}" foi para o carrinho.'
    else:
        texto = 'Não foi possível adicionar o produto.'

    if ajax:
        return JsonResponse({
            'ok': bool(quantidade),
            'mensagem': texto,
            'total_itens': sessao.total_itens(request),
            'quantidade': quantidade,
            'estoque': produto.estoque,
        })

    if quantidade:
        messages.success(request, texto)
    else:
        messages.error(request, texto)

    return redirect('carrinho:index')


def atualizar(request, produto_id):
    """Grava a nova quantidade digitada na pagina do carrinho."""
    produto = get_object_or_404(Produto, pk=produto_id)

    if request.method != 'POST':
        return redirect('carrinho:index')

    try:
        quantidade = int(request.POST.get('quantidade', 1))
    except (TypeError, ValueError):
        quantidade = 1

    sessao.definir_quantidade(request, produto.id, quantidade, produto.estoque)

    return redirect('carrinho:index')


def remover(request, produto_id):
    """Tira o item do carrinho."""
    if request.method != 'POST':
        return redirect('carrinho:index')

    produto = get_object_or_404(Produto, pk=produto_id)

    sessao.remover(request, produto.id)
    messages.success(request, f'"{produto.nome}" saiu do carrinho.')

    return redirect('carrinho:index')


def esvaziar(request):
    """Limpa o carrinho inteiro."""
    if request.method != 'POST':
        return redirect('carrinho:index')

    sessao.limpar(request)
    messages.success(request, 'Carrinho esvaziado.')

    return redirect('carrinho:index')