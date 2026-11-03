---
document_id: "TEC"
title: "Técnico — funcionalidades, acessos e procedimentos mobile"
roles: ["tecnico"]
status: "REFERENCIA_MOBILE"
audience: "usuario_mobile"
responsibility: "Orientar o Técnico sobre navegação, acesso, conta, ocorrências, criação e execução de OS, tarefas, inspeções, eventos, exportação e ajuda no mobile. Os procedimentos compartilhados aplicáveis estão integralmente neste documento."
version: "1.1.0"
updated_at: "2026-11-02"
channel: "mobile"
language: "pt-BR"
validation_scope: "Telas e conexões do Figma; declarações do responsável pelo projeto. Não é auditoria da aplicação em produção."
---

# Técnico — funcionalidades, acessos e procedimentos

Responsabilidade deste documento: Orientar o Técnico sobre navegação, acesso, conta, ocorrências, criação e execução de OS, tarefas, inspeções, eventos, exportação e ajuda no mobile. Os procedimentos compartilhados aplicáveis estão integralmente neste documento.

## TEC-001 — Papel, menu e limites

Estado da informação: REFERENCIA_MOBILE.

O Técnico acessa Home, Gerencie todas as etapas (Quadros e Ocorrências), Manu, Inspeções e Eventos nas cinco abas do menu inferior. A posição central abre a Manu, e não a equipe. Avatar/perfil oferece dados pessoais, configurações, FAQ, Sobre o app, Exportar excel, Manu e Sair.

Pode consultar o quadro de OS, filtrar estados, abrir detalhes, criar uma nova OS pelo botão +, realizar tarefas, desfazer a conclusão de uma tarefa no fluxo disponível e finalizar uma OS após concluir suas tarefas. Pode registrar e consultar ocorrências e acessar as opções de edição/exclusão apresentadas nesse fluxo. Pode selecionar checklists e inspecionar aparelhos.

Não há acesso confirmado do Técnico ao painel de equipe, edição de competências, análise/aprovação/recusa de solicitações, atribuição de responsável e prazo pelo fluxo do Gestor ou administração de categorias/modelos/aparelhos e criação de checklists. Exportar excel não concede acesso global aos dados de outros usuários.

Regras de propriedade e autorização de cada registro devem ser aplicadas pela aplicação. Os nomes exibidos nos cards são exemplos; não demonstram que um Técnico real possa editar ou executar qualquer OS da instituição.

## TEC-002 — Abrir as áreas de trabalho do Técnico

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Abrir as áreas de trabalho do Técnico.

Caminho no mobile: Home → menu inferior → Gerencie todas as etapas.

Etapas:
1. Use Home para consultar o resumo e os cards do seu fluxo.
2. Na aba de etapas, escolha Quadros para acessar Gerencie os estados das OS ou Ocorrências para consultar os serviços registrados.
3. Use a aba central para a Manu, a aba de inspeções para os checklists e o calendário para Eventos.
4. Em telas com menu inferior, toque no ícone da área desejada para navegar diretamente.

Regras e variações:
- Os destinos devem permanecer dentro do perfil Técnico; não usar o ícone central para Gerencie equipe.
- Gráficos e títulos da Home são informativos.

## TEC-003 — Procedimentos de OS e inspeção aplicáveis ao Técnico

Estado da informação: REFERENCIA_MOBILE.

Usar OS-001 para consultar e filtrar o quadro; OS-002 para criar OS do zero; OS-003 para tarefas do planejamento; OS-005 para concluir/desfazer tarefas; OS-006 para finalizar a OS e OS-007 para abrir detalhes de uma OS concluída. A atribuição OS-004 pertence somente ao Gestor.

Inspeções: INS-001 abre checklists e filtra aparelhos; INS-002 preenche e envia a inspeção. Criar/editar definições de checklists e administrar equipamentos são caminhos do Gestor, não do Técnico.

Conta/acesso/eventos/FAQ: COM-002 a COM-011 deste documento. Exportação: COM-012 deste documento. As seções MAN-001 a MAN-004 citadas para Manu e histórico não constam no material recebido; não presumir procedimentos que não estão descritos.

## TEC-004 — Consultar e filtrar ocorrências

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Consultar e filtrar ocorrências.

Caminho no mobile: Etapas → Ocorrências.

Etapas:
1. Na aba Gerencie todas as etapas, abra Ocorrências.
2. Use Período para escolher a faixa disponível e aplicar o filtro.
3. Abra o card desejado para visualizar o serviço, os dados e as evidências.
4. Use Voltar no detalhe para retornar à lista; restaure o período sem restrição para ampliar os resultados.

Resultado esperado no fluxo: Consulta da ocorrência selecionada; lista sem correspondências apresenta estado vazio.

Regras e variações:
- O detalhe é uma tela de visualização, com Voltar; não reutiliza o botão Registrar de uma criação.

Não presumir:
- Não há filtro Autor confirmado na lista do Técnico; ele aparece no Gestor.

Intenções equivalentes: ver ocorrências; histórico de serviço.

## TEC-005 — Registrar uma ocorrência de serviço

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Registrar uma ocorrência de serviço.

Caminho no mobile: Etapas → Ocorrências → + → Descrição → Local e data → Resultado → Confirmar.

