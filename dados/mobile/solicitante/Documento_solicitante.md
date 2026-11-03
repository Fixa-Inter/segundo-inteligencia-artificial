---
document_id: "SOL"
title: "Solicitante — funcionalidades, acessos e procedimentos mobile"
roles: ["solicitante"]
status: "REFERENCIA_MOBILE"
audience: "usuario_mobile"
responsibility: "Orientar o Solicitante sobre suas solicitações, navegação, acesso, conta, notificações, eventos e ajuda no mobile. Os procedimentos compartilhados aplicáveis estão integralmente neste documento."
version: "1.1.0"
updated_at: "2026-11-02"
channel: "mobile"
language: "pt-BR"
validation_scope: "Telas e conexões do Figma; declarações do responsável pelo projeto. Não é auditoria da aplicação em produção."
---

# Solicitante — funcionalidades, acessos e procedimentos

Responsabilidade deste documento: Orientar o Solicitante sobre suas solicitações, navegação, acesso, conta, notificações, eventos e ajuda no mobile. Os procedimentos compartilhados aplicáveis estão integralmente neste documento.

## SOL-001 — Papel, acesso e limites

Estado da informação: REFERENCIA_MOBILE.

O Solicitante registra problemas de manutenção, consulta suas solicitações e acompanha a situação de cada uma. Pode abrir detalhes, usar busca/filtros e as opções de edição/exclusão disponibilizadas no próprio fluxo. Também acessa a Home, eventos, Manu, perfil, configurações e FAQ.

Não há acesso confirmado do Solicitante a analisar/aprovar/recusar solicitações, planejar ou atribuir OS, executar tarefas de OS, registrar ocorrências técnicas, inspecionar aparelhos, administrar equipe, editar competências, gerenciar equipamentos ou criar checklists. Ele não deve ser orientado a usar os menus do Gestor ou do Técnico para essas ações.

O escopo das solicitações é o apresentado como Minhas solicitações. O protótipo não é uma especificação de autorização do servidor: a exposição de um exemplo não concede direito sobre os dados de outra pessoa. Os procedimentos de acesso, conta, eventos e FAQ estão nas seções COM-002 a COM-011 deste documento; as seções MAN-001 a MAN-004 citadas para conversa com a assistente não constam no material recebido, portanto não presumir seus procedimentos.

## SOL-002 — Usar a Home e a navegação do Solicitante

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Usar a Home e a navegação do Solicitante.

Caminho no mobile: Home → cards/atalhos ou menu inferior.

Etapas:
1. Consulte o resumo e a área Minhas solicitações na Home.
2. Role o conteúdo vertical para visualizar os cards completos abaixo da primeira área visível.
3. Abra um card para consultar aquela solicitação ou use o acesso à lista/registro disponível.
4. Use as quatro abas inferiores, na ordem Home, Minhas solicitações, Eventos e Manu. A segunda aba abre a lista completa; a terceira usa o calendário para Eventos e a quarta abre a assistente.
5. Abra o avatar para as opções da conta.

Regras e variações:
- Minhas solicitações é um título informativo; tocar no texto não executa uma ação.
- Indicadores e gráficos da Home são de visualização. O destino da navegação é determinado pelo card, botão ou ícone apropriado.

Não presumir:
- Não transportar o menu de cinco abas do Gestor para este perfil.

## SOL-003 — Registrar uma solicitação de manutenção

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Registrar uma solicitação de manutenção.

Caminho no mobile: Home/lista de solicitações → +/novo registro → Descrição → Local → Fotos → Confirmar.

Etapas:
1. Acione o registro de nova solicitação e avance a apresentação do fluxo.
2. Em Descreva o seu Problema, informe Título e Descrição. Use uma descrição objetiva do que apresenta defeito.
3. Toque em Próximo. Selecione o Local e detalhe a localização no campo Descrição do local.
4. Avance para Fotos. Escolha o Aparelho com problema no seletor.
5. Adicione a evidência pela área Fazer upload de imagens ou por Tirar foto. Confira a imagem na área de prévia.
6. Avance para Confirmar informações e confira os dados apresentados.
7. Toque em Finalizar para confirmar o registro.
8. Na confirmação de sucesso, retorne à Home ou use Registrar novo para iniciar outra solicitação.

Campos e escolhas:
- Título; descrição do problema.
- Local escolhido na lista e descrição complementar do local.
- Aparelho escolhido no seletor.
- Foto/evidência visual.

Resultado esperado no fluxo: A solicitação é apresentada como registrada no protótipo, com acesso ao acompanhamento.

Voltar ou cancelar: Use Voltar para revisar a etapa anterior antes da confirmação.

Regras e variações:
- Novo registro deve iniciar limpo, sem reaproveitar título, descrição, local, aparelho ou imagem da solicitação anterior.
- A foto mockada aparece na área de imagem, sem sobrepor o texto ao ícone de câmera.
- A abertura de solicitação não garante aprovação nem define, por si só, prazo de execução.

Não presumir:
- Tamanho/quantidade/tipos permitidos de anexos e obrigatoriedade de cada campo não foram formalizados como validação de produção.
- Não há campo confirmado para o Solicitante definir a prioridade da OS; prioridade da OS pertence ao planejamento.

Intenções equivalentes: abrir chamado; informar problema; criar solicitação; registrar problema.

## SOL-004 — Buscar e filtrar minhas solicitações

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Buscar e filtrar minhas solicitações.

Caminho no mobile: Lista Minhas solicitações → busca, status e filtros.

