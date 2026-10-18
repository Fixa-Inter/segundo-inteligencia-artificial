from langchain.tools import ToolRuntime, tool

from app.schemas import UsuarioContexto
from app.services.ordensServico import (
    consultar_minhas_ordens_servico,
)
from app.tools.ordensServico.utilitarios import montar_tabelas


@tool
async def listar_minhas_ordens_servico(runtime: ToolRuntime) -> dict:
    """Lista OS do tecnico ou gestor autenticado nos ultimos tres meses.

Nao recebe argumentos da IA. O SELECT filtra usuario, CNPJ e periodo.
Apresente a tabela Markdown e o periodo retornado sem inventar ordens."""
    contexto = runtime.context

    if not isinstance(contexto, dict) or not isinstance(contexto.get("usuario"), UsuarioContexto):
        raise ValueError("Forneça uma instância de UsuarioContexto em context['usuario'].")
    
    usuario = contexto["usuario"]

    if usuario.tipo_acesso.lower() not in ("tecnico", "gestor"):
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": "Somente técnicos e gestores podem consultar suas ordens de serviço.",
        }
    
    resultado = await consultar_minhas_ordens_servico(usuario)

    if resultado["status"] == "SUCESSO":
        resultado["tabelas_markdown"] = montar_tabelas(resultado["ordens_servico"])
        
    return resultado
