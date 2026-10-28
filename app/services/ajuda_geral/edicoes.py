"""Consultas e mutações SQL com escopo do usuário autenticado."""

from sqlalchemy import text

from app.core.clients.postgres import executar_consulta, obter_motor
from app.schemas import UsuarioContexto
from app.schemas.imagem import LIMITE_IMAGENS_POR_MENSAGEM, validar_url_imagem
from app.services.gerais import obter_unidade_id


CAMPOS_EDITAVEIS = {
    "titulo": 100,
    "descricao_problema": 255,
    "descricao_local": 255,
}
CAMPOS_RELACIONAIS = {"categoria_equipamento_id", "local_unidade_id"}
FKS_FOTO = {
    "solicitacao": "problema_id",
    "ocorrencia": "ocorrencia_id",
    "observacao_conclusao": "observacao_conclusao_id",
}


def _validar_id(registro_id: int) -> None:
    if type(registro_id) is not int or registro_id <= 0:
        raise ValueError("O ID do registro deve ser um inteiro positivo.")


def _sql_alvo(tipo: str, usuario: UsuarioContexto) -> str:
    if tipo == "solicitacao":
        return """
            SELECT p.id, p.titulo, p.descricao_problema, p.descricao_local,
                   p.status, p.local_unidade_id, local.nome AS local,
                   p.categoria_equipamento_id, categoria.nome AS categoria_equipamento
            FROM problema AS p
            JOIN local_unidade AS local ON local.id = p.local_unidade_id
            LEFT JOIN categoria_equipamento AS categoria
              ON categoria.id = p.categoria_equipamento_id
            WHERE p.id = :registro_id AND p.usuario_id = :usuario_id
              AND p.status = 0 AND p.esta_ativo IS TRUE
              AND local.unidade_id = :unidade_id AND local.esta_ativo IS TRUE
        """
    if tipo == "ocorrencia" and usuario.tipo_acesso in {"tecnico", "gestor", "administrador"}:
        dono = "AND o.usuario_id = :usuario_id" if usuario.tipo_acesso in {"tecnico", "administrador"} else ""
        return f"""
            SELECT o.id, o.titulo, o.descricao_ocorrencia, local.nome AS local
            FROM ocorrencia AS o
            JOIN local_unidade AS local ON local.id = o.local_unidade_id
            WHERE o.id = :registro_id AND o.esta_ativo IS TRUE
              AND local.unidade_id = :unidade_id AND local.esta_ativo IS TRUE
              {dono}
        """
    if tipo == "observacao_conclusao" and usuario.tipo_acesso in {"tecnico", "gestor", "administrador"}:
        responsavel = "AND os.usuario_id = :usuario_id" if usuario.tipo_acesso in {"tecnico", "administrador"} else ""
        return f"""
            SELECT obs.id, obs.observacao, obs.ordem_servico_id,
                   p.titulo AS titulo_problema, local.nome AS local
            FROM observacao_conclusao AS obs
            JOIN ordem_servico AS os ON os.id = obs.ordem_servico_id
            JOIN problema AS p ON p.id = os.problema_id
            JOIN local_unidade AS local ON local.id = p.local_unidade_id
            WHERE obs.id = :registro_id AND obs.esta_ativo IS TRUE
              AND os.esta_ativo IS TRUE AND p.esta_ativo IS TRUE
              AND local.unidade_id = :unidade_id AND local.esta_ativo IS TRUE
              {responsavel}
        """
    raise PermissionError("Perfil sem acesso a esse tipo de registro.")


async def localizar_registro(usuario: UsuarioContexto, tipo: str, registro_id: int) -> dict | None:
    _validar_id(registro_id)
    unidade_id = await obter_unidade_id(usuario)
    linhas = await executar_consulta(usuario.tipo_acesso, _sql_alvo(tipo, usuario), {
        "registro_id": registro_id,
        "usuario_id": usuario.usuario_id,
        "unidade_id": unidade_id,
    })
    return linhas[0] if linhas else None


async def localizar_opcao(
    usuario: UsuarioContexto, campo: str, identificador: int,
) -> dict | None:
    """Confere o novo local ou categoria ativa na unidade autenticada."""
    _validar_id(identificador)
    unidade_id = await obter_unidade_id(usuario)
    if campo == "local_unidade_id":
        sql = """
            SELECT local.id, local.nome
            FROM local_unidade AS local
            WHERE local.id = :identificador AND local.unidade_id = :unidade_id
              AND local.esta_ativo IS TRUE
        """
    elif campo == "categoria_equipamento_id":
        sql = """
            SELECT categoria.id, categoria.nome
            FROM categoria_equipamento AS categoria
            JOIN usuario AS criador ON criador.id = categoria.usuario_id
            WHERE categoria.id = :identificador AND categoria.esta_ativo IS TRUE
              AND criador.unidade_id = :unidade_id
        """
    else:
        raise ValueError("Campo relacional inválido.")
    linhas = await executar_consulta(usuario.tipo_acesso, sql, {
        "identificador": identificador, "unidade_id": unidade_id,
    })
    return linhas[0] if linhas else None


