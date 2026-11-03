# Responsabilidade: dados

## Objetivo do módulo

Armazenar documentos de referência do produto e manuais de uso por perfil.

## O que deve ser armazenado aqui

Fontes Markdown do FIXA, com escopo, estado da informação e público explicitados. Arquivos `RESPONSABILIDADE.md` descrevem a organização e não são conteúdo de FAQ para ingestão.

## Conteúdo e submódulos

| Pasta | Responsabilidade |
| --- | --- |
| [fixa](fixa/RESPONSABILIDADE.md) | Contexto institucional e proposta de política operacional dos agentes de IA, abrangendo web e mobile, com regras e decisões pendentes explícitas. |
| [mobile](mobile/RESPONSABILIDADE.md) | Manuais completos de solicitante, técnico e gestor, com conteúdo compartilhado duplicado nos perfis aplicáveis. |

## Uso na ingestão de FAQ

O comando `python -m app.scripts.ingerir_faq` reúne todos os Markdown de `fixa/` para cada perfil indexado e acrescenta somente os de `mobile/solicitante/`, `mobile/tecnico/` ou `mobile/gestor/`, conforme o destino. O administrador reutiliza o FAQ do gestor pela regra atual de busca. Subpastas dessas fontes são incluídas; arquivos `RESPONSABILIDADE.md` e outros formatos são excluídos da descoberta. Cada perfil é atualizado uma única vez com todos os seus documentos. O comando não utiliza a pasta técnica `docs/`.

## Limites das fontes

Os documentos mobile são referências de interface/protótipo; não ampliam permissões de produção nem descrevem a versão web. A política operacional da IA é uma proposta em validação; não é uma política vigente, Termos de Uso ou Política de Privacidade. Suas regras não concedem ferramentas nem substituem controles no código. Organizar estas fontes não executa a ingestão no Qdrant.
