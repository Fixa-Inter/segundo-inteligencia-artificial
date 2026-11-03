# Responsabilidade: observability/grafana/provisioning/datasources

## Objetivo do módulo

Registrar fonte Prometheus no Grafana.

## O que deve ser armazenado aqui

prometheus.yml com UID, tipo e URL.

## Comportamento e limites atuais

UID prometheus, acesso proxy, http://prometheus:9090, padrão e não editável.

Módulo pai: [observability/grafana/provisioning](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

Os arquivos abaixo são referências ou configuração; não expõem métodos Python.

### [prometheus.yml](prometheus.yml)

Fonte Prometheus padrão com UID fixo e URL interna do compose.
