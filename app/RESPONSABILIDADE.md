# Responsabilidade: app

## Objetivo do módulo

Compor e executar a API de inteligência artificial da plataforma FIXA.

## O que deve ser armazenado aqui

Ponto de entrada FastAPI e pacotes de aplicação.

## Comportamento e limites atuais

main.py registra /api/v1, CORS, política de métricas e lifespan de clientes e índices. Site e aplicativo são consumidores; não há frontend neste checkout.

Módulo pai: [.](../RESPONSABILIDADE.md).

## Submódulos

| Pasta | Responsabilidade |
| --- | --- |
| [agents](agents/RESPONSABILIDADE.md) | Construir, selecionar e avaliar agentes especializados. |
| [api](api/RESPONSABILIDADE.md) | Compor a interface HTTP da aplicação. |
| [core](core/RESPONSABILIDADE.md) | Centralizar configuração e regras comuns de conversa. |
| [graph](graph/RESPONSABILIDADE.md) | Orquestrar o turno da conversa e a execução de operações aprovadas. |
| [guardrails](guardrails/RESPONSABILIDADE.md) | Validar mensagens e proteger dados pessoais. |
| [mcp](mcp/RESPONSABILIDADE.md) | Agrupar integrações cliente com servidores MCP. |
| [memory](memory/RESPONSABILIDADE.md) | Organizar memória conversacional e recursos vetoriais. |
| [observability](observability/RESPONSABILIDADE.md) | Instrumentar execução sem exportar conteúdo de conversa em traces. |
| [rag](rag/RESPONSABILIDADE.md) | Reservar pacote para organização de RAG. |
| [schemas](schemas/RESPONSABILIDADE.md) | Definir contratos e validadores de fronteira da aplicação. |
| [scripts](scripts/RESPONSABILIDADE.md) | Disponibilizar comandos operacionais explícitos. |
| [services](services/RESPONSABILIDADE.md) | Implementar casos de uso, consultas e gravações. |
| [tests](tests/RESPONSABILIDADE.md) | Verificar contratos e comportamento interno. |
| [tools](tools/RESPONSABILIDADE.md) | Expor capacidades como ferramentas para agentes. |

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Marcador de pacote Python; sem funções ou regras implementadas neste arquivo.

### [main.py](main.py)

Cria FastAPI, registra middlewares/rotas e gerencia clientes/índices no lifespan.

- `async lifespan(app: FastAPI)`: Inicializa clientes/índices e garante encerramento dos recursos, inclusive em falha de startup.
- Constantes, aliases e estado de módulo: `app`.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/api](api/RESPONSABILIDADE.md).
- [app/core/clients](core/clients/RESPONSABILIDADE.md).
- [app/memory/persistencia](memory/persistencia/RESPONSABILIDADE.md).
- [app/memory/vectorSearch](memory/vectorSearch/RESPONSABILIDADE.md).
- [app/observability](observability/RESPONSABILIDADE.md).
