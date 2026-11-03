---
document_id: "GES"
title: "Gestor — funcionalidades, acessos e procedimentos mobile"
roles: ["gestor"]
status: "REFERENCIA_MOBILE"
audience: "usuario_mobile"
responsibility: "Orientar o Gestor sobre triagem, planejamento e atribuição de OS, tarefas, equipe, equipamentos, checklists, inspeções, acesso, conta, eventos, exportação e ajuda no mobile. Os procedimentos compartilhados aplicáveis estão integralmente neste documento. Não documenta a versão web nem um perfil administrador."
version: "1.1.0"
updated_at: "2026-11-02"
channel: "mobile"
language: "pt-BR"
validation_scope: "Telas e conexões do Figma; declarações do responsável pelo projeto. Não é auditoria da aplicação em produção."
---

# Gestor — funcionalidades, acessos e procedimentos mobile

Responsabilidade deste documento: Orientar o Gestor sobre triagem, planejamento e atribuição de OS, tarefas, equipe, equipamentos, checklists, inspeções, acesso, conta, eventos, exportação e ajuda no mobile. Os procedimentos compartilhados aplicáveis estão integralmente neste documento. Não documenta a versão web nem um perfil administrador.

## GES-001 — Papel, áreas e limites

Estado da informação: REFERENCIA_MOBILE.

O Gestor acessa Home, Gerencie todas as etapas, Gerencie equipe, Gerenciamento de equipamentos e Eventos pelo menu inferior de cinco abas. Em Etapas há Solicitações, Planejamento, Quadros e Ocorrências. Pelo perfil acessa Meu perfil, Editar perfil, Configurações, FAQ, Sobre o app, Exportar excel, Manu e Sair.

No fluxo mobile pode analisar/aprovar/recusar solicitações; planejar/criar OS; atribuir responsável e prazo; acompanhar e realizar tarefas conforme as telas disponíveis; consultar ocorrências; consultar equipe e editar avaliações de competências; gerenciar categorias, modelos, aparelhos e checklists; realizar inspeções; consultar eventos e conversar com a Manu.

Ocorrências são somente para visualização pelo Gestor. Ele não registra, edita, exclui ou aprova ocorrências no fluxo atual, conforme correção expressa do responsável. Modais antigos que ainda constem no arquivo não ampliam essa permissão.

Não há fluxo mobile documentado de criar/excluir contas da equipe, redefinir o papel de outro usuário, administrar instituições, configurar cobrança ou gerenciar um administrador. A versão web está fora desta entrega.

## GES-002 — Navegar pelas áreas do Gestor

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Navegar pelas áreas do Gestor.

Caminho no mobile: Home → menu inferior → área de trabalho.

Etapas:
1. Na Home, consulte resumos e role para visualizar todos os cards de solicitações para planejar.
2. Abra a aba Gerencie todas as etapas para Solicitações, Planejamento, Quadros ou Ocorrências.
3. Use o ícone de equipe para Gerencie equipe, inclusive quando estiver na Home ou em Gerencie todas as etapas.
4. Use a chave/ferramenta para Gerenciamento de equipamentos e o calendário para Eventos.
5. Para conversar com a assistente, abra o perfil e selecione Manu.

Regras e variações:
- O ícone de equipe não deve redirecionar para Etapas.
- Gráficos, indicadores e títulos são de visualização; o acesso às áreas ocorre por cards, botões e ícones.

## GES-003 — Consultar solicitações para análise

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Consultar solicitações para análise.

Caminho no mobile: Etapas → Solicitações/Analise os pedidos.

Etapas:
1. Abra Solicitações no painel Gerencie todas as etapas.
2. Use a busca e os seletores Autor e Período para reduzir a lista.
3. Escolha o autor e a faixa de período no componente correspondente e aplique a escolha.
4. Abra um card para conferir o relato e suas evidências.
5. Limpe os filtros para voltar à visão sem restrição.

Resultado esperado no fluxo: Detalhe da solicitação escolhida, com as ações de análise disponíveis.

Não presumir:
- Autor representa filtro por responsável pelo registro; não muda o solicitante nem atribui um técnico.
- Não confundir o filtro de período da lista com o prazo de uma OS.

Intenções equivalentes: analisar pedidos; filtrar por autor; filtrar por data.

## GES-004 — Aprovar solicitação e seguir para planejamento

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Aprovar solicitação e seguir para planejamento.

Caminho no mobile: Solicitações → card → Aprovar.

Etapas:
1. Abra o relato que será analisado.
2. Confira problema, local e evidências.
3. Toque em Aprovar e confirme no modal.
4. Na confirmação de aprovação, use Voltar para a lista ou Planejar OS para iniciar o planejamento dessa demanda.

Resultado esperado no fluxo: Solicitação aprovada no fluxo, com opção de planejar OS.

Voltar ou cancelar: Cancelar no modal retorna sem confirmar a aprovação.

Regras e variações:
- Aprovar solicitação não equivale a concluir serviço nem a registrar ocorrência.

Não presumir:
- Não foram formalizados critérios institucionais de aprovação, SLA ou notificações automáticas ao solicitante.

Intenções equivalentes: aceitar solicitação.

## GES-005 — Recusar uma solicitação

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Recusar uma solicitação.

Caminho no mobile: Solicitações → card → Recusar.

Etapas:
1. Abra o relato e confira o contexto.
2. Selecione Recusar.
3. Informe o motivo se desejar, conforme campo opcional apresentado.
4. Confirme a recusa e use a tela de resultado para retornar.

Resultado esperado no fluxo: A solicitação segue o estado recusado no fluxo.

