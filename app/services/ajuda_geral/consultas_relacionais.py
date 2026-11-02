"""Consultas exatas no FIXA, com descrições obtidas do Qdrant."""


from datetime import date, datetime, timedelta

from qdrant_client import models

from app.core import configuracao
from app.core.clients.postgres import executar_consulta
from app.core.clients.qdrant import abrir_cliente_qdrant
from app.schemas import UsuarioContexto
from app.services.gerais import obter_unidade_id
from app.services.ajuda_geral.consultas import (
    _CAMPOS_PAYLOAD,
    _erro,
    _filtro,
    _registro,
    _resultado,
    _validar_colecao,
    _validar_limite,
    _validar_texto,
    _validar_usuario,
)

from app.core.respostas import MENSAGENS


def _somente_tecnico_gestor(usuario: UsuarioContexto) -> None:
    if usuario.tipo_acesso not in {"tecnico", "gestor", "administrador"}:
        raise PermissionError(MENSAGENS['consulta_disponivel_apenas_para_tecnicos_e_gestores'])


def _texto_busca(valor: str | None) -> str | None:
    return f"%{_validar_texto(valor, 100)}%" if valor is not None else None


def _valor_json(valor):
    return valor.isoformat() if isinstance(valor, (date, datetime)) else valor


async def _consultar(
    usuario: UsuarioContexto, colecao: str, sql: str, parametros: dict,
    limite: int, maximo: int = 20,
) -> dict:
    """Aplica escopo SQL e só devolve linhas com ponto ativo no Qdrant."""
    _validar_usuario(usuario)
    _validar_colecao(usuario, colecao)
    _validar_limite(limite, maximo)
    unidade_id = await obter_unidade_id(usuario)
    linhas = await executar_consulta(
        usuario.tipo_acesso,
        sql,
        {**parametros, "unidade_id": unidade_id, "usuario_id": usuario.usuario_id, "limite": limite},
    )
    if not linhas:
        return _resultado([])

    ids = [linha["entidade_id"] for linha in linhas]
    if any(type(identificador) is not int or identificador <= 0 for identificador in ids):
        raise RuntimeError(MENSAGENS['o_banco_retornou_um_id_invalido'])
    condicao = models.FieldCondition(
        key=configuracao.QDRANT_CAMPO_ENTIDADE_ID,
        match=models.MatchAny(any=list(set(ids))),
    )
    registros = {}
    async with abrir_cliente_qdrant() as cliente:
        deslocamento = None
        while True:
            pontos, deslocamento = await cliente.scroll(
                collection_name=colecao,
                scroll_filter=_filtro(colecao, unidade_id, condicao),
                offset=deslocamento,
                limit=20,
                with_payload=_CAMPOS_PAYLOAD,
                with_vectors=False,
            )
            for ponto in pontos:
                registro = _registro(colecao, ponto, unidade_id)
                registros.setdefault(registro["entidade_id"], registro)
            if deslocamento is None:
                break

    resultados = []
    for linha in linhas:
        registro = registros.get(linha["entidade_id"])
        if registro is None:
            continue
        metadados = {
            chave: _valor_json(valor)
            for chave, valor in linha.items()
            if chave != "entidade_id"
        }
        resultados.append({**registro, **metadados})
    return _resultado(resultados)


async def buscar_problemas_por_local(
    usuario: UsuarioContexto, nome_local: str, limite: int = 10,
) -> dict:
    try:
        _validar_usuario(usuario)
        nome_local = _texto_busca(nome_local)
        filtro_dono = "AND p.usuario_id = :usuario_id" if usuario.tipo_acesso == "solicitante" else ""
        return await _consultar(usuario, "problema", f"""
            SELECT p.id AS entidade_id, local.id AS local_id, local.nome AS local,
                   CASE p.status WHEN 0 THEN 'Pendente'
                        WHEN 1 THEN 'Reprovado' WHEN 2 THEN 'Aprovado'
                        WHEN 3 THEN 'Concluído' END AS situacao
            FROM problema AS p
            JOIN local_unidade AS local ON local.id = p.local_unidade_id
            WHERE local.unidade_id = :unidade_id AND local.esta_ativo IS TRUE
              AND p.esta_ativo IS TRUE AND local.nome ILIKE :nome_local
              {filtro_dono}
            ORDER BY p.data_criacao DESC, p.id DESC LIMIT :limite
        """, {"nome_local": nome_local}, limite, 10)
    except Exception as erro:
        return _erro(erro)


