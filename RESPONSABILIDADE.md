# Responsabilidade: raiz do projeto

## Objetivo do módulo

Organizar o backend multiagente FIXA e seus recursos de execução, entrega e referência.

## O que deve ser armazenado aqui

Código em app, testes, contratos externos, configuração de contêiner e automações.

## Comportamento e limites atuais

Monólito organizado por responsabilidades e interfaces públicas. A refatoração preserva contratos e regras; consulte docs/refatoracao_arquitetura.md para decisões, caracterização e limites da validação.

## Submódulos

| Pasta | Responsabilidade |
| --- | --- |
| [.github](.github/RESPONSABILIDADE.md) | Agrupar a automação do repositório no GitHub. |
| [app](app/RESPONSABILIDADE.md) | Compor e executar a API de inteligência artificial da plataforma FIXA. |
| [dados](dados/RESPONSABILIDADE.md) | Manuais mobile completos por perfil, referências institucionais e proposta de política operacional da IA do FIXA. |
| [docs](docs/RESPONSABILIDADE.md) | Guardar contratos e referências técnicas. |
| [observability](observability/RESPONSABILIDADE.md) | Configurar coleta/apresentação de métricas. |
| [tests](tests/RESPONSABILIDADE.md) | Verificar compras e contrato MCP Pechincha. |

## Funcionalidades disponíveis e arquivos

Os arquivos abaixo são referências ou configuração; não expõem métodos Python.

### [.dockerignore](.dockerignore)

Exclusões do contexto Docker, incluindo testes internos, docs e observabilidade.

### [.gitignore](.gitignore)

Exclusões de ambiente virtual, segredos e caches locais.

### [Dockerfile](Dockerfile)

Imagem Python 3.12 e Uvicorn como appuser na porta 8000.

### [LICENSE](LICENSE)

Licença de uso e distribuição do repositório.

### [README.md](README.md)

Visão de uso e fluxos do assistente; contém referências a documentos/migração ausentes neste checkout.

### [compose.observability.yml](compose.observability.yml)

Executa Prometheus/Grafana com volumes e configurações locais montadas.

### [pytest.ini](pytest.ini)

Define descoberta de app/tests e /tests, excluindo metadados, ambiente virtual e caches locais.

### [requirements.txt](requirements.txt)

Dependências Python da API, agentes, bancos, métricas e testes.

### [teste.md](teste.md)

Notas de semântica dos indicadores BI; não é teste executável nem implementação de KPI.

## Fluxo e pontos de reutilização

1. `app/main.py` inicia a API, abre clientes compartilhados e garante índices.
2. `api/dependencies/auth.py` resolve o Bearer e cria `UsuarioContexto` consultando o FIXA.
3. `services/chat.py` valida a sessão e chama `graph/executor.py`, que prepara histórico, rascunhos, contexto temporal e mensagem anonimizada.
4. `graph/fluxo.py` conecta proteção de entrada, supervisor, especialista e julgamento. `agents/orquestrador.py` decide intenção; continuações explícitas também têm tratamento determinístico.
5. Tools consultam serviços ou preparam operações. O juiz avalia evidências; `graph/operacoes.py` executa apenas conteúdo aprovado. Revisão de texto não repete ferramentas de escrita.
6. A proteção de saída remove PII. O executor persiste a resposta e só libera confirmação de proposta após registrar sua apresentação. Visualização também exige captura, aprovação e publicação validadas.
7. Encerramento pode gerar resumo e indexar histórico no Qdrant; exclusão do histórico é lógica e tem serviço separado.

| Necessidade | Recurso existente |
| --- | --- |
| Configuração e conexões | [core](app/core/RESPONSABILIDADE.md) e [clients](app/core/clients/RESPONSABILIDADE.md) |
| Identidade e autorização HTTP | [dependencies](app/api/dependencies/RESPONSABILIDADE.md) |
| Unidade autenticada | `app/services/gerais/unidade.py::obter_unidade_id` |
| Aceite e confirmação versionada | `app/core/confirmacoes.py`, `app/core/propostas.py`, `app/tools/atualizacoes.py` |
| Textos e renderização padronizados | `app/core/respostas.py` e `app/graph/respostas_padrao.py` |
| Preparar/aprovar/executar gravação | `app/services/operacoes.py`, `app/memory/persistencia/operacoes.py`, `app/graph/operacoes.py` |
| Histórico, anexos e rascunhos | [persistencia](app/memory/persistencia/RESPONSABILIDADE.md) |
| Busca/validação de local e categoria | [vectorSearch](app/memory/vectorSearch/RESPONSABILIDADE.md) |
| SQL analítico com polling e limites | `app/services/indicadores/gerais/databricks.py::executar_consulta` |
| Catálogo e cálculo de gráficos | [visualizacoes](app/services/visualizacoes/RESPONSABILIDADE.md) |
| Compra e MCP | [compras](app/agents/compras/RESPONSABILIDADE.md) e [pechincha](app/mcp/pechincha/RESPONSABILIDADE.md) |

