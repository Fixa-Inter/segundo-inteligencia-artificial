# Responsabilidade: .github/workflows

## Objetivo do módulo

Disparar implantação e criação de releases.

## O que deve ser armazenado aqui

Workflows YAML, gatilhos, parâmetros e referências externas.

## Comportamento e limites atuais

deploy-ecs.yml implanta a API ia no ECS; auto-release.yaml dispara release em pushes na main. Não há workflow local de testes.

Módulo pai: [.github](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

Os arquivos abaixo são referências ou configuração; não expõem métodos Python.

### [auto-release.yaml](auto-release.yaml)

Aciona criação de release pelo workflow reutilizável na main.

### [deploy-ecs.yml](deploy-ecs.yml)

Aciona workflow reutilizável ECS na main ou manualmente, com revisão opcional de task definition.
