"""Resolução de interfaces públicas sem importar antecipadamente os domínios."""

from importlib import import_module

def resolver_exportacao(nome: str, pacote: str, exportacoes: dict, namespace: dict):
    """Resolve um símbolo do __init__; usado pelas fachadas para evitar ciclos.

    O mapa explícito associa o nome público ao módulo proprietário e ao nome
    original. Importlib reutiliza o módulo, mantendo a identidade dos objetos.
    Valores não são copiados: substituições no proprietário continuam visíveis.
    """
    # Validação: nomes fora da interface não provocam importações arbitrárias.
    if nome not in exportacoes:
        raise AttributeError(f"{pacote} não exporta {nome!r}.")
    modulo, atributo = exportacoes[nome]
    # Lógica: o pacote só importa o proprietário quando o recurso é solicitado.
    origem = import_module(modulo, pacote)
    valor = origem if atributo is None else getattr(origem, atributo)
    # Python registra submódulos no pacote pai. Se o nome público coincide com
    # o arquivo (salvar_mensagem, por exemplo), restaura o símbolo, não o módulo.
    if nome == modulo.rsplit('.', 1)[-1] and atributo is not None:
        namespace[nome] = valor
    return valor
