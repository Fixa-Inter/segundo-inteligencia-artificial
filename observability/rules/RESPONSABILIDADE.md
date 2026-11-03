# Responsabilidade: observability/rules

## Objetivo do módulo

Pré-calcular séries Prometheus para visualizações.

## O que deve ser armazenado aqui

Regras PromQL de taxas e percentis.

## Comportamento e limites atuais

Janela cinco minutos: chamadas por análise/resultado, duração p95 e tamanho JSON p95 por etapa.

Módulo pai: [observability](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

Os arquivos abaixo são referências ou configuração; não expõem métodos Python.

### [visualizacoes.yml](visualizacoes.yml)

Regras de gravação PromQL para métricas agregadas das visualizações.
