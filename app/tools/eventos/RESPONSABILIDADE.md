# Responsabilidade: app/tools/eventos

## Objetivo do módulo

Coletar e confirmar propostas de eventos.

## O que deve ser armazenado aqui

Busca de local, rascunho e preparação de criação.

## Comportamento e limites atuais

Gestor/administrador, web/mobile. Exige local, descrição, início/fim; não exige foto/categoria. Datas sem fuso usam America/Sao_Paulo e são enviadas em UTC.

Módulo pai: [app/tools](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `buscar_opcoes_evento` → `.buscarOpcoesEvento` (`buscar_opcoes_evento`).
- `criar_evento` → `.criarEvento` (`criar_evento`).
- `processar_evento` → `.criarEvento` (`processar_evento`).
- `salvar_rascunho_evento` → `.criarEvento` (`salvar_rascunho_evento`).

### [buscarOpcoesEvento.py](buscarOpcoesEvento.py)

Recursos deste arquivo: Busca locais ativos da unidade autenticada para um evento.

- `async buscar_opcoes_evento(local: str, runtime: ToolRuntime) -> dict`: Busca locais ativos da unidade autenticada para um evento.

### [criarEvento.py](criarEvento.py)

Rascunho, confirmação e preparação do envio de eventos.

- `async salvar_rascunho_evento(local_unidade_id: int, titulo: str, descricao: str, data_hora_inicio: datetime, data_hora_fim: datetime, runtime: ToolRuntime, descricao_local: str='Não foi especificado', observacao: str='Não foi especificado') -> dict`: Salva a proposta de evento antes de apresentar os dados para confirmação.
- `async criar_evento(runtime: ToolRuntime) -> dict`: Prepara o evento confirmado para aprovação interna, sem executar o POST.
- `async processar_evento(runtime: ToolRuntime, *, operacao_aprovada: dict | None=None) -> dict`: Confere proposta/aceite e prepara operação, ou faz envio quando recebe operação aprovada do executor.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_ArgumentosCriarEvento`.
- Constantes, aliases e estado de módulo: `registrador`.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../core/RESPONSABILIDADE.md).
- [app/core/clients](../../core/clients/RESPONSABILIDADE.md).
- [app/memory/persistencia](../../memory/persistencia/RESPONSABILIDADE.md).
- [app/memory/vectorSearch](../../memory/vectorSearch/RESPONSABILIDADE.md).
- [app/schemas/cadastros](../../schemas/cadastros/RESPONSABILIDADE.md).
- [app/services](../../services/RESPONSABILIDADE.md).
- [app/services/eventos](../../services/eventos/RESPONSABILIDADE.md).
- [app/services/gerais](../../services/gerais/RESPONSABILIDADE.md).
- [app/tools](../RESPONSABILIDADE.md).
