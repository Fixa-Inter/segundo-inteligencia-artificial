from langchain_core.tools import tool
from langchain.tools import ToolRuntime
from app.schemas.UsuarioContexto import UsuarioContexto

from app.memory.vectorSearch.recuperar_historico import recuperar_historico

@tool
async def buscar_historico(busca: str, runtime: ToolRuntime) -> str:
    """Consulta conversas ANTERIORES do usuário (sessões já encerradas).

    Use SOMENTE quando a resposta depende de algo dito numa conversa passada
    — preferências, decisões ou planos que o usuário mencionou antes.
    NÃO use para dados que estão no banco (gastos, saldos, eventos): para isso
    já existem as tools de consulta específicas como query_transactions,
    total_balance, daily_balance.

    Args:
        busca: assunto a procurar nos resumos das conversas anteriores.
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
