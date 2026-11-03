# Responsabilidade: app/schemas

## Objetivo do módulo

Definir contratos e validadores de fronteira da aplicação.

## O que deve ser armazenado aqui

Modelos Pydantic de API, usuário, períodos, imagens, sessões e visualizações.

## Comportamento e limites atuais

Contratos canônicos de API, cadastros e resultados de agentes estão nesta camada. Tipos são expostos por __init__.py; módulos históricos reexportam identidade e validadores. Nenhuma operação de negócio é executada pelos contratos.

Módulo pai: [app](../RESPONSABILIDADE.md).

## Submódulos

| Pasta | Responsabilidade |
| --- | --- |
| [cadastros](cadastros/RESPONSABILIDADE.md) | Definir contratos canônicos dos cadastros FIXA. |
| [resultados_agentes](resultados_agentes/RESPONSABILIDADE.md) | Definir saídas estruturadas dos especialistas. |

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [ClassificarProblema.py](ClassificarProblema.py)

Entrada de título/descrição/categoria e saída de classificação opcional.

- Classe `ClassificarProblemaRequest` (`BaseModel`).
  Campos/atributos declarados: `titulo: str`, `descricao: str`, `categoria_equipamento: str`.
- Classe `ClassificarProblemaResponse` (`BaseModel`).
  Campos/atributos declarados: `problema_classificado: bool`, `classificacao: str | None`.

### [UsuarioContexto.py](UsuarioContexto.py)

Contexto autenticado, normalização de perfil e CNPJ de 14 dígitos.

- Classe `UsuarioContexto` (`BaseModel`).
  Campos/atributos declarados: `access_token: str`, `usuario_id: int`, `nome_completo: str`, `email: str`, `tipo_acesso: str`, `cargo: str | None`, `data_nascimento: date | None`, `cnpj_endereco: str`.
  Métodos/validadores: `normalizar_tipo_acesso(cls, valor: str) -> str`; `normalizar_cnpj(cls, valor: str) -> str`.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `Agregacao` → `.visualizacao` (`Agregacao`).
