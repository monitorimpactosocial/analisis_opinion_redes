from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .analyzer import analyze_comment
from .config import Settings
from .file_importer import load_exported_comments
from .models import AnalyzedComment, RawComment


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def make_run_id(prefix: str) -> str:
    return f"{prefix}_{utc_now().strftime('%Y%m%dT%H%M%SZ')}"


def load_sample(path: Path) -> list[RawComment]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    comments: list[RawComment] = []
    for post in payload["posts"]:
        for item in post.get("comments", []):
            comments.append(
                RawComment(
                    network=payload.get("network", "facebook"),
                    source_account=payload.get("source_account", "demo"),
                    post_id=post.get("id", ""),
                    post_url=post.get("permalink_url", ""),
                    post_created_at=post.get("created_time", ""),
                    comment_id=item.get("id", ""),
                    comment_created_at=item.get("created_time", ""),
                    message=item.get("message", ""),
                    author_id_hash=item.get("author_id_hash", ""),
                    author_name=item.get("author_name", ""),
                    like_count=int(item.get("like_count", 0)),
                    reply_count=int(item.get("reply_count", 0)),
                    parent_id=item.get("parent_id", ""),
                )
            )
    return comments


def collect_from_meta(settings: Settings) -> list[RawComment]:
    if not settings.meta_ready():
        raise ValueError("META_ACCESS_TOKEN and META_PAGE_ID are required for collect mode.")
    from .meta_client import MetaClient

    since = utc_now() - timedelta(days=settings.meta_since_days)
    client = MetaClient(settings.meta_access_token or "", settings.meta_graph_version)
    account = settings.meta_page_id or ""
    return client.collect_page_comments(
        page_id=account,
        since=since,
        source_account=account,
        salt=settings.anonymization_salt,
        store_author_name=settings.store_author_name,
        limit_posts=settings.meta_limit_posts,
        limit_comments_per_post=settings.meta_limit_comments_per_post,
        page_access_token=settings.meta_page_access_token,
    )


def import_from_file(path: Path, settings: Settings, network: str, source_account: str) -> list[RawComment]:
    return load_exported_comments(
        path,
        network=network,
        source_account=source_account,
        salt=settings.anonymization_salt,
        store_author_name=settings.store_author_name,
    )


def analyze_comments(comments: list[RawComment]) -> list[AnalyzedComment]:
    return [analyze_comment(comment) for comment in comments]


def build_daily_metrics(run_id: str, comments: list[AnalyzedComment]) -> list[list]:
    groups: dict[tuple[str, str, str, str], list[AnalyzedComment]] = defaultdict(list)
    for comment in comments:
        date = comment.raw.comment_created_at[:10] or utc_now().date().isoformat()
        key = (date, comment.raw.network, comment.raw.source_account, run_id)
        groups[key].append(comment)

    rows: list[list] = []
    for (date, network, source_account, rid), items in sorted(groups.items()):
        sentiments = Counter(item.sentiment for item in items)
        categories = Counter(item.category for item in items)
        alerts_total = sum(1 for item in items if item.needs_response)
        top_categories = ", ".join(f"{name}:{count}" for name, count in categories.most_common(5))
        rows.append(
            [
                rid,
                date,
                network,
                source_account,
                len(items),
                sentiments.get("positivo", 0),
                sentiments.get("neutro", 0),
                sentiments.get("negativo", 0),
                alerts_total,
                top_categories,
            ]
        )
    return rows


