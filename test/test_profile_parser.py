"""Profile parser tests against a saved fixture (no network)."""

from __future__ import annotations

from pathlib import Path

from royalroad_api.parsers import profile

FIXTURES = Path(__file__).parent / "fixtures"


def _profile():
    return profile.parse_profile((FIXTURES / "profile.html").read_text(encoding="utf-8"))


def test_overview_fields():
    p = _profile()
    assert p.name == "AuthorName"
    assert p.avatar == "https://www.royalroadcdn.com/avatars/777.png"
    assert p.follows == 100
    assert p.favorites == 50
    assert p.ratings == 30
    assert p.joined == 1500000000
    assert p.active == 1600000000
    assert p.gender == "Male"
    assert p.location == "Internet"
    assert p.biography == "Just a writer."


def test_author_stats():
    stats = _profile().authorStats
    assert stats.fictions == 5
    assert stats.words == 123456
    assert stats.reviews == 12
    assert stats.followers == 200
    assert stats.favorites == 40
