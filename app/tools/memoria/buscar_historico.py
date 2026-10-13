from langchain_core.tools import tool
from langchain.tools import ToolRuntime
from app.schemas.UsuarioContexto import UsuarioContexto

from app.memory.vectorSearch.recuperar_historico import recuperar_historico

@tool
async def buscar_historico(busca: str, runtime: ToolRuntime) -> str:
    """Consulta relatos anteriores do usuário, incluindo conversas ainda abertas.

    Use para recordar informações ou decisões mencionadas pelo usuário.
    Resumos históricos não comprovam o estado atual de cadastros; para isso,
    consulte as tools de solicitações, ordens de serviço e ocorrências.
    """
    contexto = runtime.context
    
    if not isinstance(contexto, dict) or not isinstance(contexto.get("usuario"), UsuarioContexto):
        raise ValueError("Forneça uma instância de UsuarioContexto em context['usuario'].")
    
    usuario = contexto["usuario"]

    user_id = usuario.usuario_id

    if not user_id:
        return "Não foi possível identificar o usuário para buscar o histórico."

    historico = await recuperar_historico(user_id=user_id, busca=busca, limite=3)

    if not historico:
        return "Nenhuma conversa anterior relevante encontrada."

    linhas = []
    for h in historico:
        data = h["iniciada_em"]
        if hasattr(data, "strftime"):
            data_fmt = data.strftime("%d/%m/%Y")
        else:
            data_fmt = str(data)[:10]
        linhas.append(f"[{data_fmt}] {h['resumo']}")
    return "\n\n".join(linhas)


TOOLS_MEMORIA = [buscar_historico]