def write_local_outputs(run_id: str, analyzed: list[AnalyzedComment], settings: Settings) -> dict[str, Path]:
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    settings.evidence_dir.mkdir(parents=True, exist_ok=True)
    base_name = run_id
    jsonl_path = settings.output_dir / f"{base_name}_comentarios.jsonl"
    csv_path = settings.output_dir / f"{base_name}_comentarios.csv"
    metrics_path = settings.output_dir / f"{base_name}_metricas.json"
    evidence_path = settings.evidence_dir / f"{base_name}_evidencia.md"

    with jsonl_path.open("w", encoding="utf-8") as fh:
        for item in analyzed:
            fh.write(json.dumps(item.to_dict(), ensure_ascii=False) + "\n")

    fieldnames = list(analyzed[0].to_dict().keys()) if analyzed else ["message"]
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for item in analyzed:
            writer.writerow(item.to_dict())

    metrics = {
        "run_id": run_id,
        "timestamp_utc": utc_now().isoformat(),
        "comments_total": len(analyzed),
        "alerts_total": sum(1 for item in analyzed if item.needs_response),
        "sentiment": dict(Counter(item.sentiment for item in analyzed)),
        "category": dict(Counter(item.category for item in analyzed)),
    }
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

    evidence_path.write_text(
        "\n".join(
            [
                f"# Evidencia {run_id}",
                "",
                f"- Generado UTC: {metrics['timestamp_utc']}",
                f"- Comentarios procesados: {metrics['comments_total']}",
                f"- Alertas: {metrics['alerts_total']}",
                f"- JSONL: {jsonl_path.name}",
                f"- CSV: {csv_path.name}",
                f"- Metricas: {metrics_path.name}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {"jsonl": jsonl_path, "csv": csv_path, "metrics": metrics_path, "evidence": evidence_path}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_google_outputs(
    run_id: str,
    source: str,
    analyzed: list[AnalyzedComment],
    artifacts: dict[str, Path],
    settings: Settings,
) -> list[str]:
    notes: list[str] = []
    from .drive_writer import DriveWriter
    from .sheets_writer import SheetsWriter

    sheets = SheetsWriter(settings.google_spreadsheet_id)
    sheets.ensure_schema()
    sheets.append_rows(
        "EJECUCIONES",
        [
            [
                run_id,
                utc_now().isoformat(),
                source,
                "ok",
                len(analyzed),
                sum(1 for item in analyzed if item.needs_response),
                ", ".join(path.name for path in artifacts.values()),
                "pipeline",
            ]
        ],
    )
    sheets.append_rows("COMENTARIOS", [item.to_sheet_row(run_id) for item in analyzed])
    sheets.append_rows("METRICAS_DIARIAS", build_daily_metrics(run_id, analyzed))
    sheets.append_rows(
        "ALERTAS",
        [
            [
                run_id,
                item.raw.comment_created_at,
                item.raw.network,
                item.raw.source_account,
                item.raw.post_url,
                item.raw.comment_id,
                item.raw.message,
                item.category,
                item.urgency,
                item.sentiment,
                item.matched_keywords,
                "pendiente",
            ]
            for item in analyzed
            if item.needs_response
        ],
    )

    drive = DriveWriter(settings.google_drive_folder_id)
    evidence_rows = []
    for artifact_type, path in artifacts.items():
        drive_url = drive.upload_file(path)
        evidence_rows.append(
            [
                run_id,
                utc_now().isoformat(),
                artifact_type,
                path.name,
                drive_url,
                str(path),
                file_sha256(path),
                "subido por pipeline",
            ]
        )
    sheets.append_rows("EVIDENCIAS", evidence_rows)
    notes.append("google_write_ok")
    return notes


def run_pipeline(
    source: str,
    settings: Settings,
    sample_path: Path | None = None,
    import_path: Path | None = None,
    import_network: str = "facebook",
    import_source_account: str = "archivo_exportado",
    write_google: bool = False,
) -> dict:
    run_id = make_run_id(source)
    if source == "sample":
        comments = load_sample(sample_path or Path("samples/facebook_comments_sample.json"))
    elif source == "collect":
        comments = collect_from_meta(settings)
    elif source == "import_file":
        if import_path is None:
            raise ValueError("--input is required for import-file mode.")
        comments = import_from_file(import_path, settings, import_network, import_source_account)
    else:
        raise ValueError(f"Unknown source: {source}")

    analyzed = analyze_comments(comments)
    artifacts = write_local_outputs(run_id, analyzed, settings)
    from .dashboard_export import build_public_status, write_public_status

    dashboard_status = build_public_status(run_id, source, analyzed, artifacts, settings)
    write_public_status(settings.dashboard_status_path, dashboard_status)
    google_notes: list[str] = []
    if write_google or settings.write_google:
        google_notes = write_google_outputs(run_id, source, analyzed, artifacts, settings)

    return {
        "run_id": run_id,
        "source": source,
        "comments_total": len(analyzed),
        "alerts_total": sum(1 for item in analyzed if item.needs_response),
        "artifacts": {key: str(value) for key, value in artifacts.items()},
        "google_notes": google_notes,
    }