async def consultar_situacao_problema(
    usuario: UsuarioContexto, problema_id: int,
) -> dict:
    try:
        _validar_usuario(usuario)
        if type(problema_id) is not int or problema_id <= 0:
            raise ValueError(MENSAGENS['problema_id_deve_ser_positivo'])
        filtro_dono = "AND p.usuario_id = :usuario_id" if usuario.tipo_acesso == "solicitante" else ""
        return await _consultar(usuario, "problema", f"""
            SELECT p.id AS entidade_id,
                   CASE p.status WHEN 0 THEN 'Pendente'
                        WHEN 1 THEN 'Reprovado' WHEN 2 THEN 'Aprovado'
                        WHEN 3 THEN 'Concluído' END AS situacao,
                   p.motivo_recusa
            FROM problema AS p
            JOIN local_unidade AS local ON local.id = p.local_unidade_id
            WHERE local.unidade_id = :unidade_id AND local.esta_ativo IS TRUE
              AND p.esta_ativo IS TRUE AND p.id = :problema_id
              {filtro_dono}
            LIMIT :limite
        """, {"problema_id": problema_id}, 1, 1)
    except Exception as erro:
        return _erro(erro)


async def consultar_modelos_por_marca_categoria(
    usuario: UsuarioContexto, marca: str | None, categoria: str | None,
    limite: int = 10,
) -> dict:
    try:
        if marca is None and categoria is None:
            raise ValueError(MENSAGENS['informe_marca_ou_categoria'])
        filtros = []
        parametros = {}
        if marca is not None:
            filtros.append("marca.nome ILIKE :marca")
            parametros["marca"] = _texto_busca(marca)
        if categoria is not None:
            filtros.append("categoria.nome ILIKE :categoria")
            parametros["categoria"] = _texto_busca(categoria)
        return await _consultar(usuario, "modelo_equipamento", f"""
            SELECT modelo.id AS entidade_id, modelo.nome AS modelo,
                   marca.nome AS marca, categoria.nome AS categoria
            FROM modelo_equipamento AS modelo
            JOIN marca_equipamento AS marca ON marca.id = modelo.marca_equipamento_id
            JOIN categoria_equipamento AS categoria
              ON categoria.id = modelo.categoria_equipamento_id
            JOIN usuario AS criador ON criador.id = categoria.usuario_id
            WHERE criador.unidade_id = :unidade_id AND modelo.esta_ativo IS TRUE
              AND marca.esta_ativo IS TRUE AND categoria.esta_ativo IS TRUE
              AND {' AND '.join(filtros)}
            ORDER BY modelo.nome, modelo.id LIMIT :limite
        """, parametros, limite, 10)
    except Exception as erro:
        return _erro(erro)


_EQUIPAMENTO_BASE = """
    SELECT equipamento.id AS entidade_id, equipamento.codigo,
           modelo.nome AS modelo, marca.nome AS marca,
           categoria.nome AS categoria, local.nome AS local, local.id AS local_id
    FROM equipamento
    JOIN local_unidade AS local ON local.id = equipamento.local_unidade_id
    JOIN modelo_equipamento AS modelo ON modelo.id = equipamento.modelo_equipamento_id
    JOIN marca_equipamento AS marca ON marca.id = modelo.marca_equipamento_id
    JOIN categoria_equipamento AS categoria
      ON categoria.id = modelo.categoria_equipamento_id
    WHERE local.unidade_id = :unidade_id AND local.esta_ativo IS TRUE
      AND equipamento.esta_ativo IS TRUE AND modelo.esta_ativo IS TRUE
      AND marca.esta_ativo IS TRUE AND categoria.esta_ativo IS TRUE
"""


