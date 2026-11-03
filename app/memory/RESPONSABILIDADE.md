# Responsabilidade: app/memory

## Objetivo do módulo

Organizar memória conversacional e recursos vetoriais.

## O que deve ser armazenado aqui

Persistência MongoDB, embeddings e consultas/índices Qdrant.

## Comportamento e limites atuais

Persistência e buscas mantêm escopos próprios. Embeddings e resumo usam clientes de core/clients, sem depender das fábricas de agentes.

Módulo pai: [app](../RESPONSABILIDADE.md).

## Submódulos

| Pasta | Responsabilidade |
| --- | --- |
| [embedding](embedding/RESPONSABILIDADE.md) | Gerar embeddings e substituir o corpus de FAQ Markdown/PDF por perfil, preservando os demais perfis. |
| [persistencia](persistencia/RESPONSABILIDADE.md) | Persistir conversas, propostas e operações de escrita. |
| [vectorSearch](vectorSearch/RESPONSABILIDADE.md) | Pesquisar registros vetoriais e garantir índices de filtro. |

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `embedding` → `.embedding` (submódulo).
- `persistencia` → `.persistencia` (submódulo).
- `vectorSearch` → `.vectorSearch` (submódulo).

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../core/RESPONSABILIDADE.md).
