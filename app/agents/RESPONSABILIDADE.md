# Responsabilidade: app/agents

## Objetivo do módulo

Construir, selecionar e avaliar agentes especializados.

## O que deve ser armazenado aqui

Fábricas, modelos de linguagem, roteamento de intenção, julgamento e emoção.

## Comportamento e limites atuais

Registro compõe especialistas por perfil; modelos.py é compatibilidade para core/clients/modelos.py. Resultados canônicos estão em schemas/resultados_agentes. Juiz avalia evidências e revisão altera somente texto.

Módulo pai: [app](../RESPONSABILIDADE.md).

## Submódulos

| Pasta | Responsabilidade |
| --- | --- |
| [agentsResult](agentsResult/RESPONSABILIDADE.md) | Preservar importações históricas dos resultados estruturados. |
| [compras](compras/RESPONSABILIDADE.md) | Separar as etapas de coleta e comparação de promoções. |
| [prompts](prompts/RESPONSABILIDADE.md) | Compor instruções dos especialistas para cada perfil. |

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `AGENTES_POR_PERFIL` → `.registro` (`AGENTES_POR_PERFIL`).
- `CRITERIOS_EMOCAO` → `.emocoes` (`CRITERIOS_EMOCAO`).
- `CRITERIOS_MOTIVO` → `.juiz` (`CRITERIOS_MOTIVO`).
- `CRITERIOS_VEREDITO` → `.juiz` (`CRITERIOS_VEREDITO`).
- `DecisaoRoteamento` → `.orquestrador` (`DecisaoRoteamento`).
- `FEEDBACK_MOTIVO` → `.juiz` (`FEEDBACK_MOTIVO`).
- `LimiteConsultasVisualizacao` → `.visualizacao` (`LimiteConsultasVisualizacao`).
- `POLITICAS_PERFIL` → `.juiz` (`POLITICAS_PERFIL`).
- `PROMPT_CLASSIFICACAO` → `.emocoes` (`PROMPT_CLASSIFICACAO`).
- `RespostaRevisada` → `.juiz` (`RespostaRevisada`).
- `TABELAS_LISTAGEM` → `.juiz` (`TABELAS_LISTAGEM`).
- `TEMPO_LIMITE_CLASSIFICACAO` → `.emocoes` (`TEMPO_LIMITE_CLASSIFICACAO`).
- `agentsResult` → `.agentsResult` (submódulo).
- `ajuda_geral_administrador` → `.registro` (`ajuda_geral_administrador`).
- `ajuda_geral_gestor` → `.registro` (`ajuda_geral_gestor`).
- `ajuda_geral_solicitante` → `.registro` (`ajuda_geral_solicitante`).
- `ajuda_geral_tecnico` → `.registro` (`ajuda_geral_tecnico`).
- `classificar_emocao` → `.emocoes` (`classificar_emocao`).
- `compras` → `.compras` (submódulo).
- `criar_agente_ajuda_geral` → `.ajuda_geral` (`criar_agente_ajuda_geral`).
- `criar_agente_faq` → `.faq` (`criar_agente_faq`).
- `criar_agente_indicadores` → `.indicadores` (`criar_agente_indicadores`).
- `criar_agente_retorno_usuario` → `.retorno_usuario` (`criar_agente_retorno_usuario`).
- `criar_agente_solicitacoes` → `.solicitacoes` (`criar_agente_solicitacoes`).
- `criar_agente_visualizacao` → `.visualizacao` (`criar_agente_visualizacao`).
- `emocao_alternativa` → `.emocoes` (`emocao_alternativa`).
- `emocao_fluxo` → `.emocoes` (`emocao_fluxo`).
- `executar` → `.analista_compras` (`executar`).
- `faq_administrador` → `.registro` (`faq_administrador`).
- `faq_gestor` → `.registro` (`faq_gestor`).
- `faq_solicitante` → `.registro` (`faq_solicitante`).
- `faq_tecnico` → `.registro` (`faq_tecnico`).
- `feedback` → `.registro` (`feedback`).
- `formatar_contexto_conversa` → `.juiz` (`formatar_contexto_conversa`).
- `indicadores_administrador` → `.registro` (`indicadores_administrador`).
- `indicadores_gestor` → `.registro` (`indicadores_gestor`).
- `julgar_compra` → `.juiz_compras` (`julgar_compra`).
- `julgar_resposta` → `.juiz` (`julgar_resposta`).
- `llm_especialista` → `.modelos` (`llm_especialista`).
- `llm_luna` → `.modelos` (`llm_luna`).
- `llm_rapido` → `.modelos` (`llm_rapido`).
- `obter_modelo_embedding` → `.modelos` (`obter_modelo_embedding`).
- `obter_pergunta` → `.juiz` (`obter_pergunta`).
- `pedido_compra_explicito` → `.orquestrador` (`pedido_compra_explicito`).
- `prompts` → `.prompts` (submódulo).
- `resumir_operacoes` → `.emocoes` (`resumir_operacoes`).
- `revisar_resposta` → `.juiz` (`revisar_resposta`).
- `roteador_estruturado` → `.orquestrador` (`roteador_estruturado`).
- `rotear_orquestrador` → `.orquestrador` (`rotear_orquestrador`).
- `selecionar_agente` → `.registro` (`selecionar_agente`).
- `solicitacoes_administrador` → `.registro` (`solicitacoes_administrador`).
- `solicitacoes_gestor` → `.registro` (`solicitacoes_gestor`).
- `solicitacoes_solicitante` → `.registro` (`solicitacoes_solicitante`).
- `solicitacoes_tecnico` → `.registro` (`solicitacoes_tecnico`).
- `visualizacoes_administrador` → `.registro` (`visualizacoes_administrador`).
- `visualizacoes_gestor` → `.registro` (`visualizacoes_gestor`).

