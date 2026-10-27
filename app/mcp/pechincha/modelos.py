"""Contrato de entrada e normalização das respostas de promoções."""

from urllib.parse import urlparse

from pydantic import BaseModel, Field, model_validator

from .transporte import ErroPechincha


class BuscaOfertas(BaseModel):
    query: str = Field(min_length=1)
    store: str | None = None
    category: str | None = None
    min_price: float | None = Field(default=None, ge=0)
    max_price: float | None = Field(default=None, ge=0)
    page: int = Field(default=1, ge=1)

    @model_validator(mode="after")
    def validar_faixa(self):
        self.query = self.query.strip()
        if not self.query:
            raise ValueError("A palavra chave é obrigatória.")
        if self.min_price is not None and self.max_price is not None and self.min_price > self.max_price:
            raise ValueError("O preço mínimo não pode superar o máximo.")
        return self


def _texto(valor: object) -> str:
    if isinstance(valor, dict):
        return str(valor.get("name") or valor.get("nome") or "").strip()
    return str(valor or "").strip()


def _url(valor: object) -> str | None:
    if not isinstance(valor, str):
        return None
    try:
        partes = urlparse(valor.strip())
    except ValueError:
        return None
    return valor.strip() if partes.scheme == "https" and partes.netloc else None


def normalizar_ofertas(conteudo: dict) -> dict:
    ofertas = conteudo.get("deals")
    if not isinstance(ofertas, list) or any(not isinstance(item, dict) for item in ofertas):
        raise ErroPechincha("protocolo", "A busca não retornou uma lista válida de promoções.")
    normalizadas = []
    for oferta in ofertas:
        preco = oferta.get("price")
        if isinstance(preco, bool) or not isinstance(preco, (int, float)):
            preco = None
        normalizadas.append({
            "title": _texto(oferta.get("title") or oferta.get("name")),
            "short_description": _texto(oferta.get("description") or oferta.get("summary")),
            "store_name": _texto(oferta.get("store_name") or oferta.get("store")),
            "price": preco,
            "url": _url(oferta.get("url") or oferta.get("deal_url") or oferta.get("link")),
        })
    return {"ofertas": normalizadas, "total": conteudo.get("total"),
            "pagina": conteudo.get("page"), "paginas": conteudo.get("pages")}
