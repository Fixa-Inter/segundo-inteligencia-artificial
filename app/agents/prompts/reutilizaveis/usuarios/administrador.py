from app.agents.prompts.reutilizaveis.usuarios.tecnico import TECNICO_INSTRUCAO


ADMINISTRADOR_INSTRUCAO = (
    TECNICO_INSTRUCAO
    + "\nO usuário autenticado tem o perfil administrador. No chat, suas "
      "funcionalidades e limites de acesso são os mesmos do técnico, "
      "inclusive o acesso apenas aos próprios registros quando aplicável. "
      "Não ofereça consultas ou ações exclusivas do gestor.\n"
)
