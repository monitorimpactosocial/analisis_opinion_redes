from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .config import Settings
from .pipeline import run_pipeline


def cmd_validate_config(settings: Settings) -> int:
    status = {
        "meta_graph_version": settings.meta_graph_version,
        "meta_ready": settings.meta_ready(),
        "meta_page_id_present": bool(settings.meta_page_id),
        "google_spreadsheet_id": settings.google_spreadsheet_id,
        "google_drive_folder_id": settings.google_drive_folder_id,
        "write_google": settings.write_google,
        "store_author_name": settings.store_author_name,
    }
    print(json.dumps(status, indent=2, ensure_ascii=False))
    return 0


def cmd_list_pages(settings: Settings) -> int:
    if not settings.meta_access_token:
        print("META_ACCESS_TOKEN is required to list pages.", file=sys.stderr)
        return 2
    from .meta_client import MetaClient

    client = MetaClient(settings.meta_access_token, settings.meta_graph_version)
    payload = {"user": client.validate_token(), "pages": client.list_pages()}
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analisis de comentarios de redes sociales.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sample = subparsers.add_parser("sample", help="Ejecuta el flujo con datos de muestra.")
    sample.add_argument("--sample-path", default="samples/facebook_comments_sample.json")
    sample.add_argument("--write-google", action="store_true")

    collect = subparsers.add_parser("collect", help="Descarga comentarios reales desde Meta Graph API.")
    collect.add_argument("--write-google", action="store_true")

    import_file = subparsers.add_parser("import-file", help="Importa comentarios desde un archivo exportado.")
    import_file.add_argument("--input", required=True, help="Ruta del CSV, TSV, JSON o JSONL exportado.")
    import_file.add_argument("--network", default="facebook", help="Red social a registrar si el archivo no trae columna.")
    import_file.add_argument(
        "--source-account",
        default="archivo_exportado",
        help="Cuenta o pagina a registrar si el archivo no trae columna.",
    )
    import_file.add_argument("--write-google", action="store_true")

    subparsers.add_parser("validate-config", help="Muestra configuracion sin revelar secretos.")
    subparsers.add_parser("list-pages", help="Lista paginas administradas visibles para el token.")

    args = parser.parse_args(argv)
    settings = Settings.from_env()

    if args.command == "validate-config":
        return cmd_validate_config(settings)
    if args.command == "list-pages":
        return cmd_list_pages(settings)
    if args.command == "sample":
        result = run_pipeline(
            "sample",
            settings,
            sample_path=Path(args.sample_path),
            write_google=args.write_google,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    if args.command == "collect":
        result = run_pipeline("collect", settings, write_google=args.write_google)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    if args.command == "import-file":
        result = run_pipeline(
            "import_file",
            settings,
            import_path=Path(args.input),
            import_network=args.network,
            import_source_account=args.source_account,
            write_google=args.write_google,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
