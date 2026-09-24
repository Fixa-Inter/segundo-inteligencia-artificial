from langchain.tools import ToolRuntime, tool
from pydantic import model_validator

from app.core.config import QDRANT_LOCAL_COLLECTION
from app.schemas.UsuarioContexto import UsuarioContexto
from app.memory.vectorSearch.busca import validar_selecao
from app.core.clients.qdrant import abrir_cliente_qdrant
from app.services.ocorrencias.buscarOcorrencias import buscar_equipamento_por_codigo
from app.services.ocorrencias.criarOcorrencia import adicionar_ocorrencia
from app.tools.toolsRequest.CriarOcorrenciaRequest import CriarOcorrenciaRequest


class _ArgumentosCriarOcorrencia(CriarOcorrenciaRequest):
    @model_validator(mode="before")
    @classmethod
    def separar_runtime_injetado(cls, dados):
        # A integração injeta runtime antes de validar args_schema.
        if isinstance(dados, dict) and isinstance(dados.get("runtime"), ToolRuntime):
            return {chave: valor for chave, valor in dados.items() if chave != "runtime"}
        return dados


@tool(args_schema=_ArgumentosCriarOcorrencia)
async def criar_ocorrencia(
    local_endereco_id: int,
    categoria_problema_id: int,
    titulo: str,
    descricao_ocorrencia: str,
    descricao_local: str,
    prioridade: int,
    runtime: ToolRuntime,
    equipamento_codigo: str | None = None,
) -> dict:
    """Cria uma ocorrência imediatamente, somente após confirmação explícita dos dados.

    Exclusiva para técnico e gestor. Use local consultado, categoria do prompt
    e prioridade alta=0, média=1, baixa=2. O código do equipamento é opcional,
    mas, se informado, deve corresponder a um único equipamento ativo.
    UsuarioId e token vêm do contexto; não peça esses dados ao usuário.
    A tool não gerencia a conversa nem solicita confirmação por conta própria.
    """
    contexto = runtime.context

    if not isinstance(contexto, dict) or not isinstance(contexto.get("usuario"), UsuarioContexto):
        raise ValueError("Forneça uma instância de UsuarioContexto em context['usuario'].")
    
    usuario = contexto["usuario"]

    if usuario.tipo_acesso.lower() not in ("tecnico", "gestor"):
        return {"status": "ACESSO_NEGADO", "mensagem": "Somente técnicos e gestores podem criar ocorrências."}
    
    entrada = CriarOcorrenciaRequest(
        local_endereco_id=local_endereco_id, categoria_problema_id=categoria_problema_id,
        titulo=titulo, descricao_ocorrencia=descricao_ocorrencia,
        descricao_local=descricao_local, prioridade=prioridade,
        equipamento_codigo=equipamento_codigo,
    )

    equipamento_id = None

    if entrada.equipamento_codigo is not None:
        resultado = await buscar_equipamento_por_codigo(entrada.equipamento_codigo, usuario.access_token)
        if resultado["status"] != "SUCESSO":
            return resultado
        equipamento_id = resultado["equipamento"]["id"]

    async with abrir_cliente_qdrant() as client:
        try:
            await validar_selecao(QDRANT_LOCAL_COLLECTION, entrada.local_endereco_id, usuario.cnpj_endereco, client)
        except ValueError:
            return {"status": "ERRO_VALIDACAO", "mensagem": "Local indisponível na sede. Consulte os locais e confirme os dados novamente."}
        
    return await adicionar_ocorrencia(
        entrada, usuario.access_token, usuario_id=usuario.usuario_id, equipamento_id=equipamento_id,
    )
