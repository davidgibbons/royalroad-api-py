"""STUB service: chapters and chapter comments.

Port target: ChapterService in services/chapter.ts. get_chapter / get_comments
are read-only; publish / post_comment require authentication (left as stubs,
they belong with the auth/user work).
"""

from __future__ import annotations

from .._parsing import get_last_page
from ..models import RoyalResponse
from ..parsers import chapter as parser
from ..requester import AsyncRequester, Requester


class ChapterService:
    def __init__(self, req: Requester) -> None:
        self._req = req

    def get_chapter(self, chapter_id: int) -> RoyalResponse:
        body = self._req.get(f"/fiction/0/_/chapter/{chapter_id}/_")
        return RoyalResponse(parser.parse_chapter(body))

    def get_comments(self, chapter_id: int, page: int | str = 1) -> RoyalResponse:
        path = f"/fiction/chapter/{chapter_id}/comments/"
        if page == "last":
            page = get_last_page(self._req.get(path))
        body = self._req.get(f"{path}{page}")
        return RoyalResponse(parser.parse_comments(body))

    def publish(self, fiction_id: int, chapter: dict) -> RoyalResponse:
        # Requires auth + token POST — see ChapterService.publish in chapter.ts.
        raise NotImplementedError("publish: auth-only, port with the user service")

    def post_comment(self, chapter_id: int, content: str) -> RoyalResponse:
        # Requires auth + token POST — see ChapterService.postComment.
        raise NotImplementedError("post_comment: auth-only, port with the user service")


class AsyncChapterService:
    def __init__(self, req: AsyncRequester) -> None:
        self._req = req

    async def get_chapter(self, chapter_id: int) -> RoyalResponse:
        body = await self._req.get(f"/fiction/0/_/chapter/{chapter_id}/_")
        return RoyalResponse(parser.parse_chapter(body))

    async def get_comments(self, chapter_id: int, page: int | str = 1) -> RoyalResponse:
        path = f"/fiction/chapter/{chapter_id}/comments/"
        if page == "last":
            page = get_last_page(await self._req.get(path))
        body = await self._req.get(f"{path}{page}")
        return RoyalResponse(parser.parse_comments(body))

    async def publish(self, fiction_id: int, chapter: dict) -> RoyalResponse:
        raise NotImplementedError("publish: auth-only, port with the user service")

    async def post_comment(self, chapter_id: int, content: str) -> RoyalResponse:
        raise NotImplementedError("post_comment: auth-only, port with the user service")