- `Analise` → `.visualizacao` (`Analise`).
- `ApiResponse` → `.common` (`ApiResponse`).
- `AprovacaoVisualizacao` → `.visualizacao` (`AprovacaoVisualizacao`).
- `BaseCalculoVisualizacao` → `.visualizacao` (`BaseCalculoVisualizacao`).
- `ClassificarProblemaRequest` → `.ClassificarProblema` (`ClassificarProblemaRequest`).
- `ClassificarProblemaResponse` → `.ClassificarProblema` (`ClassificarProblemaResponse`).
- `ComparacaoPeriodosRequest` → `.analytics` (`ComparacaoPeriodosRequest`).
- `ConsultaVisualizacaoCapturada` → `.visualizacao` (`ConsultaVisualizacaoCapturada`).
- `ConsultaVisualizacaoPeriodo` → `.visualizacao` (`ConsultaVisualizacaoPeriodo`).
- `ConsultaVisualizacaoSnapshot` → `.visualizacao` (`ConsultaVisualizacaoSnapshot`).
- `ConversaEntrada` → `.chat` (`ConversaEntrada`).
- `ConversaEspecificaEntrada` → `.sessao` (`ConversaEspecificaEntrada`).
- `ConversaEspecificaSaida` → `.sessao` (`ConversaEspecificaSaida`).
- `ConversaHistorico` → `.sessao` (`ConversaHistorico`).
- `ConversaSaida` → `.chat` (`ConversaSaida`).
- `DadosBoxplot` → `.visualizacao` (`DadosBoxplot`).
- `DadosCategorias` → `.visualizacao` (`DadosCategorias`).
- `DadosHistograma` → `.visualizacao` (`DadosHistograma`).
- `DadosSerieTemporal` → `.visualizacao` (`DadosSerieTemporal`).
- `DadosVisualizacao` → `.visualizacao` (`DadosVisualizacao`).
- `DimensoesGrupo` → `.visualizacao` (`DimensoesGrupo`).
- `EncerrarSessaoSaida` → `.sessao` (`EncerrarSessaoSaida`).
- `ExcluirConversaSaida` → `.sessao` (`ExcluirConversaSaida`).
- `FiltroObrigatorio` → `.visualizacao` (`FiltroObrigatorio`).
- `Fonte` → `.visualizacao` (`Fonte`).
- `FormatoDados` → `.visualizacao` (`FormatoDados`).
- `GranularidadeTemporal` → `.visualizacao` (`GranularidadeTemporal`).
- `GrupoBoxplot` → `.visualizacao` (`GrupoBoxplot`).
- `GrupoSemBaseBoxplot` → `.visualizacao` (`GrupoSemBaseBoxplot`).
- `HealthResponse` → `.health` (`HealthResponse`).
- `IdSessaoCaminho` → `.id_sessao` (`IdSessaoCaminho`).
- `IntervaloHistograma` → `.visualizacao` (`IntervaloHistograma`).
- `LIMITE_CARACTERES_URL_IMAGEM` → `.imagem` (`LIMITE_CARACTERES_URL_IMAGEM`).
- `LIMITE_ID_SESSAO` → `.id_sessao` (`LIMITE_ID_SESSAO`).
- `LIMITE_IMAGENS_POR_MENSAGEM` → `.imagem` (`LIMITE_IMAGENS_POR_MENSAGEM`).
- `MensagemHistorico` → `.sessao` (`MensagemHistorico`).
- `MetadadosConsultaVisualizacao` → `.visualizacao` (`MetadadosConsultaVisualizacao`).
- `MetadadosVisualizacaoPublica` → `.visualizacao` (`MetadadosVisualizacaoPublica`).
- `PeriodoRequest` → `.analytics` (`PeriodoRequest`).
- `PeriodoSerieTemporal` → `.visualizacao` (`PeriodoSerieTemporal`).
- `PeriodoVisualizacao` → `.visualizacao` (`PeriodoVisualizacao`).
- `PontoCategoria` → `.visualizacao` (`PontoCategoria`).
- `PontoSerieTemporal` → `.visualizacao` (`PontoSerieTemporal`).
- `ReferenciaVisualizacao` → `.visualizacao` (`ReferenciaVisualizacao`).
- `ResultadoConsultaVisualizacao` → `.visualizacao` (`ResultadoConsultaVisualizacao`).
- `ResultadoGrupoBoxplot` → `.visualizacao` (`ResultadoGrupoBoxplot`).
- `ResumoGrupoPequeno` → `.visualizacao` (`ResumoGrupoPequeno`).
- `SelecaoFiltro` → `.visualizacao` (`SelecaoFiltro`).
- `StatusConsultaVisualizacao` → `.visualizacao` (`StatusConsultaVisualizacao`).
- `StatusVisualizacao` → `.visualizacao` (`StatusVisualizacao`).
- `TodasConversasSaida` → `.sessao` (`TodasConversasSaida`).
- `UsuarioContexto` → `.UsuarioContexto` (`UsuarioContexto`).
- `ValorFiltro` → `.visualizacao` (`ValorFiltro`).
- `ValorMedida` → `.visualizacao` (`ValorMedida`).
- `VisualizacaoPublica` → `.visualizacao` (`VisualizacaoPublica`).
- `cadastros` → `.cadastros` (submódulo).
- `normalizar_id_sessao` → `.id_sessao` (`normalizar_id_sessao`).
- `resultados_agentes` → `.resultados_agentes` (submódulo).
- `validar_url_imagem` → `.imagem` (`validar_url_imagem`).

### [analytics.py](analytics.py)

Períodos e comparação com validação de intervalo.

- Classe `PeriodoRequest` (`BaseModel`).
  Campos/atributos declarados: `inicio: date`, `fim: date`.
  Métodos/validadores: `validar_periodo(self)`.
- Classe `ComparacaoPeriodosRequest` (`BaseModel`).
  Campos/atributos declarados: `periodo_atual: PeriodoRequest`, `periodo_anterior: PeriodoRequest`.

