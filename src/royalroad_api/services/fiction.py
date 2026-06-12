"""STUB service: a single fiction, its reviews, random fiction.

Port target: FictionService in services/fiction.ts. Wiring mirrors the fully
implemented services/fictions.py — fill in parsers/fiction.py and these calls
work. All three endpoints are read-only (no auth needed).
"""

from __future__ import annotations

from .._parsing import get_last_page
from ..models import RoyalResponse
from ..parsers import fiction as parser
from ..requester import AsyncRequester, Requester


class FictionService:
    def __init__(self, req: Requester) -> None:
        self._req = req

    def get_fiction(self, id: int) -> RoyalResponse:
        body = self._req.get(f"/fiction/{id}")
        return RoyalResponse(parser.parse_fiction(body))

    def get_random(self) -> RoyalResponse:
        body = self._req.get("/fiction/random")
        return RoyalResponse(parser.parse_fiction(body))

    def get_reviews(self, id: int, page: int | str = 1) -> RoyalResponse:
        path = f"/fiction/{id}"
        if page == "last":
            page = get_last_page(self._req.get(path))
        body = self._req.get(path, {"reviews": str(page)})
        return RoyalResponse(parser.parse_reviews(body))


class AsyncFictionService:
    def __init__(self, req: AsyncRequester) -> None:
        self._req = req

    async def get_fiction(self, id: int) -> RoyalResponse:
        body = await self._req.get(f"/fiction/{id}")
        return RoyalResponse(parser.parse_fiction(body))

    async def get_random(self) -> RoyalResponse:
        body = await self._req.get("/fiction/random")
        return RoyalResponse(parser.parse_fiction(body))

    async def get_reviews(self, id: int, page: int | str = 1) -> RoyalResponse:
        path = f"/fiction/{id}"
        if page == "last":
            page = get_last_page(await self._req.get(path))
        body = await self._req.get(path, {"reviews": str(page)})
        return RoyalResponse(parser.parse_reviews(body))
