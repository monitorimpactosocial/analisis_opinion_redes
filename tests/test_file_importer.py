import tempfile
import unittest
from pathlib import Path

from analisis_opinion_redes.file_importer import load_exported_comments


class FileImporterTest(unittest.TestCase):
    def test_imports_csv_with_spanish_columns(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "comentarios.csv"
            path.write_text(
                "\n".join(
                    [
                        "fecha;red;pagina;comentario;autor;likes;respuestas",
                        "19/06/2026 08:30;facebook;Monitorimpactosocial;Excelente iniciativa;Persona Demo;2;1",
                    ]
                ),
                encoding="utf-8",
            )
            comments = load_exported_comments(
                path,
                network="facebook",
                source_account="Monitorimpactosocial",
                salt="test",
            )
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0].message, "Excelente iniciativa")
        self.assertEqual(comments[0].source_account, "Monitorimpactosocial")
        self.assertEqual(comments[0].like_count, 2)
        self.assertEqual(comments[0].reply_count, 1)
        self.assertTrue(comments[0].comment_created_at.startswith("2026-06-19"))
        self.assertTrue(comments[0].author_id_hash)
        self.assertEqual(comments[0].author_name, "")

    def test_imports_sample_like_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "comentarios.json"
            path.write_text(
                """
                {
                  "network": "facebook",
                  "source_account": "pagina_demo",
                  "posts": [
                    {
                      "id": "post_1",
                      "permalink_url": "https://example.test/post_1",
                      "created_time": "2026-06-19T08:00:00+0000",
                      "comments": [
                        {"id": "c1", "created_time": "2026-06-19T09:00:00+0000", "message": "Muy bueno"}
                      ]
                    }
                  ]
                }
                """,
                encoding="utf-8",
            )
            comments = load_exported_comments(path, salt="test")
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0].post_id, "post_1")
        self.assertEqual(comments[0].comment_id, "c1")

    def test_imports_nested_author_without_storing_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "comentarios.jsonl"
            path.write_text(
                '{"message":"Consulta sobre empleo","created_time":"2026-06-19T09:00:00+0000","from":{"id":"u1","name":"Persona Demo"},"parent":{"id":"p1"}}\n',
                encoding="utf-8",
            )
            comments = load_exported_comments(path, salt="test")
        self.assertEqual(len(comments), 1)
        self.assertTrue(comments[0].author_id_hash)
        self.assertEqual(comments[0].author_name, "")
        self.assertEqual(comments[0].parent_id, "p1")


if __name__ == "__main__":
    unittest.main()
