"""Limites e validação das URLs de imagens recebidas pelo chat."""

import ipaddress
import re
from pydantic import AnyHttpUrl, TypeAdapter, ValidationError
from app.core import MENSAGENS

# LIMITE_IMAGENS_POR_MENSAGEM: Limite operacional/contratual usado pela validação e pelo processamento deste módulo.
LIMITE_IMAGENS_POR_MENSAGEM = 3
# LIMITE_CARACTERES_URL_IMAGEM: Limite operacional/contratual usado pela validação e pelo processamento deste módulo.
LIMITE_CARACTERES_URL_IMAGEM = 255

# _ADAPTADOR_URL: Recurso compartilhado de adaptador url usado pelas funções deste módulo e pela interface pública.
_ADAPTADOR_URL = TypeAdapter(AnyHttpUrl)
# _ROTULO_DNS: Recurso compartilhado de rotulo dns usado pelas funções deste módulo e pela interface pública.
_ROTULO_DNS = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\Z")
# _SUFIXOS_LOCAIS: Recurso compartilhado de sufixos locais usado pelas funções deste módulo e pela interface pública.
_SUFIXOS_LOCAIS = (".local", ".localhost", ".internal", ".test", ".invalid")


def validar_url_imagem(valor: str) -> str:
    """Aceita uma URL HTTP(S) de origem pública, sem credenciais ou fragmento."""
    # Validação: rejeita entrada/contexto incompatível antes de prosseguir.
    if not isinstance(valor, str):
        raise ValueError(MENSAGENS['a_imagem_deve_ser_uma_url_http_s_publica'])
    url = valor.strip()
    if (
        not url
        or len(url) > LIMITE_CARACTERES_URL_IMAGEM
        or "\\" in url
        or any(ord(caractere) < 33 or ord(caractere) == 127 for caractere in url)
    ):
        raise ValueError(MENSAGENS['a_imagem_deve_ser_uma_url_http_s_publica_de_ate_255'])

    # Lógica: executa esta etapa e preserva o tratamento de falhas do domínio.
    try:
        partes = _ADAPTADOR_URL.validate_python(url)
    except ValidationError as erro:
        raise ValueError(MENSAGENS['a_imagem_deve_ser_uma_url_http_s_valida']) from erro

    if partes.username or partes.password or partes.fragment:
        raise ValueError(MENSAGENS['a_url_da_imagem_nao_pode_conter_credenciais_ou_fragmento'])

    host = (partes.host or "").strip("[]").rstrip(".").lower()
    try:
        endereco = ipaddress.ip_address(host)
    except ValueError:
        try:
            dominio = host.encode("idna").decode("ascii")
        except UnicodeError as erro:
            raise ValueError(MENSAGENS['a_url_da_imagem_deve_ter_uma_origem_publica']) from erro
        if (
            "." not in dominio
            or dominio.endswith(_SUFIXOS_LOCAIS)
            or any(not _ROTULO_DNS.fullmatch(rotulo) for rotulo in dominio.split("."))
        ):
            raise ValueError(MENSAGENS['a_url_da_imagem_deve_ter_uma_origem_publica'])
    else:
        if not endereco.is_global:
            raise ValueError(MENSAGENS['a_url_da_imagem_deve_ter_uma_origem_publica'])

    return url
