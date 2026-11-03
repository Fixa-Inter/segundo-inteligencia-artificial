# Responsabilidade: app/api

## Objetivo do módulo

Compor a interface HTTP da aplicação.

## O que deve ser armazenado aqui

Roteador principal, endpoints e dependências FastAPI.

## Comportamento e limites atuais

router.py agrega cinco roteadores; /api/v1 é aplicado em app/main.py.

Módulo pai: [app](../RESPONSABILIDADE.md).

## Submódulos

| Pasta | Responsabilidade |
| --- | --- |
| [dependencies](dependencies/RESPONSABILIDADE.md) | Resolver autenticação e restrição por perfil para endpoints. |
| [routes](routes/RESPONSABILIDADE.md) | Expor chat, sessões, saúde, métricas e classificação. |

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `api_router` → `.router` (`api_router`).
- `dependencies` → `.dependencies` (submódulo).
- `routes` → `.routes` (submódulo).

### [router.py](router.py)

Agrega roteadores de saúde, chat, métricas, classificação e sessões.

- Constantes, aliases e estado de módulo: `api_router`.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/api/routes](routes/RESPONSABILIDADE.md).
- [app/core](../core/RESPONSABILIDADE.md).
