"""
Torna a quantidade de itens do carrinho disponivel em todos os
templates, sem cada view ter que calcular.

Registrado em settings.py como
'carrinho.context_processors.carrinho_ativo', o que injetar o
nome total_itens em todo request.
"""

from . import sessao


def carrinho_ativo(request):
    return {'total_itens': sessao.total_itens(request)}