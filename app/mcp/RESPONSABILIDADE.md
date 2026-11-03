# Responsabilidade: app/mcp

## Objetivo do módulo

Agrupar integrações cliente com servidores MCP.

## O que deve ser armazenado aqui

Adaptadores de transporte, contratos e ferramentas por provedor.

## Comportamento e limites atuais

Pechincha é o único provedor implementado. O pacote raiz não oferece outras ferramentas.

Módulo pai: [app](../RESPONSABILIDADE.md).

## Submódulos

| Pasta | Responsabilidade |
| --- | --- |
| [pechincha](pechincha/RESPONSABILIDADE.md) | Consultar promoções no MCP público Pechincha.ai. |

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `pechincha` → `.pechincha` (submódulo).

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../core/RESPONSABILIDADE.md).