### [chat.py](chat.py)

Entrada/saída de chat com plataforma, imagens, intenção, emoção, confirmação e visualização opcional.

- Classe `ConversaEntrada` (`BaseModel`).
  Campos/atributos declarados: `mensagem: str`, `plataforma: Literal['web', 'mobile']`, `thread_id: str | None`, `imagens: list[str]`.
  Métodos/validadores: `normalizar_texto(cls, valor)`; `validar_imagens(cls, imagens: list[str]) -> list[str]`.
- Classe `ConversaSaida` (`BaseModel`).
  Campos/atributos declarados: `thread_id: str`, `intencao: Literal['ajuda_geral', 'faq', 'solicitacao', 'ocorrencia', 'evento', 'analytics', 'visualizacao', 'feedback', 'analista_compras', 'fora_de_escopo'] | None`, `resposta: str`, `emocao: Emocao`, `confirmacao: Literal['sim', 'nao']`, `visualizacao: VisualizacaoPublica | None`.

### [common.py](common.py)

Envelope genérico ApiResponse: status, mensagem e dados opcionais.

- Classe `ApiResponse` (`BaseModel`).
  Campos/atributos declarados: `status: str`, `mensagem: str`, `dados: Any | None`.

### [health.py](health.py)

Resposta de saúde tipada.

- Classe `HealthResponse` (`BaseModel`).
  Campos/atributos declarados: `status: str`, `service: str`.

### [id_sessao.py](id_sessao.py)

Normalização de ID e parâmetro de caminho de até 100 caracteres.

- `normalizar_id_sessao(valor: str) -> str`: Remove espaços externos do ID de sessão quando recebido como texto.
- Constantes, aliases e estado de módulo: `LIMITE_ID_SESSAO`, `IdSessaoCaminho`.

### [imagem.py](imagem.py)

Limites e validação das URLs de imagens recebidas pelo chat.

- `validar_url_imagem(valor: str) -> str`: Aceita uma URL HTTP(S) de origem pública, sem credenciais ou fragmento.
- Constantes, aliases e estado de módulo: `LIMITE_IMAGENS_POR_MENSAGEM`, `LIMITE_CARACTERES_URL_IMAGEM`, `_ADAPTADOR_URL`, `_ROTULO_DNS`, `_SUFIXOS_LOCAIS`.

### [sessao.py](sessao.py)

Contratos de histórico/encerramento/exclusão e mensagens com timestamp UTC ou null legado.

- Classe `EncerrarSessaoSaida` (`BaseModel`).
  Campos/atributos declarados: `thread_id: str`, `status: str`, `mensagem: str`, `titulo: str | None`, `resumo: str | None`.
- Classe `ExcluirConversaSaida` (`BaseModel`).
  Campos/atributos declarados: `session_id: str`, `status: Literal['EXCLUIDA']`, `mensagem: str`.
- Classe `ConversaEspecificaEntrada` (`BaseModel`).
  Campos/atributos declarados: `session_id: str`.
  Métodos/validadores: `normalizar_session_id(cls, valor)`.
- Classe `MensagemHistorico` (`BaseModel`).
  Campos/atributos declarados: `role: Literal['human', 'assistant']`, `mensagem: str`, `timestamp: datetime | None`, `emocao: Emocao | None`, `confirmacao: Literal['sim', 'nao']`, `imagens: list[str] | None`, `visualizacao: VisualizacaoPublica | None`.
  Métodos/validadores: `normalizar_timestamp(cls, valor: datetime | None) -> datetime | None`; `validar_papel_visualizacao(self)`.
- Classe `ConversaHistorico` (`BaseModel`).
  Campos/atributos declarados: `session_id: str`, `iniciada_em: datetime`, `atualizada_em: datetime`, `titulo: str`, `resumo: str`, `mensagens: list[MensagemHistorico]`.
- Classe `TodasConversasSaida` (`BaseModel`).
  Campos/atributos declarados: `status: Literal['SUCESSO', 'SEM_DADOS']`, `mensagem: str`, `conversas: list[ConversaHistorico]`.
