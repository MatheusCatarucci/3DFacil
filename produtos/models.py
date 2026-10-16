from django.db import models


# Classe PRODUTO
class Produto(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    estoque = models.IntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


class ProdutoFoto(models.Model):
    """
    Uma foto do produto. Um produto pode ter quantas quiser.

    O campo imagem e um caminho dentro da pasta estatica do projeto
    (ex: img/produtos/capa-hd.jpg). Assim a foto viaja no Git e ja
    entra no deploy pelo collectstatic, sem configurar storage.
    """

    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name='fotos',
        verbose_name='produto',
    )

    # Caminho do arquivo dentro de STATICFILES_DIRS (pasta assets/).
    imagem = models.CharField(
        max_length=200,
        help_text='Ex: img/produtos/capa-hd-01.jpg (arquivo fica em assets/)',
    )

    legenda = models.CharField(max_length=150, blank=True)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordem', 'id']
        verbose_name = 'Foto do produto'
        verbose_name_plural = 'Fotos do produto'

    def __str__(self):
        return self.imagem