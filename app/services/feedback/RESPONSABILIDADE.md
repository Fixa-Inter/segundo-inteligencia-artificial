# Responsabilidade: app/services/feedback

## Objetivo do módulo

Gravar e consultar feedback próprio.

## O que deve ser armazenado aqui

INSERT de comentário/ideia central e SELECT por usuário autenticado.

## Comportamento e limites atuais

Listagem ordenada por data/ID decrescentes, sem o limite de três registros ou três meses de outras consultas.

Módulo pai: [app/services](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `criar_feedback` → `.criar_feedback` (`criar_feedback`).
- `listar_feedbacks` → `.listarFeedbacks` (`listar_feedbacks`).

### [criar_feedback.py](criar_feedback.py)

Recursos deste arquivo: Registra feedback e resumo categorizado para o usuario autenticado.

- `async criar_feedback(usuario: UsuarioContexto, comentario: str, ideia_central: str) -> dict`: Registra feedback e resumo categorizado para o usuario autenticado.
- Constantes, aliases e estado de módulo: `registrador`, `_SQL_CRIAR_FEEDBACK`, `_PERFIS_COM_ACESSO`.

### [listarFeedbacks.py](listarFeedbacks.py)

Todos os feedbacks próprios, ordenados por data/ID decrescentes.

- `async listar_feedbacks(usuario: UsuarioContexto) -> dict`: Consulta todos os feedbacks do usuário autenticado em ordem decrescente de data/ID.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../core/RESPONSABILIDADE.md).
- [app/core/clients](../../core/clients/RESPONSABILIDADE.md).
- [app/schemas](../../schemas/RESPONSABILIDADE.md).
