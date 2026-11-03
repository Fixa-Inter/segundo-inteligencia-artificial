# Responsabilidade: docs

## Objetivo do módulo

Guardar contratos e referências técnicas.

## O que deve ser armazenado aqui

DDL PostgreSQL, permissões SQL, Swagger FIXA e enums.

## Comportamento e limites atuais

Referências podem divergir entre si e do código. validacao_fluxo.md e observabilidade.md citados no README estão ausentes.

Módulo pai: [.](../RESPONSABILIDADE.md).

## Submódulos

| Pasta | Responsabilidade |
| --- | --- |
| [api](api/RESPONSABILIDADE.md) | Guardar contrato de referência da API FIXA. |
| [database](database/RESPONSABILIDADE.md) | Documentar estrutura relacional e permissões. |
| [enum](enum/RESPONSABILIDADE.md) | Documentar códigos/nomes dos enums FIXA. |

## Funcionalidades disponíveis e arquivos

Os arquivos abaixo são referências ou configuração; não expõem métodos Python.

### [refatoracao_arquitetura.md](refatoracao_arquitetura.md)

Decisões de extração, duplicações consolidadas, semelhanças mantidas e evidências de preservação de comportamento.

### [sdd_visualizacoes.md](sdd_visualizacoes.md)

Catálogo de referência das 27 análises existentes, restaurado para o teste de consistência.
