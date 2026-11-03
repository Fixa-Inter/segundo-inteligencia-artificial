# Responsabilidade: observability/grafana/provisioning

## Objetivo do módulo

Provisionar recursos Grafana.

## O que deve ser armazenado aqui

Providers de dashboards e fontes de dados.

## Comportamento e limites atuais

Configuração dividida em dashboards e datasources; painéis JSON ficam em diretório próprio.

Módulo pai: [observability/grafana](../RESPONSABILIDADE.md).

## Submódulos

| Pasta | Responsabilidade |
| --- | --- |
| [dashboards](dashboards/RESPONSABILIDADE.md) | Registrar provider de dashboards em arquivo. |
| [datasources](datasources/RESPONSABILIDADE.md) | Registrar fonte Prometheus no Grafana. |

## Funcionalidades disponíveis e arquivos

Este diretório agrupa os submódulos listados acima; não contém implementação executável própria.
