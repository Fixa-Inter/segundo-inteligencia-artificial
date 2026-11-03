# Responsabilidade: app/tools/solicitacoes

## Objetivo do módulo

Adaptar cadastro, consulta e atualização.

## O que deve ser armazenado aqui

Busca de categoria/local, rascunhos, propostas e listagens.

## Comportamento e limites atuais

Compartilha armazenamento com operacao=criar/atualizar. Atualização tem dois aceites e escolha explícita de adicionar/substituir fotos; sem novas imagens preserva as existentes.

Módulo pai: [app/tools](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `atualizar_solicitacao` → `.atualizarSolicitacao` (`atualizar_solicitacao`).
- `buscar_opcoes_solicitacao` → `.buscarOpcoes` (`buscar_opcoes_solicitacao`).
- `buscar_solicitacoes_para_atualizar` → `.atualizarSolicitacao` (`buscar_solicitacoes_para_atualizar`).
- `criar_solicitacao` → `.criarSolicitacao` (`criar_solicitacao`).
- `listar_minhas_solicitacoes` → `.listarMinhasSolicitacoes` (`listar_minhas_solicitacoes`).
- `listar_todas_solicitacoes_pendentes` → `.listarTodasSolicitacoesPendentes` (`listar_todas_solicitacoes_pendentes`).
- `processar_atualizacao` → `.atualizarSolicitacao` (`processar_atualizacao`).
- `processar_solicitacao` → `.criarSolicitacao` (`processar_solicitacao`).
- `salvar_rascunho_solicitacao` → `.criarSolicitacao` (`salvar_rascunho_solicitacao`).

### [atualizarSolicitacao.py](atualizarSolicitacao.py)

Seleção, proposta e aceite de atualização no mesmo rascunho de solicitação.

- `async buscar_solicitacoes_para_atualizar(descricao: str, runtime: ToolRuntime) -> dict`: Busca no Qdrant solicitações próprias pendentes pelo significado da descrição.
- `async atualizar_solicitacao(runtime: ToolRuntime, problema_id: int | None=None, titulo: str | None=None, descricao_problema: str | None=None, descricao_local: str | None=None, local_unidade_id: int | None=None, categoria_equipamento_id: int | None=None, acao_fotos: Literal['adicionar', 'substituir'] | None=None) -> dict`: Seleciona uma solicitação encontrada, coleta várias alterações e prepara atualização após dois aceites.
- `async processar_atualizacao(runtime, *, operacao_aprovada: dict | None=None) -> dict`: Confere proposta final de atualização; prepara operação ou efetiva pelo serviço quando já aprovada.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_salvar`, `_resposta`, `_erro`.

### [buscarOpcoes.py](buscarOpcoes.py)

Consulta categoria/local em paralelo com unidade autenticada.

- `async buscar_opcoes_solicitacao(equipamento: str, local: str, runtime: ToolRuntime) -> dict`: Busca categorias do equipamento e locais da sede autenticada.

### [criarSolicitacao.py](criarSolicitacao.py)

Salva proposta, confere aceite e prepara criação; processar_solicitacao atende execução aprovada.

- `async salvar_rascunho_solicitacao(categoria_equipamento_id: int, local_endereco_id: int, titulo: str, descricao_problema: str, runtime: ToolRuntime, descricao_local: str) -> dict`: Persiste no Mongo a proposta de solicitação antes de pedir confirmação.
- `async criar_solicitacao(runtime: ToolRuntime) -> dict`: Prepara o envio da solicitação confirmada para aprovação interna.
- `async processar_solicitacao(runtime: ToolRuntime, *, operacao_aprovada: dict | None=None) -> dict`: Confere proposta/aceite/anexos e prepara operação, ou envia a operação já aprovada.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_ArgumentosCriarSolicitacao`, `_normalizar_status_backend`.
- Constantes, aliases e estado de módulo: `registrador`.

### [listarMinhasSolicitacoes.py](listarMinhasSolicitacoes.py)

Wrapper das três solicitações próprias recentes na janela de três meses.

- `async listar_minhas_solicitacoes(runtime: ToolRuntime) -> dict`: Lista ate tres solicitacoes do usuario nos ultimos tres meses.
- Constantes, aliases e estado de módulo: `registrador`.

### [listarTodasSolicitacoesPendentes.py](listarTodasSolicitacoesPendentes.py)

Wrapper das cinco pendências recentes da unidade para gestor/administrador.

- `async listar_todas_solicitacoes_pendentes(runtime: ToolRuntime) -> dict`: Lista ate cinco pendencias do gestor nos ultimos tres meses.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../core/RESPONSABILIDADE.md).
- [app/core/clients](../../core/clients/RESPONSABILIDADE.md).
- [app/memory/persistencia](../../memory/persistencia/RESPONSABILIDADE.md).
- [app/memory/vectorSearch](../../memory/vectorSearch/RESPONSABILIDADE.md).
- [app/schemas](../../schemas/RESPONSABILIDADE.md).
- [app/schemas/cadastros](../../schemas/cadastros/RESPONSABILIDADE.md).
- [app/services](../../services/RESPONSABILIDADE.md).
- [app/services/gerais](../../services/gerais/RESPONSABILIDADE.md).
- [app/services/solicitacoes](../../services/solicitacoes/RESPONSABILIDADE.md).
- [app/tools](../RESPONSABILIDADE.md).
- [app/tools/ajuda_geral](../ajuda_geral/RESPONSABILIDADE.md).
