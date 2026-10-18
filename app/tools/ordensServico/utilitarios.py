from datetime import date
from html import escape

from app.services.ordensServico.buscarOrdensServico import chave_ordenacao_status


def _celula(valor) -> str:
    if valor is None:
        return "Não informada"
    texto = escape(str(valor), quote=False)
    # Evita que o conteúdo do cadastro crie colunas, linhas, links ou imagens.
    for caractere in ("\\", "`", "*", "_", "[", "]", "|", "~"):
        texto = texto.replace(caractere, f"&#{ord(caractere)};")
    return texto.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>")


def montar_tabelas(ordens: list[dict]) -> str:
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
        linhas = [
            f"### {status}",
            "",
            "| " + " | ".join(titulo for titulo, _ in colunas) + " |",
            "| " + " | ".join("---" for _ in colunas) + " |",
        ]
        for ordem in grupo:
            valores = []
            for _, campo in colunas:
                valor = ordem[campo]
                if campo in {"dataCriacao", "dataPrevista"} and valor is not None:
                    valor = date.fromisoformat(valor).strftime("%d-%m-%Y")
                valores.append(_celula(valor))
            linhas.append("| " + " | ".join(valores) + " |")
        tabelas.append("\n".join(linhas))
    return "\n\n".join(tabelas)


