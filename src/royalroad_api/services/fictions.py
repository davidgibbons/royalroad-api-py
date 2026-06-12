"""Public fiction lists and search — the fully-ported reference service.

Sync and async classes are thin wrappers: pick the list URL, fetch it, hand the
HTML to a pure parser, wrap the result. The two classes are deliberately near
identical (only ``await`` differs) because the substance lives in
``parsers.fictions``.
"""

from __future__ import annotations

from ..errors import RoyalError
from ..models import RoyalResponse
from ..parsers import fictions as parser
from ..requester import AsyncRequester, Requester


def _validate_list(body: str) -> str:
    """Port of the inline validPage() check in getList."""
    if "There is nothing here :(" in body:
        raise RoyalError("No fictions found.")
    return body


class FictionsService:
    def __init__(self, req: Requester) -> None:
        self._req = req

    def _get_list(self, type_: str, page: int) -> str:
        body = self._req.get(f"/fictions/{type_}", {"page": str(page)})
        return _validate_list(body)

    def get_latest(self, page: int = 1) -> RoyalResponse:
        return RoyalResponse(parser.parse_latest(self._get_list("latest-updates", page)))

    def get_popular(self, page: int = 1) -> RoyalResponse:
        return RoyalResponse(parser.parse_popular(self._get_list("active-popular", page)))

    def get_best(self, page: int = 1) -> RoyalResponse:
        return RoyalResponse(parser.parse_best(self._get_list("best-rated", page)))

    def get_new_releases(self, page: int = 1) -> RoyalResponse:
        return RoyalResponse(
            parser.parse_new_releases(self._get_list("new-releases", page))
        )

    def search(self, query: str, page: int = 1) -> RoyalResponse:
        return RoyalResponse(parser.parse_search(self._get_list(f"search?{query}", page)))


class AsyncFictionsService:
    def __init__(self, req: AsyncRequester) -> None:
        self._req = req

    async def _get_list(self, type_: str, page: int) -> str:
        body = await self._req.get(f"/fictions/{type_}", {"page": str(page)})
        return _validate_list(body)

    async def get_latest(self, page: int = 1) -> RoyalResponse:
        return RoyalResponse(
            parser.parse_latest(await self._get_list("latest-updates", page))
        )

    async def get_popular(self, page: int = 1) -> RoyalResponse:
        return RoyalResponse(
            parser.parse_popular(await self._get_list("active-popular", page))
        )

    async def get_best(self, page: int = 1) -> RoyalResponse:
        return RoyalResponse(parser.parse_best(await self._get_list("best-rated", page)))

    async def get_new_releases(self, page: int = 1) -> RoyalResponse:
        return RoyalResponse(
            parser.parse_new_releases(await self._get_list("new-releases", page))
        )

    async def search(self, query: str, page: int = 1) -> RoyalResponse:
        return RoyalResponse(
            parser.parse_search(await self._get_list(f"search?{query}", page))
        )