## Escopo e validação da organização

O inventário da refatoração abrangeu 361 arquivos de código, testes, configuração e referências, documentados em 73 diretórios e seus submódulos. Interfaces de 55 pacotes são carregadas sob demanda. Código, contratos, constantes e cenários de teste foram analisados; os recursos de responsabilidade compartilhada foram extraídos conforme [decisões da refatoração](docs/refatoracao_arquitetura.md). Os manuais adicionados posteriormente estão organizados em [dados](dados/RESPONSABILIDADE.md), com a migração dos conteúdos mobile compartilhados documentada em [dados/mobile](dados/mobile/RESPONSABILIDADE.md).

`.env` é configuração local sigilosa; seus valores não são copiados. `.git`, `.venv`, `__pycache__` e caches pytest são metadados/dependências/artefatos gerados, não módulos da aplicação. O pytest.ini restringe a descoberta às duas suítes.

As referências anteriores de contratos e resultados ficam em tests/fixtures. Os testes existentes foram mantidos, e os testes novos em /tests verificam equivalência de contratos/resultados, limites, permissões e importações. Serviços externos/LLM reais não são validados por esses testes simulados.

## Divergências de referência observadas

- `README.md` ainda cita `docs/validacao_fluxo.md` e `docs/observabilidade.md`, ausentes. O script de migração de timestamps e o SDD de visualizações referenciados pelos testes agora estão presentes.
- `app/rag` não tem implementação de recuperação/geração; o RAG usado pelo FAQ está distribuído por ferramentas e memória.
- O comando `python -m app.scripts.ingerir_faq` utiliza os Markdown de `dados/fixa/` para todos os perfis e os de `dados/mobile/<perfil>/` para seu respectivo perfil, excluindo `RESPONSABILIDADE.md`. Administrador reutiliza gestor. Cada corpus é publicado completo antes da limpeza dos pontos antigos daquele perfil; os caminhos PDF legados não são usados pelo comando.
- `contexto.py` menciona administrador como técnico, mas o registro de agentes e `ADMINISTRADOR_INSTRUCAO` seguem gestor. A permissão efetiva deve ser conferida no código do fluxo/ferramenta.
- `docs/enum/statusProblema.txt` inclui `OS_CRIADA=4`; o CHECK de `problema.status` em `docs/database/script_completo.sql` admite 0 a 3.
- A média de tarefas por OS tem ferramenta registrada, mas o serviço devolve `INDICADOR_INDISPONIVEL`. As notas de BI em `teste.md` não substituem as regras implementadas.
- O indicador de ocorrências ativas usa pendências de revisão/aprovação na gold; não deve ser confundido com filtro `esta_ativo` da edição operacional ou interpretado como OS aberta.
- Existe `services/gerais/rotear.py::rotear_jev`, mas o supervisor atual chama `agents/orquestrador.py::rotear_orquestrador`.

## Índice completo dos módulos

