# Responsabilidade: tests/fixtures

## Objetivo do módulo

Preservar referências capturadas antes da refatoração.

## O que deve ser armazenado aqui

JSON de contratos HTTP/tools e resultados/requisições simulados dos cadastros originais.

## Comportamento e limites atuais

Dados exclusivamente simulados, usados pelos testes de caracterização. Alterar estes arquivos exige verificar uma mudança intencional no contrato, não apenas atualizar expectativas para fazer um teste passar.

Módulo pai: [tests](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

Os arquivos abaixo são referências ou configuração; não expõem métodos Python.

### [cadastros_antes_refatoracao.json](cadastros_antes_refatoracao.json)

132 resultados e requisições simuladas do código anterior; consumidos por test_refatoracao_cadastros.py.

### [contratos_antes_refatoracao.json](contratos_antes_refatoracao.json)

Captura anterior do OpenAPI, de 90 schemas de ferramentas e de 19 instruções/prompt builders; consumida por test_refatoracao_contratos.py. Sem credenciais.