Regras e variações:
- Recusadas pertence a solicitações; não existe filtro Recusadas no quadro de OS.

Não presumir:
- Recurso, reabertura, categorias de motivo e efeitos sobre OS já existentes não foram formalizados.

Intenções equivalentes: rejeitar pedido.

## GES-006 — Escolher uma solicitação para planejar OS

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Escolher uma solicitação para planejar OS.

Caminho no mobile: Etapas → Planejamento/Defina tarefas da OS.

Etapas:
1. Abra Planejamento em Gerencie todas as etapas ou use Planejar OS após aprovar uma solicitação.
2. Na lista Planeje as tarefas da OS, utilize busca, Autor e Período se necessário.
3. Abra o card escolhido para iniciar o assistente de criação de OS.
4. Siga OS-002 e OS-003 para definir informações e tarefas, revisar e finalizar a criação.

Resultado esperado no fluxo: Início do planejamento para a demanda selecionada.

Regras e variações:
- O botão + do quadro também cria nova OS; não obrigar todos os registros a partir desta lista.

Intenções equivalentes: planejar manutenção; definir tarefas.

## GES-007 — OS: consulta, criação, atribuição e execução

Estado da informação: REFERENCIA_MOBILE.

Usar OS-001 para quadro e filtros; OS-002 para criar uma OS; OS-003 para adicionar/editar tarefas; OS-004 para escolher responsável, prazo e confirmar a atribuição; OS-005 para realizar/desfazer tarefas; OS-006 para finalizar e OS-007 para consultar a OS concluída.

Uma indicação Recomendado na escolha de responsável é exibida no protótipo; o algoritmo, os critérios e a existência de recomendação por IA em produção não foram comprovados. A decisão do responsável só fica confirmada na etapa final da atribuição. Não tratar uma seleção provisória como atribuição já salva.

## GES-008 — Consultar ocorrências registradas pelos técnicos

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Consultar ocorrências registradas pelos técnicos.

Caminho no mobile: Etapas → Ocorrências → card.

Etapas:
1. Abra Ocorrências no painel de etapas.
2. Use Autor e Período para filtrar os registros quando necessário.
3. Abra o card e leia os dados do serviço e suas evidências.
4. Use o único botão Voltar para retornar à lista.

Resultado esperado no fluxo: Visualização de ocorrência, sem registrar ou aprovar nada.

Regras e variações:
- O Gestor apenas visualiza ocorrências. Não oferecer Registrar, Editar, Excluir ou Aprovar.
- A tela de detalhe é própria para consulta; não é a revisão de uma criação.

Intenções equivalentes: ver serviço realizado; consultar ocorrência.

## GES-009 — Consultar equipe e responsabilidades de um técnico

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Consultar equipe e responsabilidades de um técnico.

Caminho no mobile: Menu inferior Equipe → card de integrante.

Etapas:
1. Abra Gerencie equipe pelo ícone de equipe.
2. Consulte a lista e o seletor Área disponível; depois selecione o integrante desejado.
3. Consulte identificação, função, quantidade de OS e competências. A lista também apresenta horário e disponibilidade nos exemplos.
4. Role quando houver conteúdo abaixo para ver as responsabilidades completas.
5. Use o acesso de responsabilidade/OS quando disponível ou volte à lista.

Regras e variações:
- O título Competências e os cards de notas resumidas são somente de visualização. Para detalhar, use Ver mais.
- Números de OS, nomes e notas exibidos são exemplos do protótipo.

Não presumir:
- Não há caminho confirmado de contratar, cadastrar, excluir ou bloquear integrantes neste mobile.

Intenções equivalentes: ver técnico; responsabilidades da equipe.

## GES-010 — Consultar e alterar uma avaliação de competência

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Consultar e alterar uma avaliação de competência.

Caminho no mobile: Equipe → técnico → Competências → Ver mais → lápis.

Etapas:
1. Abra os detalhes do integrante na equipe.
2. Toque em Ver mais na seção Competências.
3. Na competência desejada, use o ícone de edição.
4. Confira o valor anterior e informe o novo valor no formulário.
5. Toque em Salvar; Cancelar abandona a edição.

Resultado esperado no fluxo: Atualização da avaliação na demonstração.

Não presumir:
- Escala de validação, critérios de avaliação, histórico e efeitos na recomendação de técnicos não foram formalizados. Os exemplos usam notas sobre 10; não inventar regra de cálculo.

Intenções equivalentes: mudar nota de competência; avaliar habilidade.

## GES-011 — Equipamentos, checklists e inspeções

Estado da informação: REFERENCIA_MOBILE.

Gerenciamento de equipamentos abre Categorias, Modelos e Checklists. Usar EQP-001 para categorias; EQP-002 para modelos; EQP-003 para aparelhos; CHK-001 para consultar e excluir checklists; CHK-002 para o assistente de criação; CHK-003 para campos e opções; INS-001 e INS-002 para realizar inspeções.

Categoria agrupa modelos; modelo representa o tipo de equipamento; aparelho é a unidade identificada e localizada. Checklist define o que verificar, sua periodicidade e quais modelos abrange. Inspeção é um preenchimento para um aparelho. Não trocar esses conceitos na orientação.

## GES-012 — Regras específicas e cuidado na gestão

Estado da informação: REGRAS_CONFIRMADAS_E_ORIENTACOES_PROPOSTAS.

Regras confirmadas: somente visualização de ocorrências; equipe acessível pelo ícone correto; competências resumidas são leitura e a edição tem caminho próprio; atribuição de OS requer responsável, prazo e confirmação; não existe recusa de OS no quadro.