async def consultar_equipamento_por_codigo(
    usuario: UsuarioContexto, codigo: str,
) -> dict:
    try:
        _validar_usuario(usuario)
        _somente_tecnico_gestor(usuario)
        codigo = _validar_texto(codigo, 100)
        return await _consultar(
            usuario, "equipamento",
            _EQUIPAMENTO_BASE + " AND equipamento.codigo = :codigo ORDER BY equipamento.id LIMIT :limite",
            {"codigo": codigo}, 10, 10,
        )
    except Exception as erro:
        return _erro(erro)


async def encontrar_codigo_equipamento(
    usuario: UsuarioContexto, modelo: str | None, local: str | None,
    marca: str | None, categoria: str | None, limite: int = 10,
) -> dict:
    try:
        _validar_usuario(usuario)
        _somente_tecnico_gestor(usuario)
        filtros = []
        parametros = {}
        for campo, valor in (("modelo", modelo), ("local", local),
                             ("marca", marca), ("categoria", categoria)):
            if valor is not None:
                filtros.append(f"{campo}.nome ILIKE :{campo}")
                parametros[campo] = _texto_busca(valor)
        if not filtros:
            raise ValueError(MENSAGENS['informe_ao_menos_modelo_local_marca_ou_categoria'])
        return await _consultar(
            usuario, "equipamento",
            _EQUIPAMENTO_BASE + " AND " + " AND ".join(filtros)
            + " ORDER BY equipamento.codigo, equipamento.id LIMIT :limite",
            parametros, limite, 10,
        )
    except Exception as erro:
        return _erro(erro)


async def listar_equipamentos_por_local(
    usuario: UsuarioContexto, nome_local: str, limite: int = 10,
) -> dict:
    try:
        _validar_usuario(usuario)
        _somente_tecnico_gestor(usuario)
        return await _consultar(
            usuario, "equipamento",
            _EQUIPAMENTO_BASE + " AND local.nome ILIKE :nome_local"
            + " ORDER BY equipamento.codigo, equipamento.id LIMIT :limite",
            {"nome_local": _texto_busca(nome_local)}, limite, 10,
        )
    except Exception as erro:
        return _erro(erro)


async def listar_ocorrencias_por_local(
    usuario: UsuarioContexto, nome_local: str, limite: int = 10,
) -> dict:
    try:
        _validar_usuario(usuario)
        _somente_tecnico_gestor(usuario)
        return await _consultar(usuario, "ocorrencia", """
            SELECT ocorrencia.id AS entidade_id, local.nome AS local,
                   local.id AS local_id,
                   CASE ocorrencia.prioridade WHEN 0 THEN 'Alta'
                        WHEN 1 THEN 'Média' WHEN 2 THEN 'Baixa' END AS prioridade,
                   ocorrencia.data_criacao
            FROM ocorrencia
            JOIN local_unidade AS local ON local.id = ocorrencia.local_unidade_id
            WHERE local.unidade_id = :unidade_id AND local.esta_ativo IS TRUE
              AND ocorrencia.esta_ativo IS TRUE AND local.nome ILIKE :nome_local
            ORDER BY ocorrencia.data_criacao DESC, ocorrencia.id DESC LIMIT :limite
        """, {"nome_local": _texto_busca(nome_local)}, limite, 10)
    except Exception as erro:
        return _erro(erro)


