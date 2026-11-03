# Responsabilidade: app/core

## Objetivo do módulo

Centralizar configuração e regras comuns de conversa.

## O que deve ser armazenado aqui

Configuração, relógios, enums, confirmações, projeções de propostas/operações, validações comuns, apresentação e clientes de infraestrutura.

## Comportamento e limites atuais

Regras e projeções comuns são puras e não importam grafo, agentes, serviços ou tools. A interface pública é resolvida sob demanda; clientes e política de observabilidade têm módulos próprios.

Módulo pai: [app](../RESPONSABILIDADE.md).

## Submódulos

| Pasta | Responsabilidade |
| --- | --- |
| [apresentacao](apresentacao/RESPONSABILIDADE.md) | Renderizar textos determinísticos compartilhados sem depender da orquestração. |
| [clients](clients/RESPONSABILIDADE.md) | Gerenciar conexões compartilhadas com serviços de dados. |

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `ACEITES` → `.confirmacoes` (`ACEITES`).
- `ACOES_ACEITE` → `.confirmacoes` (`ACOES_ACEITE`).
- `ALVOS` → `.confirmacoes` (`ALVOS`).
- `BANCO_URL_GESTOR` → `.configuracao` (`BANCO_URL_GESTOR`).
- `BANCO_URL_SOLICITANTE` → `.configuracao` (`BANCO_URL_SOLICITANTE`).
- `BANCO_URL_TECNICO` → `.configuracao` (`BANCO_URL_TECNICO`).
- `CAMINHO_PDF_FAQ_GESTOR` → `.configuracao` (`CAMINHO_PDF_FAQ_GESTOR`).
- `CAMINHO_PDF_FAQ_SOLICITANTE` → `.configuracao` (`CAMINHO_PDF_FAQ_SOLICITANTE`).
- `CAMINHO_PDF_FAQ_TECNICO` → `.configuracao` (`CAMINHO_PDF_FAQ_TECNICO`).
- `CATEGORIA_PROBLEMA_POR_ID` → `.manutencao` (`CATEGORIA_PROBLEMA_POR_ID`).
- `COMPLEMENTOS_BASE_CALCULO` → `.respostas` (`COMPLEMENTOS_BASE_CALCULO`).
- `DATABRICKS_HOST` → `.configuracao` (`DATABRICKS_HOST`).
- `DATABRICKS_TOKEN` → `.configuracao` (`DATABRICKS_TOKEN`).
- `DATABRICKS_WAREHOUSE_ID` → `.configuracao` (`DATABRICKS_WAREHOUSE_ID`).
- `DIMENSOES_VETORIZACAO_FAQ` → `.configuracao` (`DIMENSOES_VETORIZACAO_FAQ`).
- `DIMENSOES_VETORIZACAO_OPERACIONAL` → `.configuracao` (`DIMENSOES_VETORIZACAO_OPERACIONAL`).
- `DIRETORIO_BASE` → `.configuracao` (`DIRETORIO_BASE`).
- `DIRETORIO_DADOS` → `.configuracao` (`DIRETORIO_DADOS`).
- `Emocao` → `.emocoes` (`Emocao`).
- `FAQ_SEM_INFORMACAO` → `.respostas` (`FAQ_SEM_INFORMACAO`).
- `FERRAMENTA_INDISPONIVEL` → `.respostas` (`FERRAMENTA_INDISPONIVEL`).
- `FIXA_URL_BASE_API` → `.configuracao` (`FIXA_URL_BASE_API`).
- `FRASES_ACEITE` → `.confirmacoes` (`FRASES_ACEITE`).
- `FRASE_SEGURA` → `.respostas` (`FRASE_SEGURA`).
- `FUSO_HORARIO` → `.tempo` (`FUSO_HORARIO`).
- `JEV_MODELO` → `.configuracao` (`JEV_MODELO`).
- `JEV_URL` → `.configuracao` (`JEV_URL`).
- `LIMIAR` → `.configuracao` (`LIMIAR`).
- `LIMIAR_PONTUACAO_VETORIAL` → `.configuracao` (`LIMIAR_PONTUACAO_VETORIAL`).
- `LIMITE_BUSCA_VETORIAL` → `.configuracao` (`LIMITE_BUSCA_VETORIAL`).
- `MENSAGEM_BLOQUEIO_MOBILE` → `.respostas` (`MENSAGEM_BLOQUEIO_MOBILE`).
- `MENSAGENS` → `.respostas` (`MENSAGENS`).
- `MONGODB_URI` → `.configuracao` (`MONGODB_URI`).
- `MONGO_BANCO_DADOS` → `.configuracao` (`MONGO_BANCO_DADOS`).
- `MONGO_COLECAO_SESSOES` → `.configuracao` (`MONGO_COLECAO_SESSOES`).
- `Manifestacao` → `.confirmacoes` (`Manifestacao`).
- `NOMES_CAMPOS` → `.respostas` (`NOMES_CAMPOS`).
- `OBRIGATORIAS` → `.configuracao` (`OBRIGATORIAS`).
- `OBSERVABILIDADE_GROQ_ENTRADA_USD_MILHAO` → `.configuracao` (`OBSERVABILIDADE_GROQ_ENTRADA_USD_MILHAO`).
- `OBSERVABILIDADE_GROQ_SAIDA_USD_MILHAO` → `.configuracao` (`OBSERVABILIDADE_GROQ_SAIDA_USD_MILHAO`).
- `OBSERVABILIDADE_MENSAGENS_SEMANAIS_USUARIO` → `.configuracao` (`OBSERVABILIDADE_MENSAGENS_SEMANAIS_USUARIO`).
- `OBSERVABILIDADE_OPENAI_ENTRADA_USD_MILHAO` → `.configuracao` (`OBSERVABILIDADE_OPENAI_ENTRADA_USD_MILHAO`).
- `OBSERVABILIDADE_OPENAI_SAIDA_USD_MILHAO` → `.configuracao` (`OBSERVABILIDADE_OPENAI_SAIDA_USD_MILHAO`).
- `OBSERVABILIDADE_REAIS_DOLAR` → `.configuracao` (`OBSERVABILIDADE_REAIS_DOLAR`).
- `OBSERVABILIDADE_TOKENS_ESTIMADOS_ENTRADA_MENSAGEM` → `.configuracao` (`OBSERVABILIDADE_TOKENS_ESTIMADOS_ENTRADA_MENSAGEM`).
- `OBSERVABILIDADE_TOKENS_ESTIMADOS_SAIDA_MENSAGEM` → `.configuracao` (`OBSERVABILIDADE_TOKENS_ESTIMADOS_SAIDA_MENSAGEM`).
- `OBSERVABILIDADE_VALOR_RESOLUCAO_BRL` → `.configuracao` (`OBSERVABILIDADE_VALOR_RESOLUCAO_BRL`).
- `OPENAI_CHAVE_API` → `.configuracao` (`OPENAI_CHAVE_API`).
- `ORDEM_PRIORIDADE` → `.manutencao` (`ORDEM_PRIORIDADE`).
- `PRIORIDADE_POR_ID` → `.manutencao` (`PRIORIDADE_POR_ID`).
- `QDRANT_CAMPO_ATIVO` → `.configuracao` (`QDRANT_CAMPO_ATIVO`).
- `QDRANT_CAMPO_ENTIDADE_ID` → `.configuracao` (`QDRANT_CAMPO_ENTIDADE_ID`).
- `QDRANT_CAMPO_TEXTO` → `.configuracao` (`QDRANT_CAMPO_TEXTO`).
- `QDRANT_CAMPO_UNIDADE` → `.configuracao` (`QDRANT_CAMPO_UNIDADE`).
- `QDRANT_CHAVE_API` → `.configuracao` (`QDRANT_CHAVE_API`).
- `QDRANT_COLECAO_CATEGORIA` → `.configuracao` (`QDRANT_COLECAO_CATEGORIA`).
- `QDRANT_COLECAO_FAQ` → `.configuracao` (`QDRANT_COLECAO_FAQ`).
- `QDRANT_COLECAO_HISTORICO` → `.configuracao` (`QDRANT_COLECAO_HISTORICO`).
- `QDRANT_COLECAO_LOCAL` → `.configuracao` (`QDRANT_COLECAO_LOCAL`).
- `QDRANT_COLECOES_OPERACIONAIS` → `.configuracao` (`QDRANT_COLECOES_OPERACIONAIS`).
- `QDRANT_ESPACO_NOMES_PONTOS` → `.configuracao` (`QDRANT_ESPACO_NOMES_PONTOS`).
- `QDRANT_NOME_VETOR` → `.configuracao` (`QDRANT_NOME_VETOR`).
- `QDRANT_URL` → `.configuracao` (`QDRANT_URL`).
- `RESPOSTAS_BLOQUEIO` → `.respostas` (`RESPOSTAS_BLOQUEIO`).
- `RESPOSTAS_OPERACAO_FALHA` → `.respostas` (`RESPOSTAS_OPERACAO_FALHA`).
- `RESPOSTAS_OPERACAO_SUCESSO` → `.respostas` (`RESPOSTAS_OPERACAO_SUCESSO`).
- `RESPOSTA_APROVACAO_INVALIDA` → `.respostas` (`RESPOSTA_APROVACAO_INVALIDA`).
- `RESPOSTA_FALHA_INDICADOR_PROMPT` → `.respostas` (`RESPOSTA_FALHA_INDICADOR_PROMPT`).
- `RESPOSTA_VISUALIZACAO_INVALIDA` → `.respostas` (`RESPOSTA_VISUALIZACAO_INVALIDA`).
- `STATUS_ACAO` → `.continuacoes` (`STATUS_ACAO`).
- `STATUS_ORDEM_SERVICO_POR_ID` → `.manutencao` (`STATUS_ORDEM_SERVICO_POR_ID`).
- `STATUS_RASCUNHO` → `.continuacoes` (`STATUS_RASCUNHO`).
- `TEXTOS_COMPRAS` → `.respostas` (`TEXTOS_COMPRAS`).
- `TEXTOS_CONFIRMACAO` → `.respostas` (`TEXTOS_CONFIRMACAO`).
- `TRECHO_FAQ_AUSENTE` → `.respostas` (`TRECHO_FAQ_AUSENTE`).
- `TYPESAFE_API_KEY` → `.configuracao` (`TYPESAFE_API_KEY`).
- `URL_PECHINCHA` → `.configuracao` (`URL_PECHINCHA`).
- `VERSAO_PROTOCOLO` → `.configuracao` (`VERSAO_PROTOCOLO`).
- `aceite_explicito` → `.confirmacoes` (`aceite_explicito`).
- `agora_local` → `.tempo` (`agora_local`).
- `agora_utc` → `.tempo` (`agora_utc`).
- `apresentacao` → `.apresentacao` (submódulo).
- `avaliar_confirmacao` → `.propostas` (`avaliar_confirmacao`).
- `campos_aceite` → `.propostas` (`campos_aceite`).
- `campos_pendentes` → `.propostas` (`campos_pendentes`).
- `chave_ordenacao_status` → `.manutencao` (`chave_ordenacao_status`).
- `classificar_manifestacao` → `.confirmacoes` (`classificar_manifestacao`).
- `clients` → `.clients` (submódulo).
- `dados_atualizacao` → `.operacoes` (`dados_atualizacao`).
- `dados_cadastro` → `.operacoes` (`dados_cadastro`).
- `dados_edicao` → `.operacoes` (`dados_edicao`).
- `data_atual` → `.tempo` (`data_atual`).
- `data_iso_banco` → `.tempo` (`data_iso_banco`).
- `escapar_celula` → `.tabelas` (`escapar_celula`).
- `formatar_periodo` → `.tempo` (`formatar_periodo`).
- `inicio_periodo_listagem` → `.tempo` (`inicio_periodo_listagem`).
- `metadados_proposta` → `.propostas` (`metadados_proposta`).
- `montar_tabela_markdown` → `.tabelas` (`montar_tabela_markdown`).
- `normalizar_mensagem` → `.confirmacoes` (`normalizar_mensagem`).
- `propostas_pendentes` → `.continuacoes` (`propostas_pendentes`).
- `resolver_exportacao` → `.interfaces` (`resolver_exportacao`).
- `resumo_confirmacao` → `.propostas` (`resumo_confirmacao`).
- `subtrair_meses` → `.tempo` (`subtrair_meses`).
- `validar_configuracao` → `.configuracao` (`validar_configuracao`).
- `validar_titulo_cadastro` → `.validacao` (`validar_titulo_cadastro`).

