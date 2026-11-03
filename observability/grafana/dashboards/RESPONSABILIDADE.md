# Responsabilidade: observability/grafana/dashboards

## Objetivo do módulo

Definir painéis de observabilidade FIXA.

## O que deve ser armazenado aqui

Dashboard JSON com consultas PromQL.

## Comportamento e limites atuais

Cobre custo, latência, erros, resoluções, ROI e visualizações. Consome séries da aplicação e regras de observability/rules.

Módulo pai: [observability/grafana](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

Os arquivos abaixo são referências ou configuração; não expõem métodos Python.

### [fixa-observability.json](fixa-observability.json)

Dashboard FIXA de custo, latência, erros, resoluções, ROI e análises.

Painéis existentes:

- Custo semanal \| 100 usuários (USD).
- Custo semanal \| 1.000 usuários (USD).
- Tempo total de resposta (p95).
- Índice de erros de chat (5 min).
- Latência por agente/nó (p95).
- Custo LLM acumulado (USD).
- Resoluções (ocorrências concluídas, 7d).
- Custo médio da requisição que registrou resolução (USD, 7d).
- ROI estimado (7d, BRL).
- Execuções de nós e operações de negócio por resultado.
- Visualizações \| métricas agregadas.
- Visualizações \| chamadas por análise e resultado (por min).
- Visualizações \| duração do serviço (p95).
- Visualizações \| tamanho JSON por etapa (p95).
- Visualizações \| falhas técnicas (por min).
- Visualizações \| objetos públicos projetados (1h).
- Coleta Prometheus \| API disponível.
