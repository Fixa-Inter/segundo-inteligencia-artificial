# Responsabilidade: observability/grafana/provisioning/dashboards

## Objetivo do módulo

Registrar provider de dashboards em arquivo.

## O que deve ser armazenado aqui

dashboards.yml com pasta/caminho/comportamento.

## Comportamento e limites atuais

Provider FIXA lê /var/lib/grafana/dashboards, permite edição e desativa exclusão pelo provisionamento.

Módulo pai: [observability/grafana/provisioning](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

Os arquivos abaixo são referências ou configuração; não expõem métodos Python.

### [dashboards.yml](dashboards.yml)

Provider Grafana que carrega painéis JSON montados no contêiner.