### [configuracao.py](configuracao.py)

Carrega .env, desativa tracing e declara conexões, coleções, limites, preços e validação de configuração.

- `validar_configuracao() -> list[str]`: Devolve a lista de problemas de configuração (vazia = tudo certo).
- Constantes, aliases e estado de módulo: `DIRETORIO_BASE`, `DIRETORIO_DADOS`, `CAMINHO_PDF_FAQ_SOLICITANTE`, `CAMINHO_PDF_FAQ_TECNICO`, `CAMINHO_PDF_FAQ_GESTOR`, `OPENAI_CHAVE_API`, `FIXA_URL_BASE_API`, `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, `DATABRICKS_WAREHOUSE_ID`, `BANCO_URL_SOLICITANTE`, `BANCO_URL_TECNICO`, `BANCO_URL_GESTOR`, `QDRANT_CHAVE_API`, `QDRANT_URL`, `QDRANT_COLECAO_CATEGORIA`, `QDRANT_COLECAO_LOCAL`, `QDRANT_COLECOES_OPERACIONAIS`, `QDRANT_COLECAO_FAQ`, `QDRANT_COLECAO_HISTORICO`, `QDRANT_CAMPO_UNIDADE`, `QDRANT_CAMPO_ENTIDADE_ID`, `QDRANT_CAMPO_TEXTO`, `QDRANT_CAMPO_ATIVO`, `QDRANT_NOME_VETOR`, `QDRANT_ESPACO_NOMES_PONTOS`, `DIMENSOES_VETORIZACAO_OPERACIONAL`, `DIMENSOES_VETORIZACAO_FAQ`, `LIMITE_BUSCA_VETORIAL`, `LIMIAR_PONTUACAO_VETORIAL`, `MONGODB_URI`, `MONGO_COLECAO_SESSOES`, `MONGO_BANCO_DADOS`, `OBSERVABILIDADE_MENSAGENS_SEMANAIS_USUARIO`, `OBSERVABILIDADE_TOKENS_ESTIMADOS_ENTRADA_MENSAGEM`, `OBSERVABILIDADE_TOKENS_ESTIMADOS_SAIDA_MENSAGEM`, `OBSERVABILIDADE_OPENAI_ENTRADA_USD_MILHAO`, `OBSERVABILIDADE_OPENAI_SAIDA_USD_MILHAO`, `OBSERVABILIDADE_GROQ_ENTRADA_USD_MILHAO`, `OBSERVABILIDADE_GROQ_SAIDA_USD_MILHAO`, `OBSERVABILIDADE_VALOR_RESOLUCAO_BRL`, `OBSERVABILIDADE_REAIS_DOLAR`, `TYPESAFE_API_KEY`, `JEV_URL`, `JEV_MODELO`, `LIMIAR`, `URL_PECHINCHA`, `VERSAO_PROTOCOLO`, `OBRIGATORIAS`.

### [confirmacoes.py](confirmacoes.py)

Classifica integralmente aceite, pergunta, negação, cancelamento, pausa e retomada.

- `normalizar_mensagem(texto: str) -> str`: Remove acentos/pontuação e normaliza espaços para comparação.
- `classificar_manifestacao(texto: str) -> Manifestacao`: Classifica toda a mensagem; perguntas/correções não autorizam gravação por prefixo.
- `aceite_explicito(texto: str, *, acoes: tuple[str, ...] | None=None) -> bool`: Confere aceite integral e opcionalmente restringe a ação autorizada.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_construir_frases_aceite`.
- Constantes, aliases e estado de módulo: `Manifestacao`, `ACEITES`, `ACOES_ACEITE`, `ALVOS`, `FRASES_ACEITE`.