Orientações propostas de uso responsável: conferir a demanda antes de decidir, registrar decisões compatíveis com o problema, atribuir serviços de forma adequada e revisar o escopo antes de excluir equipamentos ou checklists. Não foram formalizados critérios institucionais de prioridade, distribuição, pontuação de competência ou sanções. O rótulo P0 e os exemplos do protótipo não bastam para estabelecer toda uma política de classificação.

## COM-001 — Escopo, leitura e comportamento do protótipo

Estado da informação: REFERENCIA_MOBILE.

Este material descreve o mobile observado no Figma em 01/11/2026 e as regras confirmadas pelo responsável. Uma tela existente comprova um fluxo desenhado; não comprova implementação, segurança, persistência ou integração em produção.

No protótipo, entradas podem ser preenchidas por exemplos ao toque, fotos são simuladas, conversas têm respostas preparadas e algumas ações representam resultados sem executar serviços externos. Isso foi autorizado para demonstrar os fluxos. Os exemplos não são credenciais, usuários reais ou dados institucionais atuais. Na orientação ao usuário do aplicativo, descrever o objetivo do campo; não fornecer senha ou código fixo do protótipo como procedimento de autenticação.

Campos preenchidos devem se distinguir dos placeholders. Uma nova criação deve iniciar com os campos do novo registro vazios; o preenchimento anterior não representa uma nova solicitação ou OS já cadastrada. Voltar dentro do mesmo rascunho é diferente de iniciar outro registro.

Títulos, gráficos, indicadores e resumos de competências são informativos. Botões, ícones de navegação, ações de menus e cards com destino são interativos. O menu de três pontos abre opções junto ao acionador; confirmação de uma ação é um modal separado.

## COM-002 — Entrar no aplicativo

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Entrar no aplicativo.

Caminho no mobile: Abertura → apresentação inicial → Login.

Etapas:
1. Avance as telas de apresentação, quando exibidas, até chegar ao Login.
2. Informe seu e-mail e sua senha nos respectivos campos.
3. Use o ícone de olho se precisar conferir a senha e toque novamente para ocultá-la.
4. Toque em Entrar e acesse a Home correspondente ao perfil da conta.

Campos e escolhas:
- E-mail da conta.
- Senha da conta; o campo deve iniciar sem uma senha predefinida.

Resultado esperado no fluxo: Acesso à Home do perfil autenticado.

Não presumir:
- Não há especificação de mensagens de erro, bloqueio por tentativas, duração da sessão ou requisitos mínimos de senha.
- O fluxo desenhado não define como a instituição concede o perfil; cadastrar-se não comprova poder escolher Gestor ou Técnico.

Intenções equivalentes: fazer login; entrar na conta; mostrar senha.

## COM-003 — Usar a alternativa de entrada Google

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Usar a alternativa de entrada Google.

Caminho no mobile: Login → Ou entre com → Google.

Etapas:
1. Na tela Login, selecione a opção Google em Ou entre com.
2. Na aplicação integrada, siga a autenticação do provedor e retorne ao FIXA.

Resultado esperado no fluxo: No protótipo, a ação simula a entrada no fluxo do perfil.

Não presumir:
- A autenticação Google real, a vinculação de contas e os domínios aceitos não foram verificados.
- Não orientar a digitar a senha Google em uma mensagem para a Manu.

Intenções equivalentes: entrar com Google.

## COM-004 — Criar conta

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Criar conta.

Caminho no mobile: Login → Cadastre-se → Instituição e unidade → Dados pessoais → Criar.

Etapas:
1. Toque em Cadastre-se no Login.
2. Abra Instituição e selecione a instituição disponível; escolha a Unidade correspondente.
3. Toque em Continuar.
4. Preencha nome completo, data de nascimento, e-mail e telefone.
5. Defina uma senha e repita-a em Confirmar Senha. Use o olho, quando exibido, para conferir o que foi preenchido.
6. Revise os dados e toque em Criar.

Campos e escolhas:
- Instituição e unidade: escolhas dos seletores; não texto livre para criar instituições.
- Nome completo; data de nascimento no formato DD/MM/AAAA; e-mail; telefone.
- Senha e confirmação da mesma senha.

Resultado esperado no fluxo: Conclusão do caminho de cadastro e entrada no fluxo demonstrado.

Voltar ou cancelar: Já possui uma conta? Login retorna à entrada.

Não presumir:
- Não foram definidos convites, aprovação institucional, verificação de e-mail, idade mínima, regras de domínio ou concessão de privilégios.
- As opções institucionais do mock não são uma lista pública de instituições atendidas.

Intenções equivalentes: cadastrar; criar uma conta; primeiro acesso.

## COM-005 — Recuperar o acesso por nova senha

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Recuperar o acesso por nova senha.

Caminho no mobile: Login → Esqueceu a senha? → E-mail → Código → Nova senha.

Etapas:
1. Toque em Esqueceu a senha? no Login.
2. Informe o e-mail da conta e toque em Enviar e-mail para solicitar a recuperação.
3. Informe o código de seis dígitos recebido pelo canal de recuperação e toque em Confirmar código. Se necessário, há o comando Reenviar na tela.
4. Defina a nova senha e preencha a confirmação com o mesmo valor.
5. Use os olhos dos campos para conferir ou ocultar as senhas.
6. Toque em Confirmar para concluir a alteração e use Voltar para login na tela de sucesso.

Resultado esperado no fluxo: O fluxo apresenta confirmação de senha alterada.

