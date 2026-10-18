import re
from datetime import date

from pydantic import BaseModel, field_validator


class UsuarioContexto(BaseModel):
    access_token: str
    usuario_id: int
    nome_completo: str
    email: str
    tipo_acesso: str
    cargo: str | None = None
    data_nascimento: date | None = None
    cnpj_endereco: str

    @field_validator("tipo_acesso", mode="before")
    @classmethod
    def normalizar_tipo_acesso(cls, valor: str) -> str:
        if not isinstance(valor, str):
            raise ValueError("O tipo de acesso deve ser um texto.")

        perfil = valor.strip().lower()
        if perfil in {"técnico", "tecnico"}:
            return "tecnico"
        return perfil

    @field_validator("cnpj_endereco")
    @classmethod
    def normalizar_cnpj(cls, valor: str) -> str:
        if not isinstance(valor, str):
            raise ValueError("O CNPJ do endereço deve ser uma string.")

        cnpj = re.sub(r"\D", "", valor)

        if len(cnpj) != 14:
            raise ValueError(
                "O CNPJ do endereço deve possuir 14 dígitos."
            )

        return cnpj