async def alterar_solicitacao(
    usuario: UsuarioContexto, registro_id: int, campo: str, valor: int | str,
) -> dict | None:
    _validar_id(registro_id)
    if campo not in CAMPOS_EDITAVEIS and campo not in CAMPOS_RELACIONAIS:
        raise ValueError("Campo não permitido para edição.")
    if campo in CAMPOS_RELACIONAIS:
        _validar_id(valor)
    elif not isinstance(valor, str) or not valor.strip() or len(valor.strip()) > CAMPOS_EDITAVEIS[campo]:
        raise ValueError("O novo valor está vazio ou excede o limite do campo.")
    unidade_id = await obter_unidade_id(usuario)
    validacao_destino = ""
    if campo == "local_unidade_id":
        validacao_destino = """
          AND EXISTS (
              SELECT 1 FROM local_unidade AS destino
              WHERE destino.id = :valor AND destino.unidade_id = :unidade_id
                AND destino.esta_ativo IS TRUE
          )
        """
    elif campo == "categoria_equipamento_id":
        validacao_destino = """
          AND EXISTS (
              SELECT 1 FROM categoria_equipamento AS destino
              JOIN usuario AS criador ON criador.id = destino.usuario_id
              WHERE destino.id = :valor AND destino.esta_ativo IS TRUE
                AND criador.unidade_id = :unidade_id
          )
        """
    # O nome da coluna vem da lista fixa; todos os valores são parâmetros SQL.
    sql = text(f"""
        UPDATE problema AS p SET {campo} = :valor, data_atualizacao = NOW()
        FROM local_unidade AS local
        WHERE p.id = :registro_id AND p.usuario_id = :usuario_id
          AND p.local_unidade_id = local.id AND p.status = 0
          AND p.esta_ativo IS TRUE AND local.unidade_id = :unidade_id
          AND local.esta_ativo IS TRUE
          {validacao_destino}
        RETURNING p.id
    """)
    parametros = {
        "registro_id": registro_id, "usuario_id": usuario.usuario_id,
        "unidade_id": unidade_id,
        "valor": valor if campo in CAMPOS_RELACIONAIS else valor.strip(),
    }
    async with obter_motor(usuario.tipo_acesso).begin() as conexao:
        resultado = await conexao.execute(sql, parametros)
        if resultado.first() is None:
            return None
        atualizado = await conexao.execute(
            text(_sql_alvo("solicitacao", usuario)), parametros,
        )
        linha = atualizado.mappings().first()
        return dict(linha) if linha else None


async def anexar_fotos(
    usuario: UsuarioContexto, tipo: str, registro_id: int, urls: list[str],
) -> list[int] | None:
    _validar_id(registro_id)
    if tipo not in FKS_FOTO:
        raise ValueError("Tipo de foto não permitido.")
    if not urls or len(urls) > LIMITE_IMAGENS_POR_MENSAGEM:
        raise ValueError("Envie de uma a três imagens.")
    urls = [validar_url_imagem(url) for url in urls]
    unidade_id = await obter_unidade_id(usuario)
    parametros = {
        "registro_id": registro_id, "usuario_id": usuario.usuario_id,
        "unidade_id": unidade_id,
    }
    tabela = {"solicitacao": "problema", "ocorrencia": "ocorrencia",
              "observacao_conclusao": "observacao_conclusao"}[tipo]
    fk = FKS_FOTO[tipo]
    async with obter_motor(usuario.tipo_acesso).begin() as conexao:
        # Trava a entidade enquanto verifica a autorização e insere as fotos.
        trava = await conexao.execute(text(
            f"SELECT id FROM {tabela} WHERE id = :registro_id FOR UPDATE"
        ), {"registro_id": registro_id})
        if trava.first() is None:
            return None
        alvo = await conexao.execute(text(_sql_alvo(tipo, usuario)), parametros)
        if alvo.first() is None:
            return None
        ids = []
        for url in urls:
            resultado = await conexao.execute(text(
                f"INSERT INTO foto ({fk}, url) VALUES (:registro_id, :url) RETURNING id"
            ), {"registro_id": registro_id, "url": url})
            ids.append(resultado.scalar_one())
    return ids
