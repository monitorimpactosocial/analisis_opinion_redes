import unittest

from analisis_opinion_redes.analyzer import analyze_comment
from analisis_opinion_redes.models import RawComment


def make_comment(message: str) -> RawComment:
    return RawComment(
        network="facebook",
        source_account="pagina_demo",
        post_id="post",
        post_url="",
        post_created_at="2026-06-18T00:00:00+0000",
        comment_id="comment",
        comment_created_at="2026-06-18T01:00:00+0000",
        message=message,
        author_id_hash="hash",
        author_name="",
        like_count=0,
        reply_count=0,
        parent_id="",
    )


class AnalyzerTest(unittest.TestCase):
    def test_positive_comment(self):
        result = analyze_comment(make_comment("Excelente iniciativa, gracias."))
        self.assertEqual(result.sentiment, "positivo")
        self.assertEqual(result.category, "elogio")
        self.assertFalse(result.needs_response)

    def test_urgent_claim_requires_response(self):
        result = analyze_comment(make_comment("Reclamo urgente: hay un problema y no responden."))
        self.assertEqual(result.sentiment, "negativo")
        self.assertEqual(result.urgency, "alta")
        self.assertTrue(result.needs_response)

    def test_question_requires_response(self):
        result = analyze_comment(make_comment("Tengo una consulta sobre trabajo."))
        self.assertEqual(result.category, "consulta")
        self.assertTrue(result.needs_response)


if __name__ == "__main__":
    unittest.main()