### [continuacoes.py](continuacoes.py)

Seleção pura de propostas pendentes, usada por roteadores e pelo grafo.

- `propostas_pendentes(estado: dict, *, pausadas: bool=False) -> dict[str, dict]`: Obtém propostas ativas ou pausadas do estado.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_chave_estado`.
- Constantes, aliases e estado de módulo: `STATUS_RASCUNHO`, `STATUS_ACAO`.

### [emocoes.py](emocoes.py)

Enum Emocao compartilhado entre fluxo, API e persistência.

- Classe `Emocao` (`str, Enum`).
  Campos/atributos declarados: `NEUTRO`, `CURIOSO`, `PENSATIVO`, `CONFIRMACAO`, `SUCESSO`, `EMPATICO`, `ALERTA`, `ERRO`, `BLOQUEADO`, `CONSELHEIRO`, `AGUARDANDO`, `CELEBRACAO`.

### [interfaces.py](interfaces.py)

Resolução de interfaces públicas sem importar antecipadamente os domínios.

- `resolver_exportacao(nome: str, pacote: str, exportacoes: dict, namespace: dict)`: Resolve um símbolo do __init__; usado pelas fachadas para evitar ciclos.

### [manutencao.py](manutencao.py)

Enums e ordenação compartilhados das consultas de manutenção; sem acesso a bancos.

- `chave_ordenacao_status(status: str) -> tuple[int, str]`: Ordena pelos status definidos no enum da ordem de serviço.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_normalizar_filtro`.
- Constantes, aliases e estado de módulo: `ORDEM_PRIORIDADE`, `PRIORIDADE_POR_ID`, `STATUS_ORDEM_SERVICO_POR_ID`, `CATEGORIA_PROBLEMA_POR_ID`, `_ID_POR_CATEGORIA_PROBLEMA`, `_ID_POR_PRIORIDADE`, `_ID_POR_STATUS`.