Regras e variações:
- No protótipo, os dígitos aparecem juntos ao acionar o preenchimento, sem primeiro dígito pré-selecionado.
- O olho altera a visibilidade; não altera a senha.

Não presumir:
- Envio real, validade do código, funcionamento externo do reenvio, quantidade de tentativas e formatos de erro não foram documentados.
- Não pedir o código de recuperação na conversa com a Manu.

Intenções equivalentes: esqueci minha senha; redefinir senha; código de recuperação.

## COM-006 — Consultar e editar o próprio perfil

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Consultar e editar o próprio perfil.

Caminho no mobile: Avatar/perfil → Meu perfil ou Editar perfil.

Etapas:
1. Abra o perfil pelo avatar ou acesso de perfil disponível na Home.
2. Selecione Meu perfil para consultar os dados.
3. Selecione Editar perfil para abrir o formulário de edição.
4. Altere apenas os campos disponibilizados: nome, nascimento, e-mail, telefone e senha, conforme a tela. O acesso na foto representa troca de imagem no protótipo, sem comprovar upload real.
5. Use a ação de salvar/confirmar disponível na edição; cancelar ou voltar encerra a edição sem confirmar as mudanças.

Resultado esperado no fluxo: O protótipo representa a atualização do próprio perfil.

Não presumir:
- Não há caminho confirmado para mudar o perfil de acesso, a instituição ou a unidade por este formulário.
- Não foi validada alteração real de credenciais no servidor nem reverificação de e-mail.

Intenções equivalentes: meus dados; editar conta; alterar telefone.

## COM-007 — Configurar notificações

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Configurar notificações.

Caminho no mobile: Perfil → Configurações → Notificações.

Etapas:
1. Abra o perfil e selecione Configurações.
2. Use o controle de Notificações para ativar ou desativar a preferência demonstrada.
3. Volte à tela anterior.

Resultado esperado no fluxo: A preferência muda visualmente no protótipo.

Não presumir:
- Categorias de notificação, permissões do sistema operacional e entrega de push não foram especificadas.

Intenções equivalentes: desligar notificações; preferências.

## COM-008 — Consultar notificações

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Consultar notificações.

Caminho no mobile: Home → Ícone de notificações.

Etapas:
1. Na Home, toque no ícone de notificações.
2. Leia os avisos exibidos e utilize o acesso ao registro relacionado quando houver uma ação disponível.
3. Use Voltar para retornar.

Resultado esperado no fluxo: Consulta dos avisos demonstrados.

Não presumir:
- Avisos e datas de exemplo não são dados atuais. Não foram formalizadas regras de leitura, exclusão, prioridade ou frequência de envio.

## COM-009 — Navegar pelo calendário e consultar eventos

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Navegar pelo calendário e consultar eventos.

Caminho no mobile: Aba Eventos → Semana/dia → Card ou ícone de visualização.

Etapas:
1. Abra a aba Eventos pelo ícone de calendário do menu inferior.
2. Toque em um dos dias da semana exibida para consultar a lista daquele dia.
3. Abra o seletor de calendário para escolher outra semana; use a navegação de mês e selecione uma data da semana desejada.
4. Após escolher a semana, selecione o dia que deseja consultar.
5. Abra um evento pelo card ou pelo ícone de olho e consulte suas informações.
6. Volte para a agenda para mudar o dia ou a semana.

Resultado esperado no fluxo: Lista de eventos correspondente ao dia escolhido ou estado vazio.

Regras e variações:
- Sem eventos, apresentar a mensagem de ausência de resultados com o mesmo padrão visual dos demais estados vazios.
- Outubro de 2026 e os eventos mostrados são dados de demonstração; não um calendário institucional atualizado.

Não presumir:
- Não foi encontrado fluxo mobile de criar, editar, excluir, inscrever-se ou confirmar presença em eventos.
- Não prometer sincronização com Outlook, Google Calendar ou calendário letivo externo.

Intenções equivalentes: ver eventos; mudar semana; outro dia; nenhum evento encontrado.

## COM-010 — Consultar FAQ e informações do aplicativo

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Consultar FAQ e informações do aplicativo.

Caminho no mobile: Perfil → FAQ ou Sobre o app.

Etapas:
1. Abra FAQ no menu do perfil.
2. Toque na pergunta para expandir ou recolher a resposta: O que é o FIXA?, Como abrir um registro?, Como acompanhar o status? ou Como usar a Manu?.
3. Abra Sobre o app pelo menu do perfil para consultar a apresentação disponível.
4. Retorne pelo controle Voltar.

Regras e variações:
- Guia de uso, Política de Privacidade e Termos de Uso ainda não têm conteúdos/links oficiais fornecidos.
- A minuta de políticas deste pacote não equivale a uma Política de Privacidade ou contrato publicado.

Não presumir:
- Não fabricar destinos para os três conteúdos ausentes.

Intenções equivalentes: ajuda; perguntas frequentes; sobre o app; política de privacidade; termos.

## COM-011 — Sair da conta

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Sair da conta.

Caminho no mobile: Perfil → Sair → Confirmação.

Etapas:
1. Abra o perfil e selecione Sair.
2. Confira o pedido de confirmação.
3. Confirme para retornar ao Login; cancele para continuar na sessão.

Resultado esperado no fluxo: O fluxo retorna à tela de entrada.

Não presumir:
- Sair não é excluir conta. Revogação de sessões em outros aparelhos e limpeza de dados locais não foram formalizadas.

Intenções equivalentes: logout; desconectar.

## COM-012 — Solicitar a exportação disponível no perfil

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Solicitar a exportação disponível no perfil.

