# royalroad-api (Python)

A minimal, unofficial Python API for [royalroad.com](https://www.royalroad.com) —
a port of the TypeScript [`@fsoc/royalroadl-api`](https://github.com/fs-c/royalroad-api).

RoyalRoad exposes no public API, so this scrapes HTML. It is **inherently
fragile** to site changes — selectors will break when RR changes its markup.

## Install

From a published GitHub Release (built by CI on each `v*` tag):

```bash
# prebuilt wheel attached to the release
pip install https://github.com/davidgibbons/royalroad-api-py/releases/download/v0.1.0/royalroad_api-0.1.0-py3-none-any.whl

# or straight from source at a tag
pip install "git+https://github.com/davidgibbons/royalroad-api-py@v0.1.0"
```

From a clone (with test deps):

```bash
pip install -e ".[dev]"
```

Runtime deps: `httpx`, `selectolax`, `python-dateutil`.

> **Note:** GitHub Packages has no Python (pip) registry — it hosts npm,
> Docker, Maven, NuGet, and RubyGems only. So releases are published as
> **GitHub Release assets** (wheel + sdist), installable with the commands
> above. If you later want a plain `pip install royalroad-api`, publish to
> PyPI instead (the release workflow is easy to extend for that).

## Releasing

The version is single-sourced from `__version__` in
`src/royalroad_api/__init__.py` (hatchling reads it dynamically). To cut a
release:

1. Bump `__version__`.
2. Commit, then tag and push: `git tag v0.1.0 && git push origin v0.1.0`.

The `Release` workflow runs the tests, verifies the tag matches `__version__`,
builds the wheel + sdist, `twine check`s them, and attaches them to an
auto-generated GitHub Release. CI (`ci.yml`) runs the test matrix on every push
and PR.

## Usage

Sync:

```python
from royalroad_api import RoyalRoadAPI

with RoyalRoadAPI() as api:
    res = api.fictions.get_popular()
    for fic in res.data:
        print(fic.id, fic.title, fic.stats.followers)
```

Async:

```python
import asyncio
from royalroad_api import AsyncRoyalRoadAPI

async def main():
    async with AsyncRoyalRoadAPI() as api:
        res = await api.fictions.get_popular()
        print([f.title for f in res.data])

asyncio.run(main())
```

Results are wrapped in `RoyalResponse` (mirroring the TS lib): read `.data` for
the payload. `.success` and `.timestamp` (epoch ms) round it out.

## Status

| Service    | Methods                                            | State |
|------------|----------------------------------------------------|-------|
| `fictions` | `get_latest` `get_popular` `get_best` `get_new_releases` `search` | **Implemented** (sync + async) |
| `fiction`  | `get_fiction` `get_random` `get_reviews`           | **Implemented** (sync + async) |
| `chapter`  | `get_chapter` `get_comments`                       | **Implemented** (sync + async) |
| `profile`  | `get_profile`                                      | **Implemented** (sync + async) |
| `chapter`  | `publish` `post_comment`                           | Stub — auth-only, deferred with the user service |
| auth/user  | login, register, etc.                              | Not ported (out of read-only scope) |

All read-only services are fully ported sync + async. The remaining stubs
(`chapter.publish` / `post_comment`) require an authenticated session and are
deferred along with the user/auth service.

## Architecture

```
parsers/   pure HTML -> dataclasses (no I/O)   <- shared by sync AND async
           (fictions, fiction, chapter, profile all implemented)
_parsing   shared helpers (dates, error detection, pagination)
requester  httpx.Client / httpx.AsyncClient    <- the only sync/async divergence
services/  thin wrappers: fetch -> parse -> wrap
royalroad  RoyalRoadAPI / AsyncRoyalRoadAPI containers
```

The key design choice: **parsing is pure and shared**. Sync vs async differs
only in the I/O layer and an `await`, so there is no duplicated scraping logic.

## Tests

```bash
pytest
```

Parser tests run against saved HTML fixtures in `test/fixtures/` and never hit
the network.

## License

MIT (same as the upstream project).
