# Responsabilidade: dados/mobile

## Objetivo do módulo

Manter um manual mobile específico e completo para cada perfil, sem depender de arquivos operacionais gerais externos aos manuais.

## O que deve ser armazenado aqui

Documentos `Documento_*.md` dentro das pastas de perfil. Cada manual declara somente seu perfil em `roles` e mantém `channel: mobile`. Informações compartilhadas são duplicadas nos manuais aos quais se aplicam; regras de acesso não são ampliadas pela cópia.

## Manuais disponíveis

| Perfil | Documento | Seções após a migração |
| --- | --- | --- |
| [Solicitante](solicitante/RESPONSABILIDADE.md) | [Documento_solicitante.md](solicitante/Documento_solicitante.md) | 20 |
| [Técnico](tecnico/RESPONSABILIDADE.md) | [Documento_tecnico.md](tecnico/Documento_tecnico.md) | 30 |
| [Gestor](gestor/RESPONSABILIDADE.md) | [Documento_gestor.md](gestor/Documento_gestor.md) | 41 |

## Distribuição integral do conteúdo compartilhado

As 29 seções dos dois arquivos anteriormente presentes em `mobile/geral` foram incorporadas aos manuais. Os identificadores originais foram mantidos para referências internas e rastreabilidade.

| Seções de origem | Solicitante | Técnico | Gestor |
| --- | --- | --- | --- |
| COM-001 a COM-011 e COM-013 | Sim | Sim | Sim |
| COM-012 — Exportação Excel | Não | Sim | Sim |
| OPS-000 — Entrada operacional | Não | Adaptada à navegação do Técnico | Adaptada à navegação do Gestor |
| OS-001, OS-002, OS-003, OS-005, OS-006 e OS-007 | Não | Sim | Sim |
| OS-004 — Atribuição de responsável e prazo | Não | Não | Sim |
| EQP-001 a EQP-003 — Administração de equipamentos | Não | Não | Sim |
| CHK-001 a CHK-003 — Administração de checklists | Não | Não | Sim |
| INS-001 e INS-002 — Inspeções | Não | Sim | Sim |

## Conferência da migração

Antes da exclusão da pasta geral, foram comparados os textos efetivamente gravados com as seções de origem e a distribuição esperada. Todas as 29 seções possuem destino. Os conteúdos específicos SOL, TEC e GES foram preservados, com atualização das referências que apontavam para arquivos externos removidos.

Os caminhos de OS-001, OS-002, INS-001 e a apresentação OPS-000 foram ajustados por perfil. Os demais procedimentos compartilhados foram copiados integralmente para cada perfil aplicável. Restrições, ressalvas sobre protótipo, estados da informação, pré-condições e intenções equivalentes foram mantidos.

As referências MAN-001 a MAN-004 não existiam nos arquivos recebidos; os manuais que as citavam agora registram essa ausência em vez de depender de um documento inexistente. Nenhum procedimento de Manu/histórico foi inventado.

`RESPONSABILIDADE.md` é documentação de organização, não uma fonte de FAQ. A migração dos textos não executou alterações no Qdrant. O comando `python -m app.scripts.ingerir_faq` agora seleciona somente a pasta do perfil para cada corpus, junto às fontes comuns de `dados/fixa/`; administrador reutiliza o corpus de gestor. Os manuais continuam sendo referências mobile, sem ampliar seu escopo para telas web.
