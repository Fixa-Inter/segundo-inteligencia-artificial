# Responsabilidade: app/services/eventos

## Objetivo do módulo

Enviar cadastro de evento à API FIXA.

## O que deve ser armazenado aqui

Adaptação de CriarEventoEntrada para POST autenticado.

## Comportamento e limites atuais

Token e usuário vêm do backend. Não repete POST automaticamente; resultado incerto é controlado pelo fluxo.

Módulo pai: [app/services](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `adicionar_evento` → `.criarEvento` (`adicionar_evento`).

### [criarEvento.py](criarEvento.py)

Cadastro de evento na API FIXA, sem repetição automática de POST.

- `async adicionar_evento(evento: CriarEventoEntrada, access_token: str, *, usuario_id: int) -> dict`: Faz POST autenticado de evento e interpreta sucesso, erro ou resultado incerto sem repetir envio.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../core/RESPONSABILIDADE.md).
- [app/schemas/cadastros](../../schemas/cadastros/RESPONSABILIDADE.md).
- [app/services/gerais](../gerais/RESPONSABILIDADE.md).
