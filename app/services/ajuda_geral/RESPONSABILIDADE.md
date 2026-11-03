# Responsabilidade: app/services/ajuda_geral

## Objetivo do módulo

Consultar registros operacionais e efetivar edições restritas.

## O que deve ser armazenado aqui

Buscas Qdrant, relações SQL verificadas e mutações transacionais.

## Comportamento e limites atuais

Valida unidade, coleção e perfil. Marcas têm tratamento global; problemas de solicitante exigem autoria. Consultas relacionais exigem ponto ativo Qdrant para publicar descrições.

Módulo pai: [app/services](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `CAMPOS_EDITAVEIS` → `.edicoes` (`CAMPOS_EDITAVEIS`).
- `CAMPOS_RELACIONAIS` → `.edicoes` (`CAMPOS_RELACIONAIS`).
- `COLECAO_GLOBAL` → `.consultas` (`COLECAO_GLOBAL`).
- `COLECOES_PERMITIDAS` → `.consultas` (`COLECOES_PERMITIDAS`).
- `COLECOES_SOLICITANTE` → `.consultas` (`COLECOES_SOLICITANTE`).
- `FKS_FOTO` → `.edicoes` (`FKS_FOTO`).
- `LIMITE_LISTAGEM` → `.consultas` (`LIMITE_LISTAGEM`).
- `LIMITE_LITERAL` → `.consultas` (`LIMITE_LITERAL`).
- `LIMITE_MULTIPLAS_COLECOES` → `.consultas` (`LIMITE_MULTIPLAS_COLECOES`).
- `LIMITE_POR_COLECAO` → `.consultas` (`LIMITE_POR_COLECAO`).
- `LIMITE_SEMANTICO` → `.consultas` (`LIMITE_SEMANTICO`).
- `LIMITE_SEMELHANTES` → `.consultas` (`LIMITE_SEMELHANTES`).
- `alterar_solicitacao` → `.edicoes` (`alterar_solicitacao`).
- `anexar_fotos` → `.edicoes` (`anexar_fotos`).
- `buscar_em_multiplas_colecoes` → `.consultas` (`buscar_em_multiplas_colecoes`).
- `buscar_problemas_por_local` → `.consultas_relacionais` (`buscar_problemas_por_local`).
- `buscar_semanticamente` → `.consultas` (`buscar_semanticamente`).
- `buscar_termo_literal` → `.consultas` (`buscar_termo_literal`).
- `buscar_textos_semelhantes` → `.consultas` (`buscar_textos_semelhantes`).
- `consultar_equipamento_por_codigo` → `.consultas_relacionais` (`consultar_equipamento_por_codigo`).
- `consultar_modelos_por_marca_categoria` → `.consultas_relacionais` (`consultar_modelos_por_marca_categoria`).
- `consultar_situacao_problema` → `.consultas_relacionais` (`consultar_situacao_problema`).
- `encontrar_codigo_equipamento` → `.consultas_relacionais` (`encontrar_codigo_equipamento`).
- `listar_equipamentos_por_local` → `.consultas_relacionais` (`listar_equipamentos_por_local`).
- `listar_eventos_por_local_e_periodo` → `.consultas_relacionais` (`listar_eventos_por_local_e_periodo`).
- `listar_observacoes_da_ordem` → `.consultas_relacionais` (`listar_observacoes_da_ordem`).
- `listar_ocorrencias_por_local` → `.consultas_relacionais` (`listar_ocorrencias_por_local`).
- `listar_registros` → `.consultas` (`listar_registros`).
- `listar_tarefas_da_ordem` → `.consultas_relacionais` (`listar_tarefas_da_ordem`).
- `localizar_opcao` → `.edicoes` (`localizar_opcao`).
- `localizar_registro` → `.edicoes` (`localizar_registro`).

### [consultas.py](consultas.py)

Busca registros do Qdrant dentro da unidade autenticada.

- `async buscar_semanticamente(usuario: UsuarioContexto, colecao: str, pergunta: str, limite: int) -> dict`: Pesquisa textos operacionais por significado dentro das permissões do usuário.
- `async buscar_em_multiplas_colecoes(usuario: UsuarioContexto, colecoes: list[str], pergunta: str, limite_por_colecao: int) -> dict`: Pesquisa coleções permitidas e preserva origem/escopo de cada texto.
- `async listar_registros(usuario: UsuarioContexto, colecao: str, cursor_paginacao: str | None, limite: int) -> dict`: Lista registros ativos com cursor limitado à coleção/unidade.
- `async buscar_termo_literal(usuario: UsuarioContexto, colecao: str, termo: str, limite: int) -> dict`: Pesquisa termo na ordem escrita, sem inferir relacionamentos.
- `async buscar_textos_semelhantes(usuario: UsuarioContexto, colecao: str, entidade_id: int, limite: int) -> dict`: Encontra textos semelhantes a registro autorizado sem inventar vínculos.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_validar_colecao`, `_filtro_usuario`, `_validar_limite`, `_validar_texto`, `_validar_usuario`, `_filtro`, `_registro`, `_resultado`, `_erro`, `_codificar_cursor`, `_decodificar_cursor`.
- Constantes, aliases e estado de módulo: `registrador`, `COLECOES_PERMITIDAS`, `COLECOES_SOLICITANTE`, `COLECAO_GLOBAL`, `LIMITE_SEMANTICO`, `LIMITE_MULTIPLAS_COLECOES`, `LIMITE_POR_COLECAO`, `LIMITE_LISTAGEM`, `LIMITE_LITERAL`, `LIMITE_SEMELHANTES`, `_CAMPOS_PAYLOAD`.

### [consultas_relacionais.py](consultas_relacionais.py)

Consultas exatas no FIXA, com descrições obtidas do Qdrant.

- `async buscar_problemas_por_local(usuario: UsuarioContexto, nome_local: str, limite: int=10) -> dict`: Consulta problemas relacionados a local com escopo e autoria quando aplicável.
- `async consultar_situacao_problema(usuario: UsuarioContexto, problema_id: int) -> dict`: Obtém status e motivo de recusa de problema autorizado.
- `async consultar_modelos_por_marca_categoria(usuario: UsuarioContexto, marca: str | None, categoria: str | None, limite: int=10) -> dict`: Consulta relação exata entre modelo, marca e categoria.
- `async consultar_equipamento_por_codigo(usuario: UsuarioContexto, codigo: str) -> dict`: Obtém equipamento pelo código exato dentro das permissões/unidade.
- `async encontrar_codigo_equipamento(usuario: UsuarioContexto, modelo: str | None, local: str | None, marca: str | None, categoria: str | None, limite: int=10) -> dict`: Localiza códigos por modelo, local, marca e/ou categoria.
- `async listar_equipamentos_por_local(usuario: UsuarioContexto, nome_local: str, limite: int=10) -> dict`: Lista equipamentos vinculados a local autorizado.
- `async listar_ocorrencias_por_local(usuario: UsuarioContexto, nome_local: str, limite: int=10) -> dict`: Lista ocorrências vinculadas a local autorizado.
- `async listar_tarefas_da_ordem(usuario: UsuarioContexto, ordem_servico_id: int, limite: int=20) -> dict`: Consulta tarefas relacionadas a OS autorizada.
- `async listar_observacoes_da_ordem(usuario: UsuarioContexto, ordem_servico_id: int, limite: int=20) -> dict`: Consulta observações de conclusão relacionadas a OS autorizada.
- `async listar_eventos_por_local_e_periodo(usuario: UsuarioContexto, nome_local: str, data_inicio: date, data_fim: date, limite: int=20) -> dict`: Consulta eventos por vínculo de local e intervalo de datas autorizado.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_somente_tecnico_gestor`, `_texto_busca`, `_valor_json`, `_consultar`.
- Constantes, aliases e estado de módulo: `_EQUIPAMENTO_BASE`.

### [edicoes.py](edicoes.py)

Consultas e mutações SQL com escopo do usuário autenticado.

- `async localizar_registro(usuario: UsuarioContexto, tipo: str, registro_id: int) -> dict | None`: Confere existência e autorização do alvo de edição/anexo.
- `async localizar_opcao(usuario: UsuarioContexto, campo: str, identificador: int, *, conexao=None) -> dict | None`: Confere o novo local ou categoria ativa na unidade autenticada.
- `async alterar_solicitacao(usuario: UsuarioContexto, registro_id: int, campo: str, valor: int | str) -> dict | None`: Altera um campo permitido de solicitação própria pendente em transação.
- `async anexar_fotos(usuario: UsuarioContexto, tipo: str, registro_id: int, urls: list[str]) -> list[int] | None`: Insere vínculos de foto após conferir/travar o registro autorizado na transação.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_validar_id`, `_sql_alvo`.
- Constantes, aliases e estado de módulo: `CAMPOS_EDITAVEIS`, `CAMPOS_RELACIONAIS`, `FKS_FOTO`.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../core/RESPONSABILIDADE.md).
- [app/core/apresentacao](../../core/apresentacao/RESPONSABILIDADE.md).
- [app/core/clients](../../core/clients/RESPONSABILIDADE.md).
- [app/memory/embedding](../../memory/embedding/RESPONSABILIDADE.md).
- [app/schemas](../../schemas/RESPONSABILIDADE.md).
- [app/services/gerais](../gerais/RESPONSABILIDADE.md).
