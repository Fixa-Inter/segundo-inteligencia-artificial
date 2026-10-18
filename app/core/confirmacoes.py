"""Vocabulário compartilhado de manifestações, sem autorização por prefixo."""

import re
import unicodedata
from typing import Literal

Manifestacao = Literal["aceite", "negacao", "cancelamento", "pausa", "retomada", "pergunta", "outro"]

ACEITES = frozenset({
    "sim", "confirmo", "confirmado", "autorizo", "isso", "isso mesmo",
    "tudo certo", "tudo correto", "esta correto", "esta certo", "esta bom",
    "beleza", "fechado", "perfeito", "ok", "okay", "certo", "correto",
    "de acordo", "concordo", "pode ser",
})
ACOES_ACEITE = (
    "cadastrar", "criar", "registrar", "enviar", "prosseguir", "seguir",
    "continuar", "alterar", "anexar", "salvar", "atualizar",
)
ALVOS = (
    "", "os dados", "as informacoes", "a proposta", "a solicitacao", "a ocorrencia",
    "o cadastro", "a alteracao", "a mudanca", "a foto", "as fotos", "a imagem", "as imagens",
    "o local", "o titulo", "a descricao", "a prioridade", "a categoria",
    "a categoria do equipamento", "a categoria do problema", "os detalhes do local",
)


def _construir_frases_aceite() -> frozenset[str]:
    frases = set(ACEITES)
    frases.update(f"pode {acao}" for acao in ACOES_ACEITE)
    frases.update(f"{verbo} {alvo}" for verbo in ("confirmo", "autorizo") for alvo in ALVOS if alvo)
    frases.update(f"pode {acao} {alvo}" for acao in ACOES_ACEITE for alvo in ALVOS if alvo)
    frases.update(f"{alvo} esta {adjetivo}" for alvo in ALVOS if alvo
                  for adjetivo in ("correto", "correta", "certo", "certa"))
    for prefixo in ("sim ", "ok ", "certo "):
        frases.update(prefixo + frase for frase in tuple(frases) if not frase.startswith(prefixo))
    return frozenset(frases)


FRASES_ACEITE = _construir_frases_aceite()


def normalizar_mensagem(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", texto).split())


def classificar_manifestacao(texto: str) -> Manifestacao:
    if not isinstance(texto, str) or not texto.strip():
        return "outro"
    normalizada = normalizar_mensagem(texto)
    if "?" in texto or re.match(r"^(como|qual|quando|onde|por que|sera|posso|voce pode)\b", normalizada):
        return "pergunta"
    if re.fullmatch(r"(?:nao )?(?:quero |vamos |pode )?(?:cancele|cancelar|cancela|desista|desistir|desisti|esqueca|deixa pra la|deixe para la)(?: (?:disso|isso|o cadastro|a solicitacao|a ocorrencia|a alteracao))?", normalizada):
        return "negacao" if normalizada.startswith("nao ") else "cancelamento"
    if re.fullmatch(r"nao quero (?:mais(?: continuar| cadastrar| registrar)?|continuar)(?: (?:a solicitacao|a ocorrencia|o cadastro))?", normalizada):
        return "cancelamento"
    if re.fullmatch(r"(?:vamos |quero |podemos )?(?:retomar|continuar)(?: (?:o cadastro|a solicitacao|a ocorrencia|a alteracao))?", normalizada):
        return "retomada"
    if re.fullmatch(r"(?:depois (?:eu )?(?:continuo|termino)|(?:vamos |quero )?pausar(?: (?:o cadastro|a solicitacao|a ocorrencia|a alteracao))?|(?:deixe|deixa) para depois|agora nao)", normalizada):
        return "pausa"
    if re.search(r"\b(nao|nunca|jamais|cancele|cancelar|talvez|mas|porem|se|antes|depois|corrija|corrigir|mude|mudar)\b", normalizada):
        return "negacao"
    # Toda a mensagem deve corresponder ao aceite; “sim, troque o local” não autoriza.
    normalizada = re.sub(r"\b(por favor|obrigado|obrigada)\b", "", normalizada)
    return "aceite" if " ".join(normalizada.split()) in FRASES_ACEITE else "outro"


def aceite_explicito(texto: str, *, acoes: tuple[str, ...] | None = None) -> bool:
    if classificar_manifestacao(texto) != "aceite":
        return False
    acao = re.search(r"\bpode (\w+)\b", normalizar_mensagem(texto))
    return acoes is None or acao is None or acao.group(1) == "ser" or acao.group(1) in acoes