Caminho no mobile: Perfil → Exportar excel.

Etapas:
1. Abra o menu de perfil e selecione Exportar excel.
2. Selecione as categorias disponibilizadas: Solicitações, Ordens de serviço, Ocorrências e/ou Checklists.
3. Toque em Exportar e acompanhe o resultado apresentado.

Resultado esperado no fluxo: O protótipo representa a solicitação de exportação.

Regras e variações:
- O acesso à opção não comprova permissão para exportar registros de outras pessoas ou unidades. O escopo deve ser limitado pela autorização real da aplicação.

Não presumir:
- Formato final, colunas, tamanho máximo, entrega do arquivo e integração de download não foram validados.
- Não há opção equivalente confirmada para o Solicitante.

Intenções equivalentes: baixar planilha; exportar Excel; relatório.

## COM-013 — Conexão e ausência de dados

Estado da informação: REFERENCIA_MOBILE.

Há telas de ausência de conexão nos três fluxos. Elas orientam a recuperação do acesso; sua existência não comprova suporte para criar registros offline ou sincronização posterior. Verificar a conexão e utilizar a tentativa de retorno/reconexão disponível. Se uma ação não confirmar sucesso, não afirmar que foi registrada.

Uma lista vazia com filtros ativos significa que não há resultados para aquela combinação; não prova que a instituição não possui nenhum registro. Remover o texto da busca, restaurar Todos/Todas e limpar os seletores de autor, período, local, modelo ou status aplicáveis antes de concluir que não há dados. A Manu não tem acesso aos registros reais apenas por conhecer estes documentos.

## OPS-000 — Portas de entrada operacional do Gestor

Estado da informação: REFERENCIA_MOBILE.

Gestor: menu inferior Etapas → Quadros para OS; Etapas → Planejamento para escolher uma solicitação a planejar; menu inferior Equipamentos → Categorias/Modelos/Checklists. A lista de aparelhos para inspeção é alcançada pelos checklists.

As seções OS-001 a OS-007, EQP-001 a EQP-003, CHK-001 a CHK-003, INS-001 e INS-002 deste documento se aplicam ao Gestor. Atribuição de OS e administração de equipamentos/checklists pertencem a este perfil.

As permissões são de interface documentada, sem comprovar autorização do servidor sobre qualquer registro da instituição.

## OS-001 — Consultar e filtrar o quadro de OS

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Consultar e filtrar o quadro de OS.

Caminho no mobile: Etapas → Quadros → Gerencie os estados das OS.

Etapas:
1. Abra Quadros pelo painel de etapas.
2. Use Todas para consultar o conjunto de OS disponibilizadas no seu fluxo.
3. Toque em Não iniciadas, Em andam. ou Concluídas para visualizar o estado desejado.
4. Deslize a faixa de status se necessário e utilize a busca para reduzir os resultados.
5. Abra o card desejado. O caminho seguinte depende da OS: atribuição quando ainda sem responsável, execução das tarefas ou detalhe concluído.
6. Retorne ao quadro para trocar os filtros.

Resultado esperado no fluxo: Lista correspondente ao estado selecionado, ou mensagem de ausência de registros.

Regras e variações:
- São quatro opções: Todas, Não iniciadas, Em andam. e Concluídas. Não existe Recusadas neste quadro.
- Uma OS finalizada aparece em Concluídas e em Todas, deixando Em andam.
- Filtros só alteram a visualização, não o estado. O estado é determinado pela operação no registro.
- Cor e aparência do card não substituem o estado do registro.

Não presumir:
- Não foi formalizado o evento exato que inicia uma OS nem todo o ciclo de transições do servidor.
- Atribuído para e o prazo mostrado são informações da OS; não filtros de autoria.

Intenções equivalentes: kanban; ordens de serviço; OS concluídas; serviços em andamento.

## OS-002 — Criar uma nova OS

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Criar uma nova OS.

Caminho no mobile: Quadros → + → assistente de criação.

Etapas:
1. Abra o quadro do Gestor e toque no botão + para criar uma nova OS. Também é possível iniciar pelo Planejamento de uma solicitação.
2. Avance a apresentação do assistente.
3. Em Localização do Problema, escolha Competência e Prioridade nos seletores.
4. Toque em Próximo para ir à etapa Tarefas.
5. Na tela intitulada Crie os campos de inspeção deste assistente, decida se quer Criar a primeira tarefa automaticamente ou Criar eu mesmo.
6. Revise e complete as tarefas conforme OS-003.
7. Toque em Finalizar na etapa de tarefas. Confira o modal de confirmação da criação e confirme.
8. Na tela de sucesso, use o acesso ao quadro ou Voltar disponibilizado.

Campos e escolhas:
- Competência necessária para o serviço.
- Prioridade escolhida entre as opções do seletor.
- Tarefas: título e descrição.

Resultado esperado no fluxo: A nova OS é apresentada como criada no protótipo.

Voltar ou cancelar: Voltar permite revisar o rascunho; Cancelar no modal final retorna sem confirmar a criação.

Regras e variações:
- O + do quadro do Gestor cria OS; a criação pelo quadro também existe no perfil Técnico, sem redirecioná-lo para ocorrência.
- O modal da primeira tarefa aparece na etapa Tarefas, não na etapa de competência/prioridade.
- Criar gera a primeira tarefa de exemplo; Criar eu mesmo mantém apenas + Adicionar tarefa.
- A etapa final usa Finalizar e pede confirmação, em vez de Próximo.
- Iniciar outra OS limpa competência, prioridade e tarefas do novo rascunho. Não apaga o estado das OS anteriores.
- O título Crie os campos de inspeção é um rótulo remanescente neste assistente de OS. Aqui os itens são tarefas de OS; campos de checklist têm outro fluxo.