### [operacoes.py](operacoes.py)

Projeções puras de propostas, usadas na confirmação e aprovação de operações.

- `dados_cadastro(rascunho: dict) -> dict`: Projeta campos, versão e anexos para aprovação.
- `dados_edicao(acao: dict) -> dict`: Projeta ação de edição para aprovação.
- `dados_atualizacao(rascunho: dict) -> dict`: Projeta seleção, snapshot, alterações e fotos da atualização.

### [propostas.py](propostas.py)

Valida campos pendentes, aceite parcial e versão/turno de apresentação; monta metadados.

- `campos_pendentes(rascunho: dict) -> list[str]`: Lista dados que diferem dos valores já confirmados.
- `resumo_confirmacao(rascunho: dict) -> str`: Renderiza resumo determinístico dos dados/alterações da proposta.
- `campos_aceite(texto: str, dados: dict, pendentes: list[str]) -> list[str]`: Identifica os campos aos quais o aceite textual se refere.
- `avaliar_confirmacao(rascunho: dict, contexto: dict) -> dict | None`: Valida intenção, pausa, turno, versão e dados apresentados; retorna pendência/aceite parcial ou None quando liberado.
- `metadados_proposta(rascunho: dict) -> dict`: Monta identificação, versão, dados e resumo da proposta.

