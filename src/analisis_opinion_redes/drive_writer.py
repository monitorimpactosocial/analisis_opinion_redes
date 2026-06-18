from __future__ import annotations

import mimetypes
from pathlib import Path


class DriveWriter:
    def __init__(self, folder_id: str) -> None:
        import google.auth
        from googleapiclient.discovery import build

        scopes = ["https://www.googleapis.com/auth/drive.file"]
        credentials, _ = google.auth.default(scopes=scopes)
        self.folder_id = folder_id
        self.service = build("drive", "v3", credentials=credentials, cache_discovery=False)

    def upload_file(self, path: Path) -> str:
        from googleapiclient.http import MediaFileUpload

        mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        media = MediaFileUpload(str(path), mimetype=mime_type, resumable=False)
        metadata = {"name": path.name, "parents": [self.folder_id]}
        uploaded = (
            self.service.files()
            .create(body=metadata, media_body=media, fields="id,webViewLink")
            .execute()
        )
        return uploaded.get("webViewLink", "")