Não presumir:
- Os nomes e valores de prioridade no mock não estabelecem uma política institucional completa.
- Não foram definidos vínculo obrigatório com solicitação, campos adicionais de OS avulsa ou limite de tarefas em produção. O mock tem capacidade finita e não deve ser descrito como limite comercial.

Intenções equivalentes: abrir OS; criar ordem de serviço; nova ordem; competência e prioridade.

## OS-003 — Adicionar e editar tarefas durante o planejamento

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Adicionar e editar tarefas durante o planejamento.

Caminho no mobile: Assistente de OS → Tarefas → + Adicionar tarefa ou tarefa existente.

Etapas:
1. Na etapa Tarefas, escolha Criar eu mesmo se desejar iniciar sem tarefa automática, ou Criar para usar a primeira tarefa sugerida do protótipo.
2. Toque em + Adicionar tarefa.
3. Preencha Título da tarefa e Descrição.
4. Toque em Salvar para incluir o item; Cancelar fecha o formulário sem salvar.
5. Abra a opção de edição da tarefa já incluída para corrigir título e descrição e salve a mudança.
6. Revise a lista antes de usar Finalizar e confirmar a criação da OS.

Resultado esperado no fluxo: Lista de tarefas do rascunho atualizada.

Não presumir:
- Não há procedimento separado e comprovado de excluir tarefa de planejamento ou alterar tarefas de uma OS já encerrada.
- O protótipo não comprova geração autônoma por IA da tarefa sugerida.

Intenções equivalentes: adicionar tarefa; editar tarefa planejada; primeira tarefa automática.

## OS-004 — Atribuir responsável e prazo à OS

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Atribuir responsável e prazo à OS.

Caminho no mobile: Gestor → Quadros → OS sem responsável → Atribuir OS.

Etapas:
1. Abra no quadro uma OS disponível para atribuição.
2. Na etapa Escolher o responsável, consulte os candidatos exibidos e suas informações, como competências e tarefas em andamento.
3. Selecione o responsável e toque em Próximo.
4. Na etapa Escolher o prazo de entrega, navegue no calendário e escolha a data.
5. Toque em Finalizar.
6. No modal Confirmar os dados da atribuição de OS, confira Responsável e Prazo.
7. Toque em Confirmar para concluir ou Cancelar para revisar.
8. Consulte a confirmação de sucesso e retorne ao fluxo.

Resultado esperado no fluxo: A atribuição de responsável e prazo é confirmada na demonstração.

Regras e variações:
- Selecionar um nome ou uma data ainda não é a confirmação final.
- O exemplo inclui candidatos com função Técnico e Gestor; não afirmar que só nomes com a função Técnico podem aparecer pela legenda da tela.
- O marcador Recomendado informa uma sugestão visual; critérios e algoritmo não estão formalizados.

Não presumir:
- Não foram definidos notificações ao responsável, reatribuição, aceite do técnico, limite de carga, feriados, SLA ou regra de prazo mínimo.

Intenções equivalentes: designar técnico; atribuir ordem; prazo de entrega; responsável pela OS.

## OS-005 — Realizar, concluir e desfazer uma tarefa

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Realizar, concluir e desfazer uma tarefa.

Caminho no mobile: Quadros → OS em execução → Tarefas a fazer → tarefa.

Etapas:
1. Abra a OS em execução no quadro.
2. Confira o resumo da demanda e a lista de tarefas.
3. Abra uma tarefa e leia título, descrição e status no modal Informações da tarefa.
4. Após executar o serviço, use o comando de concluir a tarefa.
5. Para desfazer, abra a mesma tarefa concluída e selecione Desfazer tarefa.
6. Retorne à lista e confira a alteração do estado daquela tarefa.

Resultado esperado no fluxo: A tarefa selecionada alterna entre pendente e concluída no fluxo demonstrado.

Regras e variações:
- Desfazer funciona inclusive para tarefa que já estava concluída ao entrar na tela, sem exigir concluí-la antes outra vez.
- Uma tarefa concluída não finaliza automaticamente a OS inteira.
- Alterar uma tarefa não deve alterar as tarefas de outra OS.
- Voltar no modal apenas fecha a consulta, sem trocar o status.

Não presumir:
- Não há regra formalizada de reabrir OS já finalizada, auditoria, autoria da conclusão ou sincronização entre usuários.

Intenções equivalentes: marcar tarefa feita; desfazer conclusão; tarefa já concluída.

## OS-006 — Finalizar a OS após realizar suas tarefas

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Finalizar a OS após realizar suas tarefas.

Caminho no mobile: Realizar as tarefas da OS → Finalizar → Confirmar.

Pré-condições: OS disponível para execução, com todas as tarefas concluídas para liberar a finalização.

Etapas:
1. Abra a OS que está realizando.
2. Conclua todas as tarefas e confira seus estados.
3. Toque em Finalizar no rodapé quando a ação estiver disponível.
4. Confira o modal de confirmação e confirme a finalização; cancele se ainda precisar revisar.
5. Na tela de sucesso, retorne ao quadro e consulte Concluídas.

Resultado esperado no fluxo: A OS é marcada como finalizada no protótipo, aparece em Concluídas/Todas e sai de Em andam.

Regras e variações:
- Desfazer uma tarefa antes de finalizar torna a lista incompleta e impede a finalização até concluí-la novamente.
- O botão Cancelar da execução não equivale a excluir a OS.
- Abrir a criação de uma nova OS não deve apagar a conclusão desta.

