# Responsabilidade: app/tools/memoria

## Objetivo do módulo

Expor recuperação de conversas aos agentes.

## O que deve ser armazenado aqui

buscar_historico e lista de registro da ferramenta.

## Comportamento e limites atuais

Inclui resumos e sessões abertas. Relatos históricos não comprovam situação atual de solicitação, ocorrência ou OS.

Módulo pai: [app/tools](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `FERRAMENTAS_MEMORIA` → `.buscar_historico` (`FERRAMENTAS_MEMORIA`).
- `buscar_historico` → `.buscar_historico` (`buscar_historico`).

### [buscar_historico.py](buscar_historico.py)

Recursos deste arquivo: Consulta relatos anteriores do usuário, incluindo conversas ainda abertas.

- `async buscar_historico(busca: str, runtime: ToolRuntime) -> str`: Consulta relatos anteriores do usuário, incluindo conversas ainda abertas.
- Constantes, aliases e estado de módulo: `FERRAMENTAS_MEMORIA`.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../core/RESPONSABILIDADE.md).
- [app/memory/vectorSearch](../../memory/vectorSearch/RESPONSABILIDADE.md).
- [app/schemas](../../schemas/RESPONSABILIDADE.md).
