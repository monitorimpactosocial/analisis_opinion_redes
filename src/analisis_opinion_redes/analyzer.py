from __future__ import annotations

import re
import unicodedata

from .models import AnalyzedComment, RawComment


POSITIVE = {
    "gracias": 2,
    "excelente": 3,
    "bueno": 1,
    "buenisimo": 3,
    "felicitaciones": 3,
    "apoyo": 2,
    "positivo": 1,
    "correcto": 1,
    "mejoro": 2,
    "solucionado": 2,
}

NEGATIVE = {
    "reclamo": -3,
    "problema": -2,
    "mal": -2,
    "pesimo": -3,
    "denuncia": -4,
    "queja": -3,
    "molesto": -2,
    "grave": -3,
    "riesgo": -3,
    "no responden": -3,
    "urgente": -3,
    "incumplimiento": -4,
}

CATEGORY_KEYWORDS = {
    "consulta": {"consulta", "pregunta", "cuando", "donde", "como", "horario", "informacion"},
    "reclamo": {"reclamo", "queja", "problema", "molesto", "no responden", "mal"},
    "empleo": {"trabajo", "empleo", "vacancia", "cv", "contratar", "puesto"},
    "precio": {"precio", "costo", "pago", "cobra", "tarifa"},
    "ambiente": {"ambiente", "agua", "ruido", "polvo", "impacto", "forestal"},
    "denuncia": {"denuncia", "grave", "riesgo", "incumplimiento"},
    "elogio": {"gracias", "excelente", "felicitaciones", "apoyo", "bueno"},
}

URGENT_KEYWORDS = {"urgente", "grave", "denuncia", "riesgo", "incumplimiento", "emergencia"}


def normalize_text(text: str) -> str:
    no_accents = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", no_accents.lower()).strip()


def score_text(text: str) -> tuple[int, list[str]]:
    normalized = normalize_text(text)
    score = 0
    hits: list[str] = []
    for keyword, weight in {**POSITIVE, **NEGATIVE}.items():
        if contains_keyword(normalized, keyword):
            score += weight
            hits.append(keyword)
    return score, sorted(set(hits))


def contains_keyword(normalized_text: str, keyword: str) -> bool:
    key = normalize_text(keyword)
    if " " in key:
        return key in normalized_text
    return re.search(rf"\b{re.escape(key)}\b", normalized_text) is not None


def classify_category(text: str) -> str:
    normalized = normalize_text(text)
    best_category = "general"
    best_hits = 0
    for category, keywords in CATEGORY_KEYWORDS.items():
        hits = sum(1 for keyword in keywords if contains_keyword(normalized, keyword))
        if hits > best_hits:
            best_category = category
            best_hits = hits
    return best_category


def classify_urgency(text: str, score: int) -> str:
    normalized = normalize_text(text)
    if any(contains_keyword(normalized, keyword) for keyword in URGENT_KEYWORDS):
        return "alta"
    if score <= -3:
        return "media"
    return "normal"


def analyze_comment(comment: RawComment) -> AnalyzedComment:
    score, hits = score_text(comment.message)
    if score > 0:
        sentiment = "positivo"
    elif score < 0:
        sentiment = "negativo"
    else:
        sentiment = "neutro"

    category = classify_category(comment.message)
    urgency = classify_urgency(comment.message, score)
    needs_response = sentiment == "negativo" or urgency != "normal" or category in {"consulta", "reclamo", "denuncia"}

    return AnalyzedComment(
        raw=comment,
        sentiment=sentiment,
        sentiment_score=score,
        category=category,
        urgency=urgency,
        needs_response=needs_response,
        matched_keywords=", ".join(hits),
    )