Não presumir:
- Não há evidência de atualização automática da solicitação vinculada, criação automática de ocorrência ou reabertura de OS finalizada.

Intenções equivalentes: encerrar OS; concluir ordem de serviço.

## OS-007 — Consultar uma OS concluída

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Consultar uma OS concluída.

Caminho no mobile: Quadros → Concluídas → card.

Etapas:
1. Selecione Concluídas no quadro.
2. Abra a OS desejada.
3. Consulte os detalhes apresentados e volte ao quadro.

Resultado esperado no fluxo: Consulta da OS finalizada, sem reiniciar sua execução.

Não presumir:
- Não há ação documentada de excluir, recusar ou reabrir esta OS pelo detalhe concluído.

Intenções equivalentes: histórico de OS; ver ordem finalizada.

## EQP-001 — Criar, editar e excluir categoria de equipamentos

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Criar, editar e excluir categoria de equipamentos.

Caminho no mobile: Gestor → Equipamentos → Categorias.

Etapas:
1. Abra Gerenciamento de equipamentos e selecione Categorias.
2. Use + para abrir Criar categoria; informe o nome e salve.
3. Para corrigir uma categoria, abra os três pontos do item e selecione Editar; ajuste o nome e salve.
4. Para excluir, abra os três pontos, selecione Excluir e confirme no modal.
5. Use Cancelar nos formulários ou na confirmação para não efetivar a ação.

Campos e escolhas:
- Nome da categoria.

Resultado esperado no fluxo: Operações de categoria representadas no protótipo.

Não presumir:
- Unicidade do nome, hierarquia de categorias e efeitos da exclusão sobre modelos/aparelhos não foram especificados. Não prometer exclusão em cascata.

Intenções equivalentes: cadastrar categoria; mudar categoria; remover categoria.

## EQP-002 — Criar, pesquisar, editar e excluir modelos

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Criar, pesquisar, editar e excluir modelos.

Caminho no mobile: Gestor → Equipamentos → Modelos.

Etapas:
1. Selecione Modelos no gerenciamento de equipamentos.
2. Use a pesquisa quando disponível para localizar um modelo.
3. Toque em + para criar: informe o nome, selecione a categoria e preencha a marca.
4. Salve o modelo ou cancele a criação.
5. Use os três pontos do modelo para Editar os campos e salvar ou Excluir e confirmar.
6. Abra o card do modelo para consultar seus aparelhos.

Campos e escolhas:
- Nome do modelo; categoria; marca.

Resultado esperado no fluxo: Consulta/manutenção dos modelos na demonstração.

Não presumir:
- Categoria inexistente deve ser tratada no fluxo de categorias; não há criação automática pelo seletor confirmada.
- Unicidade, importação, anexos e comportamento de exclusão com aparelhos/checklists vinculados não foram definidos.

Intenções equivalentes: cadastrar modelo; marca do equipamento.

## EQP-003 — Criar, editar e excluir aparelhos

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Criar, editar e excluir aparelhos.

Caminho no mobile: Gestor → Equipamentos → Modelos → modelo → Aparelhos.

Etapas:
1. Abra o modelo e consulte sua lista de aparelhos.
2. Toque em + para Criar aparelho.
3. No campo Nome, informe o identificador conforme a orientação Coloque o identificador; selecione o Local.
4. Toque em Salvar ou Cancelar.
5. Para alterar um aparelho, abra os três pontos e use Editar; ajuste os campos e salve.
6. Para remover, escolha Excluir e confirme após conferir o aparelho.

Campos e escolhas:
- Nome/identificador do aparelho.
- Local.

Resultado esperado no fluxo: Cadastro ou alteração da unidade física no modelo escolhido.

Não presumir:
- Não há QR Code, patrimônio integrado, leitura automática, inventário em tempo real ou regras de dependência da exclusão confirmados.

Intenções equivalentes: cadastrar aparelho; identificador do equipamento; local do aparelho.

## CHK-001 — Consultar, filtrar e excluir definições de checklists

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Consultar, filtrar e excluir definições de checklists.

Caminho no mobile: Gestor → Equipamentos → Checklists.

Etapas:
1. Abra Checklists pelo gerenciamento de equipamentos.
2. Consulte nome, periodicidade, modelos abrangidos e estado apresentado nos cards.
3. Use Status para filtrar as definições e restaure a opção sem restrição para ver novamente o conjunto.
4. Para excluir uma definição, use seu menu de opções e confirme Excluir checklist; cancele se não desejar prosseguir.
5. Abra um checklist para seguir à relação de aparelhos inspecionáveis ou use + para criar uma definição.

Resultado esperado no fluxo: Consulta e navegação das definições; caminho de exclusão representado.

Não presumir:
- O estado do checklist não é o mesmo que o estado da inspeção de cada aparelho.
- Não foi comprovado fluxo completo de editar uma definição já salva nem efeito de exclusão sobre inspeções históricas.

Intenções equivalentes: lista de checklists; periodicidade; remover checklist.

## CHK-002 — Criar uma definição de checklist

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Criar uma definição de checklist.

Caminho no mobile: Gestor → Equipamentos → Checklists → +.

Etapas:
1. Toque em + e avance a introdução da criação de checklist.
2. Em Informações da checklist, informe Nome, Periodicidade em dias e Data de primeira abertura.
3. Toque em Próximo para definir os campos da inspeção.
4. Use + Adicionar campo e configure as perguntas conforme CHK-003.
5. Avance para Modelos.
6. Use a busca para localizar modelos e marque os que serão abrangidos pelo checklist.
7. Toque em Finalizar e consulte a confirmação de sucesso. A tela oferece Ir para a Home e Criar nova checklist.

