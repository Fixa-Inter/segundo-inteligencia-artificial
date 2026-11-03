# Responsabilidade: app/api/dependencies

## Objetivo do módulo

Resolver autenticação e restrição por perfil para endpoints.

## O que deve ser armazenado aqui

Dependências FastAPI de Bearer, usuário atual e autorização.

## Comportamento e limites atuais

obter_usuario_atual consulta o perfil na API FIXA e constrói UsuarioContexto. exigir_perfis devolve dependência reutilizável; identidade não vem da conversa.

Módulo pai: [app/api](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `bearer_scheme` → `.auth` (`bearer_scheme`).
- `exigir_perfis` → `.permissions` (`exigir_perfis`).
- `obter_usuario_atual` → `.auth` (`obter_usuario_atual`).

### [auth.py](auth.py)

Extrai Bearer, consulta /api/v1/perfil e traduz perfil em UsuarioContexto ou erro HTTP.

- `async obter_usuario_atual(credenciais: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)]) -> UsuarioContexto`: Resolve credenciais Bearer e perfil FIXA em UsuarioContexto ou erro HTTP.
- Constantes, aliases e estado de módulo: `bearer_scheme`.

### [permissions.py](permissions.py)

Fábrica de dependência exigir_perfis que rejeita perfil não autorizado com HTTP 403.

- `exigir_perfis(*perfis_permitidos: str) -> Callable`: Cria dependência FastAPI que restringe acesso ao conjunto de perfis informado.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../core/RESPONSABILIDADE.md).
- [app/schemas](../../schemas/RESPONSABILIDADE.md).
- [app/services/gerais](../../services/gerais/RESPONSABILIDADE.md).