- Classe `ConversaEspecificaSaida` (`BaseModel`).
  Campos/atributos declarados: `status: Literal['SUCESSO']`, `mensagem: str`, `conversa: ConversaHistorico`.

### [visualizacao.py](visualizacao.py)

Contratos internos de consulta, definições e resultados de visualização.

- Classe `Fonte`.
  Campos/atributos declarados: `id: str`, `tabela: str`, `chave: tuple[str, ...]`, `campo_periodo: str | None`, `campo_snapshot: str | None`, `ids_textuais: frozenset[str]`.
- Classe `FiltroObrigatorio`.
  Campos/atributos declarados: `campo: str`, `valor: int | bool`.
- Classe `Analise`.
  Campos/atributos declarados: `id: str`, `titulo: str`, `fonte: Fonte`, `formato_dados: FormatoDados`, `dimensoes: tuple[str, ...]`, `campo_valor: str`, `agregacao: Agregacao | None`, `unidade_medida: Literal['quantidade', 'minutos', 'percentual']`, `excluir_nulos: bool`, `filtros_obrigatorios: tuple[FiltroObrigatorio, ...]`, `escala_percentual: Literal[100] | None`, `excluir_negativos: bool`.
- Classe `ResumoGrupoPequeno` (`BaseModel`): Dados analíticos de um grupo; o serviço decide quando usar o resumo.
  Campos/atributos declarados: `tipo: Literal['resumo']`, `analise_id: str`, `grupo: dict[str, StrictInt | StrictStr | None]`, `unidade: Literal['minutos']`, `qtd_registros: int`, `minimo: float`, `maximo: float`, `media: float`, `mediana: float`, `motivo: Literal['POUCOS_REGISTROS_PARA_BOXPLOT']`, `base_calculo: 'BaseCalculoVisualizacao | None'`.
  Métodos/validadores: `validar_estatisticas(self)`.
- Classe `PeriodoVisualizacao` (`_ContratoVisualizacao`).
  Campos/atributos declarados: `inicio: date`, `fim: date`.
  Métodos/validadores: `validar_formato_data(cls, valor)`; `validar_intervalo(self)`.
- Classe `ConsultaVisualizacaoPeriodo` (`_ConsultaVisualizacao`).
  Campos/atributos declarados: `periodo: PeriodoVisualizacao`, `granularidade: GranularidadeTemporal | None`.
- Classe `ConsultaVisualizacaoSnapshot` (`_ConsultaVisualizacao`): Snapshot não oferece campos de período ou granularidade.
- Classe `ReferenciaVisualizacao` (`_ContratoVisualizacao`): Seleção interna de um resultado; dados e renderização não vêm do LLM.
  Campos/atributos declarados: `analise_id: str`, `consulta_id: StrictStr`.
  Métodos/validadores: `validar_identificador(cls, valor)`.
- Classe `BaseCalculoVisualizacao` (`_ContratoVisualizacao`): Cobertura da medida dentro do recorte de unidade, período e filtros.
  Campos/atributos declarados: `qtd_registros_total: int`, `qtd_registros_elegiveis: int`, `qtd_tempos_negativos_excluidos: int`.
  Métodos/validadores: `validar_quantidades(self)`.
- Classe `PontoCategoria` (`_ContratoVisualizacao`).
  Campos/atributos declarados: `grupo: DimensoesGrupo`, `valor: ValorMedida`, `qtd_registros: int`, `base_calculo: BaseCalculoVisualizacao | None`.
  Métodos/validadores: `validar_base_calculo(self)`.
- Classe `PeriodoSerieTemporal` (`_ContratoVisualizacao`): Intervalo do calendário e sua interseção com o pedido; fins exclusivos.
  Campos/atributos declarados: `calendario: PeriodoVisualizacao`, `consultado: PeriodoVisualizacao`, `parcial: StrictBool`.
  Métodos/validadores: `validar_recorte(self)`.
