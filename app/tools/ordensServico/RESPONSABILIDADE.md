# Responsabilidade: app/tools/ordensServico

## Objetivo do módulo

Disponibilizar busca/listagem de OS aos agentes.

## O que deve ser armazenado aqui

Filtros, ferramentas sem identidade editável e tabelas Markdown.

## Comportamento e limites atuais

Busca/listagem limitadas a três OS. Renderização usa core/tabelas mantendo agrupamento por status, ordem de registros, campos opcionais e texto de ausência. Não grava OS.

Módulo pai: [app/tools](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `buscar_ordem_servico` → `.buscarOrdensServico` (`buscar_ordem_servico`).
- `listar_minhas_ordens_servico` → `.listarMinhasOrdensServico` (`listar_minhas_ordens_servico`).
- `listar_todas_ordens_servico` → `.listarTodasOrdensServico` (`listar_todas_ordens_servico`).
- `montar_tabelas` → `.utilitarios` (`montar_tabelas`).

### [buscarOrdensServico.py](buscarOrdensServico.py)

Schema de filtros e wrapper de busca de até três OS autorizadas.

- `async buscar_ordem_servico(runtime: ToolRuntime, status: str | None=None, prioridade: str | None=None, categoria_problema: str | None=None, categoria_equipamento: str | None=None, local: str | None=None, termo: str | None=None, data_criacao_inicio: date | None=None, data_criacao_fim: date | None=None, data_prevista_inicio: date | None=None, data_prevista_fim: date | None=None) -> dict`: Busca ate tres ordens recentes com filtros citados, no escopo autenticado.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_ArgumentosBuscarOrdensServico`.
  `_ArgumentosBuscarOrdensServico`: `status: str | None`, `prioridade: str | None`, `categoria_problema: str | None`, `categoria_equipamento: str | None`, `local: str | None`, `termo: str | None`, `data_criacao_inicio: date | None`, `data_criacao_fim: date | None`, `data_prevista_inicio: date | None`, `data_prevista_fim: date | None`.

### [listarMinhasOrdensServico.py](listarMinhasOrdensServico.py)

Wrapper de até três OS próprias recentes.

- `async listar_minhas_ordens_servico(runtime: ToolRuntime) -> dict`: Lista ate tres OS recentes do tecnico ou gestor nos ultimos tres meses.

### [listarTodasOrdensServico.py](listarTodasOrdensServico.py)

Wrapper de até três OS da unidade para gestor/administrador.

- `async listar_todas_ordens_servico(runtime: ToolRuntime) -> dict`: Lista ate tres OS recentes do endereco do gestor nos ultimos tres meses.

### [utilitarios.py](utilitarios.py)

Agrupa OS por status e delega renderização segura a core/tabelas; preserva datas opcionais e ordem interna.

- `montar_tabelas(ordens: list[dict]) -> str`: Agrupa OS por status e renderiza tabelas seguras, preservando a ordem dentro de cada grupo.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_celula`.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../core/RESPONSABILIDADE.md).
- [app/schemas](../../schemas/RESPONSABILIDADE.md).
- [app/services/ordensServico](../../services/ordensServico/RESPONSABILIDADE.md).
- [app/tools](../RESPONSABILIDADE.md).
