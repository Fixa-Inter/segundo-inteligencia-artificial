from html import escape

from langchain.tools import ToolRuntime, tool

from app.schemas.UsuarioContexto import UsuarioContexto
from app.services.ordensServico.buscarOrdensServico import (
    ORDEM_STATUS,
    consultar_minhas_ordens_servico,
)


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
        ("Data prevista", "dataPrevista"),
        ("Prioridade", "prioridade"),
    )
    tabelas = []
    for status in ORDEM_STATUS:
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
            linhas.append("| " + " | ".join(_celula(ordem[campo]) for _, campo in colunas) + " |")
        tabelas.append("\n".join(linhas))
    return "\n\n".join(tabelas)


@tool
async def listar_minhas_ordens_servico(runtime: ToolRuntime) -> dict:
    """Lista as OSs do técnico ou gestor autenticado, criadas nos últimos três meses.

    Não recebe argumentos da IA. Usa context['usuario'] e seu Bearer token.
    Retorna uma tabela Markdown por status, na ordem ATRASADA, PENDENTE,
    EM ANDAMENTO, CONCLUIDA; em cada grupo, prioridade 0, 1 e 2.
    Apresente integralmente o campo tabelas_markdown na resposta ao usuário,
    preservando as oito colunas e a ordenação. Data prevista nula aparece como
    Não informada. Informe também o período consultado; não invente OSs.
    """
    contexto = runtime.context

    if not isinstance(contexto, dict) or not isinstance(contexto.get("usuario"), UsuarioContexto):
        raise ValueError("Forneça uma instância de UsuarioContexto em context['usuario'].")
    
    usuario = contexto["usuario"]

    if usuario.tipo_acesso.lower() not in ("tecnico", "gestor"):
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": "Somente técnicos e gestores podem consultar suas ordens de serviço.",
        }
    
    resultado = await consultar_minhas_ordens_servico(usuario.access_token)

    if resultado["status"] == "SUCESSO":
        resultado["tabelas_markdown"] = montar_tabelas(resultado["ordens_servico"])
        
    return resultado
