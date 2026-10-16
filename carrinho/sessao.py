"""
Logica do carrinho guardada na sessao.

O carrinho fica em request.session como um dicionario
{ id_do_produto: quantidade }. Nao ha tabela no banco: a sessao
ja resolve quem e o comprador sem precisar de login, e some
so quando o navegador fecha.

Formato guardado:

    {"itens": {"3": 2, "7": 1}}
"""

CHAVE = 'carrinho'


def obter_itens(request):
    """Devolve { id_produto: quantidade } a partir da sessao."""
    carrinho = request.session.get(CHAVE) or {}
    itens = carrinho.get('itens') or {}

    # Converte as chaves de texto (JSON) para inteiro.
    return {int(id_produto): int(quantidade) for id_produto, quantidade in itens.items()}


def gravar_itens(request, itens):
    """Salva o dicionario de itens na sessao."""
    request.session[CHAVE] = {'itens': {str(k): v for k, v in itens.items()}}
    request.session.modified = True


def adicionar(request, produto, quantidade=1):
    """
    Acrescenta o produto ao carrinho, respeitando o estoque.

    Devolve a quantidade final do item no carrinho.
    """
    itens = obter_itens(request)
    atual = itens.get(produto.id, 0)

    nova = min(atual + quantidade, produto.estoque)

    if nova <= 0:
        itens.pop(produto.id, None)
    else:
        itens[produto.id] = nova

    gravar_itens(request, itens)
    return nova


def definir_quantidade(request, produto_id, quantidade, estoque):
    """Fixa a quantidade de um item. Quantidade zero remove o item."""
    itens = obter_itens(request)

    quantidade = max(0, min(int(quantidade), estoque))

    if quantidade == 0:
        itens.pop(produto_id, None)
    else:
        itens[produto_id] = quantidade

    gravar_itens(request, itens)
    return quantidade


def remover(request, produto_id):
    """Tira o produto do carrinho."""
    itens = obter_itens(request)
    itens.pop(produto_id, None)
    gravar_itens(request, itens)


def total_itens(request):
    """Quantidade de peças no carrinho (para o badge do menu)."""
    return sum(obter_itens(request).values())


def limpar(request):
    """Esvazia o carrinho."""
    request.session.pop(CHAVE, None)
    request.session.modified = True