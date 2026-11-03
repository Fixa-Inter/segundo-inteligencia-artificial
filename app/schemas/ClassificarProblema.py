from pydantic import BaseModel

# ClassificarProblemaRequest: contrato/estrutura de ClassificarProblema; usado pelos consumidores desta interface.
class ClassificarProblemaRequest(BaseModel):
    titulo: str
    descricao: str
    categoria_equipamento: str


# ClassificarProblemaResponse: contrato/estrutura de ClassificarProblema; usado pelos consumidores desta interface.
class ClassificarProblemaResponse(BaseModel):
    problema_classificado: bool
    classificacao: str | None = None
