# Assistente FIXA

Aplicação multiagente para gestão de manutenção, com LangGraph, especialistas por perfil, juiz, proteção de mensagens e persistência de conversas.

A revisão do fluxo interno, as divergências reproduzidas e as sugestões de modularização estão em [docs/validacao_fluxo.md](docs/validacao_fluxo.md). A validação funcional da API está fora dessa revisão.

## Fluxo interno

1. `app/graph/executor.py` recupera o histórico e os rascunhos, anonimiza a mensagem e prepara o contexto autenticado.
2. `app/graph/fluxo.py` conecta validação de entrada, supervisor, especialista e juiz.
3. O juiz aprova, bloqueia ou pede uma revisão de texto. A revisão não repete ferramentas de cadastro.
4. A proteção de saída remove dados pessoais; o executor persiste a resposta final no MongoDB.
5. Ao encerrar a conversa, a persistência pode gerar um resumo e indexá-lo no Qdrant.

## Organização

| Pasta | Responsabilidade |
| --- | --- |
| `app/agents` | Fábricas, modelos, registro dos agentes e instruções por perfil |
| `app/graph` | Estado, contexto, decisões, nós e execução do fluxo |
| `app/tools` | Ferramentas disponíveis aos agentes e seus argumentos |
| `app/services` | Consultas e operações dos domínios |
| `app/memory` | Persistência, rascunhos, histórico e vetorização |
| `app/guardrails` | Validações de entrada e proteção de dados pessoais |
| `app/schemas` | Contratos de entrada, saída e usuário autenticado |
| `app/core` | Configuração e clientes dos bancos |
| `app/observability` | Métricas de execução, custo e operações |
| `app/tests` | Testes e reproduções das divergências |
| `docs` | Esquema SQL, enums, referências e relatório da revisão |

## Importações

Os `__init__.py` declaram as interfaces públicas dos domínios. Exemplos:

```python
from app.graph import EstadoGrafo, ContextoGrafo
from app.agents import criar_agente_faq
from app.schemas import UsuarioContexto
from app.services.gerais import obter_unidade_id
from app.tools.ajuda_geral import consultar_situacao_problema
from app.memory.persistencia import salvar_mensagem
```

Dentro de um pacote, importe seus detalhes diretamente quando necessário para evitar ciclos. O pacote `app.graph` não compila o fluxo ao exportar os tipos.

A configuração está em `app/core/configuracao.py`. Os nomes das variáveis do `.env`, das pastas e dos contratos externos foram preservados. Os módulos renomeados exigem a atualização dos imports usados fora deste repositório.

## Validação

O comando da seleção interna está em [docs/validacao_fluxo.md](docs/validacao_fluxo.md#testes-e-limites). As reproduções com `xfail(strict=True)` indicam divergências ainda pendentes; não significam que o problema foi corrigido.

As consultas reais aos bancos, as chamadas aos modelos e a API precisam de validação integrada em ambiente apropriado.

Para Prometheus e Grafana, consulte [docs/observabilidade.md](docs/observabilidade.md).
