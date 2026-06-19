from __future__ import annotations

import csv
import hashlib
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import RawComment


MESSAGE_FIELDS = [
    "message",
    "comment",
    "comentario",
    "texto",
    "text",
    "body",
    "content",
    "contenido",
    "opinion",
    "review",
    "comment_message",
    "comment_text",
]
COMMENT_DATE_FIELDS = [
    "comment_created_at",
    "created_time",
    "created_at",
    "timestamp",
    "date",
    "fecha",
    "fecha_comentario",
    "time",
]
COMMENT_ID_FIELDS = ["comment_id", "id", "comentario_id", "commentid"]
POST_ID_FIELDS = ["post_id", "publication_id", "publicacion_id", "postid"]
POST_URL_FIELDS = ["post_url", "permalink_url", "url", "link", "enlace"]
POST_DATE_FIELDS = ["post_created_at", "post_created_time", "fecha_publicacion"]
AUTHOR_ID_FIELDS = ["author_id", "user_id", "from_id", "profile_id", "id_autor"]
AUTHOR_HASH_FIELDS = ["author_id_hash", "autor_hash"]
AUTHOR_NAME_FIELDS = ["author_name", "author", "user_name", "from_name", "name", "autor"]
LIKE_FIELDS = ["like_count", "likes", "me_gusta", "reactions", "reacciones"]
REPLY_FIELDS = ["reply_count", "comment_count", "replies", "respuestas"]
PARENT_FIELDS = ["parent_id", "parent", "comment_parent_id"]
NETWORK_FIELDS = ["network", "red", "platform", "plataforma"]
SOURCE_FIELDS = ["source_account", "page_name", "pagina", "page", "account", "cuenta"]


def load_exported_comments(
    path: Path,
    *,
    network: str = "facebook",
    source_account: str = "archivo_exportado",
    salt: str = "",
    store_author_name: bool = False,
) -> list[RawComment]:
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo exportado: {path}")
    rows = load_rows(path)
    comments: list[RawComment] = []
    for index, row in enumerate(rows, start=1):
        normalized = normalize_row(row)
        message = first_value(normalized, MESSAGE_FIELDS)
        if not message:
            continue
        comment_created_at = normalize_datetime(first_value(normalized, COMMENT_DATE_FIELDS))
        post_created_at = normalize_datetime(first_value(normalized, POST_DATE_FIELDS))
        comment_id = first_value(normalized, COMMENT_ID_FIELDS) or make_stable_id(
            "comment",
            path.name,
            str(index),
            comment_created_at,
            message,
        )
        post_id = first_value(normalized, POST_ID_FIELDS)
        author_id = first_value(normalized, AUTHOR_ID_FIELDS)
        author_hash = first_value(normalized, AUTHOR_HASH_FIELDS)
        author_name = first_value(normalized, AUTHOR_NAME_FIELDS)
        if not author_hash and (author_id or author_name):
            author_hash = hash_identifier(author_id or author_name, salt or "archivo-exportado")
        comments.append(
            RawComment(
                network=first_value(normalized, NETWORK_FIELDS) or network,
                source_account=first_value(normalized, SOURCE_FIELDS) or source_account,
                post_id=post_id,
                post_url=first_value(normalized, POST_URL_FIELDS),
                post_created_at=post_created_at,
                comment_id=comment_id,
                comment_created_at=comment_created_at,
                message=message,
                author_id_hash=author_hash,
                author_name=author_name if store_author_name else "",
                like_count=parse_int(first_value(normalized, LIKE_FIELDS)),
                reply_count=parse_int(first_value(normalized, REPLY_FIELDS)),
                parent_id=first_value(normalized, PARENT_FIELDS),
            )
        )
    return comments


def load_rows(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix in {".csv", ".tsv", ".txt"}:
        return load_delimited_rows(path)
    if suffix == ".jsonl":
        return [
            json.loads(line)
            for line in path.read_text(encoding="utf-8-sig").splitlines()
            if line.strip()
        ]
    if suffix == ".json":
        return flatten_json_payload(json.loads(path.read_text(encoding="utf-8-sig")))
    raise ValueError("Formato no soportado. Usar CSV, TSV, TXT, JSON o JSONL.")


def load_delimited_rows(path: Path) -> list[dict[str, Any]]:
    text = read_text_with_fallback(path)
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel_tab if path.suffix.lower() == ".tsv" else csv.excel
    reader = csv.DictReader(text.splitlines(), dialect=dialect)
    return [dict(row) for row in reader]


def read_text_with_fallback(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-16", "cp1252"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def flatten_json_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    if isinstance(payload.get("posts"), list):
        rows: list[dict[str, Any]] = []
        for post in payload["posts"]:
            if not isinstance(post, dict):
                continue
            comments = post.get("comments") or []
            for comment in comments:
                if isinstance(comment, dict):
                    row = dict(comment)
                    row.setdefault("post_id", post.get("id", ""))
                    row.setdefault("post_url", post.get("permalink_url", ""))
                    row.setdefault("post_created_at", post.get("created_time", ""))
                    row.setdefault("network", payload.get("network", "facebook"))
                    row.setdefault("source_account", payload.get("source_account", "archivo_exportado"))
                    rows.append(row)
        return rows
    for key in ("data", "comments", "comentarios", "rows", "items"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    if any(normalize_key(key) in MESSAGE_FIELDS for key in payload):
        return [payload]
    return []


def normalize_row(row: dict[str, Any]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for key, value in row.items():
        key_name = normalize_key(str(key))
        if isinstance(value, dict):
            if key_name in {"from", "author", "autor", "user"}:
                if value.get("id"):
                    normalized["author_id"] = str(value.get("id", "")).strip()
                if value.get("name"):
                    normalized["author_name"] = str(value.get("name", "")).strip()
            if key_name == "parent" and value.get("id"):
                normalized["parent_id"] = str(value.get("id", "")).strip()
            continue
        if value is None:
            value = ""
        normalized[key_name] = str(value).strip()
    return normalized


def normalize_key(value: str) -> str:
    text = unicodedata.normalize("NFKD", value)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def first_value(row: dict[str, str], keys: list[str]) -> str:
    for key in keys:
        value = row.get(key, "")
        if value:
            return value
    return ""


def normalize_datetime(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    cleaned = value.replace("Z", "+0000").replace(" UTC", "+0000")
    formats = [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%d %H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y",
    ]
    for fmt in formats:
        try:
            parsed = datetime.strptime(cleaned, fmt)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.isoformat().replace("+00:00", "+0000")
        except ValueError:
            continue
    return value


def parse_int(value: str) -> int:
    if not value:
        return 0
    match = re.search(r"-?\d+", str(value))
    return int(match.group(0)) if match else 0


def make_stable_id(*parts: str) -> str:
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def hash_identifier(value: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}:{value}".encode("utf-8")).hexdigest()
