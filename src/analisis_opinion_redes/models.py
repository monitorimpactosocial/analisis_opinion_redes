from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class RawComment:
    network: str
    source_account: str
    post_id: str
    post_url: str
    post_created_at: str
    comment_id: str
    comment_created_at: str
    message: str
    author_id_hash: str
    author_name: str
    like_count: int
    reply_count: int
    parent_id: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class AnalyzedComment:
    raw: RawComment
    sentiment: str
    sentiment_score: int
    category: str
    urgency: str
    needs_response: bool
    matched_keywords: str

    def to_dict(self) -> dict:
        data = self.raw.to_dict()
        data.update(
            {
                "sentiment": self.sentiment,
                "sentiment_score": self.sentiment_score,
                "category": self.category,
                "urgency": self.urgency,
                "needs_response": self.needs_response,
                "matched_keywords": self.matched_keywords,
            }
        )
        return data

    def to_sheet_row(self, run_id: str) -> list:
        data = self.to_dict()
        return [
            run_id,
            data["network"],
            data["source_account"],
            data["post_id"],
            data["post_url"],
            data["post_created_at"],
            data["comment_id"],
            data["comment_created_at"],
            data["message"],
            data["author_id_hash"],
            data["author_name"],
            data["like_count"],
            data["reply_count"],
            data["parent_id"],
            data["sentiment"],
            data["sentiment_score"],
            data["category"],
            data["urgency"],
            data["needs_response"],
            data["matched_keywords"],
        ]

