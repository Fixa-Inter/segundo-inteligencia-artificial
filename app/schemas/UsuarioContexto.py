from pydantic import BaseModel
from datetime import date

class UsuarioContexto(BaseModel):
    access_token: str
    usuario_id: int
    gerente_id: int
    endereco_id: int
    nome_completo: str
    tipo_acesso: str
    cargo: str
    data_nascimento: date
    esta_ativo: bool