from datetime import date
from html import escape


def _celula(valor) -> str:
    if valor is None:
        return "Não informado"
    texto = escape(str(valor), quote=False)
    for caractere in ("\\", "`", "*", "_", "[", "]", "|", "~"):
        texto = texto.replace(caractere, f"&#{ord(caractere)};")
    return texto.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>")


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
    linhas = [
        "| " + " | ".join(titulo for titulo, _ in colunas) + " |",
        "| " + " | ".join("---" for _ in colunas) + " |",
    ]
    for ocorrencia in ocorrencias:
        valores = []
        for _, campo in colunas:
            valor = ocorrencia[campo]
            if campo == "dataCriacao":
                valor = date.fromisoformat(valor).strftime("%d-%m-%Y")
            valores.append(_celula(valor))
        linhas.append("| " + " | ".join(valores) + " |")
    return "\n".join(linhas)
