# segundo-template-init
Repositório responsável por armazenar o template inicial padrão dentro dos repositórios da organização.

## Estrutura de Pastas

A estrutura de pastas do projeto foi organizada com o objetivo de manter uma separação clara entre as responsabilidades de cada camada da aplicação, facilitando o desenvolvimento em equipe, a manutenção do código e a evolução da arquitetura ao longo do projeto.

Como o sistema utiliza FastAPI, agentes de IA, LangChain, LangGraph, RAG, memória, MCP, A2A, guardrails e observabilidade, foi necessário dividir o código por domínio e responsabilidade, evitando concentrar toda a lógica em poucos arquivos.

A estrutura principal segue o padrão abaixo:
app/
│
├── main.py
│
├── api/
│   ├── routes/
│   │   ├── chat.py
│   │   ├── tickets.py
│   │   ├── analytics.py
│   │   └── feedback.py
│   └── dependencies/
│       ├── auth.py
│       └── permissions.py
│
├── agents/
│   ├── supervisor.py
│   ├── faq_agent.py
│   ├── ticket_agent.py
│   ├── analytics_agent.py
│   ├── visualization_agent.py
│   ├── feedback_agent.py
│   └── judge_agent.py
│
├── graph/
│   ├── state.py
│   ├── nodes.py
│   ├── edges.py
│   └── workflow.py
│
├── tools/
│   ├── tickets.py
│   ├── analytics.py
│   ├── technicians.py
│   └── feedback.py
│
├── rag/
│   ├── loaders.py
│   ├── embeddings.py
│   ├── vectorstore.py
│   └── retriever.py
│
├── memory/
│   ├── short_term.py
│   ├── long_term.py
│   └── preferences.py
│
├── guardrails/
│   ├── input.py
│   └── output.py
│
├── mcp/
│   ├── server.py
│   └── tools.py
│
├── a2a/
│   ├── client.py
│   └── notification_agent.py
│
├── schemas/
│   ├── graph.py
│   ├── ticket.py
│   ├── analytics.py
│   └── common.py
│
├── services/
│   ├── ticket_service.py
│   ├── analytics_service.py
│   └── user_service.py
│
├── llm/
│   ├── provider.py
│   ├── gemini.py
│   ├── groq.py
│   └── ollama.py
│
├── observability/
│   ├── logging.py
│   ├── tracing.py
│   └── metrics.py
│
└── core/
    ├── config.py
    ├── errors.py
    └── security.py
