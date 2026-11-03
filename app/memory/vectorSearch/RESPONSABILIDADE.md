# Responsabilidade: app/memory/vectorSearch

## Objetivo do módulo

Pesquisar registros vetoriais e garantir índices de filtro.

## O que deve ser armazenado aqui

Busca de categoria/local, validação de seleção e recuperação histórica.

## Comportamento e limites atuais

Cadastro usa unidade, atividade e payload esperado. Histórico é restrito ao usuário e conferido com sessões MongoDB; não comprova estado atual da manutenção.

Módulo pai: [app/memory](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `buscar_categoria_equipamento` → `.busca` (`buscar_categoria_equipamento`).
- `buscar_local_endereco` → `.busca` (`buscar_local_endereco`).
- `garantir_indice_faq` → `.garantir_indice` (`garantir_indice_faq`).
- `garantir_indice_historico` → `.garantir_indice` (`garantir_indice_historico`).
- `garantir_indices_operacionais` → `.garantir_indice` (`garantir_indices_operacionais`).
- `recuperar_historico` → `.recuperar_historico` (`recuperar_historico`).
- `validar_selecao` → `.busca` (`validar_selecao`).

### [busca.py](busca.py)

Busca categoria/local ativos na unidade e confere seleção por ID.

- `async buscar_categoria_equipamento(descricao: str, unidade_id: int, cliente: AsyncQdrantClient) -> dict[int, str]`: Pesquisa categorias ativas por significado dentro da unidade.
- `async buscar_local_endereco(descricao: str, unidade_id: int, cliente: AsyncQdrantClient) -> dict[int, str]`: Pesquisa locais ativos por significado dentro da unidade.
- `async validar_selecao(colecao: str, registro_id: int, unidade_id: int, cliente: AsyncQdrantClient) -> str`: Confere ID selecionado, unidade, atividade e descrição na coleção de cadastro.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_filtro`, `_registro`, `_buscar`.
- Constantes, aliases e estado de módulo: `_COLECOES_CADASTRO`.

### [garantir_indice.py](garantir_indice.py)

Garante os índices usados pelos filtros do Qdrant.

- `async garantir_indice_historico() -> None`: Garante índices de filtro usados na coleção de histórico Qdrant.
- `async garantir_indice_faq() -> None`: Garante o índice usado para filtrar o FAQ pelo perfil autenticado.
- `async garantir_indices_operacionais() -> None`: Indexa unidade, atividade, ID e texto nas collections já existentes.

### [recuperar_historico.py](recuperar_historico.py)

Combina resumos vetoriais e sessões abertas do MongoDB por usuário.

- `async recuperar_historico(usuario_id: int, busca: str='', limite: int=3) -> list[dict]`: Busca resumos e sessões abertas do usuário e devolve relatos anteriores autorizados.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../core/RESPONSABILIDADE.md).
- [app/core/clients](../../core/clients/RESPONSABILIDADE.md).
- [app/memory/embedding](../embedding/RESPONSABILIDADE.md).
