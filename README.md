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

## Respostas de limitações e horários das mensagens

A ausência de ferramenta para uma ação e uma busca no FAQ sem informação
suficiente recebem respostas padronizadas, com convite para enviar outra mensagem
como feedback de melhoria. Erros técnicos, restrições de acesso e resultados de
cadastro mantêm seu tratamento próprio. Dúvidas sobre quais dados fornecer para
um cadastro seguem para o FAQ.

Cada nova mensagem humana ou do assistente recebe `timestamp` em UTC no MongoDB.
`GET /api/v1/sessoes` e `POST /api/v1/sessoes/conversa` retornam esse campo em todas
as mensagens, como ISO 8601 com `Z`. Mensagens antigas sem horário registrado
retornam `null`. Para adicionar o campo nulo também aos documentos antigos no
banco, execute uma vez por ambiente:

```bash
python -m app.scripts.migrar_timestamps_mensagens
```

A migração pode ser repetida e preserva timestamps já existentes.

## Criação de eventos

Gestores e administradores podem criar eventos pela web ou pelo mobile. O agente
`solicitacoes` coleta a descrição, o local e as datas e horas de início e fim,
busca o local no Qdrant e guarda `evento_pendente` na sessão do MongoDB. Detalhes
do local e observação ausentes recebem "Não foi especificado". Eventos não exigem
foto nem categoria de equipamento.

Horários sem fuso usam `America/Sao_Paulo` e são enviados em UTC (`Z`). O fim deve
ser estritamente posterior ao início; eventos no passado são permitidos. O usuário
confere a proposta antes do aceite. A tool prepara a operação, o juiz a avalia e
somente então `executar_operacoes` faz `POST /api/v1/eventos`, usando a identidade
e o Bearer do usuário autenticado. Resultados indeterminados impedem reenvio automático.

## Pesquisa de compras

Técnicos, administradores e gestores podem pedir lojas ou comparar materiais, peças e equipamentos. O fluxo `analista_compras` guarda `analise_compra_pendente` no documento MongoDB da sessão. Só o nome do item é obrigatório. O especialista oferece uma vez os filtros opcionais (loja, categoria e faixa de preço) e detalhes para avaliar as ofertas (especificações, quantidade e exclusões). Se a pessoa dispensar os opcionais, a pesquisa prossegue com a palavra chave. Loja e categoria são convertidas para os slugs do Pechincha.ai por `list_stores` e `list_categories`.

O cliente usa o MCP público `https://pechincha.ai/mcp`, sem chave de API, e consulta `search_deals`, `list_stores` e `list_categories`. A métrica `fixa_pechincha_requests_total` registra chamadas e erros. Uma busca vazia significa que não há promoções ativas cadastradas para os critérios, não que o produto esteja indisponível em todas as lojas. Preços devem ser confirmados na loja.

Os testes locais do contrato e do fluxo estão em `tests/test_pechincha_mcp.py` e `tests/test_compras_unit.py`. Para testar o serviço real explicitamente no PowerShell, defina `RUN_PECHINCHA_LIVE_TESTS=1` e rode `python -m pytest tests/test_pechincha_mcp_contract.py -q`.