### [respostas.py](respostas.py)

Catálogos de mensagens, rótulos, templates de confirmação e textos de resultado/limitação.

- Constantes, aliases e estado de módulo: `FERRAMENTA_INDISPONIVEL`, `FAQ_SEM_INFORMACAO`, `TRECHO_FAQ_AUSENTE`, `MENSAGENS`, `RESPOSTAS_OPERACAO_SUCESSO`, `RESPOSTAS_OPERACAO_FALHA`, `RESPOSTA_APROVACAO_INVALIDA`, `RESPOSTA_VISUALIZACAO_INVALIDA`, `FRASE_SEGURA`, `MENSAGEM_BLOQUEIO_MOBILE`, `RESPOSTA_FALHA_INDICADOR_PROMPT`, `TEXTOS_CONFIRMACAO`, `COMPLEMENTOS_BASE_CALCULO`, `TEXTOS_COMPRAS`, `NOMES_CAMPOS`, `RESPOSTAS_BLOQUEIO`.

### [tabelas.py](tabelas.py)

Renderização Markdown segura, compartilhada por listagens operacionais.

- `escapar_celula(valor, *, ausente: str) -> str`: Escapa conteúdo cadastrado sem permitir colunas, links ou imagens extras.
- `montar_tabela_markdown(registros, colunas, *, campos_data=(), ausente: str, datas_nulas: bool=False) -> str`: Renderiza uma tabela sem ordenar/filtrar registros ou definir regras do domínio.

### [tempo.py](tempo.py)

Relógio de negócio e data atual em America/Sao_Paulo.

- `agora_local() -> datetime`: Devolve datetime atual com o fuso America/Sao_Paulo.
- `data_atual() -> date`: Devolve a data do relógio de negócio local.
- `agora_utc() -> datetime`: Relógio UTC usado pela persistência, sem depender de clientes de banco.
- `data_iso_banco(valor, *, permitir_nulo: bool=False) -> str | None`: Normaliza date/datetime de SQL; OS permite None, outros registros não.
- `subtrair_meses(hoje: date, meses: int) -> date`: Subtrai meses de calendário, ajustando dias inexistentes no mês de destino.
- `inicio_periodo_listagem(hoje: date) -> date`: Janela de três meses usada por consultas de solicitações, ocorrências e OS.
- `formatar_periodo(inicio: date, fim: date) -> dict[str, str]`: Projeta datas de período analítico sem modificar seus limites [início, fim).
- Constantes, aliases e estado de módulo: `FUSO_HORARIO`.

