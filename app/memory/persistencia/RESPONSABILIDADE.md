# Responsabilidade: app/memory/persistencia

## Objetivo do módulo

Persistir conversas, propostas e operações de escrita.

## O que deve ser armazenado aqui

Mensagens, timestamps UTC, rascunhos versionados, anexos, resumos e registros MongoDB.

## Comportamento e limites atuais

Conversas/propostas são associadas a usuário/sessão e mantêm versão/turno/apresentação. operacoes_chat controla execução durável. Relógio UTC é reutilizado de core/tempo; não há credenciais persistidas nas operações.

Módulo pai: [app/memory](../RESPONSABILIDADE.md).

## Submódulos

| Pasta | Responsabilidade |
| --- | --- |
| [sessoes](sessoes/RESPONSABILIDADE.md) | Iniciar e encerrar sessões persistidas. |

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `ARQUIVOS_RASCUNHOS` → `.rascunho_solicitacao` (`ARQUIVOS_RASCUNHOS`).
- `CAMPO` → `.analise_compra` (`CAMPO`).
- `COLECAO` → `.operacoes` (`COLECAO`).
- `ResumoGerado` → `.gerar_resumo` (`ResumoGerado`).
- `STATUS_ATIVOS_ANALISE_COMPRA` → `.analise_compra` (`STATUS_ATIVOS`).
- `STATUS_ATIVOS_RASCUNHO_SOLICITACAO` → `.rascunho_solicitacao` (`STATUS_ATIVOS`).
- `TipoRascunho` → `.rascunho_solicitacao` (`TipoRascunho`).
- `adicionar_imagens_sessao` → `.rascunho_solicitacao` (`adicionar_imagens_sessao`).
- `agora` → `.utilitarios` (`agora`).
- `atualizar_acao` → `.acao_ajuda_geral` (`atualizar_acao`).
- `atualizar_analise_compra` → `.analise_compra` (`atualizar_analise_compra`).
- `atualizar_rascunho_solicitacao` → `.rascunho_solicitacao` (`atualizar_rascunho_solicitacao`).
- `finalizar` → `.operacoes` (`finalizar`).
- `garantir_indice_persistencia` → `.garantir_indice` (`garantir_indice_persistencia`).
- `gerar_resumo` → `.gerar_resumo` (`gerar_resumo`).
- `iniciar` → `.operacoes` (`iniciar`).
- `iniciar_acao` → `.acao_ajuda_geral` (`iniciar_acao`).
- `marcar_confirmacao_mensagem` → `.salvar_mensagem` (`marcar_confirmacao_mensagem`).
- `obter` → `.operacoes` (`obter`).
- `obter_acao` → `.acao_ajuda_geral` (`obter_acao`).
- `obter_analise_compra` → `.analise_compra` (`obter_analise_compra`).
- `obter_documento_sessao_id` → `.utilitarios` (`obter_documento_sessao_id`).
- `obter_quantidade_anexos_pendentes` → `.rascunho_solicitacao` (`obter_quantidade_anexos_pendentes`).
- `obter_rascunho_solicitacao` → `.rascunho_solicitacao` (`obter_rascunho_solicitacao`).
- `preparar` → `.operacoes` (`preparar`).
- `recuperar_mensagens` → `.recuperar_mensagens` (`recuperar_mensagens`).
- `registrar_coleta_parcial` → `.rascunho_solicitacao` (`registrar_coleta_parcial`).
- `salvar_acao` → `.acao_ajuda_geral` (`salvar_acao`).
- `salvar_analise_compra` → `.analise_compra` (`salvar_analise_compra`).
- `salvar_mensagem` → `.salvar_mensagem` (`salvar_mensagem`).
- `salvar_rascunho_solicitacao` → `.rascunho_solicitacao` (`salvar_rascunho_solicitacao`).
- `sessao_acessivel` → `.utilitarios` (`sessao_acessivel`).
- `sessoes` → `.sessoes` (submódulo).
- `sessoes_ativas` → `.utilitarios` (`sessoes_ativas`).

### [acao_ajuda_geral.py](acao_ajuda_geral.py)

