from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def load_env_file(path: str | Path = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "si"}


def env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return int(value)


@dataclass(frozen=True)
class Settings:
    meta_graph_version: str
    meta_access_token: str | None
    meta_page_id: str | None
    meta_page_access_token: str | None
    meta_since_days: int
    meta_limit_posts: int
    meta_limit_comments_per_post: int
    anonymization_salt: str
    store_author_name: bool
    google_spreadsheet_id: str
    google_drive_folder_id: str
    write_google: bool
    meta_page_name: str
    dashboard_status_path: Path
    output_dir: Path
    evidence_dir: Path

    @classmethod
    def from_env(cls) -> "Settings":
        load_env_file()
        return cls(
            meta_graph_version=os.getenv("META_GRAPH_VERSION", "v23.0"),
            meta_access_token=os.getenv("META_ACCESS_TOKEN") or None,
            meta_page_id=os.getenv("META_PAGE_ID") or None,
            meta_page_access_token=os.getenv("META_PAGE_ACCESS_TOKEN") or None,
            meta_since_days=env_int("META_SINCE_DAYS", 1),
            meta_limit_posts=env_int("META_LIMIT_POSTS", 25),
            meta_limit_comments_per_post=env_int("META_LIMIT_COMMENTS_PER_POST", 100),
            anonymization_salt=os.getenv("ANONYMIZATION_SALT", "local-dev-only"),
            store_author_name=env_bool("STORE_AUTHOR_NAME", False),
            google_spreadsheet_id=os.getenv(
                "GOOGLE_SPREADSHEET_ID",
                "19qCi8dMDZa89OrZhUth5EhQ0qvkrup6PaqTN3BN7NCc",
            ),
            google_drive_folder_id=os.getenv(
                "GOOGLE_DRIVE_FOLDER_ID",
                "1RGaWR4DJLrjHRNOoDEw7tdELaAYACcLd",
            ),
            write_google=env_bool("WRITE_GOOGLE", False),
            meta_page_name=os.getenv("META_PAGE_NAME", ""),
            dashboard_status_path=Path(os.getenv("DASHBOARD_STATUS_PATH", "docs/status.json")),
            output_dir=Path(os.getenv("OUTPUT_DIR", "outputs")),
            evidence_dir=Path(os.getenv("EVIDENCE_DIR", "evidence")),
        )

    def meta_ready(self) -> bool:
        return bool(self.meta_access_token and self.meta_page_id)
