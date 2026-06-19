from __future__ import annotations

import json
import hashlib
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from .config import Settings
from .models import AnalyzedComment


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_public_status(
    run_id: str,
    source: str,
    analyzed: list[AnalyzedComment],
    artifacts: dict[str, Path],
    settings: Settings,
    status: str = "ok",
    posts_visible: int | None = None,
) -> dict:
    sentiment_counts = Counter(item.sentiment for item in analyzed)
    category_counts = Counter(item.category for item in analyzed)
    daily = build_daily_series(analyzed)
    comments = [public_comment_row(item) for item in analyzed[:100]]
    alerts = [public_alert_row(item) for item in analyzed if item.needs_response][:100]
    page_name = settings.meta_page_name or settings.meta_page_id or "Pagina Meta"
    comments_total = len(analyzed)
    alerts_total = len(alerts)

    return {
        "generated_at_utc": utc_timestamp(),
        "scope_note": build_scope_note(source),
        "meta_page": {
            "id": settings.meta_page_id or "",
            "name": page_name,
            "api_status": "API visible" if settings.meta_ready() else "Pendiente de token",
        },
        "profile": {
            "status": "no_disponible_por_api",
            "detail": "Meta Graph API no permite extraer comentarios diarios de un perfil personal comun como si fuera una Pagina.",
        },
        "website": {
            "status": "Pendiente",
            "detail": "Para visitas, clicks y trafico web hay que conectar GA4, Search Console o logs del sitio.",
        },
        "latest_run": {
            "run_id": run_id,
            "timestamp_utc": utc_timestamp(),
            "source": source,
            "status": status,
            "posts_visible": posts_visible if posts_visible is not None else "",
            "comments_total": comments_total,
            "alerts_total": alerts_total,
        },
        "sentiment": {
            "total": comments_total,
            "positivo": sentiment_counts.get("positivo", 0),
            "neutro": sentiment_counts.get("neutro", 0),
            "negativo": sentiment_counts.get("negativo", 0),
        },
        "categories": [
            {"name": name, "count": count}
            for name, count in category_counts.most_common(12)
        ],
        "trend": daily,
        "alerts": alerts,
        "comments": comments,
        "diagnostic": build_diagnostic(comments_total, posts_visible, settings.meta_ready(), source),
        "next_step": build_next_step(comments_total, posts_visible, source),
        "destinations": {
            "spreadsheet_url": f"https://docs.google.com/spreadsheets/d/{settings.google_spreadsheet_id}/edit",
            "drive_folder_url": f"https://drive.google.com/drive/folders/{settings.google_drive_folder_id}",
        },
        "automation": {
            "workflow_url": "https://github.com/monitorimpactosocial/analisis_opinion_redes/actions/workflows/update-dashboard.yml",
            "mode": "github_actions_manual",
        },
        "evidence": build_evidence_rows(artifacts),
        "security_note": "No contiene tokens, passwords ni identificadores crudos de autores.",
    }


def build_daily_series(analyzed: list[AnalyzedComment]) -> list[dict]:
    grouped: dict[str, list[AnalyzedComment]] = defaultdict(list)
    if not analyzed:
        return [
            {
                "date": datetime.now(timezone.utc).date().isoformat(),
                "comments_total": 0,
                "positivo": 0,
                "neutro": 0,
                "negativo": 0,
                "alerts_total": 0,
            }
        ]
    for item in analyzed:
        date = item.raw.comment_created_at[:10] or datetime.now(timezone.utc).date().isoformat()
        grouped[date].append(item)
    rows = []
    for date, items in sorted(grouped.items()):
        sentiments = Counter(item.sentiment for item in items)
        rows.append(
            {
                "date": date,
                "comments_total": len(items),
                "positivo": sentiments.get("positivo", 0),
                "neutro": sentiments.get("neutro", 0),
                "negativo": sentiments.get("negativo", 0),
                "alerts_total": sum(1 for item in items if item.needs_response),
            }
        )
    return rows[-30:]


