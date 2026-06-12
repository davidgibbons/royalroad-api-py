"""Service-level tests using a fake requester (no network).

Guards the request wiring — notably that search sends `title`/`page` as real
query params rather than folding the query into the path (which collided with
the page param and silently returned the popular list).
"""

from __future__ import annotations

from royalroad_api.services.fictions import AsyncFictionsService, FictionsService

# Minimal page that passes _validate_list and parses to an empty result set.
_EMPTY_PAGE = "<html><body><div class='fiction-list'></div></body></html>"


class FakeReq:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def get(self, path: str, data: dict | None = None) -> str:
        self.calls.append((path, data or {}))
        return _EMPTY_PAGE


class FakeAsyncReq:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    async def get(self, path: str, data: dict | None = None) -> str:
        self.calls.append((path, data or {}))
        return _EMPTY_PAGE


def test_search_sends_title_and_page_as_query_params():
    req = FakeReq()
    FictionsService(req).search("dungeon", page=2)
    assert req.calls == [("/fictions/search", {"title": "dungeon", "page": "2"})]


def test_search_does_not_fold_query_into_path():
    req = FakeReq()
    FictionsService(req).search("a&b=c")
    path, data = req.calls[0]
    assert path == "/fictions/search"  # no `?<query>` smuggled into the path
    assert data["title"] == "a&b=c"


def test_list_endpoints_use_page_param():
    req = FakeReq()
    svc = FictionsService(req)
    svc.get_popular(3)
    assert req.calls[-1] == ("/fictions/active-popular", {"page": "3"})


async def test_async_search_sends_title_and_page():
    req = FakeAsyncReq()
    await AsyncFictionsService(req).search("dungeon", page=2)
    assert req.calls == [("/fictions/search", {"title": "dungeon", "page": "2"})]