- Classe `PontoSerieTemporal` (`PontoCategoria`).
  Campos/atributos declarados: `data_referencia: date`, `periodo: PeriodoSerieTemporal | None`.
  Métodos/validadores: `validar_referencia_periodo(self)`.
- Classe `DadosCategorias` (`_ContratoVisualizacao`).
  Campos/atributos declarados: `tipo: Literal['categorias']`, `pontos: list[PontoCategoria]`.
- Classe `DadosSerieTemporal` (`_ContratoVisualizacao`).
  Campos/atributos declarados: `tipo: Literal['serie_temporal']`, `pontos: list[PontoSerieTemporal]`.
- Classe `IntervaloHistograma` (`_ContratoVisualizacao`).
  Campos/atributos declarados: `inferior: float`, `superior: float`, `frequencia: int`, `inclui_superior: bool`.
  Métodos/validadores: `validar_limites(self)`.
- Classe `DadosHistograma` (`_ContratoVisualizacao`).
  Campos/atributos declarados: `tipo: Literal['histograma']`, `intervalos: list[IntervaloHistograma]`, `qtd_registros: int`.
  Métodos/validadores: `validar_frequencias(self)`.
- Classe `GrupoBoxplot` (`_ContratoVisualizacao`).
  Campos/atributos declarados: `tipo: Literal['boxplot']`, `analise_id: str`, `grupo: DimensoesGrupo`, `unidade: Literal['minutos']`, `qtd_registros: int`, `minimo: float`, `q1: float`, `mediana: float`, `q3: float`, `maximo: float`, `limite_inferior: float`, `limite_superior: float`, `bigode_inferior: float`, `bigode_superior: float`, `valores_extremos: list[float]`, `qtd_extremos_total: int`, `qtd_extremos_omitidos: int`, `base_calculo: BaseCalculoVisualizacao | None`.
  Métodos/validadores: `validar_estatisticas(self)`.
- Classe `GrupoSemBaseBoxplot` (`_ContratoVisualizacao`): Preserva um grupo observado sem inventar estatísticas ou um resumo.
  Campos/atributos declarados: `tipo: Literal['sem_base']`, `analise_id: str`, `grupo: DimensoesGrupo`, `unidade: Literal['minutos']`, `qtd_registros: int`, `motivo: Literal['SEM_OBSERVACOES_ELEGIVEIS']`, `base_calculo: BaseCalculoVisualizacao`.
  Métodos/validadores: `validar_base(self)`.
- Classe `DadosBoxplot` (`_ContratoVisualizacao`).
  Campos/atributos declarados: `tipo: Literal['boxplot']`, `grupos: list[ResultadoGrupoBoxplot]`.
- Classe `MetadadosConsultaVisualizacao` (`_ContratoVisualizacao`).
  Campos/atributos declarados: `analise_id: str`, `fonte: str`, `formato_dados: FormatoDados`, `campo_valor: str`, `agregacao: Agregacao | None`, `unidade_medida: Literal['quantidade', 'minutos', 'percentual']`, `escala_percentual: Literal[100] | None`, `periodo: PeriodoVisualizacao | None`, `granularidade: GranularidadeTemporal | None`, `instante_snapshot: datetime | None`, `consultado_em: datetime`, `consulta_id: str`, `filtros_solicitados: dict[str, SelecaoFiltro]`, `filtros_aplicados: dict[str, SelecaoFiltro]`, `filtros_nao_aplicados: list[str]`, `qtd_registros_considerados: int`, `base_calculo: BaseCalculoVisualizacao | None`.
  Métodos/validadores: `validar_fuso_consulta(cls, valor)`; `validar_referencia_temporal(self)`.
- Classe `ResultadoConsultaVisualizacao` (`_ContratoVisualizacao`): Retorno analítico interno das tools, sem configuração de renderização.
  Campos/atributos declarados: `versao_contrato: Literal['1.0']`, `status: StatusConsultaVisualizacao`, `mensagem: str`, `metadados: MetadadosConsultaVisualizacao | None`, `dados: DadosVisualizacao | None`, `avisos: list[str]`.
  Métodos/validadores: `validar_conteudo(self)`.
