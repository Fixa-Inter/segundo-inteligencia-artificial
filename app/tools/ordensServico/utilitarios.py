from datetime import date
from html import escape
from app.core import chave_ordenacao_status, escapar_celula, montar_tabela_markdown

def _celula(valor) -> str:
    """Compatibilidade da célula com o texto de ausência deste domínio."""
    return escapar_celula(valor, ausente='Não informada')


def montar_tabelas(ordens: list[dict]) -> str:
    """Agrupa OS por status e renderiza tabelas seguras, preservando a ordem de cada grupo."""
    colunas = (
        ("Título", "titulo"),
        ("Descrição do problema", "descricaoProblema"),
        ("Local", "local"),
        ("Descrição do local", "descricaoLocal"),
        ("Status", "statusOrdemServico"),
        ("Categoria do problema", "categoriaProblema"),
        ("Categoria do equipamento", "categoriaEquipamento"),
        ("Data de criação", "dataCriacao"),
        ("Data prevista", "dataPrevista"),
        ("Prioridade", "prioridade"),
    )
    if ordens and "categoriaEquipamento" not in ordens[0]:
        colunas = tuple(
            coluna for coluna in colunas if coluna[1] != "categoriaEquipamento"
        )
    tabelas = []
    status_encontrados = sorted(
        {ordem["statusOrdemServico"] for ordem in ordens},
        key=chave_ordenacao_status,
    )
    for status in status_encontrados:
        grupo = [ordem for ordem in ordens if ordem["statusOrdemServico"] == status]
        if not grupo:
            continue
        tabela = montar_tabela_markdown(
            grupo, colunas, campos_data=("dataCriacao", "dataPrevista"),
            ausente="Não informada", datas_nulas=True,
        )
        tabelas.append(f"### {status}\n\n{tabela}")
    return "\n\n".join(tabelas)
