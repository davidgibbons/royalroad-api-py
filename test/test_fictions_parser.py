"""Parser tests against saved HTML fixtures (no network)."""

from __future__ import annotations

from pathlib import Path

from royalroad_api.parsers import fictions

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_parse_popular_extracts_both_items():
    result = fictions.parse_popular(_load("active-popular.html"))
    assert len(result) == 2


def test_parse_popular_blurb_fields():
    first = fictions.parse_popular(_load("active-popular.html"))[0]
    assert first.id == 12345
    assert first.title == "The First Story"
    assert first.type == "ORIGINAL"
    assert first.image == "https://www.royalroadcdn.com/covers/12345.jpg"
    assert first.tags == ["Fantasy", "Adventure"]


def test_parse_popular_description_joins_paragraphs():
    first = fictions.parse_popular(_load("active-popular.html"))[0]
    assert first.description == (
        "A hero rises in a doomed kingdom.\nSecond paragraph of the blurb.\n"
    )


def test_parse_popular_stats():
    first = fictions.parse_popular(_load("active-popular.html"))[0]
    stats = first.stats
    assert stats.followers == 12345
    assert stats.pages == 678
    assert stats.chapters == 42
    assert stats.rating == 4.65
    # 2024-01-15T10:30:00+00:00 -> epoch ms
    assert stats.latest == 1705314600000


def test_parse_popular_second_item():
    second = fictions.parse_popular(_load("active-popular.html"))[1]
    assert second.id == 67890
    assert second.type == "FANFICTION"
    assert second.tags == ["LitRPG"]
    assert second.stats.followers == 2000
    assert second.stats.pages == 150
    assert second.stats.chapters == 9
    assert second.stats.rating == 4.10