Proposta de edição do ajuda_geral vinculada ao usuário e à sessão.

- `async obter_acao(sessao_id: str, usuario_id: int) -> dict | None`: Lê a proposta de edição/anexo da sessão.
- `async salvar_acao(sessao_id: str, usuario_id: int, dados: dict) -> dict`: Persiste proposta de edição/anexo com identificação própria.
- `async atualizar_acao(sessao_id: str, usuario_id: int, acao_id: str, campos: dict, *, status: str) -> bool`: Atualiza campos da proposta ajuda_geral_pendente com condições de escopo.
- `async iniciar_acao(sessao_id: str, usuario_id: int, acao_id: str) -> bool`: Tenta transição condicional da proposta para execução.

### [analise_compra.py](analise_compra.py)

Rascunho de pesquisa de compras no documento MongoDB da sessão.

- `async obter_analise_compra(sessao_id: str, usuario_id: int) -> dict | None`: Lê pesquisa de compras da sessão.
- `async salvar_analise_compra(sessao_id: str, usuario_id: int, *, dados: dict, status_fluxo: str, opcionais_oferecidos: bool, turno_id: str, ultima_busca: dict | None=None, pergunta_pendente: str | None=None) -> dict`: Persiste dados de pesquisa de compras.
- `async atualizar_analise_compra(sessao_id: str, usuario_id: int, *, id_analise: str, versao: int, status_esperado: str, campos: dict, exigir_ativo: bool=False) -> dict`: Atualiza campos/estado da pesquisa própria.
- Constantes, aliases e estado de módulo: `CAMPO`, `STATUS_ATIVOS`.

### [garantir_indice.py](garantir_indice.py)

Índices de sessão e normalização do campo de atividade de documentos antigos.

- `async garantir_indice_persistencia()`: Cria índices da coleção de sessões e preenche atividade de documentos antigos.

### [gerar_resumo.py](gerar_resumo.py)

Produz título/resumo estruturados e validados antes do encerramento.

- Classe `ResumoGerado` (`BaseModel`).
  Campos/atributos declarados: `titulo: str`, `resumo: str`.
  Métodos/validadores: `limpar_texto(cls, valor)`; `validar_titulo(cls, titulo: str) -> str`; `campos_independentes(self)`.
- `async gerar_resumo(mensagens: list[dict]) -> ResumoGerado`: Gera e valida título e resumo antes de persistir a sessão.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_formatar_conversa`.
- Constantes, aliases e estado de módulo: `_PROMPT_RESUMO`.

### [operacoes.py](operacoes.py)

Controle durável das gravações aprovadas no chat, sem dados de autenticação.

- `async preparar(documento: dict) -> dict`: Persiste operação preparada ou verifica consistência de preparação repetida.
- `async obter(operacao_id: str, usuario_id: int, sessao_id: str) -> dict | None`: Obtém registro durável da operação pelo identificador.
- `async iniciar(documento: dict, aprovacao: dict) -> bool`: Somente um executor pode retirar a operação do estado preparada.
- `async finalizar(documento: dict, resultado: dict) -> None`: Registra resultado da operação iniciada, preservando transição durável.
- Constantes, aliases e estado de módulo: `COLECAO`.

### [rascunho_solicitacao.py](rascunho_solicitacao.py)

Rascunhos dos três cadastros, coleta parcial, anexos e atualização versionada na sessão.

- `async obter_quantidade_anexos_pendentes(sessao_id: str, usuario_id: int) -> int`: Conta anexos ainda pendentes da sessão.
- `async registrar_coleta_parcial(sessao_id: str, usuario_id: int, *, tipo: TipoRascunho, turno_id: str, relato: str, operacao: Literal['criar', 'atualizar']='criar') -> dict[str, Any]`: Guarda o relato do usuário sem exigir IDs ou propor um cadastro completo.
- `async adicionar_imagens_sessao(sessao_id: str, usuario_id: int, imagens: list[str], *, tipo: TipoRascunho | None=None) -> None`: Associa novas URLs aos anexos/rascunhos da sessão.
- `async salvar_rascunho_solicitacao(sessao_id: str, usuario_id: int, dados: dict[str, Any], *, tipo: TipoRascunho='solicitacao', turno_id: str, rotulos: dict[str, str] | None=None) -> dict[str, Any]`: Salva/versiona proposta por tipo e preserva anexos, relatos e aceites compatíveis.
- `async obter_rascunho_solicitacao(sessao_id: str, usuario_id: int, *, tipo: TipoRascunho='solicitacao') -> dict[str, Any] | None`: Recupera rascunho do tipo solicitado na sessão.
- `async atualizar_rascunho_solicitacao(sessao_id: str, usuario_id: int, campos: dict[str, Any], *, status_esperados: set[str] | None=None, tipo: TipoRascunho='solicitacao', rascunho_id: str | None=None, versao: int | None=None, exigir_ativo: bool=False) -> bool`: Atualiza rascunho por usuário, sessão, tipo e identificação esperada.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_campo_rascunho`, `_urls_validas`, `_anexos_legados`.
- Constantes, aliases e estado de módulo: `TipoRascunho`, `ARQUIVOS_RASCUNHOS`, `STATUS_ATIVOS`.

