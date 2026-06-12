"""Minimal Python RoyalRoad API.

Port of @fsoc/royalroadl-api (TypeScript). Scrapes RoyalRoad's HTML — no
official API exists, so it is inherently fragile to site changes.

Both sync and async clients are provided; all HTML parsing is shared between
them (see ``parsers`` / ``_parsing``).
"""

from __future__ import annotations

__version__ = "0.1.0"

from .errors import RoyalError
from .models import (
    BestBlurb,
    FictionBlurb,
    FictionStats,
    LatestBlurb,
    LatestItem,
    NewReleaseBlurb,
    PopularBlurb,
    RoyalResponse,
    SearchBlurb,
)
from .royalroad import AsyncRoyalRoadAPI, RoyalRoadAPI

__all__ = [
    "RoyalRoadAPI",
    "AsyncRoyalRoadAPI",
    "RoyalResponse",
    "RoyalError",
    "FictionBlurb",
    "PopularBlurb",
    "BestBlurb",
    "LatestBlurb",
    "LatestItem",
    "NewReleaseBlurb",
    "SearchBlurb",
    "FictionStats",
    "__version__",
]
