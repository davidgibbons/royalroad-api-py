"""Container classes — the public entry points, mirroring royalroad.ts.

``RoyalRoadAPI`` is the sync facade, ``AsyncRoyalRoadAPI`` the async one. Each
owns a requester (shared cookie session) and exposes the services as
attributes, exactly like the TS ``RoyalRoadAPI``.
"""

from __future__ import annotations

from .requester import AsyncRequester, Requester
from .services.chapter import AsyncChapterService, ChapterService
from .services.fiction import AsyncFictionService, FictionService
from .services.fictions import AsyncFictionsService, FictionsService
from .services.profile import AsyncProfileService, ProfileService


class RoyalRoadAPI:
    """Synchronous RoyalRoad API client."""

    def __init__(self, requester: Requester | None = None) -> None:
        self._req = requester or Requester()
        self.fictions = FictionsService(self._req)
        self.fiction = FictionService(self._req)
        self.chapter = ChapterService(self._req)
        self.profile = ProfileService(self._req)

    @property
    def is_authenticated(self) -> bool:
        return self._req.is_authenticated

    def close(self) -> None:
        self._req.close()

    def __enter__(self) -> "RoyalRoadAPI":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


class AsyncRoyalRoadAPI:
    """Asynchronous RoyalRoad API client."""

    def __init__(self, requester: AsyncRequester | None = None) -> None:
        self._req = requester or AsyncRequester()
        self.fictions = AsyncFictionsService(self._req)
        self.fiction = AsyncFictionService(self._req)
        self.chapter = AsyncChapterService(self._req)
        self.profile = AsyncProfileService(self._req)

    @property
    def is_authenticated(self) -> bool:
        return self._req.is_authenticated

    async def aclose(self) -> None:
        await self._req.aclose()

    async def __aenter__(self) -> "AsyncRoyalRoadAPI":
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()
