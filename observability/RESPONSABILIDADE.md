# Responsabilidade: observability

## Objetivo do módulo

Configurar coleta/apresentação de métricas.

## O que deve ser armazenado aqui

Prometheus, regras de gravação e recursos Grafana.

## Comportamento e limites atuais

Coleta /api/v1/metrics a cada 15s em host.docker.internal:8000. Compose na raiz monta os arquivos; instrumentação Python fica em app/observability.

Módulo pai: [.](../RESPONSABILIDADE.md).

## Submódulos

| Pasta | Responsabilidade |
| --- | --- |
| [grafana](grafana/RESPONSABILIDADE.md) | Organizar dashboard e provisionamento Grafana. |
| [rules](rules/RESPONSABILIDADE.md) | Pré-calcular séries Prometheus para visualizações. |

## Funcionalidades disponíveis e arquivos

Os arquivos abaixo são referências ou configuração; não expõem métodos Python.

### [prometheus.yml](prometheus.yml)

Agenda coleta de métricas e carregamento das regras Prometheus.