Etapas:
1. Abra a lista de solicitações pelo acesso disponível na Home.
2. Use a busca para localizar o registro pelo texto.
3. Selecione Todas, Em análise, Aprovadas, Concluídas ou Recusadas para limitar a lista.
4. Deslize a faixa de status horizontalmente para alcançar os demais filtros.
5. Abra os filtros adicionais e selecione período e/ou local; aplique a escolha.
6. Para ampliar os resultados, limpe a busca e restaure Todas e os filtros sem restrição.

Resultado esperado no fluxo: A combinação de filtros determina os cards exibidos; nenhuma correspondência apresenta estado vazio.

Regras e variações:
- As opções são filtros de visualização; não mudam o status de uma solicitação.
- Uma solicitação excluída não deve reaparecer ao trocar o filtro.

Não presumir:
- As opções de período/local mostradas na demonstração não fixam todos os valores possíveis da aplicação.

Intenções equivalentes: não encontro minha solicitação; filtrar solicitações; solicitações recusadas.

## SOL-005 — Consultar detalhes e estado atual da solicitação

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Consultar detalhes e estado atual da solicitação.

Caminho no mobile: Minhas solicitações → card → Estado atual.

Etapas:
1. Abra o card da solicitação que deseja acompanhar.
2. Consulte as informações do problema, local, evidências e dados apresentados.
3. Confira a linha de progresso/estado correspondente à situação do registro.
4. Use Voltar para retornar à lista.

Resultado esperado no fluxo: Detalhe coerente com a solicitação selecionada: em análise, aprovada, concluída ou recusada.

Regras e variações:
- Concluída apresenta a progressão completa; recusada apresenta o estado de recusa, e não uma progressão de serviço concluído.
- O acompanhamento não é uma autorização para o Solicitante alterar etapas de execução da OS.

Não presumir:
- Não foram especificadas datas reais de cada transição, prazo de resposta, mecanismo de recurso ou reabertura automática.

Intenções equivalentes: acompanhar chamado; barra de progresso; estado atual.

## SOL-006 — Editar uma solicitação

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Editar uma solicitação.

Caminho no mobile: Card da solicitação → três pontos → Editar.

Etapas:
1. Localize a solicitação que deseja corrigir.
2. Toque nos três pontos do card para abrir o menu de opções ancorado ao acionador.
3. Selecione Editar e ajuste os campos disponibilizados no formulário.
4. Salve e confirme a edição no pedido de confirmação.
5. Retorne à lista e confira o registro alterado.

Resultado esperado no fluxo: O fluxo confirma a edição da solicitação selecionada.

Voltar ou cancelar: Cancelar/Voltar abandona a confirmação.

Não presumir:
- Não foram formalizadas restrições por status, propriedade de anexos, histórico de versões ou quais mudanças seriam permitidas depois de iniciada uma OS.
- Se a aplicação não disponibilizar Editar para o registro, não orientar a contornar a restrição.

Intenções equivalentes: corrigir chamado; alterar solicitação.

## SOL-007 — Excluir uma solicitação selecionada

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Excluir uma solicitação selecionada.

Caminho no mobile: Card → três pontos → Excluir → Motivo → Confirmação.

Etapas:
1. Localize o card correto e abra seus três pontos.
2. Selecione Excluir.
3. Preencha o motivo no modal se solicitado pela tela e prossiga.
4. Confirme a exclusão somente após conferir o registro.
5. Verifique o retorno à lista sem aquele card. Trocar o filtro não deve trazê-lo de volta.

Resultado esperado no fluxo: O protótipo remove o registro selecionado da lista, preservando os demais.

Voltar ou cancelar: Cancelar encerra o pedido sem excluir.

Não presumir:
- Exclusão lógica/física, retenção, restauração e restrições por status não foram definidas. Não prometer recuperação posterior.

Intenções equivalentes: apagar solicitação; deletar chamado.

## SOL-008 — Regras específicas e cuidado no relato

Estado da informação: REGRAS_CONFIRMADAS_E_ORIENTACOES_PROPOSTAS.

Regras confirmadas: relatar pelo fluxo de solicitação; acompanhar o registro selecionado; os comandos de analisar e executar pertencem a outros perfis. A edição e a exclusão devem atingir o card escolhido, e um novo registro não deve herdar o rascunho anterior.

Orientações propostas de uso responsável, sujeitas à aprovação da política: informar o que foi observado, descrever o local com clareza, anexar evidência pertinente, evitar dados pessoais desnecessários e não registrar conteúdo ofensivo ou falso. O aplicativo organiza a demanda; não substitui a comunicação imediata à equipe responsável diante de um risco presente. Estas recomendações não definem prazo institucional de atendimento ou punições.

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

## COM-013 — Conexão e ausência de dados

Estado da informação: REFERENCIA_MOBILE.

Há telas de ausência de conexão nos três fluxos. Elas orientam a recuperação do acesso; sua existência não comprova suporte para criar registros offline ou sincronização posterior. Verificar a conexão e utilizar a tentativa de retorno/reconexão disponível. Se uma ação não confirmar sucesso, não afirmar que foi registrada.

Uma lista vazia com filtros ativos significa que não há resultados para aquela combinação; não prova que a instituição não possui nenhum registro. Remover o texto da busca, restaurar Todos/Todas e limpar os seletores de autor, período, local, modelo ou status aplicáveis antes de concluir que não há dados. A Manu não tem acesso aos registros reais apenas por conhecer estes documentos.
