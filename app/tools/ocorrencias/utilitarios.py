from datetime import date
from html import escape
from app.core import escapar_celula, montar_tabela_markdown

def _celula(valor) -> str:
    """Compatibilidade da célula com o texto de ausência deste domínio."""
    return escapar_celula(valor, ausente='Não informado')


def montar_tabela(ocorrencias: list[dict]) -> str:
    """Apresenta as ocorrências na mesma ordem retornada pela API."""
    colunas = (
        ("Título", "titulo"),
        ("Descrição", "descricaoOcorrencia"),
        ("Categoria do Problema", "categoriaProblema"),
        ("Prioridade", "prioridade"),
        ("Local", "localEndereco"),
        ("Descrição do Local", "descricaoLocal"),
        ("Data de criação", "dataCriacao"),
        ("Código do equipamento", "equipamentoCodigo"),
    )
    return montar_tabela_markdown(
        ocorrencias, colunas, campos_data=("dataCriacao",), ausente="Não informado",
    )
