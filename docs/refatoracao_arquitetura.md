# Organização do monólito e preservação de comportamento

## Interfaces dos módulos

Os `__init__.py` expõem nomes públicos por um mapa explícito de proprietários. `app/core/interfaces.py` resolve os recursos sob demanda; importar um pacote não cria agentes, compila o grafo ou abre bancos. Classes e ferramentas mantêm identidade. Nomes ambíguos recebem exportações específicas por domínio, preservando os nomes canônicos já públicos.

Os arquivos de implementação continuam com responsabilidade própria. A centralização é da interface de importação. A lógica não foi acumulada nos inicializadores. O catálogo analítico passou a `services/visualizacoes/catalogo.py`; os registros de ferramentas ficam em `tools/*/registro.py`.

## Responsabilidades corrigidas

| Antes | Proprietário atual | Compatibilidade |
| --- | --- | --- |
| Regras de classificação dentro do handler HTTP | `services/classificacao_problema.py` | Rota, campos, descrições e status HTTP preservados |
| Contratos de cadastro em `tools/toolsRequest` | `schemas/cadastros` | Módulos antigos reexportam as mesmas classes |
| Respostas estruturadas em `agents/agentsResult` | `schemas/resultados_agentes` | Tipos antigos continuam disponíveis |
| Clientes LLM/embedding em `agents/modelos.py` | `core/clients/modelos.py` | Alias de compatibilidade, mesmos modelos e opções |
| Memória/guardrails importando fábricas de agentes | Clientes de `core/clients` | Sem mudança na identidade/configuração dos modelos |
| Renderização genérica em `graph/respostas_padrao.py` | `core/apresentacao` por assunto | Seleção de resposta do fluxo permanece no grafo; nomes antigos reexportados |
| Projeções puras de operações em `services/operacoes.py` | `core/operacoes.py` | Serviço mantém preparação, hash e persistência |
| Consulta pura de propostas no grafo | `core/continuacoes.py` | Grafo mantém transições e gravações |
| Contexto compartilhado de cadastro em tool de solicitação | `tools/contexto.py` | Domínios compartilham validação sem depender da criação de solicitação |
| Calendário/enums genéricos em consulta SQL de OS | `core/tempo.py` e `core/manutencao.py` | Imports anteriores continuam disponíveis |

## Duplicações consolidadas

| Duplicação identificada | Recurso comum | Diferença mantida |
| --- | --- | --- |
| Validação de período em três serviços KPI | `validar_periodo_indicadores` | Exige `date` estrito e início anterior ao fim exclusivo |
| Tratamento de falhas/resultados Databricks em três serviços | `consultar_linhas_indicador` | Adaptadores preservam tipos dos parâmetros, snapshot/período e retorno de linha/lista |
| Separação de `ToolRuntime` em oito schemas | `ArgumentosComRuntime` | Configurações/limites de cada schema e rejeição de runtime JSON mantidos |
| Conversão de data SQL em solicitações, ocorrências e OS | `data_iso_banco` | Somente OS admite data nula |
| Relógio UTC em quatro arquivos de persistência | `agora_utc` | Referência local de negócio permanece em America/Sao_Paulo |
| Janela de três meses em consultas relacionadas | `inicio_periodo_listagem` e `subtrair_meses` | Ajuste de dia inexistente e ano bissexto preservados |
| Células e linhas Markdown em duas ferramentas | `escapar_celula` e `montar_tabela_markdown` | Textos de ausência, política de datas, colunas e agrupamento por status das OS preservados |
| Interpretação HTTP de três cadastros FIXA | `interpretar_cadastro` | Payload, ordem de validação, ID de resposta, mensagem, detalhes de falha e status de solicitação continuam por domínio |
| Limite de dez palavras em evento e proposta de solicitação | `validar_titulo_cadastro` | A validação continua nas mesmas fronteiras; não foi estendida a outros cadastros |

Adaptadores pequenos preservam pontos de substituição e contratos históricos. Eles não repetem a lógica consolidada e não acrescentam reenvio automático.

## Semelhanças que permanecem separadas

- Atualizações de solicitação e ocorrência compartilham versionamento, mas diferem em autoria/perfis, status, atividade, campos e enums. As transações, snapshots e SQL de autorização continuam específicos.
- Os três cadastros têm payloads e ordem de validação diferentes, incluindo aliases distintos para local e identidade. Somente a interpretação comprovadamente comum foi abstraída.
- Normalização de aceite, filtros de enum e texto de anúncio tem regras diferentes de pontuação, caixa e espaço. Não foi criado um normalizador universal.
- `PeriodoRequest` aceita datas iguais; os KPIs usam intervalo exclusivo não vazio. Esses contratos não foram unificados.
- As exceções de perfil e de histórico representam domínios diferentes, embora seus construtores sejam parecidos. Os tipos públicos foram preservados.
- Históricos, resultados operacionais e descrições vetoriais não são evidências intercambiáveis. As verificações de origem/permissão continuam no fluxo original.
- Fontes analíticas, histogramas, boxplots e recorrência mantêm suas populações/estatísticas específicas. Não há gerador genérico de SQL comandado pelo modelo.

## Validação

A execução inicial apresentou **1.632 testes aprovados, dois com falha e um ignorado**. As falhas eram referências a `app/scripts/migrar_timestamps_mensagens.py` e `docs/sdd_visualizacoes.md`, ausentes antes da refatoração. O comando idempotente documentado no README e o catálogo de referência das 27 análises foram disponibilizados. A migração não roda no startup e não foi executada em banco real.

Os testes novos ficam em `/tests`:

- `test_refatoracao_contratos.py`: comparação integral do OpenAPI, de 90 schemas de ferramentas e de 19 instruções/construtores de prompts, incluindo espaços; também confere identidade dos contratos reexportados.
- `test_refatoracao_cadastros.py`: 132 capturas de resultados/requisições do código anterior e falhas de transporte, conferindo envio único, payload e Bearer.
- `test_refatoracao_importacoes.py`: processos limpos em três ordens, resolução de todas as interfaces, ausência de acesso à rede nas importações e restrição das dependências de `core`.
- `test_refatoracao_recursos.py`: limites temporais, datas nulas, escape de Markdown e falhas de indicadores.

Os arquivos de `tests/fixtures` foram capturados do código anterior; contêm somente dados simulados. Os testes anteriores não foram alterados nem marcados como sucesso esperado para ocultar falhas.

Resultado final: **1.937 testes aprovados e um ignorado**, incluindo **303 novos casos** em `/tests`. A comparação estática também confirmou os mesmos textos SQL e a mesma árvore sintática do catálogo central `core/respostas.py`. Os 744 métodos da implementação têm explicação no código; handlers sem docstring mantiveram comentários para preservar as descrições do OpenAPI.

Execute a suíte com:

```powershell
.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider
```

O contrato real Pechincha continua optativo por `RUN_PECHINCHA_LIVE_TESTS=1`. Os demais testes simulam rede, bancos e modelos. Aprovação da suíte caracteriza esses cenários; não substitui validar integrações externas e respostas de um LLM real no ambiente de homologação.
