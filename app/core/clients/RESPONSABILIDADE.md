# Responsabilidade: app/core/clients

## Objetivo do módulo

Gerenciar conexões compartilhadas com serviços de dados.

## O que deve ser armazenado aqui

Pools e clientes MongoDB, Qdrant, PostgreSQL, Databricks e LLM/embedding, com ciclo de vida específico.

## Comportamento e limites atuais

Gerencia clientes MongoDB, Qdrant, PostgreSQL, HTTP Databricks e modelos LLM/embedding. Reutilize os recursos existentes; administrador usa conexão PostgreSQL de gestor. Importar a interface não inicializa clientes.

Módulo pai: [app/core](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `abrir_cliente_mongo` → `.mongo` (`abrir_cliente_mongo`).
- `abrir_cliente_qdrant` → `.qdrant` (`abrir_cliente_qdrant`).
- `executar_consulta` → `.postgres` (`executar_consulta`).
- `executar_insercao` → `.postgres` (`executar_insercao`).
- `fechar_cliente_databricks` → `.databricks` (`fechar_cliente_databricks`).
- `fechar_cliente_mongo` → `.mongo` (`fechar_cliente_mongo`).
- `fechar_cliente_qdrant` → `.qdrant` (`fechar_cliente_qdrant`).
- `fechar_conexoes_postgres` → `.postgres` (`fechar_conexoes_postgres`).
- `iniciar_cliente_mongo` → `.mongo` (`iniciar_cliente_mongo`).
- `iniciar_cliente_qdrant` → `.qdrant` (`iniciar_cliente_qdrant`).
- `llm_especialista` → `.modelos` (`llm_especialista`).
- `llm_luna` → `.modelos` (`llm_luna`).
- `llm_rapido` → `.modelos` (`llm_rapido`).
- `obter_cliente_databricks` → `.databricks` (`obter_cliente_databricks`).
- `obter_modelo_embedding` → `.modelos` (`obter_modelo_embedding`).
- `obter_motor` → `.postgres` (`obter_motor`).
- `validar_config_mongo` → `.mongo` (`validar_config_mongo`).

### [databricks.py](databricks.py)

Pool HTTP compartilhado para acesso aos serviços Databricks.

- `obter_cliente_databricks() -> httpx.AsyncClient`: Retorna um cliente assíncrono reutilizável com pool de conexões.
- `async fechar_cliente_databricks() -> None`: Fecha o pool HTTP compartilhado durante o encerramento da aplicação.
- Constantes, aliases e estado de módulo: `_CLIENTE_HTTP: httpx.AsyncClient | None`.

### [modelos.py](modelos.py)

Clientes LLM/embedding compartilhados; preserva modelos e opções existentes.

- `obter_modelo_embedding(dimensoes: int) -> OpenAIEmbeddings`: Reutiliza o modelo de embedding conforme a dimensão da coleção.
- Constantes, aliases e estado de módulo: `llm_luna`, `llm_rapido`, `llm_especialista`.

### [mongo.py](mongo.py)

Recursos deste arquivo: Interrompe a operação quando faltar configuração da persistência. Cria o pool compartilhado para o lifespan da aplicacao.

- `validar_config_mongo() -> None`: Interrompe a operação quando faltar configuração da persistência.
- `iniciar_cliente_mongo() -> None`: Cria o pool compartilhado para o lifespan da aplicacao.
- `async abrir_cliente_mongo() -> AsyncIterator[AsyncMongoClient]`: Reutiliza o pool no lifespan; fora dele, fecha o cliente ao sair.
- `async fechar_cliente_mongo() -> None`: Fecha o cliente e seu pool no encerramento da aplicacao.
- Constantes, aliases e estado de módulo: `_CLIENTE_MONGO: AsyncMongoClient | None`.

### [postgres.py](postgres.py)

Recursos deste arquivo: Executa a etapa url asyncpg no escopo de postgres. Usado por _motor_url. Executa a etapa motor url no escopo de postgres. Usado por obter_motor.

- `obter_motor(perfil: str) -> AsyncEngine`: Seleciona/reutiliza motor SQLAlchemy assíncrono por perfil/configuração.
- `async executar_consulta(perfil: str, sql: str, parametros: dict) -> list[dict]`: Executa SQL parametrizado no motor do perfil e devolve linhas como dicionários.
- `async executar_insercao(perfil: str, sql: str, parametros: dict) -> list[dict]`: Executa um INSERT em transacao e retorna as linhas de RETURNING, se houver.
- `async fechar_conexoes_postgres() -> None`: Descarta motores/pools PostgreSQL compartilhados e limpa o registro local.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_url_asyncpg`, `_motor_url`.
- Constantes, aliases e estado de módulo: `_URLS_POR_PERFIL`, `_MOTORES: dict[tuple[str, str], AsyncEngine]`.

### [qdrant.py](qdrant.py)

Recursos deste arquivo: Cria o cliente compartilhado para o lifespan da aplicacao. Reutiliza o cliente no lifespan; fora dele, fecha ao sair.

- `iniciar_cliente_qdrant() -> None`: Cria o cliente compartilhado para o lifespan da aplicacao.
- `async abrir_cliente_qdrant() -> AsyncIterator[AsyncQdrantClient]`: Reutiliza o cliente no lifespan; fora dele, fecha ao sair.
- `async fechar_cliente_qdrant() -> None`: Fecha as conexoes do cliente no encerramento da aplicacao.
- Constantes, aliases e estado de módulo: `_CLIENTE_QDRANT: AsyncQdrantClient | None`.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../RESPONSABILIDADE.md).
