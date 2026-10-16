from langchain_core.tools import tool
from langchain.tools import ToolRuntime
from app.schemas import UsuarioContexto

from app.memory.vectorSearch.recuperar_historico import recuperar_historico

@tool
async def buscar_historico(busca: str, runtime: ToolRuntime) -> str:
    """Consulta relatos anteriores do usuário, incluindo conversas ainda abertas.

    Use para recordar informações ou decisões mencionadas pelo usuário.
    Resumos históricos não comprovam o estado atual de cadastros; para isso,
    consulte as ferramentas de solicitações, ordens de serviço e ocorrências.
    """
    contexto = runtime.context
    
    if not isinstance(contexto, dict) or not isinstance(contexto.get("usuario"), UsuarioContexto):
        raise ValueError("Forneça uma instância de UsuarioContexto em context['usuario'].")
    
    usuario = contexto["usuario"]

    usuario_id = usuario.usuario_id

    if not usuario_id:
        return "Não foi possível identificar o usuário para buscar o histórico."

    historico = await recuperar_historico(usuario_id=usuario_id, busca=busca, limite=3)

    if not historico:
        return "Nenhuma conversa anterior relevante encontrada."

    linhas = []
    for h in historico:
        data = h["iniciada_em"]
        if hasattr(data, "strftime"):
            data_formatada = data.strftime("%d/%m/%Y")
        else:
            data_formatada = str(data)[:10]
        linhas.append(f"[{data_formatada}] {h['resumo']}")
    return "\n\n".join(linhas)


FERRAMENTAS_MEMORIA = [buscar_historico]