Campos e escolhas:
- Nome.
- Periodicidade em dias.
- Data de primeira abertura.
- Campos de verificação.
- Modelos selecionados.

Resultado esperado no fluxo: Definição do checklist criada no fluxo demonstrado.

Voltar ou cancelar: Voltar permite revisar as etapas anteriores.

Não presumir:
- Não foram formalizados fuso/horário de abertura, regra de recorrência em dias não úteis, atraso, notificações ou cálculo automático de próximas ocorrências.
- Selecionar modelos não comprova que o sistema permita adicionar aparelhos diretamente nessa etapa.

Intenções equivalentes: novo checklist; criar inspeção periódica; agendar checklist.

## CHK-003 — Configurar campos e alternativas de checklist

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Configurar campos e alternativas de checklist.

Caminho no mobile: Criação de checklist → Campos → + Adicionar campo/editar.

Etapas:
1. Adicione um campo e informe o enunciado/nome disponibilizado.
2. Escolha o tipo: Sim ou Não, Texto, Número, Múltipla Escolha/Várias Opções ou Avaliação.
3. Ative ou desative o controle Obrigatório conforme a necessidade da pergunta.
4. No tipo de múltipla escolha, adicione as alternativas pelo comando de nova opção e salve cada texto.
5. Abra a edição de uma alternativa para corrigir seu conteúdo quando necessário.
6. Salve o campo; para ajustar um campo da lista, abra sua edição e salve novamente.
7. Cancele o formulário para voltar sem confirmar aquela edição.

Resultado esperado no fluxo: Conjunto de perguntas configuradas no rascunho de checklist.

Regras e variações:
- Campos de checklist são respostas de inspeção; não são tarefas da OS.
- Obrigatório é uma propriedade do campo, distinta do tipo de resposta.

Não presumir:
- Não foram definidos limites de opções, múltipla seleção versus resposta única em todos os casos, validações de número/texto ou escala de avaliação.
- Não foram comprovados anexos por pergunta, condições entre campos ou fórmulas.

Intenções equivalentes: campo obrigatório; pergunta de inspeção; alternativas de checklist.

## INS-001 — Escolher checklist e filtrar aparelhos para inspecionar

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Escolher checklist e filtrar aparelhos para inspecionar.

Caminho no mobile do Gestor: Equipamentos → Checklists → checklist → Aparelhos para inspeção.

Etapas:
1. Abra a lista de checklists pelo acesso do seu perfil.
2. Use o filtro Status da lista quando necessário e escolha o checklist.
3. Na tela Inspecione os aparelhos, abra Modelo para limitar a lista ao modelo desejado.
4. Use Status para escolher Todos os status, Inspeção pendente ou Inspeção realizada.
5. Abra o aparelho desejado para consultar/preencher sua inspeção.
6. Se não houver resultados, remova os filtros antes de concluir que não existem aparelhos.

Resultado esperado no fluxo: Lista dos aparelhos correspondentes ao checklist, modelo e estado escolhidos.

Regras e variações:
- Os estados pendente/realizada dizem respeito à inspeção do aparelho.
- Modelo institucional A/B e AP001/AP002 são exemplos; não nomes obrigatórios para criar registros.

Não presumir:
- Um + ou outro controle residual nesta lista não define administração de aparelhos para o Técnico; o caminho de cadastro documentado pertence ao Gestor.
- Não foram definidos filtros avançados por unidade, histórico de ciclos ou reabertura de inspeção realizada.

Intenções equivalentes: inspeções pendentes; aparelhos inspecionados; filtrar modelo.

## INS-002 — Preencher e enviar uma inspeção

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Preencher e enviar uma inspeção.

Caminho no mobile: Checklists → Aparelhos → aparelho → Inspeção.

Etapas:
1. Abra o aparelho da lista e confira seu identificador, modelo e checklist.
2. Preencha os campos apresentados para a inspeção. Na demonstração há observações opcionais, avaliação, Precisa de manutenção? e itens verificados.
3. Responda Sim ou Não sobre necessidade de manutenção de acordo com o que foi observado.
4. Marque/responda os itens verificados e confira as perguntas obrigatórias do checklist.
5. Toque em Enviar.
6. Confira o modal e confirme o envio; cancele para revisar.
7. Consulte a confirmação de sucesso e retorne ao fluxo.

Campos e escolhas:
- Observações: opcional na tela demonstrada.
- Avaliação.
- Precisa de manutenção?: Sim/Não.
- Itens e perguntas definidos pelo checklist; respeitar o tipo de resposta e a propriedade Obrigatório.

Resultado esperado no fluxo: Inspeção enviada no protótipo e representada como realizada no fluxo.

Voltar ou cancelar: Cancelar/Voltar sai do preenchimento; não afirmar que um rascunho foi salvo automaticamente.

Regras e variações:
- Liga normalmente, Sem vazamentos, Sem ruídos e Filtros limpos são os exemplos apresentados; outros checklists podem definir outras perguntas.
- Só confirmar o envio depois de efetuar as verificações cabíveis.

Não presumir:
- Assinalar necessidade de manutenção não comprova criação automática de solicitação, OS ou ocorrência.
- Não foram definidos edição após envio, assinatura, geolocalização, evidência obrigatória ou guarda histórica.

Intenções equivalentes: realizar inspeção; enviar checklist; aparelho precisa de manutenção.
