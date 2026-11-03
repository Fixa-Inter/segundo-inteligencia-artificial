# Responsabilidade: app/graph

## Objetivo do módulo

Orquestrar o turno da conversa e a execução de operações aprovadas.

## O que deve ser armazenado aqui

Estado/contexto LangGraph, nós, transições, evidências, continuações e respostas determinísticas.

## Comportamento e limites atuais

executor recupera memória e persiste a saída; fluxo compila com MemorySaver. O juiz precede gravações. executar_operacoes usa lista explícita de serviços e controle durável no MongoDB.

Módulo pai: [app](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `CONSULTAS_COM_ORIENTACAO` → `.respostas_padrao` (`CONSULTAS_COM_ORIENTACAO`).
- `ContextoGrafo` → `.contexto` (`ContextoGrafo`).
- `EstadoGrafo` → `.estado` (`EstadoGrafo`).
- `PERFIS_VALIDOS` → `.executor` (`PERFIS_VALIDOS`).
- `Perfil` → `.executor` (`Perfil`).
- `TEXTOS` → `.respostas_padrao` (`TEXTOS`).
- `alterar_continuacao` → `.continuacoes` (`alterar_continuacao`).
- `construir_grafo` → `.fluxo` (`construir_grafo`).
- `criar_estado_inicial` → `.executor` (`criar_estado_inicial`).
- `decidir_apos_entrada` → `.transicoes` (`decidir_apos_entrada`).
- `decidir_apos_julgamento` → `.transicoes` (`decidir_apos_julgamento`).
- `decidir_apos_visualizacao` → `.transicoes` (`decidir_apos_visualizacao`).
- `esclarecer_continuacao` → `.continuacoes` (`esclarecer_continuacao`).
- `executar_ajuda_geral` → `.nos` (`executar_ajuda_geral`).
- `executar_analista_compras` → `.nos` (`executar_analista_compras`).
- `executar_com_evidencias` → `.evidencias` (`executar_com_evidencias`).
- `executar_faq` → `.nos` (`executar_faq`).
- `executar_grafo` → `.executor` (`executar_grafo`).
- `executar_indicadores` → `.nos` (`executar_indicadores`).
- `executar_operacoes` → `.operacoes` (`executar_operacoes`).
- `executar_retorno_usuario` → `.nos` (`executar_retorno_usuario`).
- `executar_servico` → `.operacoes` (`executar_servico`).
- `executar_solicitacao` → `.nos` (`executar_solicitacao`).
- `executar_visualizacao` → `.nos` (`executar_visualizacao`).
- `extrair_evidencias` → `.evidencias` (`extrair_evidencias`).
- `grafo` → `.fluxo` (`grafo`).
- `ids_chamadas` → `.evidencias` (`ids_chamadas`).
- `limpar_visualizacao` → `.estado` (`limpar_visualizacao`).
- `obter_pergunta` → `.nos` (`obter_pergunta`).
- `pausar_outros_fluxos` → `.continuacoes` (`pausar_outros_fluxos`).
- `preparar_resposta` → `.propostas` (`preparar_resposta`).
- `preparar_resposta_padrao` → `.respostas_padrao` (`preparar_resposta_padrao`).
- `propostas_pendentes` → `app.core.continuacoes` (`propostas_pendentes`).
- `propostas_resposta` → `.propostas` (`propostas_resposta`).
- `resposta_interrupcao_proposta` → `.respostas_padrao` (`resposta_interrupcao_proposta`).
- `resposta_padrao_validada` → `.respostas_padrao` (`resposta_padrao_validada`).
- `resposta_resultados` → `.operacoes` (`resposta_resultados`).
- `selecionar_especialista` → `.transicoes` (`selecionar_especialista`).
- `selecionar_resposta_fallback` → `.respostas_padrao` (`selecionar_resposta_fallback`).
- `selecionar_resposta_saida` → `.respostas_padrao` (`selecionar_resposta_saida`).
- `supervisionar` → `.nos` (`supervisionar`).
- `tratar_continuacao` → `.continuacoes` (`tratar_continuacao`).
- `tratar_erro` → `.nos` (`tratar_erro`).
- `validar_entrada` → `.nos` (`validar_entrada`).
- `validar_saida` → `.nos` (`validar_saida`).

### [contexto.py](contexto.py)

TypedDict ContextoGrafo com autenticação, sessão, turno, imagens e recursos da execução.

- Classe `ContextoGrafo` (`TypedDict`).
  Campos/atributos declarados: `usuario: UsuarioContexto`, `imagens: list[str]`, `session_id: str`, `mensagem_atual: str`, `turno_id: str`, `contexto_temporal: str`, `plataforma: NotRequired[Literal['web', 'mobile']]`, `captura_visualizacao: NotRequired[object]`, `operacoes_pendentes: NotRequired[list[dict]]`, `resultados_operacoes: NotRequired[list[dict]]`.

### [continuacoes.py](continuacoes.py)

Coordena propostas pendentes, pausa, retomada, cancelamento e troca de assunto.

- `esclarecer_continuacao(mensagem: str) -> dict`: Monta resposta que pede identificação da proposta a continuar.
- `async alterar_continuacao(tipo: str, proposta: dict, contexto: dict, **campos) -> dict`: Persiste alterações de continuidade no armazenamento do tipo de proposta.
- `async tratar_continuacao(estado: dict, contexto: dict, pergunta: str) -> dict | None`: Trata aceite, pausa, cancelamento e retomada das propostas, pedindo esclarecimento quando ambíguo.
- `async pausar_outros_fluxos(estado: dict, contexto: dict, escolhido: str | None) -> dict`: Persiste pausa de fluxos ativos diferentes do escolhido.

### [estado.py](estado.py)

TypedDict EstadoGrafo e limpeza da visualização entre execuções.

- Classe `EstadoGrafo` (`TypedDict`).
  Campos/atributos declarados: `messages: Annotated[list[BaseMessage], add_messages]`, `user_id: int`, `operacao_solicitacao: Literal['criar', 'atualizar']`, `operacao_ocorrencia: Literal['criar', 'atualizar']`, `perfil: Literal['solicitante', 'tecnico', 'gestor', 'administrador']`, `intencao: Literal['ajuda_geral', 'faq', 'solicitacao', 'ocorrencia', 'evento', 'analytics', 'visualizacao', 'feedback', 'analista_compras', 'fora_de_escopo'] | None`, `entrada_valida: bool`, `mensagem_anonimizada: str`, `mapa_pii: dict[str, str]`, `motivo_bloqueio: str | None`, `motivo_resposta_padrao: Literal['ferramenta_indisponivel', 'faq_sem_informacao'] | None`, `justificativa_roteamento: str`, `evidencias: list[str]`, `operacoes_pendentes: list[dict]`, `aprovacao_operacoes: dict | None`, `resultados_operacoes: list[dict]`, `consultas_visualizacao: list[dict]`, `visualizacao_candidata: dict | None`, `visualizacao_status: str | None`, `visualizacao_execucao_id: str | None`, `visualizacao_aprovacao: dict | None`, `visualizacao_aprovada: dict | None`, `visualizacao_publica: dict | None`, `resposta_especialista: str`, `resposta_candidata: str`, `veredito: Literal['aprovado', 'revisar', 'bloqueado'] | None`, `feedback_juiz: str`, `tentativas: int`, `resposta_final: str`, `emocao: Emocao | str`, `saida_bloqueada: bool`, `erro: str | None`, `solicitacao_pendente: dict | None`, `ocorrencia_pendente: dict | None`, `evento_pendente: dict | None`, `ajuda_geral_pendente: dict | None`, `analise_compra_pendente: dict | None`, `imagens_recebidas: bool`, `anexos_pendentes: int`, `cadastro_em_andamento: bool`, `continua_pendente: bool`, `esclarecimento_roteamento: bool`, `propostas_apresentadas: list[dict]`, `contexto_temporal: str`.
- `limpar_visualizacao() -> dict`: Descarta a seleção e os registros internos de uma execução anterior.

### [evidencias.py](evidencias.py)

Captura retornos de ferramentas reais do turno e invoca agentes com contexto temporal.

- `ids_chamadas(mensagens) -> set[str]`: Coleta identificadores de chamadas de ferramentas presentes nas mensagens.
- `extrair_evidencias(mensagens, ids_anteriores: set[str], formato_saida: str) -> list[str]`: Extrai resultados reais de chamadas novas, excluindo memória e formatação como prova operacional.
- `async executar_com_evidencias(agente, estado, contexto, formato_saida)`: Invoca agente com contexto temporal e retorna resultado junto às novas evidências.

### [executor.py](executor.py)

Inicializa estado/contexto, recupera memória/rascunhos e persiste resposta antes de liberar confirmação.

- `criar_estado_inicial(mensagens: list[AIMessage | HumanMessage], usuario: UsuarioContexto) -> EstadoGrafo`: Inicializa estado do turno e valida perfil.
- `async executar_grafo(mensagem: str, usuario: UsuarioContexto, thread_id: str, imagens: list[str] | None=None, plataforma: Literal['web', 'mobile']='web') -> EstadoGrafo`: Prepara memória/contexto, invoca grafo e persiste resposta antes de disponibilizá-la.
- Constantes, aliases e estado de módulo: `Perfil`, `PERFIS_VALIDOS`.

### [fluxo.py](fluxo.py)

Constrói grafo com nós instrumentados, arestas condicionais e checkpoint em memória.

- `construir_grafo()`: Registra nós/arestas e compila StateGraph com MemorySaver.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_instrumentar_no`.
- Constantes, aliases e estado de módulo: `grafo`.

### [nos.py](nos.py)

Supervisor, validações, invocação de especialistas, captura de gráficos e fallback.

- `obter_pergunta(estado: EstadoGrafo) -> str`: Obtém a pergunta atual das mensagens do estado.
- `validar_entrada(estado: EstadoGrafo) -> dict`: Aplica proteção da entrada e descarta visualização herdada de execução anterior.
- `async supervisionar(estado: EstadoGrafo, runtime: Runtime[ContextoGrafo]) -> dict`: Resolve continuações determinísticas ou roteia intenção, pausando outros fluxos quando necessário.
- `async executar_analista_compras(estado: EstadoGrafo, runtime: Runtime[ContextoGrafo]) -> dict`: Adapta o coordenador de compras ao estado/contexto do grafo.
- `async executar_ajuda_geral(estado: EstadoGrafo, runtime: Runtime[ContextoGrafo]) -> dict`: Invoca agente de ajuda do perfil, injeta propostas e acumula evidências.
- `async executar_faq(estado: EstadoGrafo, runtime: Runtime[ContextoGrafo]) -> dict`: Invoca FAQ do perfil e trata ausência de informação com resposta padronizada.
- `async executar_solicitacao(estado: EstadoGrafo, runtime: Runtime[ContextoGrafo]) -> dict`: Coordena especialista de cadastro/atualização, coleta parcial, rascunhos, anexos e evidências.
- `async executar_indicadores(estado: EstadoGrafo, runtime: Runtime[ContextoGrafo]) -> dict`: Invoca especialista gerencial de KPIs com contexto autenticado.
- `async executar_visualizacao(estado: EstadoGrafo, runtime: Runtime[ContextoGrafo]) -> dict`: Valida acesso/plataforma, captura consultas reais e confere referência escolhida pelo agente.
- `async executar_retorno_usuario(estado: EstadoGrafo, runtime: Runtime[ContextoGrafo]) -> dict`: Invoca especialista de feedback e acumula evidências/operações preparadas.
- `validar_saida(estado: EstadoGrafo, runtime: Runtime[ContextoGrafo]=None) -> dict`: Protege texto, confere visualização aprovada e monta resposta final do estado.
- `tratar_erro(estado: EstadoGrafo) -> dict`: Produz fallback seguro e limpa dados de visualização incompatíveis.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_validar_entrada`, `_bloquear_saida_visualizacao`, `_validar_saida`, `_tratar_erro`.
- Constantes, aliases e estado de módulo: `registrador`.

### [operacoes.py](operacoes.py)

Executa operações aprovadas com controle durável e produz resposta factual do resultado.

- `async executar_servico(documento: dict, contexto: dict) -> dict`: Lista explícita de serviços permitidos; o modelo não escolhe funções Python.
- `resposta_resultados(resultados: list[dict]) -> dict`: Converte resultados reais de gravação em texto/mensagem do grafo.
- `async executar_operacoes(estado: dict, runtime) -> dict`: Confere aprovação e registro durável, executa serviços permitidos e preserva resultado real/incerto sem reenvio automático.
- Constantes, aliases e estado de módulo: `registrador`.

### [propostas.py](propostas.py)

Extrai propostas das evidências e separa texto do agente dos resumos do backend.

- `propostas_resposta(estado: dict) -> list[dict]`: Seleciona propostas verificáveis produzidas pelas ferramentas do turno.
- `preparar_resposta(resposta: str, estado: dict) -> tuple[str, list[str], str]`: Separa o texto do agente dos resumos produzidos pelo backend.

### [respostas_padrao.py](respostas_padrao.py)

Seleção de respostas do fluxo e reexportação histórica dos renderizadores de core/apresentacao.

- `selecionar_resposta_saida(estado: dict, resposta: str) -> tuple[str, str | None] | None`: Aplica texto padronizado compatível com o estado final do fluxo.
- `resposta_interrupcao_proposta(tipo: str, manifestacao: str) -> str`: Renderiza mensagem de pausa/cancelamento da proposta.
- `preparar_resposta_padrao(status: str, intencao: str, evidencias: list[str], contexto: dict) -> dict`: Confere status/intenção/evidências antes de padronizar limitação ou FAQ sem informação.
- `resposta_padrao_validada(estado: dict) -> str | None`: Revalida a resposta padronizada antes do julgamento.
- `selecionar_resposta_fallback(estado: dict) -> str`: Escolhe resposta segura compatível com falha ou pedido fora do escopo.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_registros`, `_pode_padronizar`, `_anexar_orientacao_consulta`.
- Constantes, aliases e estado de módulo: `TEXTOS`, `CONSULTAS_COM_ORIENTACAO`.

### [transicoes.py](transicoes.py)

Decisões de aresta após entrada, supervisor, visualização e julgamento.

- `decidir_apos_entrada(estado: EstadoGrafo) -> str`: Seleciona supervisor ou fallback conforme validação da entrada.
- `selecionar_especialista(estado: EstadoGrafo) -> str`: Seleciona o próximo nó por intenção, erro e necessidade de esclarecimento.
- `decidir_apos_visualizacao(estado: EstadoGrafo) -> str`: Decide se visualização segue para julgamento ou finalização sem consulta.
- `decidir_apos_julgamento(estado: EstadoGrafo) -> str`: Decide entre proteção de saída, execução de operações, revisão textual ou fallback.

## Orquestração e efeitos

Estado e contexto continuam no grafo. O supervisor usa o roteador e regras puras de continuidade de core; o grafo persiste pausas/retomadas. Evidências são obtidas das ferramentas reais do turno.

`respostas_padrao.py` escolhe a resposta de acordo com o estado e reexporta os renderizadores históricos. A implementação de renderização está em core/apresentacao. `executar_operacoes` continua conferindo aprovação, conteúdo/contexto e transições duráveis antes do efeito. Resultados indeterminados não autorizam reenvio automático.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/agents](../agents/RESPONSABILIDADE.md).
- [app/agents/prompts/reutilizaveis](../agents/prompts/reutilizaveis/RESPONSABILIDADE.md).
- [app/core](../core/RESPONSABILIDADE.md).
- [app/core/apresentacao](../core/apresentacao/RESPONSABILIDADE.md).
- [app/guardrails](../guardrails/RESPONSABILIDADE.md).
- [app/memory/persistencia](../memory/persistencia/RESPONSABILIDADE.md).
- [app/observability](../observability/RESPONSABILIDADE.md).
- [app/schemas](../schemas/RESPONSABILIDADE.md).
- [app/schemas/resultados_agentes](../schemas/resultados_agentes/RESPONSABILIDADE.md).
- [app/services](../services/RESPONSABILIDADE.md).
- [app/services/feedback](../services/feedback/RESPONSABILIDADE.md).
- [app/services/visualizacoes](../services/visualizacoes/RESPONSABILIDADE.md).
- [app/tools/ajuda_geral](../tools/ajuda_geral/RESPONSABILIDADE.md).
- [app/tools/eventos](../tools/eventos/RESPONSABILIDADE.md).
- [app/tools/ocorrencias](../tools/ocorrencias/RESPONSABILIDADE.md).
- [app/tools/solicitacoes](../tools/solicitacoes/RESPONSABILIDADE.md).
- [app/tools/visualizacoes](../tools/visualizacoes/RESPONSABILIDADE.md).
