from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

import requests

from .models import RawComment


class MetaApiError(RuntimeError):
    pass


class MetaClient:
    def __init__(self, access_token: str, graph_version: str = "v23.0") -> None:
        self.access_token = access_token
        self.base_url = f"https://graph.facebook.com/{graph_version.strip('/')}"

    def _get(self, path_or_url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if path_or_url.startswith("https://"):
            url = path_or_url
            request_params = None
        else:
            url = f"{self.base_url}/{path_or_url.strip('/')}"
            request_params = dict(params or {})
            request_params["access_token"] = self.access_token

        response = requests.get(url, params=request_params, timeout=45)
        if response.status_code >= 400:
            try:
                detail = response.json()
            except ValueError:
                detail = {"error": response.text}
            raise MetaApiError(f"Meta API error {response.status_code}: {detail}")
        return response.json()

    def _paginate(
        self,
        path: str,
        params: dict[str, Any],
        item_limit: int | None = None,
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        payload = self._get(path, params)
        while True:
            items.extend(payload.get("data", []))
            if item_limit is not None and len(items) >= item_limit:
                return items[:item_limit]
            next_url = payload.get("paging", {}).get("next")
            if not next_url:
                return items
            payload = self._get(next_url)

    def validate_token(self) -> dict[str, Any]:
        return self._get("me", {"fields": "id,name"})

    def list_pages(self) -> list[dict[str, Any]]:
        pages = self._paginate(
            "me/accounts",
            {"fields": "id,name,tasks,category", "limit": 100},
        )
        return [
            {
                "id": page.get("id", ""),
                "name": page.get("name", ""),
                "category": page.get("category", ""),
                "tasks": page.get("tasks", []),
            }
            for page in pages
        ]

    def collect_page_comments(
        self,
        page_id: str,
        since: datetime,
        source_account: str,
        salt: str,
        store_author_name: bool,
        limit_posts: int,
        limit_comments_per_post: int,
        page_access_token: str | None = None,
    ) -> list[RawComment]:
        token_before = self.access_token
        if page_access_token:
            self.access_token = page_access_token
        try:
            posts = self._paginate(
                f"{page_id}/posts",
                {
                    "fields": "id,message,created_time,permalink_url",
                    "since": int(since.replace(tzinfo=timezone.utc).timestamp()),
                    "limit": min(limit_posts, 100),
                },
                item_limit=limit_posts,
            )
            comments: list[RawComment] = []
            for post in posts:
                post_comments = self._paginate(
                    f"{post['id']}/comments",
                    {
                        "fields": "id,message,created_time,permalink_url,like_count,comment_count,from,parent",
                        "since": int(since.replace(tzinfo=timezone.utc).timestamp()),
                        "order": "reverse_chronological",
                        "limit": min(limit_comments_per_post, 100),
                    },
                    item_limit=limit_comments_per_post,
                )
                for item in post_comments:
                    actor = item.get("from") or {}
                    actor_id = str(actor.get("id", ""))
                    actor_name = str(actor.get("name", "")) if store_author_name else ""
                    comments.append(
                        RawComment(
                            network="facebook",
                            source_account=source_account,
                            post_id=str(post.get("id", "")),
                            post_url=str(post.get("permalink_url", "")),
                            post_created_at=str(post.get("created_time", "")),
                            comment_id=str(item.get("id", "")),
                            comment_created_at=str(item.get("created_time", "")),
                            message=str(item.get("message", "")),
                            author_id_hash=hash_identifier(actor_id, salt) if actor_id else "",
                            author_name=actor_name,
                            like_count=int(item.get("like_count", 0) or 0),
                            reply_count=int(item.get("comment_count", 0) or 0),
                            parent_id=str((item.get("parent") or {}).get("id", "")),
                        )
                    )
            return comments
        finally:
            self.access_token = token_before


def hash_identifier(value: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}:{value}".encode("utf-8")).hexdigest()
