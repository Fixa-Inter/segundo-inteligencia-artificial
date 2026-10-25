from pydantic import BaseModel


class ClassificarProblemaRequest(BaseModel):
    titulo: str
    descricao: str
    categoria_equipamento: str


class ClassificarProblemaResponse(BaseModel):
    problema_classificado: bool
    classificacao: str | None = None
