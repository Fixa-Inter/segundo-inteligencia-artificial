# Responsabilidade: dados/fixa

## Objetivo do módulo

Armazenar as referências institucionais do FIXA e a política operacional proposta para seus agentes de IA.

## O que deve ser armazenado aqui

Documentos de contexto do projeto, com limites e estado de aprovação explícitos.

O comando `python -m app.scripts.ingerir_faq` inclui todos os Markdown desta pasta e suas subpastas em cada corpus de FAQ: solicitante, técnico e gestor. Administrador utiliza o corpus do gestor. `RESPONSABILIDADE.md` é excluído da ingestão. Compartilhar o documento não muda seu estado de aprovação nem concede permissões adicionais.

## Documentos disponíveis

- [Documento_FIXA.md](Documento_FIXA.md): identidade, objetivo, origem, equipe, contexto e limites das informações fornecidas.
- [Documento_politicas_uso.md](Documento_politicas_uso.md): proposta de Política de Uso da IA, versão 2.0.0, para web e mobile. Define escopo dos agentes, permissões, confirmações, dados, ferramentas, evidências, segurança, comunicação, exceções, rastreabilidade e manutenção em 12 seções. Utiliza obrigações verificáveis e marca decisões pendentes com `[A DEFINIR]`. Não deve ser apresentada como política aprovada, termos publicados ou política de privacidade; a edição do documento não implementa controles nem atualiza o Qdrant.

O documento institucional foi preservado; a política foi integralmente reescrita para orientar o comportamento multiagente. A distribuição dos antigos arquivos compartilhados mobile está documentada em [dados/mobile](../mobile/RESPONSABILIDADE.md). Este arquivo de responsabilidade não integra a fonte de FAQ.