async def listar_tarefas_da_ordem(
    usuario: UsuarioContexto, ordem_servico_id: int, limite: int = 20,
) -> dict:
    try:
        _validar_usuario(usuario)
        _somente_tecnico_gestor(usuario)
        if type(ordem_servico_id) is not int or ordem_servico_id <= 0:
            raise ValueError(MENSAGENS['ordem_servico_id_deve_ser_positivo'])
        return await _consultar(usuario, "tarefa", """
            SELECT tarefa.id AS entidade_id, tarefa.ordem_servico_id,
                   CASE tarefa.status_ordem_servico
                        WHEN 0 THEN 'Não iniciada' WHEN 1 THEN 'Atrasada'
                        WHEN 2 THEN 'Pausada' WHEN 3 THEN 'Em andamento'
                        WHEN 4 THEN 'Concluída' END AS situacao
            FROM tarefa
            JOIN ordem_servico AS ordem ON ordem.id = tarefa.ordem_servico_id
            JOIN problema ON problema.id = ordem.problema_id
            JOIN local_unidade AS local ON local.id = problema.local_unidade_id
            WHERE local.unidade_id = :unidade_id AND local.esta_ativo IS TRUE
              AND problema.esta_ativo IS TRUE AND ordem.esta_ativo IS TRUE
              AND tarefa.esta_ativo IS TRUE AND ordem.id = :ordem_servico_id
            ORDER BY tarefa.data_criacao, tarefa.id LIMIT :limite
        """, {"ordem_servico_id": ordem_servico_id}, limite)
    except Exception as erro:
        return _erro(erro)


async def listar_observacoes_da_ordem(
    usuario: UsuarioContexto, ordem_servico_id: int, limite: int = 20,
) -> dict:
    try:
        _validar_usuario(usuario)
        _somente_tecnico_gestor(usuario)
        if type(ordem_servico_id) is not int or ordem_servico_id <= 0:
            raise ValueError(MENSAGENS['ordem_servico_id_deve_ser_positivo'])
        return await _consultar(usuario, "observacao_conclusao", """
            SELECT observacao.id AS entidade_id, observacao.ordem_servico_id,
                   CASE observacao.dificuldade WHEN 1 THEN 'Fácil'
                        WHEN 2 THEN 'Médio' WHEN 3 THEN 'Difícil' END AS dificuldade,
                   observacao.data_criacao
            FROM observacao_conclusao AS observacao
            JOIN ordem_servico AS ordem ON ordem.id = observacao.ordem_servico_id
            JOIN problema ON problema.id = ordem.problema_id
            JOIN local_unidade AS local ON local.id = problema.local_unidade_id
            WHERE local.unidade_id = :unidade_id AND local.esta_ativo IS TRUE
              AND problema.esta_ativo IS TRUE AND ordem.esta_ativo IS TRUE
              AND observacao.esta_ativo IS TRUE AND ordem.id = :ordem_servico_id
            ORDER BY observacao.data_criacao DESC, observacao.id DESC LIMIT :limite
        """, {"ordem_servico_id": ordem_servico_id}, limite)
    except Exception as erro:
        return _erro(erro)


async def listar_eventos_por_local_e_periodo(
    usuario: UsuarioContexto, nome_local: str, data_inicio: date,
    data_fim: date, limite: int = 20,
) -> dict:
    try:
        _validar_usuario(usuario)
        _somente_tecnico_gestor(usuario)
        if not isinstance(data_inicio, date) or not isinstance(data_fim, date):
            raise ValueError(MENSAGENS['informe_datas_validas'])
        if data_inicio > data_fim or data_fim == date.max:
            raise ValueError(MENSAGENS['o_periodo_informado_e_invalido'])
        return await _consultar(usuario, "evento", """
            SELECT evento.id AS entidade_id, local.nome AS local,
                   evento.data_hora_inicio, evento.data_hora_fim
            FROM evento
            JOIN local_unidade AS local ON local.id = evento.local_unidade_id
            WHERE local.unidade_id = :unidade_id AND local.esta_ativo IS TRUE
              AND evento.esta_ativo IS TRUE AND local.nome ILIKE :nome_local
              AND evento.data_hora_inicio >= :data_inicio
              AND evento.data_hora_inicio < :data_fim_exclusivo
            ORDER BY evento.data_hora_inicio, evento.id LIMIT :limite
        """, {
            "nome_local": _texto_busca(nome_local),
            "data_inicio": data_inicio,
            "data_fim_exclusivo": data_fim + timedelta(days=1),
        }, limite)
    except Exception as erro:
        return _erro(erro)
