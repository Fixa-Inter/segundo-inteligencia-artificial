"""Adapta o perfil validado pela API Web ao contexto da IA."""

from fastapi import HTTPException

from app.core.clients.postgres import executar_consulta


async def completar_perfil(perfil: dict) -> dict:
    tipo = perfil.get("tipoAcesso")
    if isinstance(tipo, dict):
        tipo = tipo.get("nome")
    if not isinstance(tipo, str):
        raise ValueError("Perfil sem tipo de acesso válido.")
    tipo = tipo.strip().lower().replace("técnico", "tecnico")
    if tipo not in {"gestor", "tecnico", "solicitante"}:
        raise HTTPException(403, "Perfil sem permissão de acesso ao chat.")
    usuario_id = perfil.get("id")
    if type(usuario_id) is not int or usuario_id <= 0:
        raise ValueError("Perfil sem usuário válido.")
    cnpj = perfil.get("cnpjUnidade")
    if not cnpj:
        # A identidade vem exclusivamente do perfil autenticado na API FIXA.
        # A API atual não expõe CNPJ no perfil; nunca o recebemos do navegador.
        linhas = await executar_consulta(
            tipo,
            """
            SELECT unidade.cnpj
            FROM usuario
            JOIN unidade ON unidade.id = usuario.unidade_id
            WHERE usuario.id = :usuario_id
              AND usuario.esta_ativo IS TRUE
              AND unidade.esta_ativo IS TRUE
            """,
            {"usuario_id": usuario_id},
        )
        if len(linhas) != 1:
            raise HTTPException(403, "Unidade autenticada não encontrada.")
        cnpj = linhas[0]["cnpj"]
    return {**perfil, "tipoAcesso": tipo, "cnpjUnidade": cnpj}
