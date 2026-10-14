# Observabilidade no Grafana

O projeto exporta métricas no formato Prometheus em `GET /api/v1/metrics`. O Grafana e o Prometheus locais são iniciados pelo Compose; o Prometheus coleta os dados da API a cada 15 segundos e o dashboard FIXA é carregado automaticamente.

## Subir localmente

1. Instale o [Docker Desktop](https://www.docker.com/products/docker-desktop/) e confirme que ele está em execução.
2. Instale a dependência Python junto das demais: `python -m pip install -r requirements.txt`.
3. Inicie a API na porta 8000: `python -m uvicorn app.main:app --reload --port 8000`.
4. Em outro terminal, na raiz do repositório, execute: `docker compose -f compose.observability.yml up -d`.
5. Acesse Grafana em `http://localhost:3000` (usuário e senha iniciais locais: `admin` / `admin`). O dashboard fica na pasta **FIXA**. O Prometheus pode ser consultado em `http://localhost:9090`.

Para parar: `docker compose -f compose.observability.yml down`. Os volumes mantêm os dados entre reinicializações. Para apagar também os dados locais coletados, use `docker compose -f compose.observability.yml down -v`.

O Prometheus está configurado para buscar a API em `host.docker.internal:8000`. Se a API rodar em outra porta, ajuste o destino em `observability/prometheus.yml`. O endpoint de métricas não tem autenticação e este Compose é para desenvolvimento local; não exponha a porta 8000 ou o endpoint publicamente sem restringir o acesso.

## Métricas e cálculos

- **Estimativa para 100/1.000 usuários ativos por semana:** usuários × mensagens por usuário/semana × custo estimado por mensagem. Os padrões são 4 mensagens por usuário, 6.000 tokens de entrada e 1.600 de saída por mensagem. Com os preços configurados para `gpt-6-luna` (US$ 0,10 / milhão de tokens de entrada e US$ 0,50 / milhão de saída), isso resulta em cerca de **US$ 0,56/semana para 100 usuários** e **US$ 5,60/semana para 1.000**. É uma projeção só do modelo principal, não uma medição de tráfego; chamadas de fallback não entram nesses dois cenários.
- **Latência por agente:** duração de cada nó do LangGraph. O gráfico mostra p95 por nó, que ajuda a identificar em que etapa o fluxo demora. O tempo total no chat é medido no serviço, desde o processamento da mensagem até a resposta preparada pela API; não inclui a autenticação anterior à rota nem o transporte de rede até o cliente.
- **Índice de erros:** requisições que chegaram ao serviço de chat e terminaram com exceção ou estado de erro no grafo, dividido pelo total processado. Falhas anteriores à chamada do serviço (por exemplo, autenticação) ficam fora desse indicador. Bloqueios normais de segurança e respostas fora do escopo não contam como erro técnico.
- **Custo por resolução:** o denominador é uma ocorrência de manutenção registrada com sucesso pelo fluxo do técnico (manutenção já realizada). O painel calcula a média do custo de LLM da requisição que registrou essa ocorrência, em uma janela de 7 dias. Não inclui o custo de conversas anteriores da mesma tarefa.
- **ROI estimado:** `(valor atribuído às resoluções − custo de LLM convertido para BRL) ÷ custo de LLM convertido para BRL × 100`. A cotação configurada é uma referência PTAX arredondada e deve ser atualizada; o valor por resolução continua em branco até haver uma estimativa de benefício. O painel de ROI fica sem dados enquanto faltar qualquer uma dessas duas premissas.

## Ajustar premissas

Adicione as variáveis abaixo ao `.env` antes de iniciar a API. Os valores de tokens por mensagem e mensagens por usuário servem apenas para a projeção dos cenários. O preço OpenAI deve ser mantido de acordo com o contrato/tarifa efetivamente aplicada. Os valores de câmbio e de retorno são premissas de negócio.

```env
OBSERVABILITY_WEEKLY_MESSAGES_PER_USER=4
OBSERVABILITY_ESTIMATED_INPUT_TOKENS_PER_MESSAGE=6000
OBSERVABILITY_ESTIMATED_OUTPUT_TOKENS_PER_MESSAGE=1600
OBSERVABILITY_OPENAI_INPUT_USD_PER_MILLION=0.10
OBSERVABILITY_OPENAI_OUTPUT_USD_PER_MILLION=0.50
OBSERVABILITY_GROQ_INPUT_USD_PER_MILLION=0.15
OBSERVABILITY_GROQ_OUTPUT_USD_PER_MILLION=0.60
OBSERVABILITY_BRL_PER_USD=5.01
# Defina um valor estimado somente quando houver uma base para ele.
OBSERVABILITY_VALUE_PER_RESOLUTION_BRL=
```

O custo medido vem dos tokens reportados pelo modelo nas respostas de LLM. O fallback usado pelo juiz está precificado conforme a tarifa pública atual do Groq para `openai/gpt-oss-120b`; confirme a tarifa da sua conta. O cálculo usa a tarifa cheia de entrada, sem descontar tokens em cache, então pode superestimar essas chamadas. Custos de embeddings, banco, Qdrant, imagens, hospedagem e o próprio Grafana/Prometheus não estão incluídos no custo de LLM.

As métricas são agregadas e usam rótulos de baixa cardinalidade (nome de agente, provedor, modelo e resultado); prompts, respostas, IDs de usuário e IDs de sessão não são exportados.
