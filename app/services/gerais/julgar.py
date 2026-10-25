"""Classificação fechada pelo JEV usada pelo endpoint de problemas."""

from app.core.configuracao import LIMIAR
from app.services.gerais.jev import ErroJEV, consultar_jev, ler_choice, ler_noul


FRASE_SEGURA = "Não tenho evidência para afirmar isso."


def _publicar(texto: str, agente: str, rotulo: str) -> dict:
    return {
        "messages": [{"role": "assistant", "content": texto.strip()}],
        "agentes_chamados": [f"{agente}:{rotulo}"],
    }


async def julgar_jev(
    estado: dict, chave_texto: str, agente: str, prompt: str,
    instrucao: str, criterio: dict, nouls: dict,
    nao_classificavel: str | None = None,
) -> dict:
    # chave_texto permanece na assinatura para preservar o contrato do endpoint.
    perguntas = {
        "veredito": {
            "type": "choice", "instructions": instrucao, "criteria": criterio,
        },
        **{
            nome: {"type": "noul", "instructions": instrucoes}
            for nome, instrucoes in nouls.items()
        },
    }
    try:
        dados = await consultar_jev(
            {**estado, "regras": prompt}, perguntas, operacao="classificador",
        )
        respostas = dados["answers"]
        choice, _ = ler_choice(respostas, "veredito", set(criterio))
        if choice == nao_classificavel:
            return _publicar(FRASE_SEGURA, agente, "nao_classificavel")
        if nouls:
            if choice not in nouls:
                raise ErroJEV("Categoria sem pergunta de confirmação.")
            noul = ler_noul(respostas, choice)
            if noul < LIMIAR:
                return _publicar(FRASE_SEGURA, agente, f"abaixo_do_limiar noul={noul:.2f}")
            rotulo = f"aprovado noul={noul:.2f}"
        else:
            rotulo = "aprovado"
        return _publicar(choice, agente, rotulo)
    except (ErroJEV, KeyError, TypeError, ValueError):
        return _publicar(FRASE_SEGURA, agente, "resposta_invalida")
