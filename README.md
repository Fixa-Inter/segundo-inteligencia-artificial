# Assistente FIXA

Aplicação multiagente para gestão de manutenção, com LangGraph, orquestrador e especialistas por perfil, julgamento pelo JEV, proteção de mensagens e persistência de conversas.

A revisão do fluxo interno, as divergências reproduzidas e as sugestões de modularização estão em [docs/validacao_fluxo.md](docs/validacao_fluxo.md). A validação funcional da API está fora dessa revisão.

## Fluxo interno

1. `app/graph/executor.py` recupera o histórico e os rascunhos, anonimiza a mensagem e prepara o contexto autenticado.
2. `app/graph/fluxo.py` conecta validação de entrada, supervisor, especialista e julgamento. O supervisor resolve confirmações, pausas e retomadas explícitas por código; o agente orquestrador analisa o histórico e os rascunhos do MongoDB para as demais mensagens, inclusive retomadas de propostas pausadas.
3. O JEV aprova, bloqueia ou pede uma revisão de texto a partir das evidências. A revisão não repete ferramentas de cadastro.
4. A proteção de saída remove dados pessoais; o executor persiste a resposta final no MongoDB. A API retorna `confirmacao: "sim"` somente quando uma proposta é exibida e sua apresentação é registrada; nos demais casos retorna `"nao"`.
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

A configuração está em `app/core/configuracao.py`. `OPENAI_API_KEY` é usada pelo agente orquestrador; `TYPESAFE_API_KEY` é necessária para a classificação de problemas e o julgamento. `JEV_MODEL` permite fixar uma versão durante avaliações; sem ela, é usado `jev-latest`.

## Validação

O comando da seleção interna está em [docs/validacao_fluxo.md](docs/validacao_fluxo.md#testes-e-limites). As reproduções com `xfail(strict=True)` indicam divergências ainda pendentes; não significam que o problema foi corrigido.

Os testes em `app/tests/test_orquestrador.py` verificam o roteamento e a continuidade dos rascunhos; `app/tests/test_jev_fluxos.py` verifica o cliente JEV e o julgamento sem acesso externo. O cliente JEV registra duração, resultado, modelo resolvido e tokens; os limiares de julgamento devem ser acompanhados com casos reais anonimizados antes de alterações de versão do modelo.

Para Prometheus e Grafana, consulte [docs/observabilidade.md](docs/observabilidade.md).

## Pesquisa de compras

Técnicos, administradores e gestores podem pedir lojas ou comparar materiais, peças e equipamentos. O fluxo `analista_compras` guarda `analise_compra_pendente` no documento MongoDB da sessão, pede item, requisitos obrigatórios e quantidade, e oferece aplicação, orçamento, preferências e exclusões uma vez. Se a pessoa dispensar os opcionais, a busca prossegue com os três campos prioritários. O MCP recebe somente esse resumo técnico.

O cliente usa `https://www.buscazap.com.br/mcp` sem credencial por padrão. Para acesso contratado, configure `BUSCAZAP_MCP_TOKEN` no ambiente. As métricas `fixa_buscazap_requests_total` e `fixa_buscazap_access_total` mostram chamadas, erros e sinais do tier observado. Sem um tier informado pelo fornecedor, a métrica registra `unknown`; uma credencial configurada não comprova que o tier contratado foi usado.

Os testes de contrato consomem a cota real do serviço e ficam desativados na suíte padrão. Para executá-los explicitamente no PowerShell, defina `RUN_BUSCAZAP_LIVE_TESTS=1` no ambiente e rode `python -m pytest tests/test_buscazap_mcp_contract.py -q`. Os testes locais de roteamento, coleta e erros estão em `tests/test_compras_unit.py`.
