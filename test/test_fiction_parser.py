"""Fiction + reviews parser tests against saved fixtures (no network)."""

from __future__ import annotations

from pathlib import Path

from royalroad_api.parsers import fiction

FIXTURES = Path(__file__).parent / "fixtures"


def _fiction():
    return fiction.parse_fiction((FIXTURES / "fiction.html").read_text(encoding="utf-8"))


def test_header_fields():
    f = _fiction()
    assert f.title == "Test Fiction"
    assert f.image == "https://www.royalroadcdn.com/covers/12.jpg"
    assert f.type == "ORIGINAL"
    assert f.status == "ONGOING"
    assert f.tags == ["Fantasy", "Action"]
    assert f.warnings == ["Gore", "Profanity"]
    assert f.description == "A long description."


def test_author():
    a = _fiction().author
    assert a is not None
    assert a.id == 777
    assert a.name == "AuthorName"
    assert a.title == "Sage (4)"
    assert a.avatar == "https://www.royalroadcdn.com/avatars/777.png"


def test_stats():
    s = _fiction().stats
    assert s.pages == 678
    assert s.ratings == 1200
    assert s.followers == 5000
    assert s.favorites == 2500
    assert s.views.total == 1000000
    assert s.views.average == 10000
    assert s.score.overall == 4.5
    assert s.score.style == 4.2
    assert s.score.story == 4.6
    assert s.score.character == 4.1
    assert s.score.grammar == 4.8


def test_chapters():
    chapters = _fiction().chapters
    assert len(chapters) == 2
    assert chapters[0].id == 100
    assert chapters[0].title == "Chapter 1"
    assert chapters[0].release == 1705314600000  # 2024-01-15T10:30:00Z
    assert chapters[1].id == 101


def test_reviews():
    reviews = fiction.parse_reviews(
        (FIXTURES / "reviews.html").read_text(encoding="utf-8")
    )
    assert len(reviews) == 1
    r = reviews[0]
    assert r.posted == 1700000000
    assert r.content == "This is a great story."
    assert r.author["id"] == 55
    assert r.author["name"] == "ReviewerName"
    assert r.author["avatar"] == "https://www.royalroadcdn.com/avatars/55.png"
    assert r.score["overall"] == 4.5
