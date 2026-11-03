"""Enums e ordenação compartilhados das consultas de manutenção; sem acesso a bancos."""

import unicodedata

# ORDEM_PRIORIDADE: Recurso compartilhado de ordem prioridade usado pelas funções deste módulo e pela interface pública.
ORDEM_PRIORIDADE = ("ALTA", "MEDIA", "BAIXA")

# PRIORIDADE_POR_ID: Mapeamento entre códigos e rótulos do contrato de manutenção.
PRIORIDADE_POR_ID = {0: "ALTA", 1: "MEDIA", 2: "BAIXA"}

# STATUS_ORDEM_SERVICO_POR_ID: Estados reconhecidos no fluxo deste domínio; usados para validar continuidade e execução.
STATUS_ORDEM_SERVICO_POR_ID = {
    0: "Não Iniciada",
    1: "Atrasada",
    2: "Pausada",
    3: "Em andamento",
    4: "Concluída",
}

# CATEGORIA_PROBLEMA_POR_ID: Mapeamento entre códigos e rótulos do contrato de manutenção.
CATEGORIA_PROBLEMA_POR_ID = {
    1: "Elétrica",
    2: "Hidráulica",
    3: "Mecânica",
    4: "Informática",
    5: "Mobiliário",
    6: "Climatização",
    7: "Rede e Conectividade",
    8: "Segurança",
    9: "Iluminação",
    10: "Limpeza e Conservação",
}

def _normalizar_filtro(valor: str) -> str:
    """Normaliza rótulos de enum para comparação dos filtros operacionais. Usado por chave_ordenacao_status."""
    texto = unicodedata.normalize("NFD", valor.strip().upper())
    return "".join(caractere for caractere in texto if unicodedata.category(caractere) != "Mn")

# _ID_POR_CATEGORIA_PROBLEMA: Mapeamento entre códigos e rótulos do contrato de manutenção.
_ID_POR_CATEGORIA_PROBLEMA = {
    _normalizar_filtro(nome): identificador
    for identificador, nome in CATEGORIA_PROBLEMA_POR_ID.items()
}

# _ID_POR_PRIORIDADE: Mapeamento entre códigos e rótulos do contrato de manutenção.
_ID_POR_PRIORIDADE = {
    _normalizar_filtro(nome): identificador
    for identificador, nome in PRIORIDADE_POR_ID.items()
}

# _ID_POR_STATUS: Mapeamento entre códigos e rótulos do contrato de manutenção.
_ID_POR_STATUS = {_normalizar_filtro(nome): codigo for codigo, nome in STATUS_ORDEM_SERVICO_POR_ID.items()}

_ID_POR_STATUS.update({
    "NAO INICIADAS": 0,
    "FINALIZADAS": 4,
})

def chave_ordenacao_status(status: str) -> tuple[int, str]:
    """Ordena pelos status definidos no enum da ordem de serviço."""
    nome = _normalizar_filtro(status)
    return (_ID_POR_STATUS.get(nome, 5), nome)
