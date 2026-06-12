"""HTTP layer — the only place sync and async diverge.

Both requesters share the exact same cookie handling, headers, status checks
and body-error detection. The only difference is ``httpx.Client`` vs
``httpx.AsyncClient`` and the ``await``. All parsing lives in ``_parsing``/
``parsers`` and is shared.
"""

from __future__ import annotations

import httpx

from . import __version__
from ._parsing import catch_generic_error, find_token
from .errors import RoyalError

HOST_NAME = "www.royalroad.com"
BASE_ADDRESS = f"https://{HOST_NAME}"
USER_AGENT = f"royalroad-api@{__version__}:github.com/fs-c/royalroad-api"

AUTH_COOKIE = ".AspNetCore.Identity.Application"


def _check_response(
    status_code: int,
    body: str,
    *,
    ignore_status: bool,
    ignore_parser: bool,
    success_status: int,
) -> str:
    """Shared validation for both stacks. Returns the body or raises."""
    if status_code != success_status and not ignore_status:
        raise RoyalError(f"Request error: HTTP {status_code}")
    generic = catch_generic_error(body)
    if not ignore_parser and generic is not None:
        raise RoyalError(generic)
    return body


class Requester:
    """Synchronous requester backed by ``httpx.Client``."""

    def __init__(self, client: httpx.Client | None = None) -> None:
        self._client = client or httpx.Client(
            base_url=BASE_ADDRESS,
            headers={"User-Agent": USER_AGENT},
            follow_redirects=True,
            timeout=30.0,
        )

    @property
    def is_authenticated(self) -> bool:
        return AUTH_COOKIE in self._client.cookies

    def get(
        self,
        path: str,
        data: dict[str, str] | None = None,
        *,
        ignore_status: bool = False,
        ignore_parser: bool = False,
        success_status: int = 200,
    ) -> str:
        resp = self._client.get(path, params=data or {})
        return _check_response(
            resp.status_code,
            resp.text,
            ignore_status=ignore_status,
            ignore_parser=ignore_parser,
            success_status=success_status,
        )

    def post(
        self,
        path: str,
        data: dict[str, str],
        *,
        fetch_token: bool = False,
        ignore_status: bool = False,
        ignore_parser: bool = False,
        success_status: int = 200,
    ) -> str:
        if fetch_token:
            data = {**data, "__RequestVerificationToken": self._fetch_token(path)}
        resp = self._client.post(path, data=data)
        return _check_response(
            resp.status_code,
            resp.text,
            ignore_status=ignore_status,
            ignore_parser=ignore_parser,
            success_status=success_status,
        )

    def _fetch_token(self, path: str) -> str:
        # Disregard ignore_parser here: we must know when the token is missing.
        body = self.get(path)
        token = find_token(body)
        if not token:
            raise RoyalError("Token not found.")
        return token

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "Requester":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


class AsyncRequester:
    """Asynchronous requester backed by ``httpx.AsyncClient``."""

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client or httpx.AsyncClient(
            base_url=BASE_ADDRESS,
            headers={"User-Agent": USER_AGENT},
            follow_redirects=True,
            timeout=30.0,
        )

    @property
    def is_authenticated(self) -> bool:
        return AUTH_COOKIE in self._client.cookies

    async def get(
        self,
        path: str,
        data: dict[str, str] | None = None,
        *,
        ignore_status: bool = False,
        ignore_parser: bool = False,
        success_status: int = 200,
    ) -> str:
        resp = await self._client.get(path, params=data or {})
        return _check_response(
            resp.status_code,
            resp.text,
            ignore_status=ignore_status,
            ignore_parser=ignore_parser,
            success_status=success_status,
        )

    async def post(
        self,
        path: str,
        data: dict[str, str],
        *,
        fetch_token: bool = False,
        ignore_status: bool = False,
        ignore_parser: bool = False,
        success_status: int = 200,
    ) -> str:
        if fetch_token:
            data = {**data, "__RequestVerificationToken": await self._fetch_token(path)}
        resp = await self._client.post(path, data=data)
        return _check_response(
            resp.status_code,
            resp.text,
            ignore_status=ignore_status,
            ignore_parser=ignore_parser,
            success_status=success_status,
        )

    async def _fetch_token(self, path: str) -> str:
        body = await self.get(path)
        token = find_token(body)
        if not token:
            raise RoyalError("Token not found.")
        return token

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncRequester":
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()