### [ajuda_geral.py](ajuda_geral.py)

Fábrica de consultas/edições com ferramentas por perfil e resposta FAQResultado.

- `criar_agente_ajuda_geral(modelo, instrucao: str, *, perfil: str)`: Constrói agente de ajuda geral com ferramentas e contrato de saída descritos neste arquivo.

### [analista_compras.py](analista_compras.py)

Coordena cobertura de lojas, coleta, busca, avaliação e persistência da análise.

- `async executar(estado: dict, contexto: dict) -> dict`: Coordena pesquisa de lojas/ofertas e atualiza rascunho e evidências da compra.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_pede_cobertura`, `_responder_cobertura`.
- Constantes, aliases e estado de módulo: `LOGGER`.

### [emocoes.py](emocoes.py)

Classifica emoção com JEV, timeout e alternativas determinísticas a partir do fluxo.

- `resumir_operacoes(estado: 'EstadoGrafo') -> list[dict[str, str]]`: Extrai status/resultados operacionais das evidências para classificação de emoção.
- `emocao_fluxo(estado: 'EstadoGrafo') -> Emocao | None`: Seleciona emoção determinística para situações específicas do fluxo.
- `emocao_alternativa(operacoes: list[dict[str, str]]) -> Emocao`: Escolhe emoção a partir de status e operações quando o classificador não decide.
- `async classificar_emocao(estado: 'EstadoGrafo') -> dict`: Classifica a resposta final com JEV, timeout e alternativas determinísticas.
- Constantes, aliases e estado de módulo: `registrador`, `TEMPO_LIMITE_CLASSIFICACAO`, `PROMPT_CLASSIFICACAO`, `CRITERIOS_EMOCAO`.

### [faq.py](faq.py)

Fábrica FAQ com memória, busca vetorial e fallback de modelo opcional.

- `criar_agente_faq(modelo, instrucao: str, modelo_alternativo=None)`: Constrói agente de faq com ferramentas e contrato de saída descritos neste arquivo.

### [indicadores.py](indicadores.py)

Fábrica com 36 ferramentas de indicadores, memória e resposta estruturada; deduplica por nome.

- `criar_agente_indicadores(modelo, instrucao: str, ferramentas=None)`: Constrói agente de indicadores com ferramentas e contrato de saída descritos neste arquivo.

### [juiz.py](juiz.py)

Julga evidências/resposta via JEV, vincula aprovação de operações/gráficos e permite revisão textual.

- `obter_pergunta(estado: EstadoGrafo) -> str`: Obtém a pergunta atual das mensagens do estado.
- `formatar_contexto_conversa(estado: EstadoGrafo) -> str`: Serializa histórico e propostas relevantes para o julgamento.
- Classe `RespostaRevisada` (`BaseModel`).
  Campos/atributos declarados: `resposta: str`.
- `async revisar_resposta(estado: EstadoGrafo, runtime: Runtime[ContextoGrafo]=None) -> dict`: Revisa texto com base nas evidências, preserva dados capturados e exige novo julgamento.
- `async julgar_resposta(estado: EstadoGrafo, runtime: Runtime[ContextoGrafo]=None) -> dict`: Avalia resposta/evidências e aprova, bloqueia ou solicita revisão, vinculando operações e gráficos aprovados.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_revisar_resposta`, `_evidencias_jev`, `_evidencias_avaliacao`, `_julgar_resposta`.
- Constantes, aliases e estado de módulo: `POLITICAS_PERFIL`, `CRITERIOS_VEREDITO`, `CRITERIOS_MOTIVO`, `FEEDBACK_MOTIVO`, `registrador`, `TABELAS_LISTAGEM`.

