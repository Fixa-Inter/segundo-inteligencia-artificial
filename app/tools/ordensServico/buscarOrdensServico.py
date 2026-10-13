from datetime import date

from langchain.tools import ToolRuntime, tool
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.UsuarioContexto import UsuarioContexto
from app.services.ordensServico.buscarOrdensServico import buscar_ordens_servico as consultar_ordens
from app.tools.ordensServico.utilitarios import montar_tabelas


class _ArgumentosBuscarOrdensServico(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    status: str | None = Field(default=None, min_length=1, max_length=100, description="Status: Não iniciada, Em andamento, Pausadas ou Finalizadas.")
    prioridade: str | None = Field(default=None, min_length=1, max_length=20, description="Prioridade: ALTA, MEDIA ou BAIXA.")
    categoria_problema: str | None = Field(default=None, min_length=1, max_length=50, description="Categoria do problema mencionada pelo usuario.")
    categoria_equipamento: str | None = Field(default=None, min_length=1, max_length=100, description="Categoria do equipamento mencionada pelo usuario.")
    local: str | None = Field(default=None, min_length=1, max_length=100, description="Nome ou trecho do nome do local.")
    termo: str | None = Field(default=None, min_length=1, max_length=100, description="Termo a procurar no titulo ou descricao do problema.")
    data_criacao_inicio: date | None = Field(default=None, description="Inicio do periodo de criacao, em YYYY-MM-DD.")
    data_criacao_fim: date | None = Field(default=None, description="Fim do periodo de criacao, em YYYY-MM-DD.")
    data_prevista_inicio: date | None = Field(default=None, description="Inicio do periodo previsto, em YYYY-MM-DD.")
    data_prevista_fim: date | None = Field(default=None, description="Fim do periodo previsto, em YYYY-MM-DD.")

    @model_validator(mode="before")
    @classmethod
    def separar_runtime_injetado(cls, dados):
        if isinstance(dados, dict) and isinstance(dados.get("runtime"), ToolRuntime):
            return {chave: valor for chave, valor in dados.items() if chave != "runtime"}
        return dados


@tool(args_schema=_ArgumentosBuscarOrdensServico)
async def buscar_ordem_servico(
    runtime: ToolRuntime,
    status: str | None = None,
    prioridade: str | None = None,
    categoria_problema: str | None = None,
    categoria_equipamento: str | None = None,
    local: str | None = None,
    termo: str | None = None,
    data_criacao_inicio: date | None = None,
    data_criacao_fim: date | None = None,
    data_prevista_inicio: date | None = None,
    data_prevista_fim: date | None = None,
) -> dict:
    """Busca ordens com filtros citados, dentro do escopo autenticado."""
    contexto = runtime.context
    if not isinstance(contexto, dict) or not isinstance(
        contexto.get("usuario"), UsuarioContexto
    ):
        raise ValueError("Forneca UsuarioContexto em context['usuario'].")

    usuario = contexto["usuario"]
    if usuario.tipo_acesso.lower() not in {"tecnico", "gestor"}:
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": "Somente tecnicos e gestores podem consultar ordens de servico.",
        }

    resultado = await consultar_ordens(
        usuario,
        status=status,
        prioridade=prioridade,
        categoria_problema=categoria_problema,
        categoria_equipamento=categoria_equipamento,
        local=local,
        termo=termo,
        data_criacao_inicio=data_criacao_inicio,
        data_criacao_fim=data_criacao_fim,
        data_prevista_inicio=data_prevista_inicio,
        data_prevista_fim=data_prevista_fim,
    )
    if resultado["status"] == "SUCESSO":
        resultado["tabelas_markdown"] = montar_tabelas(resultado["ordens_servico"])
    return resultado
