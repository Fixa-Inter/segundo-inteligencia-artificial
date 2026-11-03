"""Renderização Markdown segura, compartilhada por listagens operacionais."""

from datetime import date
from html import escape

def escapar_celula(valor, *, ausente: str) -> str:
    """Escapa conteúdo cadastrado sem permitir colunas, links ou imagens extras."""
    if valor is None:
        return ausente
    texto = escape(str(valor), quote=False)
    for caractere in ("\\", "`", "*", "_", "[", "]", "|", "~"):
        texto = texto.replace(caractere, f"&#{ord(caractere)};")
    return texto.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>")


def montar_tabela_markdown(registros, colunas, *, campos_data=(), ausente: str, datas_nulas: bool = False) -> str:
    """Renderiza uma tabela sem ordenar/filtrar registros ou definir regras do domínio.

    Ocorrências exigem datas válidas; OS preservam datas ausentes. O chamador
    informa essa política, as colunas e o texto de ausência já usados na tela.
    """
    linhas = [
        "| " + " | ".join(titulo for titulo, _ in colunas) + " |",
        "| " + " | ".join("---" for _ in colunas) + " |",
    ]
    for registro in registros:
        valores = []
        for _, campo in colunas:
            valor = registro[campo]
            if campo in campos_data and (valor is not None or not datas_nulas):
                valor = date.fromisoformat(valor).strftime("%d-%m-%Y")
            valores.append(escapar_celula(valor, ausente=ausente))
        linhas.append("| " + " | ".join(valores) + " |")
    return "\n".join(linhas)