| Módulo | Objetivo |
| --- | --- |
| [.github](.github/RESPONSABILIDADE.md) | Agrupar a automação do repositório no GitHub. |
| [.github/workflows](.github/workflows/RESPONSABILIDADE.md) | Disparar implantação e criação de releases. |
| [app](app/RESPONSABILIDADE.md) | Compor e executar a API de inteligência artificial da plataforma FIXA. |
| [app/agents](app/agents/RESPONSABILIDADE.md) | Construir, selecionar e avaliar agentes especializados. |
| [app/agents/agentsResult](app/agents/agentsResult/RESPONSABILIDADE.md) | Preservar importações históricas dos resultados estruturados. |
| [app/agents/compras](app/agents/compras/RESPONSABILIDADE.md) | Separar as etapas de coleta e comparação de promoções. |
| [app/agents/prompts](app/agents/prompts/RESPONSABILIDADE.md) | Compor instruções dos especialistas para cada perfil. |
| [app/agents/prompts/especialistas](app/agents/prompts/especialistas/RESPONSABILIDADE.md) | Definir atuação e uso de ferramentas de cada especialidade. |
| [app/agents/prompts/reutilizaveis](app/agents/prompts/reutilizaveis/RESPONSABILIDADE.md) | Expor blocos de instruções compartilhados. |
| [app/agents/prompts/reutilizaveis/gerais](app/agents/prompts/reutilizaveis/gerais/RESPONSABILIDADE.md) | Descrever contexto e vocabulário comuns do FIXA. |
| [app/agents/prompts/reutilizaveis/usuarios](app/agents/prompts/reutilizaveis/usuarios/RESPONSABILIDADE.md) | Adaptar instruções ao papel do usuário autenticado. |
| [app/api](app/api/RESPONSABILIDADE.md) | Compor a interface HTTP da aplicação. |
| [app/api/dependencies](app/api/dependencies/RESPONSABILIDADE.md) | Resolver autenticação e restrição por perfil para endpoints. |
| [app/api/routes](app/api/routes/RESPONSABILIDADE.md) | Expor chat, sessões, saúde, métricas e classificação. |
| [app/core](app/core/RESPONSABILIDADE.md) | Centralizar configuração e regras comuns de conversa. |
| [app/core/apresentacao](app/core/apresentacao/RESPONSABILIDADE.md) | Renderizar textos determinísticos compartilhados sem depender da orquestração. |
| [app/core/clients](app/core/clients/RESPONSABILIDADE.md) | Gerenciar conexões compartilhadas com serviços de dados. |
| [app/graph](app/graph/RESPONSABILIDADE.md) | Orquestrar o turno da conversa e a execução de operações aprovadas. |
| [app/guardrails](app/guardrails/RESPONSABILIDADE.md) | Validar mensagens e proteger dados pessoais. |
| [app/mcp](app/mcp/RESPONSABILIDADE.md) | Agrupar integrações cliente com servidores MCP. |
| [app/mcp/pechincha](app/mcp/pechincha/RESPONSABILIDADE.md) | Consultar promoções no MCP público Pechincha.ai. |
| [app/memory](app/memory/RESPONSABILIDADE.md) | Organizar memória conversacional e recursos vetoriais. |
| [app/memory/embedding](app/memory/embedding/RESPONSABILIDADE.md) | Gerar embeddings e ingerir a base de FAQ. |
| [app/memory/persistencia](app/memory/persistencia/RESPONSABILIDADE.md) | Persistir conversas, propostas e operações de escrita. |
| [app/memory/persistencia/sessoes](app/memory/persistencia/sessoes/RESPONSABILIDADE.md) | Iniciar e encerrar sessões persistidas. |
| [app/memory/vectorSearch](app/memory/vectorSearch/RESPONSABILIDADE.md) | Pesquisar registros vetoriais e garantir índices de filtro. |
| [app/observability](app/observability/RESPONSABILIDADE.md) | Instrumentar execução sem exportar conteúdo de conversa em traces. |
| [app/rag](app/rag/RESPONSABILIDADE.md) | Reservar pacote para organização de RAG. |
| [app/schemas](app/schemas/RESPONSABILIDADE.md) | Definir contratos e validadores de fronteira da aplicação. |
| [app/schemas/cadastros](app/schemas/cadastros/RESPONSABILIDADE.md) | Definir contratos canônicos dos cadastros FIXA. |
| [app/schemas/resultados_agentes](app/schemas/resultados_agentes/RESPONSABILIDADE.md) | Definir saídas estruturadas dos especialistas. |
| [app/scripts](app/scripts/RESPONSABILIDADE.md) | Disponibilizar comandos operacionais explícitos. |
| [app/services](app/services/RESPONSABILIDADE.md) | Implementar casos de uso, consultas e gravações. |
| [app/services/ajuda_geral](app/services/ajuda_geral/RESPONSABILIDADE.md) | Consultar registros operacionais e efetivar edições restritas. |
| [app/services/eventos](app/services/eventos/RESPONSABILIDADE.md) | Enviar cadastro de evento à API FIXA. |
| [app/services/feedback](app/services/feedback/RESPONSABILIDADE.md) | Gravar e consultar feedback próprio. |
| [app/services/gerais](app/services/gerais/RESPONSABILIDADE.md) | Oferecer serviços de identidade, unidade e decisão JEV. |
| [app/services/indicadores](app/services/indicadores/RESPONSABILIDADE.md) | Consultar indicadores gerenciais no Databricks. |
| [app/services/indicadores/gerais](app/services/indicadores/gerais/RESPONSABILIDADE.md) | Executar consultas analíticas e validar escopo comum. |
| [app/services/ocorrencias](app/services/ocorrencias/RESPONSABILIDADE.md) | Consultar, cadastrar e atualizar ocorrências. |
| [app/services/ordensServico](app/services/ordensServico/RESPONSABILIDADE.md) | Consultar ordens de serviço autorizadas. |
| [app/services/sessoes](app/services/sessoes/RESPONSABILIDADE.md) | Consultar e ocultar conversas do histórico. |
| [app/services/solicitacoes](app/services/solicitacoes/RESPONSABILIDADE.md) | Consultar, cadastrar e atualizar solicitações. |
| [app/services/tecnicos](app/services/tecnicos/RESPONSABILIDADE.md) | Consultar técnicos disponíveis ou com menor carga. |
| [app/services/visualizacoes](app/services/visualizacoes/RESPONSABILIDADE.md) | Definir/executar 27 análises e liberar dados aprovados. |
| [app/tests](app/tests/RESPONSABILIDADE.md) | Verificar contratos e comportamento interno. |
| [app/tools](app/tools/RESPONSABILIDADE.md) | Expor capacidades como ferramentas para agentes. |
| [app/tools/ajuda_geral](app/tools/ajuda_geral/RESPONSABILIDADE.md) | Adaptar consultas e edições para ajuda geral. |
| [app/tools/eventos](app/tools/eventos/RESPONSABILIDADE.md) | Coletar e confirmar propostas de eventos. |
| [app/tools/faq](app/tools/faq/RESPONSABILIDADE.md) | Recuperar trechos FAQ do perfil autenticado. |
| [app/tools/feedback](app/tools/feedback/RESPONSABILIDADE.md) | Preparar registro e listar feedback próprio. |
| [app/tools/memoria](app/tools/memoria/RESPONSABILIDADE.md) | Expor recuperação de conversas aos agentes. |
| [app/tools/metricas_kpis](app/tools/metricas_kpis/RESPONSABILIDADE.md) | Expor 36 ferramentas gerenciais de indicadores. |
| [app/tools/ocorrencias](app/tools/ocorrencias/RESPONSABILIDADE.md) | Adaptar criação, consulta própria e atualização. |
| [app/tools/ordensServico](app/tools/ordensServico/RESPONSABILIDADE.md) | Disponibilizar busca/listagem de OS aos agentes. |
| [app/tools/solicitacoes](app/tools/solicitacoes/RESPONSABILIDADE.md) | Adaptar cadastro, consulta e atualização. |
| [app/tools/tecnicos](app/tools/tecnicos/RESPONSABILIDADE.md) | Expor disponibilidade de técnicos ao agente. |
| [app/tools/toolsRequest](app/tools/toolsRequest/RESPONSABILIDADE.md) | Preservar importações históricas dos contratos de cadastro. |
| [app/tools/visualizacoes](app/tools/visualizacoes/RESPONSABILIDADE.md) | Adaptar seis ferramentas aos serviços canônicos. |
| [dados](dados/RESPONSABILIDADE.md) | Manuais de uso por perfil, referências institucionais e política operacional proposta para a IA. |
| [dados/fixa](dados/fixa/RESPONSABILIDADE.md) | Contexto do projeto e proposta de Política de Uso da IA, com 12 seções de regras, limites e decisões pendentes. |
| [dados/mobile](dados/mobile/RESPONSABILIDADE.md) | Distribuição completa dos procedimentos mobile por perfil. |
| [dados/mobile/gestor](dados/mobile/gestor/RESPONSABILIDADE.md) | Manual e procedimentos exclusivos/aplicáveis ao Gestor. |
| [dados/mobile/solicitante](dados/mobile/solicitante/RESPONSABILIDADE.md) | Manual e procedimentos exclusivos/aplicáveis ao Solicitante. |
| [dados/mobile/tecnico](dados/mobile/tecnico/RESPONSABILIDADE.md) | Manual e procedimentos exclusivos/aplicáveis ao Técnico. |
| [docs](docs/RESPONSABILIDADE.md) | Guardar contratos e referências técnicas. |
| [docs/api](docs/api/RESPONSABILIDADE.md) | Guardar contrato de referência da API FIXA. |
| [docs/database](docs/database/RESPONSABILIDADE.md) | Documentar estrutura relacional e permissões. |
| [docs/enum](docs/enum/RESPONSABILIDADE.md) | Documentar códigos/nomes dos enums FIXA. |
| [observability](observability/RESPONSABILIDADE.md) | Configurar coleta/apresentação de métricas. |
| [observability/grafana](observability/grafana/RESPONSABILIDADE.md) | Organizar dashboard e provisionamento Grafana. |
| [observability/grafana/dashboards](observability/grafana/dashboards/RESPONSABILIDADE.md) | Definir painéis de observabilidade FIXA. |
| [observability/grafana/provisioning](observability/grafana/provisioning/RESPONSABILIDADE.md) | Provisionar recursos Grafana. |
| [observability/grafana/provisioning/dashboards](observability/grafana/provisioning/dashboards/RESPONSABILIDADE.md) | Registrar provider de dashboards em arquivo. |
| [observability/grafana/provisioning/datasources](observability/grafana/provisioning/datasources/RESPONSABILIDADE.md) | Registrar fonte Prometheus no Grafana. |
| [observability/rules](observability/rules/RESPONSABILIDADE.md) | Pré-calcular séries Prometheus para visualizações. |
| [tests](tests/RESPONSABILIDADE.md) | Verificar compras e contrato MCP Pechincha. |
| [tests/fixtures](tests/fixtures/RESPONSABILIDADE.md) | Preservar referências capturadas antes da refatoração. |
