from langchain.tools import ToolRuntime, tool

from app.schemas.UsuarioContexto import UsuarioContexto
from app.memory.vectorSearch.busca import buscar_local_endereco
from app.memory.vectorSearch.cliente import abrir_cliente_qdrant
from app.services.ocorrencias.buscarOcorrencias import buscar_equipamento_por_codigo


@tool
async def buscar_opcoes_ocorrencia(
    local: str, runtime: ToolRuntime, equipamento_codigo: str | None = None,
) -> dict:
    """Busca locais da sede e, se informado, resolve o código de um equipamento ativo.

    Exclusiva de técnicos e gestores. Informe a descrição do local e somente
    o código explicitamente fornecido pelo usuário. Resultados de local são
    candidatos; esclareça ambiguidades antes de pedir confirmação do cadastro.
    """
    contexto = runtime.context

    if not isinstance(contexto, dict) or not isinstance(contexto.get("usuario"), UsuarioContexto):
        raise ValueError("Forneça uma instância de UsuarioContexto em context['usuario'].")
    
    usuario = contexto["usuario"]

    if usuario.tipo_acesso.lower() not in ("tecnico", "gestor"):
        return {"status": "ACESSO_NEGADO", "mensagem": "Somente técnicos e gestores podem preparar ocorrências."}
    
    equipamento = None

    if equipamento_codigo is not None:
        resultado = await buscar_equipamento_por_codigo(equipamento_codigo, usuario.access_token)
        if resultado["status"] != "SUCESSO":
            return resultado
        equipamento = resultado["equipamento"]

    async with abrir_cliente_qdrant() as client:
        locais = await buscar_local_endereco(local, usuario.cnpj_endereco, client)
        
    return {
        "status": "SUCESSO" if locais else "AGUARDANDO_INFORMACAO",
        "locais": {str(chave): descricao for chave, descricao in locais.items()},
        "equipamento": equipamento,
        "mensagem": "Revise os candidatos com o usuário antes do cadastro." if locais else "Nenhum local correspondente encontrado. Peça mais detalhes do local.",
    }
