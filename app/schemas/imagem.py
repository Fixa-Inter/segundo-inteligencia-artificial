"""Limites e validação das URLs de imagens recebidas pelo chat."""

import ipaddress
import re

from pydantic import AnyHttpUrl, TypeAdapter, ValidationError


LIMITE_IMAGENS_POR_MENSAGEM = 3
LIMITE_CARACTERES_URL_IMAGEM = 255

_ADAPTADOR_URL = TypeAdapter(AnyHttpUrl)
_ROTULO_DNS = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\Z")
_SUFIXOS_LOCAIS = (".local", ".localhost", ".internal", ".test", ".invalid")


def validar_url_imagem(valor: str) -> str:
    """Aceita uma URL HTTP(S) de origem pública, sem credenciais ou fragmento."""
    if not isinstance(valor, str):
        raise ValueError("A imagem deve ser uma URL HTTP(S) pública.")
    url = valor.strip()
    if (
        not url
        or len(url) > LIMITE_CARACTERES_URL_IMAGEM
        or "\\" in url
        or any(ord(caractere) < 33 or ord(caractere) == 127 for caractere in url)
    ):
        raise ValueError("A imagem deve ser uma URL HTTP(S) pública de até 255 caracteres.")

    try:
        partes = _ADAPTADOR_URL.validate_python(url)
    except ValidationError as erro:
        raise ValueError("A imagem deve ser uma URL HTTP(S) válida.") from erro

    if partes.username or partes.password or partes.fragment:
        raise ValueError("A URL da imagem não pode conter credenciais ou fragmento.")

    host = (partes.host or "").strip("[]").rstrip(".").lower()
    try:
        endereco = ipaddress.ip_address(host)
    except ValueError:
        try:
            dominio = host.encode("idna").decode("ascii")
        except UnicodeError as erro:
            raise ValueError("A URL da imagem deve ter uma origem pública.") from erro
        if (
            "." not in dominio
            or dominio.endswith(_SUFIXOS_LOCAIS)
            or any(not _ROTULO_DNS.fullmatch(rotulo) for rotulo in dominio.split("."))
        ):
            raise ValueError("A URL da imagem deve ter uma origem pública.")
    else:
        if not endereco.is_global:
            raise ValueError("A URL da imagem deve ter uma origem pública.")

    return url