def public_comment_row(item: AnalyzedComment) -> dict:
    return {
        "comment_created_at": item.raw.comment_created_at,
        "network": item.raw.network,
        "source_account": item.raw.source_account,
        "post_url": item.raw.post_url,
        "message": item.raw.message,
        "sentiment": item.sentiment,
        "sentiment_score": item.sentiment_score,
        "category": item.category,
        "urgency": item.urgency,
        "needs_response": item.needs_response,
        "matched_keywords": item.matched_keywords,
    }


def public_alert_row(item: AnalyzedComment) -> dict:
    row = public_comment_row(item)
    return row


def build_scope_note(source: str) -> str:
    if source == "import_file":
        return (
            "Este tablero reporta comentarios cargados desde archivos exportados manualmente. "
            "No depende del permiso pages_read_user_content de Meta para esta corrida."
        )
    return (
        "Este tablero reporta la Pagina de Facebook conectada por API. "
        "El perfil personal no es accesible por la API oficial; para sitio web "
        "se requiere conectar GA4/Search Console."
    )


def build_diagnostic(comments_total: int, posts_visible: int | None, meta_ready: bool, source: str) -> dict:
    if source == "import_file":
        if comments_total > 0:
            return {
                "title": "Archivo exportado cargado",
                "detail": "El tablero ya refleja comentarios importados desde archivo y clasificados por sentimiento, categoria y urgencia.",
            }
        return {
            "title": "Archivo exportado sin comentarios",
            "detail": "El archivo se proceso, pero no se detectaron filas con texto de comentario.",
        }
    if not meta_ready:
        return {
            "title": "Faltan credenciales Meta",
            "detail": "El tablero esta listo, pero la extraccion real requiere token y pagina configurados localmente.",
        }
    if comments_total > 0:
        return {
            "title": "Datos de comentarios cargados",
            "detail": "El tablero ya refleja comentarios reales clasificados por sentimiento, categoria y urgencia.",
        }
    if posts_visible == 0:
        return {
            "title": "La conexion con Meta funciona",
            "detail": "La pagina es visible para la API. La ultima corrida no trajo comentarios porque no hubo publicaciones visibles para analizar.",
        }
    return {
        "title": "Sin comentarios en la ventana analizada",
        "detail": "La API respondio correctamente, pero no devolvio comentarios para el periodo consultado.",
    }


def build_next_step(comments_total: int, posts_visible: int | None, source: str) -> dict:
    if source == "import_file":
        if comments_total > 0:
            return {
                "title": "Revisar alertas importadas",
                "detail": "Usar las tablas del tablero para priorizar respuestas y repetir la importacion cuando exista un nuevo export.",
            }
        return {
            "title": "Revisar columnas del export",
            "detail": "Confirmar que el archivo tenga una columna de texto como message, comentario, texto o content.",
        }
    if comments_total > 0:
        return {
            "title": "Revisar alertas",
            "detail": "Usar la tabla de alertas y el Google Sheet para priorizar respuestas o seguimiento.",
        }
    if posts_visible == 0:
        return {
            "title": "Publicar post de prueba",
            "detail": "Crear una publicacion en la pagina conectada, dejar al menos un comentario y repetir collect.",
        }
    return {
        "title": "Ampliar ventana o comentar",
        "detail": "Aumentar META_SINCE_DAYS o dejar comentarios de prueba en una publicacion visible.",
    }


def build_evidence_rows(artifacts: dict[str, Path]) -> list[dict]:
    rows = []
    for artifact_type, path in artifacts.items():
        if artifact_type == "jsonl":
            continue
        rows.append(
            {
                "type": artifact_type,
                "file_name": path.name,
                "sha256": file_sha256(path) if path.exists() else "",
                "url": "",
            }
        )
    return rows


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_public_status(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
