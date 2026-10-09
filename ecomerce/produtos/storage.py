"""
Storage backend que salva os arquivos no Supabase Storage
usando o client oficial do Supabase.

Usa o client em vez da API S3 porque as chaves novas
(sb_secret_...) so funcionam na API do Supabase, nao como
credencial S3.
"""

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import Storage


class SupabaseStorage(Storage):
    """Bucket publico do Supabase Storage."""

    def __init__(self):
        self.bucket = settings.SUPABASE_STORAGE_BUCKET

        from supabase import create_client

        self.client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SECRET_KEY,
        )

    # ------------------------------------------------------------
    # LEITURA
    # ------------------------------------------------------------

    def _open(self, name, mode="rb"):
        dados = self.client.storage.from_(self.bucket).download(name)
        return ContentFile(dados)

    def _save(self, name, content):
        nome_final = self.get_available_name(name, max_length=200)

        # O storage do Supabase exige bytes.
        # ContentFile ja entrega o arquivo com .read() e .name.
        self.client.storage.from_(self.bucket).upload(
            nome_final,
            content.read(),
        )

        return nome_final

    # ------------------------------------------------------------
    # URL
    # ------------------------------------------------------------

    def url(self, name):
        """
        URL publica do arquivo.

        Usa o metodo do proprio client, que ja devolve o caminho
        do bucket publico, em vez de assinar uma URL temporaria.
        """
        return self.client.storage.from_(self.bucket).get_public_url(name)

    def exists(self, name):
        # Listar a pasta do arquivo e mais barato que baixar ele.
        pasta, _, arquivo = name.rpartition("/")

        arquivos = self.client.storage.from_(self.bucket).list(pasta or None)
        return any(item.get("name") == arquivo for item in arquivos)

    def delete(self, name):
        self.client.storage.from_(self.bucket).remove([name])