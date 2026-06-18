from __future__ import annotations

from typing import Iterable

from .sheet_schema import CONFIG_ROWS, SHEET_HEADERS


class SheetsWriter:
    def __init__(self, spreadsheet_id: str) -> None:
        import google.auth
        from googleapiclient.discovery import build

        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        credentials, _ = google.auth.default(scopes=scopes)
        self.spreadsheet_id = spreadsheet_id
        self.service = build("sheets", "v4", credentials=credentials, cache_discovery=False)

    def ensure_schema(self) -> None:
        metadata = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
        existing_titles = {sheet["properties"]["title"] for sheet in metadata.get("sheets", [])}
        requests = []
        for title in SHEET_HEADERS:
            if title not in existing_titles:
                requests.append({"addSheet": {"properties": {"title": title}}})
        if requests:
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={"requests": requests},
            ).execute()

        for title, headers in SHEET_HEADERS.items():
            values = CONFIG_ROWS if title == "CONFIGURACION" else [headers]
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{title}!A1",
                valueInputOption="USER_ENTERED",
                body={"values": values},
            ).execute()

    def append_rows(self, sheet_name: str, rows: Iterable[list]) -> None:
        rows = list(rows)
        if not rows:
            return
        self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range=f"{sheet_name}!A1",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": rows},
        ).execute()

