# Responsabilidade: app/tools/ajuda_geral

## Objetivo do módulo

Adaptar consultas e edições para ajuda geral.

## O que deve ser armazenado aqui

Schemas, wrappers de consultas e propostas de edição/anexo.

## Comportamento e limites atuais

Consultas têm variantes de schema restritas ao solicitante. Edição/anexo de solicitação e foto de ocorrência delegam a atualizações; observação de conclusão usa ajuda_geral_pendente.

Módulo pai: [app/tools](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `Colecao` → `.consultas` (`Colecao`).
- `ColecaoSolicitante` → `.consultas` (`ColecaoSolicitante`).
- `Tipo` → `.edicoes` (`Tipo`).
- `alterar_informacao_solicitacao` → `.edicoes` (`alterar_informacao_solicitacao`).
- `anexar_foto_observacao_conclusao` → `.edicoes` (`anexar_foto_observacao_conclusao`).
- `anexar_foto_ocorrencia` → `.edicoes` (`anexar_foto_ocorrencia`).
- `anexar_foto_solicitacao` → `.edicoes` (`anexar_foto_solicitacao`).
- `buscar_em_multiplas_colecoes` → `.consultas` (`buscar_em_multiplas_colecoes`).
- `buscar_em_multiplas_colecoes_solicitante` → `.consultas` (`buscar_em_multiplas_colecoes_solicitante`).
- `buscar_problemas_por_local` → `.consultas_relacionais` (`buscar_problemas_por_local`).
- `buscar_semanticamente` → `.consultas` (`buscar_semanticamente`).
- `buscar_semanticamente_solicitante` → `.consultas` (`buscar_semanticamente_solicitante`).
- `buscar_termo_literal` → `.consultas` (`buscar_termo_literal`).
- `buscar_termo_literal_solicitante` → `.consultas` (`buscar_termo_literal_solicitante`).
- `buscar_textos_semelhantes` → `.consultas` (`buscar_textos_semelhantes`).
- `buscar_textos_semelhantes_solicitante` → `.consultas` (`buscar_textos_semelhantes_solicitante`).
- `consultar_equipamento_por_codigo` → `.consultas_relacionais` (`consultar_equipamento_por_codigo`).
- `consultar_modelos_por_marca_categoria` → `.consultas_relacionais` (`consultar_modelos_por_marca_categoria`).
- `consultar_situacao_problema` → `.consultas_relacionais` (`consultar_situacao_problema`).
- `encontrar_codigo_equipamento` → `.consultas_relacionais` (`encontrar_codigo_equipamento`).
- `listar_equipamentos_por_local` → `.consultas_relacionais` (`listar_equipamentos_por_local`).
- `listar_eventos_por_local_e_periodo` → `.consultas_relacionais` (`listar_eventos_por_local_e_periodo`).
- `listar_observacoes_da_ordem` → `.consultas_relacionais` (`listar_observacoes_da_ordem`).
- `listar_ocorrencias_por_local` → `.consultas_relacionais` (`listar_ocorrencias_por_local`).
- `listar_registros` → `.consultas` (`listar_registros`).
- `listar_registros_solicitante` → `.consultas` (`listar_registros_solicitante`).
- `listar_tarefas_da_ordem` → `.consultas_relacionais` (`listar_tarefas_da_ordem`).

### [consultas.py](consultas.py)

Recursos deste arquivo: Extrai o usuário autenticado do runtime sem aceitar identidade da conversa. Usado por buscar_em_multiplas_colecoes, buscar_semanticamente, buscar_termo_literal. Monta resposta estruturada de acesso negado para a ferramenta. Usado por buscar_em_multiplas_colecoes, buscar_semanticamente, buscar_termo_literal.

- `async buscar_semanticamente(colecao: Colecao, pergunta: str, runtime: ToolRuntime, limite: int=5) -> dict`: Pesquisa textos operacionais por significado dentro das permissões do usuário.
- `async buscar_em_multiplas_colecoes(colecoes: list[Colecao], pergunta: str, runtime: ToolRuntime, limite_por_colecao: int=3) -> dict`: Pesquisa coleções permitidas e preserva origem/escopo de cada texto.
- `async listar_registros(colecao: Colecao, runtime: ToolRuntime, cursor_paginacao: str | None=None, limite: int=10) -> dict`: Lista registros ativos com cursor limitado à coleção/unidade.
- `async buscar_termo_literal(colecao: Colecao, termo: str, runtime: ToolRuntime, limite: int=10) -> dict`: Pesquisa termo na ordem escrita, sem inferir relacionamentos.
- `async buscar_textos_semelhantes(colecao: Colecao, entidade_id: int, runtime: ToolRuntime, limite: int=5) -> dict`: Encontra textos semelhantes a registro autorizado sem inventar vínculos.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_Argumentos`, `_BuscaSemantica`, `_BuscaMultipla`, `_Listagem`, `_BuscaLiteral`, `_BuscaSemelhantes`, `_BuscaSemanticaSolicitante`, `_BuscaMultiplaSolicitante`, `_ListagemSolicitante`, `_BuscaLiteralSolicitante`, `_BuscaSemelhantesSolicitante`, `_usuario`, `_acesso_negado`.
  `_BuscaSemantica`: `colecao: Colecao`, `pergunta: str`, `limite: int`.
  `_BuscaMultipla`: `colecoes: list[Colecao]`, `pergunta: str`, `limite_por_colecao: int`.
  `_Listagem`: `colecao: Colecao`, `cursor_paginacao: str | None`, `limite: int`.
  `_BuscaLiteral`: `colecao: Colecao`, `termo: str`, `limite: int`.
  `_BuscaSemelhantes`: `colecao: Colecao`, `entidade_id: int`, `limite: int`.
  `_BuscaSemanticaSolicitante`: `colecao: ColecaoSolicitante`.
  `_BuscaMultiplaSolicitante`: `colecoes: list[ColecaoSolicitante]`.
  `_ListagemSolicitante`: `colecao: ColecaoSolicitante`.
  `_BuscaLiteralSolicitante`: `colecao: ColecaoSolicitante`.
  `_BuscaSemelhantesSolicitante`: `colecao: ColecaoSolicitante`.
- Constantes, aliases e estado de módulo: `Colecao`, `ColecaoSolicitante`, `buscar_semanticamente_solicitante`, `buscar_em_multiplas_colecoes_solicitante`, `listar_registros_solicitante`, `buscar_termo_literal_solicitante`, `buscar_textos_semelhantes_solicitante`.

### [consultas_relacionais.py](consultas_relacionais.py)

Ferramentas de consulta com relações verificadas no banco FIXA.

- `async buscar_problemas_por_local(nome_local: str, runtime: ToolRuntime, limite: int=10) -> dict`: Consulta problemas relacionados a local com escopo e autoria quando aplicável.
- `async consultar_situacao_problema(problema_id: int, runtime: ToolRuntime) -> dict`: Obtém status e motivo de recusa de problema autorizado.
- `async consultar_modelos_por_marca_categoria(runtime: ToolRuntime, marca: str | None=None, categoria: str | None=None, limite: int=10) -> dict`: Consulta relação exata entre modelo, marca e categoria.
- `async consultar_equipamento_por_codigo(codigo: str, runtime: ToolRuntime) -> dict`: Obtém equipamento pelo código exato dentro das permissões/unidade.
- `async encontrar_codigo_equipamento(runtime: ToolRuntime, modelo: str | None=None, local: str | None=None, marca: str | None=None, categoria: str | None=None, limite: int=10) -> dict`: Localiza códigos por modelo, local, marca e/ou categoria.
- `async listar_equipamentos_por_local(nome_local: str, runtime: ToolRuntime, limite: int=10) -> dict`: Lista equipamentos vinculados a local autorizado.
- `async listar_ocorrencias_por_local(nome_local: str, runtime: ToolRuntime, limite: int=10) -> dict`: Lista ocorrências vinculadas a local autorizado.
- `async listar_tarefas_da_ordem(ordem_servico_id: int, runtime: ToolRuntime, limite: int=20) -> dict`: Consulta tarefas relacionadas a OS autorizada.
- `async listar_observacoes_da_ordem(ordem_servico_id: int, runtime: ToolRuntime, limite: int=20) -> dict`: Consulta observações de conclusão relacionadas a OS autorizada.
- `async listar_eventos_por_local_e_periodo(nome_local: str, data_inicio: date, data_fim: date, runtime: ToolRuntime, limite: int=20) -> dict`: Consulta eventos por vínculo de local e intervalo de datas autorizado.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_PorLocal`, `_SituacaoProblema`, `_Modelos`, `_Codigo`, `_EncontrarCodigo`, `_PorOrdem`, `_Eventos`.
  `_PorLocal`: `nome_local: str`, `limite: int`.
  `_SituacaoProblema`: `problema_id: int`.
  `_Modelos`: `marca: str | None`, `categoria: str | None`, `limite: int`.
  `_Codigo`: `codigo: str`.
  `_EncontrarCodigo`: `modelo: str | None`, `local: str | None`, `marca: str | None`, `categoria: str | None`, `limite: int`.
  `_PorOrdem`: `ordem_servico_id: int`, `limite: int`.
  `_Eventos`: `nome_local: str`, `data_inicio: date`, `data_fim: date`, `limite: int`.

### [edicoes.py](edicoes.py)

Propostas e confirmação de alterações em registros existentes.

- `async alterar_informacao_solicitacao(runtime: ToolRuntime, problema_id: int | None=None, campo: str | None=None, novo_valor: int | str | None=None) -> dict`: Propõe ou confirma edição de cinco campos de solicitação própria pendente.
- `async anexar_foto_solicitacao(runtime: ToolRuntime, problema_id: int | None=None) -> dict`: Propõe ou confirma anexar imagens da mensagem a solicitação própria pendente.
- `async anexar_foto_ocorrencia(runtime: ToolRuntime, ocorrencia_id: int | None=None) -> dict`: Atualiza fotos de ocorrência própria e ativa, após seleção e proposta final.
- `async anexar_foto_observacao_conclusao(runtime: ToolRuntime, observacao_conclusao_id: int | None=None) -> dict`: Propõe ou confirma foto da observação da ordem atribuída ao técnico ou da unidade do gestor.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_Alteracao`, `_AnexoSolicitacao`, `_AnexoOcorrencia`, `_AnexoObservacao`, `_contexto`, `_imagens`, `_erro`, `_confirmacao_edicao`, `_executar_pendente`, `_propor`.
  `_Alteracao`: `problema_id: int | None`, `campo: Literal['categoria_equipamento_id', 'local_unidade_id', 'titulo', 'descricao_problema', 'descricao_local'] | None`, `novo_valor: int | str | None`.
  `_AnexoSolicitacao`: `problema_id: int | None`.
  `_AnexoOcorrencia`: `ocorrencia_id: int | None`.
  `_AnexoObservacao`: `observacao_conclusao_id: int | None`.
- Constantes, aliases e estado de módulo: `registrador`, `Tipo`.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../core/RESPONSABILIDADE.md).
- [app/core/apresentacao](../../core/apresentacao/RESPONSABILIDADE.md).
- [app/memory/persistencia](../../memory/persistencia/RESPONSABILIDADE.md).
- [app/schemas](../../schemas/RESPONSABILIDADE.md).
- [app/services](../../services/RESPONSABILIDADE.md).
- [app/services/ajuda_geral](../../services/ajuda_geral/RESPONSABILIDADE.md).
- [app/tools](../RESPONSABILIDADE.md).
- [app/tools/ocorrencias](../ocorrencias/RESPONSABILIDADE.md).
- [app/tools/solicitacoes](../solicitacoes/RESPONSABILIDADE.md).
