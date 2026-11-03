# Responsabilidade: app/services/solicitacoes

## Objetivo do módulo

Consultar, cadastrar e atualizar solicitações.

## O que deve ser armazenado aqui

Listagens SQL, POST FIXA e atualização própria transacional.

## Comportamento e limites atuais

Busca cruza Qdrant com registros próprios pendentes. Escrita revalida autoria/unidade/status 0/snapshot. Fotos e textos compartilham transação. Pendências têm limite cinco; próprias, três.

Módulo pai: [app/services](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `CAMPOS` → `.atualizarSolicitacao` (`CAMPOS`).
- `adicionar_solicitacao` → `.criarSolicitacao` (`adicionar_solicitacao`).
- `atualizar_propria_pendente` → `.atualizarSolicitacao` (`atualizar_propria_pendente`).
- `buscar_proprias_pendentes` → `.atualizarSolicitacao` (`buscar_proprias_pendentes`).
- `consultar_propria_pendente` → `.atualizarSolicitacao` (`consultar_propria_pendente`).
- `listar_minhas_solicitacoes` → `.buscarSolicitacao` (`listar_minhas_solicitacoes`).
- `listar_solicitacoes_pendentes` → `.buscarSolicitacao` (`listar_solicitacoes_pendentes`).
- `snapshot` → `.atualizarSolicitacao` (`snapshot`).
- `validar_alteracoes` → `.atualizarSolicitacao` (`validar_alteracoes`).

### [atualizarSolicitacao.py](atualizarSolicitacao.py)

Busca semântica própria e atualização transacional de solicitações pendentes.

- `validar_alteracoes(alteracoes: dict) -> dict`: Valida campos permitidos da atualização do domínio.
- `async buscar_proprias_pendentes(usuario, descricao: str) -> list[dict]`: Cruza busca vetorial com IDs de solicitações próprias pendentes na unidade.
- `async consultar_propria_pendente(usuario, registro_id: int) -> dict | None`: Lê solicitação/fotos atuais conferindo autoria, unidade e status pendente.
- `snapshot(registro: dict) -> dict`: Extrai dados originais para detectar mudança antes da escrita.
- `async atualizar_propria_pendente(usuario, dados: dict) -> dict | None`: Trava e revalida solicitação/snapshot e grava campos/fotos em transação única.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_ler`.
- Constantes, aliases e estado de módulo: `CAMPOS`.

### [buscarSolicitacao.py](buscarSolicitacao.py)

SQL de solicitações próprias e pendências da unidade com período/limites próprios.

- `async listar_solicitacoes_pendentes(usuario: UsuarioContexto) -> dict`: Lista ate cinco pendencias recentes da unidade nos ultimos tres meses.
- `async listar_minhas_solicitacoes(usuario: UsuarioContexto) -> dict`: Lista as tres solicitacoes mais recentes do usuario nos ultimos tres meses.
- Constantes, aliases e estado de módulo: `registrador`, `_SQL_BASE`.

### [criarSolicitacao.py](criarSolicitacao.py)

Recursos deste arquivo: Envia o cadastro diretamente. Sem estado de conversa ou repetição de POST.

- `async adicionar_solicitacao(solicitacao: CriarSolicitacaoEntrada, access_token: str, *, imagens: list[str]) -> dict`: Envia o cadastro diretamente. Sem estado de conversa ou repetição de POST.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../core/RESPONSABILIDADE.md).
- [app/core/apresentacao](../../core/apresentacao/RESPONSABILIDADE.md).
- [app/core/clients](../../core/clients/RESPONSABILIDADE.md).
- [app/memory/embedding](../../memory/embedding/RESPONSABILIDADE.md).
- [app/memory/vectorSearch](../../memory/vectorSearch/RESPONSABILIDADE.md).
- [app/schemas](../../schemas/RESPONSABILIDADE.md).
- [app/schemas/cadastros](../../schemas/cadastros/RESPONSABILIDADE.md).
- [app/services/ajuda_geral](../ajuda_geral/RESPONSABILIDADE.md).
- [app/services/gerais](../gerais/RESPONSABILIDADE.md).
