GLOSSARIO_PROMPT = """
## Glossário de termos importantes

- solicitação: pedido do usuário solicitante para concertar algo da instituição;
- problema: primeiro estágio da solicitação quando o pedido chega ao gestor;
- ocorrência: problema resolvido pelo técnico e registrado dentro do aplicativo para fins de auditoria;
- ordem de serviço: aprovação do problema registrado pelo usuário solicitante, ou seja, o problema é criado e quando aprovado, vira uma ordem de serviço;
- tarefa: ações que devem ser feitas para resolver a ordem de serviço;
- manutenção: efetivação da ação especificada na tarefa;
- equipamento: itens dentro da instituição, como ar condicionado, escada rolante, cadeira, entre outras;
- modelo de equipamento: Modelo de equipamento específico que contem marca, categoria (ar condicionado, escada rolante, cadeira, entre outras), quantidade e equipamentos cadastrados e checklist anexada. Junta as características comuns que um equipamento da instituição tem, a fim de melhorar as análises de checklist e organização interna do app.
- checklist: template padrão para revisão de um modelo de equipamento;
- prioridade: temos 3 níveis de prioridade diferentes - P0 (urgênte), P1 (médio), P2 (baixo);
"""