Etapas:
1. Abra Ocorrências e toque no botão +.
2. Avance a apresentação do registro.
3. Preencha Título e Problema encontrado.
4. Em Local e data, escolha o local e informe a data do serviço.
5. Em Resultado do Serviço, selecione o grau de dificuldade e descreva a solução aplicada.
6. Se necessário, relate Dificuldades encontradas no campo opcional e adicione fotos.
7. Avance para Confirmar informações e revise o resumo.
8. Toque em Registrar. Na confirmação de sucesso, retorne ao fluxo disponível ou inicie outro registro.

Campos e escolhas:
- Título e problema encontrado.
- Local e data.
- Grau de dificuldade: fácil, médio ou difícil.
- Solução aplicada.
- Dificuldades encontradas: opcional.
- Fotos do serviço.

Resultado esperado no fluxo: Ocorrência registrada no fluxo demonstrado, para consulta posterior.

Voltar ou cancelar: Voltar permite revisar etapas antes de Registrar.

Regras e variações:
- Ocorrência descreve o serviço realizado; não é um pedido de aprovação ao Gestor.
- Nova criação deve começar como um novo rascunho.

Não presumir:
- Não foram definidos quantidade/tamanho dos anexos, backdating permitido, obrigatoriedade de todos os campos ou vinculação automática à OS.

Intenções equivalentes: registrar serviço; relatar conserto; criar ocorrência.

## TEC-006 — Editar uma ocorrência pelo menu disponível

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Editar uma ocorrência pelo menu disponível.

Caminho no mobile: Ocorrências → três pontos do card → Editar.

Etapas:
1. Abra o menu de três pontos do registro correto.
2. Selecione Editar.
3. Ajuste os campos que o formulário disponibiliza.
4. Salve e confirme a alteração; cancele para voltar sem confirmá-la.

Resultado esperado no fluxo: O protótipo apresenta a confirmação de edição.

Não presumir:
- O modal de edição preserva campos de uma versão anterior (título, descrição, local, fotos e equipamento), enquanto a criação atual usa problema, data e resultado do serviço. Não há mapeamento de todos esses campos confirmado.
- Regras de propriedade, status editável, escopo entre técnicos e persistência real da alteração não foram formalizadas; não afirmar autorização global.

Intenções equivalentes: corrigir ocorrência.

## TEC-007 — Excluir uma ocorrência pelo menu disponível

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Excluir uma ocorrência pelo menu disponível.

Caminho no mobile: Ocorrências → três pontos do card → Excluir → Motivo → Confirmar.

Etapas:
1. Abra os três pontos do card da ocorrência escolhida.
2. Toque em Excluir e informe o motivo se solicitado.
3. Confira o pedido final e confirme ou cancele a exclusão.

Resultado esperado no fluxo: Caminho de exclusão representado no protótipo.

Não presumir:
- Não foram formalizados escopo por autoria, retenção, restauração ou persistência da exclusão em produção.
- O fluxo não autoriza excluir ocorrências de outros técnicos; seguir apenas ações e registros autorizados na aplicação.

Intenções equivalentes: apagar ocorrência.

## TEC-008 — Regras específicas e cuidado na execução

Estado da informação: REGRAS_CONFIRMADAS_E_ORIENTACOES_PROPOSTAS.

Regras confirmadas do fluxo: manter tarefa e OS como estados distintos; uma tarefa concluída pode ser desfeita pelo comando correspondente, inclusive se já estava concluída ao abrir; finalizar a OS exige a confirmação final após todas as tarefas estarem concluídas; uma OS finalizada deixa o filtro Em andam. e permanece em Concluídas e Todas. A nova criação de OS não pode herdar dados da anterior.

Orientações propostas de uso responsável: registrar o resultado real do serviço, descrever impedimentos com clareza, anexar evidências pertinentes e não marcar como concluído algo ainda não realizado. As informações da Manu sobre navegação não substituem qualificação profissional nem procedimentos de segurança da instituição. Não foram fornecidos procedimentos técnicos de reparo ou autorização para intervir em equipamento de risco.

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

## OPS-000 — Portas de entrada operacional do Técnico

Estado da informação: REFERENCIA_MOBILE.

Técnico: menu inferior Etapas → Quadros para OS; menu inferior Inspeções → Checklists → Aparelhos para inspeção. Não existe o painel de equipe ou o gerenciamento de categorias e modelos no seu fluxo.

As seções OS-001, OS-002, OS-003, OS-005, OS-006, OS-007, INS-001 e INS-002 deste documento se aplicam ao Técnico. Atribuir responsável/prazo (OS-004), administrar equipamentos (EQP-001 a EQP-003) e administrar definições de checklists (CHK-001 a CHK-003) pertencem ao Gestor e não são procedimentos disponíveis ao Técnico.

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
5. Abra o card desejado para executar as tarefas da OS disponibilizada ao Técnico ou consultar o detalhe de uma OS concluída. Atribuir responsável e prazo é uma ação do Gestor e não integra este procedimento do Técnico.
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
1. Abra o quadro do Técnico e toque no botão + para criar uma nova OS. O planejamento a partir da análise de uma solicitação pertence ao Gestor e não é um caminho deste perfil.
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
- O + do quadro do Técnico cria OS; não redireciona para ocorrência.
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

## INS-001 — Escolher checklist e filtrar aparelhos para inspecionar

Estado da informação: REFERENCIA_MOBILE.

Objetivo: Escolher checklist e filtrar aparelhos para inspecionar.

Caminho no mobile do Técnico: Inspeções → Checklists → checklist → Aparelhos para inspeção.

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
