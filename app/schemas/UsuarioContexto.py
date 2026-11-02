import re
from datetime import date

from pydantic import BaseModel, field_validator

from app.core.respostas import MENSAGENS


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
            raise ValueError(MENSAGENS['o_tipo_de_acesso_deve_ser_um_texto'])

        perfil = valor.strip().lower()
        if perfil in {"técnico", "tecnico"}:
            return "tecnico"
        return perfil

    @field_validator("cnpj_endereco")
    @classmethod
    def normalizar_cnpj(cls, valor: str) -> str:
        if not isinstance(valor, str):
            raise ValueError(MENSAGENS['o_cnpj_do_endereco_deve_ser_uma_string'])

        cnpj = re.sub(r"\D", "", valor)

        if len(cnpj) != 14:
            raise ValueError(
                MENSAGENS['o_cnpj_do_endereco_deve_possuir_14_digitos']
            )

        return cnpj