### [recuperar_mensagens.py](recuperar_mensagens.py)

Lê mensagens da sessão com padrões legados de emoção/confirmação.

- `async recuperar_mensagens(documento_id: str, usuario_id: int) -> list[dict]`: Lê mensagens próprias com padrões compatíveis com dados legados.

### [salvar_mensagem.py](salvar_mensagem.py)

Persiste mensagens/timestamps, valida visualização/quota e marca confirmação após salvar.

- `async salvar_mensagem(sessao_id: str, papel: str, conteudo: str, usuario_id: int, imagens: list[str] | None=None, *, associar_imagens: bool=True, emocao: Emocao | str | None=None, turno_id: str | None=None, visualizacao: dict | None=None) -> None`: Persiste mensagem própria com timestamp e anexos; aplica validação/quota quando há visualização.
- `async marcar_confirmacao_mensagem(sessao_id: str, usuario_id: int, turno_id: str) -> None`: Marca confirmação na mensagem já persistida da sessão/turno.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_salvar_com_visualizacao`.

### [utilitarios.py](utilitarios.py)

Cache de sessões ativas, relógio UTC, resolução de documento e verificação de acesso.

- `async obter_documento_sessao_id(sessao_id: str, usuario_id: int) -> str | None`: Resolve documento da sessão usando cache e MongoDB.
- `async sessao_acessivel(sessao_id: str, usuario_id: int) -> bool`: Confirma no Mongo que a conversa pertence ao usuário e está no histórico.
- Constantes, aliases e estado de módulo: `sessoes_ativas: dict[tuple[int, str], str]`.

## Estruturas persistidas e reutilização

- A coleção `sessoes` guarda `user_id`, `session_id`, atividade, datas, mensagens e, quando existentes, título/resumo.
- As mensagens incluem `role`, `mensagem`, `timestamp`, emoção/confirmação e anexos/visualização quando aplicável. Timestamp é UTC; histórico antigo sem horário retorna null.
- `rascunho_solicitacao.py` atende `solicitacao_pendente`, `ocorrencia_pendente` e `evento_pendente`. Reutilize o parâmetro de tipo, sem duplicar persistência para cada cadastro.
- Rascunhos acompanham `id`, `tipo`, `versao`, `turno_id`, `dados`, `status_fluxo`, pausa, apresentação, campos confirmados e imagens. Atualizações ainda guardam operação, etapa, candidatos, registro original, alterações e escolha de fotos.
- `acao_ajuda_geral.py` mantém `ajuda_geral_pendente`; `analise_compra.py` mantém `analise_compra_pendente`.
- `operacoes.py` mantém `operacoes_chat`, com preparação, início condicional e resultado durável. O controle local `sessoes_ativas` acelera acesso; autorização também é conferida no banco.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../core/RESPONSABILIDADE.md).
- [app/core/clients](../../core/clients/RESPONSABILIDADE.md).
- [app/memory/persistencia/sessoes](sessoes/RESPONSABILIDADE.md).
- [app/services/visualizacoes](../../services/visualizacoes/RESPONSABILIDADE.md).
