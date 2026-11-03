# Responsabilidade: observability/grafana

## Objetivo do módulo

Organizar dashboard e provisionamento Grafana.

## O que deve ser armazenado aqui

JSON de painéis e YAML de fontes/providers.

## Comportamento e limites atuais

Compose monta dashboards e provisioning separadamente. Aqui não são produzidas métricas.

Módulo pai: [observability](../RESPONSABILIDADE.md).

## Submódulos

| Pasta | Responsabilidade |
| --- | --- |
| [dashboards](dashboards/RESPONSABILIDADE.md) | Definir painéis de observabilidade FIXA. |
| [provisioning](provisioning/RESPONSABILIDADE.md) | Provisionar recursos Grafana. |

## Funcionalidades disponíveis e arquivos

Este diretório agrupa os submódulos listados acima; não contém implementação executável própria.
