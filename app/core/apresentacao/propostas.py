"""Renderização determinística de propostas, usada pelo grafo, tools e serviços."""

from app.core import (
    MENSAGENS,
    NOMES_CAMPOS,
    RESPOSTAS_OPERACAO_SUCESSO,
    RESPOSTAS_OPERACAO_FALHA,
    TEXTOS_CONFIRMACAO,
    RESPOSTAS_BLOQUEIO,
    TEXTOS_COMPRAS,
    COMPLEMENTOS_BASE_CALCULO,
)
from .textos import formatar_resposta, escolher_resposta

def resumo_confirmacao(rascunho: dict) -> str:
    """Renderiza resumo determinístico dos dados/alterações da proposta. Usado pelo fluxo de apresentacao."""
    if rascunho.get("operacao") == "atualizar":
        return resumo_atualizacao(rascunho)
    from app.core import campos_pendentes
    pendentes = campos_pendentes(rascunho)
    if not pendentes:
        return MENSAGENS['os_dados_ja_estao_confirmados_nao_e_necessario_confirma_los_novamente']
    titulo = TEXTOS_CONFIRMACAO["titulo" if not rascunho.get("dados_confirmados") else "alteracoes"]
    linhas = [titulo]
    for campo in pendentes:
        valor = rascunho.get("rotulos", {}).get(campo, rascunho["dados"][campo])
        # IDs são internos; as ferramentas devem fornecer descrições verificadas.
        if campo in {"local_endereco_id", "local_unidade_id", "categoria_equipamento_id"} and campo not in rascunho.get("rotulos", {}):
            valor = TEXTOS_CONFIRMACAO["rotulo_ausente"]
        linhas.append(TEXTOS_CONFIRMACAO["campo"].format(nome=NOMES_CAMPOS.get(campo, campo), valor=str(valor).replace(chr(10), ' ')))
    linhas.append(TEXTOS_CONFIRMACAO["pergunta"])
    return "\n".join(linhas)


def resumo_atualizacao(rascunho: dict) -> str:
    """Renderiza identificação do registro ou proposta final das alterações/fotos. Usado por resumo_confirmacao."""
    import re
    ocorrencia = rascunho["tipo"] == "ocorrencia"
    prefixo = "ocorrencia_atualizacao" if ocorrencia else "atualizacao"
    descricao = "descricao_ocorrencia" if ocorrencia else "descricao_problema"

    def texto(valor):
        # Conteúdo persistido é texto, não formatação ou instrução do sistema.
        """Executa a etapa texto no escopo de propostas. Usado por resumo_atualizacao."""
        return re.sub(r"([\\`*_{}\[\]<>])", r"\\\1", " ".join(str(valor).split()))

    if rascunho.get("etapa") == "selecao":
        original = rascunho["original"]
        return MENSAGENS[f"{prefixo}_confirmar_selecao"].format(
            titulo=texto(original["titulo"]), descricao=texto(original[descricao]),
        )
    linhas = [MENSAGENS[f"{prefixo}_titulo_final"]]
    campos = ("titulo", descricao, "descricao_local", "local_unidade_id", "categoria_equipamento_id")
    if ocorrencia:
        campos += ("categoria_problema", "prioridade")
    for campo in campos:
        valor = rascunho.get("rotulos", {}).get(campo, rascunho["dados"][campo])
        linhas.append(TEXTOS_CONFIRMACAO["campo"].format(nome=NOMES_CAMPOS[campo], valor=texto(valor)))
    acao = rascunho["acao_fotos"]
    linhas.append(MENSAGENS[f"atualizacao_fotos_{acao}"].format(
        quantidade=len(rascunho["original"].get("fotos", [])),
        existentes=len(rascunho["original"].get("fotos", [])), novas=len(rascunho.get("imagens", [])),
    ))
    linhas.append(MENSAGENS["atualizacao_pergunta_final"])
    return "\n".join(linhas)