### [validacao.py](validacao.py)

Validações pequenas compartilhadas pelos contratos de cadastro.

- `validar_titulo_cadastro(valor: str) -> str`: Exige até dez palavras sem alterar texto; usada por evento e solicitação.

## Reutilização e direção das dependências

- `tempo` centraliza relógio local, UTC, calendário de três meses, conversão SQL de datas e projeção de períodos. Políticas de nulo permanecem explícitas no chamador.
- `manutencao` guarda mapeamentos de enums e ordenação de status. `tabelas` escapa conteúdo e renderiza linhas sem decidir permissões ou agrupamentos.
- `apresentacao` separa textos gerais, propostas, compras e avisos analíticos. `propostas` mantém aceite/versionamento; `operacoes` apenas projeta dados aprováveis.
- `continuacoes` consulta propostas ativas/pausadas sem persistir transições. O grafo é proprietário das gravações de continuidade.
- `interfaces.resolver_exportacao` centraliza a resolução dos `__init__.py`. Não copia valores de modelo/cliente que precisam refletir o proprietário.
- O teste de arquitetura impede imports de core para graph, agents, services e tools. A configuração ainda aplica a política de observabilidade existente.

## Variáveis de ambiente consumidas

Valores e credenciais locais não são reproduzidos.

| Símbolo Python | Chave externa |
| --- | --- |
| `OPENAI_CHAVE_API` | `OPENAI_API_KEY` |
| `FIXA_URL_BASE_API` | `FIXA_API_BASE_URL` |
| `DATABRICKS_HOST` | `DATABRICKS_HOST` |
| `DATABRICKS_TOKEN` | `DATABRICKS_TOKEN` |
| `DATABRICKS_WAREHOUSE_ID` | `DATABRICKS_WAREHOUSE_ID` |
| `BANCO_URL_SOLICITANTE` | `DATABASE_URL_SOLICITANTE` |
| `BANCO_URL_TECNICO` | `DATABASE_URL_TECNICO` |
| `BANCO_URL_GESTOR` | `DATABASE_URL_GESTOR` |
| `QDRANT_CHAVE_API` | `QDRANT_API_KEY` |
| `QDRANT_URL` | `QDRANT_URL` |
| `MONGODB_URI` | `MONGO_URI` |
| `OBSERVABILIDADE_MENSAGENS_SEMANAIS_USUARIO` | `OBSERVABILITY_WEEKLY_MESSAGES_PER_USER` |
| `OBSERVABILIDADE_TOKENS_ESTIMADOS_ENTRADA_MENSAGEM` | `OBSERVABILITY_ESTIMATED_INPUT_TOKENS_PER_MESSAGE` |
| `OBSERVABILIDADE_TOKENS_ESTIMADOS_SAIDA_MENSAGEM` | `OBSERVABILITY_ESTIMATED_OUTPUT_TOKENS_PER_MESSAGE` |
| `OBSERVABILIDADE_OPENAI_ENTRADA_USD_MILHAO` | `OBSERVABILITY_OPENAI_INPUT_USD_PER_MILLION` |
| `OBSERVABILIDADE_OPENAI_SAIDA_USD_MILHAO` | `OBSERVABILITY_OPENAI_OUTPUT_USD_PER_MILLION` |
| `OBSERVABILIDADE_GROQ_ENTRADA_USD_MILHAO` | `OBSERVABILITY_GROQ_INPUT_USD_PER_MILLION` |
| `OBSERVABILIDADE_GROQ_SAIDA_USD_MILHAO` | `OBSERVABILITY_GROQ_OUTPUT_USD_PER_MILLION` |
| `OBSERVABILIDADE_VALOR_RESOLUCAO_BRL` | `OBSERVABILITY_VALUE_PER_RESOLUTION_BRL` |
| `OBSERVABILIDADE_REAIS_DOLAR` | `OBSERVABILITY_BRL_PER_USD` |
| `TYPESAFE_API_KEY` | `TYPESAFE_API_KEY` |
| `JEV_MODELO` | `JEV_MODEL` |

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core/apresentacao](apresentacao/RESPONSABILIDADE.md).
- [app/observability](../observability/RESPONSABILIDADE.md).
