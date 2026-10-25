from fastapi import APIRouter
from app.schemas import ClassificarProblemaRequest, ClassificarProblemaResponse
from app.services.gerais.julgar import julgar_jev
from app.agents.prompts.especialistas.classificador import CLASSIFICADOR_PROMPT_COMPLETO

router = APIRouter(tags=["Observability"],prefix="/classificar")


@router.post("/classificar-problema", response_model=ClassificarProblemaResponse)
async def classificar_problema(classificar_problema: ClassificarProblemaRequest) -> ClassificarProblemaResponse:
    """
    Endpoint para classificar um problema com base no título, descrição e categoria do equipamento.

    Args:
        classificar_problema (ClassificarProblemaRequest): Dados de entrada para classificação do problema.
    """

    estado ={
        "titulo": classificar_problema.titulo,
        "descricao": classificar_problema.descricao,
        "categoria_equipamento": classificar_problema.categoria_equipamento
    }

    criterio = {
        "ELETRICA": (
            "Falhas em energia e instalações elétricas, como tomadas, fiação, "
            "disjuntores, interruptores ou equipamentos que não ligam por falta de energia."
        ),
        "HIDRAULICA": (
            "Problemas no abastecimento ou escoamento de água, como vazamentos, "
            "torneiras, tubulações, pias, vasos sanitários ou entupimentos."
        ),
        "MECANICA": (
            "Falhas em mecanismos ou componentes móveis, como travamentos, "
            "engrenagens, dobradiças ou peças que não se movimentam corretamente."
        ),
        "INFORMATICA": (
            "Problemas em computadores, notebooks, impressoras ou periféricos, "
            "incluindo falhas de hardware, sistema operacional ou software."
        ),
        "MOBILIARIO": (
            "Danos ou defeitos em móveis e seus componentes, como mesas, cadeiras, "
            "armários, gavetas, cortina, portas de armário ou estruturas quebradas."
        ),
        "CLIMATIZACAO": (
            "Problemas em ar-condicionado, ventiladores ou outros sistemas de "
            "climatização, incluindo falhas de refrigeração, ventilação ou controle de temperatura."
        ),
        "REDE_CONECTIVIDADE": (
            "Falhas de acesso ou conexão a redes, internet ou Wi-Fi, ou problemas "
            "em cabeamento e equipamentos de conectividade."
        ),
        "SEGURANCA": (
            "Problemas em dispositivos ou estruturas de proteção e controle de acesso, "
            "como fechaduras, portões, alarmes, câmeras ou controles de entrada."
        ),
        "ILUMINACAO": (
            "Falhas na iluminação do ambiente, como lâmpadas queimadas, luminárias "
            "danificadas ou luzes que piscam ou não acendem."
        ),
        "LIMPEZA_CONSERVACAO": (
            "Necessidade de limpeza ou conservação de ambientes, como sujeira, "
            "resíduos, higienização ou deterioração que exija cuidado de conservação."
        ),
        "NAO_CLASSIFICAVEL": (
            "O relato é insuficiente, ambíguo ou não descreve um problema que se enquadre "
            "com segurança em nenhuma das categorias anteriores."
        ),
    }
    nouls_categoria = {
        categoria: f"O problema relatado se enquadra em {categoria}: {descricao}?"
        for categoria,descricao in criterio.items()
        if categoria != "NAO_CLASSIFICAVEL"
    }

    resposta = await julgar_jev(
        estado=estado,
        chave_texto="descricao",
        agente="classificador_problema",
        prompt=CLASSIFICADOR_PROMPT_COMPLETO,
        instrucao="Escolha a categoria mais específica para o problema relatado. Use NAO_CLASSIFICAVEL se o relato for insuficiente, ambíguo ou não pertencer às categorias disponíveis.",
        criterio=criterio,
        nouls=nouls_categoria,
        nao_classificavel="NAO_CLASSIFICAVEL",
    )

    classificacao = resposta.get("messages", [{}])[0].get("content", "").strip()

    if classificacao not in criterio or classificacao == "NAO_CLASSIFICAVEL":
        classificacao = None
    
    return ClassificarProblemaResponse(
        problema_classificado=bool(classificacao),
        classificacao=classificacao if classificacao else None,
    )