### [juiz_compras.py](juiz_compras.py)

Julgamento de compras com evidências compactas das promoções consultadas.

- `async julgar_compra(estado: dict) -> dict`: Avalia resposta de compras contra evidências compactas das promoções.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_evidencias_compactas`.
- Constantes, aliases e estado de módulo: `LOGGER`.

### [modelos.py](modelos.py)

Compatibilidade dos clientes LLM/embedding canônicos de core/clients/modelos.py; mesmos objetos e configuração.

### [orquestrador.py](orquestrador.py)

Decisão estruturada de intenção, continuidade e operação criar/atualizar a partir do histórico/propostas.

- Classe `DecisaoRoteamento` (`BaseModel`).
  Campos/atributos declarados: `operacao_ocorrencia: Literal['criar', 'atualizar']`, `operacao_solicitacao: Literal['criar', 'atualizar']`, `intencao: Literal['ajuda_geral', 'faq', 'solicitacao', 'ocorrencia', 'evento', 'analytics', 'visualizacao', 'feedback', 'analista_compras', 'fora_de_escopo']`, `continua_pendente: bool`, `precisa_esclarecimento: bool`, `cadastro_em_andamento: bool`, `justificativa: str`.
- `pedido_compra_explicito(pergunta: str) -> bool`: Detecta menção explícita a busca de compra/lojas para apoiar roteamento.
- `async rotear_orquestrador(estado: dict, pergunta: str) -> DecisaoRoteamento`: Produz decisão estruturada de intenção, continuidade e operação, usando conversa/propostas.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_resumir_propostas`.
- Constantes, aliases e estado de módulo: `roteador_estruturado`.

### [registro.py](registro.py)

Instâncias prontas, mapa AGENTES_POR_PERFIL e seleção por intenção/perfil.

- `selecionar_agente(tipo: str, perfil: str, candidatos=None)`: Seleciona instância pela funcionalidade e pelo perfil.
- Constantes, aliases e estado de módulo: `ajuda_geral_solicitante`, `ajuda_geral_tecnico`, `ajuda_geral_administrador`, `ajuda_geral_gestor`, `faq_solicitante`, `faq_tecnico`, `faq_administrador`, `faq_gestor`, `solicitacoes_solicitante`, `solicitacoes_tecnico`, `solicitacoes_administrador`, `solicitacoes_gestor`, `indicadores_gestor`, `indicadores_administrador`, `visualizacoes_gestor`, `visualizacoes_administrador`, `feedback`, `AGENTES_POR_PERFIL`.

### [retorno_usuario.py](retorno_usuario.py)

Fábrica de feedback com ferramentas recebidas e consulta à memória.