- Classe `ConsultaVisualizacaoCapturada` (`_ContratoVisualizacao`): Registro interno do servidor; não representa aprovação ou payload público.
  Campos/atributos declarados: `execucao_id: StrictStr`, `turno_id: StrictStr`, `sessao_id: StrictStr`, `usuario_id: int`, `chamada_id: StrictStr`, `ferramenta: StrictStr`, `unidade_id: int`, `consulta: ConsultaVisualizacaoPeriodo | ConsultaVisualizacaoSnapshot`, `resultado: ResultadoConsultaVisualizacao`.
- Classe `AprovacaoVisualizacao` (`_ContratoVisualizacao`): Vínculo interno com o conteúdo exato avaliado pelo juiz.
  Campos/atributos declarados: `texto_avaliado: StrictStr`, `conteudo_sha256: StrictStr`.
- Classe `MetadadosVisualizacaoPublica` (`_ContratoVisualizacao`).
  Campos/atributos declarados: `analise_id: StrictStr`, `unidade_id: int`, `unidade_medida: Literal['quantidade', 'minutos', 'percentual']`, `escala_percentual: Literal[100] | None`, `periodo: PeriodoVisualizacao | None`, `granularidade: GranularidadeTemporal | None`, `instante_snapshot: datetime | None`, `consultado_em: datetime`, `filtros: dict[str, SelecaoFiltro]`, `qtd_registros_considerados: int`, `base_calculo: BaseCalculoVisualizacao | None`.
  Métodos/validadores: `validar_fuso(cls, valor)`; `validar_metadados(self)`.
- Classe `VisualizacaoPublica` (`_ContratoVisualizacao`): Conteúdo versionado salvo junto da mensagem e devolvido sem recálculo.
  Campos/atributos declarados: `versao_contrato: Literal['1.0']`, `visualizacao_id: StrictStr`, `titulo: StrictStr`, `status: Literal['SUCESSO', 'SUCESSO_PARCIAL']`, `metadados: MetadadosVisualizacaoPublica`, `dados: DadosVisualizacao`, `avisos: list[StrictStr]`.
  Métodos/validadores: `validar_dados(self)`.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_ContratoVisualizacao`, `_ConsultaVisualizacao`.
  `_ConsultaVisualizacao`: `analise_id: str`, `filtros: dict[str, SelecaoFiltro]`.
- Constantes, aliases e estado de módulo: `FormatoDados`, `Agregacao`, `ValorFiltro`, `SelecaoFiltro`, `DimensoesGrupo`, `ValorMedida`, `GranularidadeTemporal`, `ResultadoGrupoBoxplot`, `DadosVisualizacao`, `StatusConsultaVisualizacao`, `StatusVisualizacao`.

## Invariantes dos contratos

- `ConversaEntrada`: mensagem de 1 a 4.000 caracteres, plataforma `web`/`mobile`, ID de sessão até 100 caracteres e até três URLs de imagem. `ConversaSaida` oferece intenção, resposta, emoção, confirmação e visualização opcional, omitida quando ausente.
- `imagem.validar_url_imagem()` exige HTTP(S), origem pública, até 255 caracteres e ausência de credenciais/fragmento; rejeita hosts locais e endereços IP não públicos. A validação não inspeciona visualmente o arquivo.
- `UsuarioContexto` normaliza perfil técnico e remove pontuação do CNPJ, que deve conter 14 dígitos. Campos de identidade são produzidos pela autenticação.
- `MensagemHistorico` preserva timestamp UTC e `null` para mensagem antiga sem horário. Contratos de sessão separam encerramento, listagem, conversa específica e exclusão lógica.
- `visualizacao.py` separa definição de análise, consulta, resultado interno, captura, aprovação e payload público. Valida período, tipos estritos, base de cálculo, cobertura, quartis/extremos e correspondência entre dados e metadados. Dados públicos não contêm configuração de renderização.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../core/RESPONSABILIDADE.md).
