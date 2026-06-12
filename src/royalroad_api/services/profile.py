"""STUB service: foreign user profiles.

Port target: ProfileService in services/profile.ts. Read-only.
"""

from __future__ import annotations

from ..models import RoyalResponse
from ..parsers import profile as parser
from ..requester import AsyncRequester, Requester


class ProfileService:
    def __init__(self, req: Requester) -> None:
        self._req = req

    def get_profile(self, id: int) -> RoyalResponse:
        body = self._req.get(f"/profile/{id}")
        return RoyalResponse(parser.parse_profile(body))


class AsyncProfileService:
    def __init__(self, req: AsyncRequester) -> None:
        self._req = req

    async def get_profile(self, id: int) -> RoyalResponse:
        body = await self._req.get(f"/profile/{id}")
        return RoyalResponse(parser.parse_profile(body))
