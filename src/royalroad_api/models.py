"""Dataclasses mirroring the TS interfaces.

These are plain data containers returned by the parsers. Field names match the
TS interfaces (camelCase preserved where the TS used it, e.g. ``id``) so the
port stays recognisable next to the original source.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class FictionBlurb:
    """Base fiction list-item, shared by every list parser."""

    id: int
    type: str
    title: str
    image: str
    tags: list[str] = field(default_factory=list)


@dataclass
class LatestItem:
    name: str
    link: str
    created: int | None  # epoch milliseconds (None if unparseable)


@dataclass
class LatestBlurb(FictionBlurb):
    latest: list[LatestItem] = field(default_factory=list)


@dataclass
class NewReleaseBlurb(FictionBlurb):
    description: str = ""


@dataclass
class FictionStats:
    pages: int = 0
    latest: int | None = None  # epoch milliseconds
    rating: float = 0.0
    chapters: int = 0
    followers: int = 0


@dataclass
class PopularBlurb(FictionBlurb):
    description: str = ""
    stats: FictionStats = field(default_factory=FictionStats)


# best-rated uses the exact same shape as active-popular
BestBlurb = PopularBlurb


@dataclass
class SearchBlurb:
    id: int
    title: str
    pages: int
    image: str
    description: str


# --- Detailed fiction / chapter / profile models (for the scaffolded services) ---


@dataclass
class FictionChapter:
    id: int
    title: str
    release: int | None  # epoch ms


@dataclass
class FictionAuthor:
    id: int
    name: str
    title: str
    avatar: str


@dataclass
class FictionViews:
    total: int = 0
    average: int = 0


@dataclass
class FictionScore:
    style: float = 0.0
    story: float = 0.0
    grammar: float = 0.0
    overall: float = 0.0
    character: float = 0.0


@dataclass
class FictionDetailStats:
    pages: int = 0
    ratings: int = 0
    favorites: int = 0
    followers: int = 0
    views: FictionViews = field(default_factory=FictionViews)
    score: FictionScore = field(default_factory=FictionScore)


@dataclass
class Fiction:
    type: str
    title: str
    image: str
    status: str
    description: str
    tags: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: FictionDetailStats = field(default_factory=FictionDetailStats)
    author: FictionAuthor | None = None
    chapters: list[FictionChapter] = field(default_factory=list)


@dataclass
class Review:
    posted: int
    content: str
    author: dict  # {id, name, avatar}
    score: dict  # {overall, style?, story?, grammar?, character?}


@dataclass
class Chapter:
    content: str
    preNote: str
    postNote: str
    next: int
    previous: int


@dataclass
class ChapterComment:
    id: int
    posted: int | None
    content: str
    author: dict  # {id, name, avatar}


@dataclass
class ProfileAuthorStats:
    words: int = 0
    reviews: int = 0
    fictions: int = 0
    followers: int = 0
    favorites: int = 0


@dataclass
class ProfileOverview:
    name: str
    avatar: str
    active: int | None
    gender: str
    joined: int | None
    follows: int
    ratings: int
    location: str
    favorites: int
    biography: str
    authorStats: ProfileAuthorStats = field(default_factory=ProfileAuthorStats)


@dataclass
class RoyalResponse(Generic[T]):
    """Lightweight mirror of the TS ``RoyalResponse<T>`` wrapper.

    Faithful to the original surface: ``.data`` holds the payload, ``.success``
    and ``.timestamp`` (epoch ms) round it out. If you prefer the payload
    directly, just read ``.data``.
    """

    data: T
    success: bool = True
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))
