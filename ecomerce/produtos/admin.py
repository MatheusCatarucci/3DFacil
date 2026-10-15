from django.contrib import admin

from .models import Produto, ProdutoFoto


class ProdutoFotoInline(admin.TabularInline):
    """Permite cadastrar quantas fotos quiser direto na tela do produto."""

    model = ProdutoFoto
    extra = 1
    fields = ['imagem', 'legenda', 'ordem']


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    """Tela de cadastro de produtos do /admin."""

    inlines = [ProdutoFotoInline]

    list_display = ['nome', 'preco', 'estoque', 'qtd_fotos', 'criado_em']
    list_editable = ['preco', 'estoque']
    list_per_page = 25
    search_fields = ['nome', 'descricao']
    readonly_fields = ['criado_em']

    fieldsets = [
        ('Produto', {'fields': ['nome', 'descricao']}),
        ('Preço e estoque', {'fields': ['preco', 'estoque']}),
        ('Sistema', {'fields': ['criado_em']}),
    ]

    @admin.display(description='Fotos')
    def qtd_fotos(self, obj):
        return obj.fotos.count()