- `criar_agente_retorno_usuario(modelo, instrucao: str, ferramentas=None)`: Constrói agente de retorno usuario com ferramentas e contrato de saída descritos neste arquivo.

### [solicitacoes.py](solicitacoes.py)

Fábrica compartilhada de solicitações/ocorrências/eventos, com ferramentas por flags de perfil.

- `criar_agente_solicitacoes(modelo, instrucao: str, modelo_alternativo=None, *, gestor: bool=False, tecnico: bool=False, solicitante: bool=False)`: Constrói agente de solicitacoes com ferramentas e contrato de saída descritos neste arquivo.

### [visualizacao.py](visualizacao.py)

Fábrica e middleware que limita a três chamadas analíticas por execução, inclusive em lotes.

- Classe `LimiteConsultasVisualizacao` (`ToolCallLimitMiddleware`): Orçamento compartilhado das seis tools, contado antes do lote executar.
  Métodos/validadores: `__init__(self)`; `_matches_tool_filter(self, tool_call)`; `after_model(self, state, runtime)`.
- `criar_agente_visualizacao(modelo, instrucao: str, ferramentas=None)`: Constrói agente de visualizacao com ferramentas e contrato de saída descritos neste arquivo.

## Composição atual

`registro.py` preserva ferramentas por perfil e as instâncias dos especialistas. `modelos.py` reexporta clientes de core/clients, com mesmo modelo, aliases e opções. Contratos estruturados são canônicos em schemas/resultados_agentes.

O juiz continua avaliando evidências antes de gravações/publicação; revisão altera somente texto. Administrador segue as ferramentas do gestor. Criação de solicitação permanece de solicitante/técnico; ocorrência de técnico/gestor/administrador; evento de gestor/administrador. Atualizações preservam autoria/unidade/status/atividade específicos de cada domínio.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/agents/compras](compras/RESPONSABILIDADE.md).
- [app/agents/prompts](prompts/RESPONSABILIDADE.md).
- [app/agents/prompts/reutilizaveis](prompts/reutilizaveis/RESPONSABILIDADE.md).
- [app/core](../core/RESPONSABILIDADE.md).
- [app/core/apresentacao](../core/apresentacao/RESPONSABILIDADE.md).
- [app/core/clients](../core/clients/RESPONSABILIDADE.md).
- [app/graph](../graph/RESPONSABILIDADE.md).
- [app/guardrails](../guardrails/RESPONSABILIDADE.md).
- [app/mcp/pechincha](../mcp/pechincha/RESPONSABILIDADE.md).
- [app/memory/persistencia](../memory/persistencia/RESPONSABILIDADE.md).
- [app/schemas](../schemas/RESPONSABILIDADE.md).
- [app/schemas/resultados_agentes](../schemas/resultados_agentes/RESPONSABILIDADE.md).
- [app/services](../services/RESPONSABILIDADE.md).
- [app/services/gerais](../services/gerais/RESPONSABILIDADE.md).
- [app/services/visualizacoes](../services/visualizacoes/RESPONSABILIDADE.md).
- [app/tools/ajuda_geral](../tools/ajuda_geral/RESPONSABILIDADE.md).
- [app/tools/eventos](../tools/eventos/RESPONSABILIDADE.md).
- [app/tools/faq](../tools/faq/RESPONSABILIDADE.md).
- [app/tools/feedback](../tools/feedback/RESPONSABILIDADE.md).
- [app/tools/memoria](../tools/memoria/RESPONSABILIDADE.md).
- [app/tools/metricas_kpis](../tools/metricas_kpis/RESPONSABILIDADE.md).
- [app/tools/ocorrencias](../tools/ocorrencias/RESPONSABILIDADE.md).
- [app/tools/ordensServico](../tools/ordensServico/RESPONSABILIDADE.md).
- [app/tools/solicitacoes](../tools/solicitacoes/RESPONSABILIDADE.md).
- [app/tools/tecnicos](../tools/tecnicos/RESPONSABILIDADE.md).
- [app/tools/visualizacoes](../tools/visualizacoes/RESPONSABILIDADE.md).
