from langchain.tools import ToolRuntime, tool
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.UsuarioContexto import UsuarioContexto
from app.services.feedback.criar_feedback import criar_feedback


class _ArgumentosCriarFeedback(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    comentario: str = Field(
        min_length=1,
        max_length=255,
        description="Comentario original do usuario sobre o aplicativo.",
    )
    ideia_central: str = Field(
        min_length=1,
        max_length=255,
        description=(
            "Categoria e resumo curto do feedback, sem acrescentar fatos que o usuario nao mencionou."
        ),
    )

    @model_validator(mode="before")
    @classmethod
    def separar_runtime_injetado(cls, dados):
        if isinstance(dados, dict) and isinstance(dados.get("runtime"), ToolRuntime):
            return {chave: valor for chave, valor in dados.items() if chave != "runtime"}
        return dados


@tool(args_schema=_ArgumentosCriarFeedback)
async def criar_nome_feedback(
    comentario: str,
    ideia_central: str,
    runtime: ToolRuntime,
) -> dict:
    """Registra feedback. A identidade e o perfil vêm do contexto autenticado."""
    contexto = runtime.context
    if not isinstance(contexto, dict) or not isinstance(
        contexto.get("usuario"), UsuarioContexto
    ):
        raise ValueError("Forneca UsuarioContexto em context['usuario'].")

    usuario = contexto["usuario"]
    return await criar_feedback(
        usuario=usuario,
        comentario=comentario,
        ideia_central=ideia_central,
    )
