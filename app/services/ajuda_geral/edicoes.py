"""Consultas e mutações SQL com escopo do usuário autenticado."""

from sqlalchemy import text
from app.core.clients import executar_consulta, obter_motor
from app.schemas import UsuarioContexto, LIMITE_IMAGENS_POR_MENSAGEM, validar_url_imagem
from app.services.gerais import obter_unidade_id
from app.core import MENSAGENS

# CAMPOS_EDITAVEIS: Recurso compartilhado de campos editaveis usado pelas funções deste módulo e pela interface pública.
CAMPOS_EDITAVEIS = {
    "titulo": 100,
    "descricao_problema": 255,
    "descricao_local": 255,
}
# CAMPOS_RELACIONAIS: Recurso compartilhado de campos relacionais usado pelas funções deste módulo e pela interface pública.
CAMPOS_RELACIONAIS = {"categoria_equipamento_id", "local_unidade_id"}
# FKS_FOTO: Recurso compartilhado de fks foto usado pelas funções deste módulo e pela interface pública.
FKS_FOTO = {
    "solicitacao": "problema_id",
    "ocorrencia": "ocorrencia_id",
    "observacao_conclusao": "observacao_conclusao_id",
}


def _validar_id(registro_id: int) -> None:
    """Rejeita identificadores de registro incompatíveis com o contrato. Usado por alterar_solicitacao, anexar_fotos, localizar_opcao."""
    if type(registro_id) is not int or registro_id <= 0:
        raise ValueError(MENSAGENS['o_id_do_registro_deve_ser_um_inteiro_positivo'])


def _sql_alvo(tipo: str, usuario: UsuarioContexto) -> str:
    """Seleciona consulta de alvo com autoria, unidade e atividade autorizadas. Usado por alterar_solicitacao, anexar_fotos, localizar_registro."""
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
        return """
            SELECT o.id, o.titulo, o.descricao_ocorrencia, o.descricao_local,
                   o.local_unidade_id, o.categoria_equipamento_id, o.categoria_problema,
                   o.prioridade, local.nome AS local, categoria.nome AS categoria_equipamento
            FROM ocorrencia AS o
            JOIN local_unidade AS local ON local.id = o.local_unidade_id
            LEFT JOIN categoria_equipamento AS categoria ON categoria.id = o.categoria_equipamento_id
            WHERE o.id = :registro_id AND o.usuario_id = :usuario_id AND o.esta_ativo IS TRUE
              AND local.unidade_id = :unidade_id AND local.esta_ativo IS TRUE
        """
    if tipo == "observacao_conclusao" and usuario.tipo_acesso in {"tecnico", "gestor", "administrador"}:
        responsavel = "AND os.usuario_id = :usuario_id" if usuario.tipo_acesso == "tecnico" else ""
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
    raise PermissionError(MENSAGENS['perfil_sem_acesso_a_esse_tipo_de_registro'])


async def localizar_registro(usuario: UsuarioContexto, tipo: str, registro_id: int) -> dict | None:
    """Confere existência e autorização do alvo de edição/anexo. Usado pelo fluxo de ajuda_geral."""
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
    *, conexao=None,
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
        raise ValueError(MENSAGENS['campo_relacional_invalido'])
    parametros = {"identificador": identificador, "unidade_id": unidade_id}
    if conexao is None:
        linhas = await executar_consulta(usuario.tipo_acesso, sql, parametros)
    else:
        resultado = await conexao.execute(text(sql), parametros)
        linhas = resultado.mappings().all()
    return linhas[0] if linhas else None


async def alterar_solicitacao(
    usuario: UsuarioContexto, registro_id: int, campo: str, valor: int | str,
) -> dict | None:
    """Altera um campo permitido de solicitação própria pendente em transação. Usado pelo fluxo de ajuda_geral."""
    _validar_id(registro_id)
    # Validação: rejeita entrada/contexto incompatível antes de prosseguir.
    if campo not in CAMPOS_EDITAVEIS and campo not in CAMPOS_RELACIONAIS:
        raise ValueError(MENSAGENS['campo_nao_permitido_para_edicao'])
    if campo in CAMPOS_RELACIONAIS:
        _validar_id(valor)
    elif not isinstance(valor, str) or not valor.strip() or len(valor.strip()) > CAMPOS_EDITAVEIS[campo]:
        raise ValueError(MENSAGENS['o_novo_valor_esta_vazio_ou_excede_o_limite_do_campo'])
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
    # Lógica: executa esta etapa e preserva o tratamento de falhas do domínio.
    async with obter_motor(usuario.tipo_acesso).begin() as conexao:
        resultado = await conexao.execute(sql, parametros)
        if resultado.first() is None:
            return None
        atualizado = await conexao.execute(
            text(_sql_alvo("solicitacao", usuario)), parametros,
        )
        linha = atualizado.mappings().first()
        # O UPDATE já confirmou a alteração. A falta de detalhes na releitura
        # não transforma essa gravação em uma recusa.
        return dict(linha) if linha else {"id": registro_id}


async def anexar_fotos(
    usuario: UsuarioContexto, tipo: str, registro_id: int, urls: list[str],
) -> list[int] | None:
    """Insere vínculos de foto após conferir/travar o registro autorizado na transação. Usado pelo fluxo de ajuda_geral."""
    _validar_id(registro_id)
    if tipo not in FKS_FOTO:
        raise ValueError(MENSAGENS['tipo_de_foto_nao_permitido'])
    if not urls or len(urls) > LIMITE_IMAGENS_POR_MENSAGEM:
        raise ValueError(MENSAGENS['envie_de_uma_a_tres_imagens'])
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
