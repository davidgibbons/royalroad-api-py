"""Chapter + comments parser tests against saved fixtures (no network)."""

from __future__ import annotations

from pathlib import Path

from royalroad_api.parsers import chapter

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_parse_chapter():
    c = chapter.parse_chapter(_load("chapter.html"))
    assert c.preNote == "Pre note here."
    assert c.postNote == "Post note here."
    assert c.content == "<p>Hello</p><p>World</p>"
    assert c.next == 101
    assert c.previous == 99


def test_parse_comments():
    comments = chapter.parse_comments(_load("chapter-comments.html"))
    assert len(comments) == 1
    c = comments[0]
    assert c.id == 321
    assert c.content == "Nice chapter.\nLooking forward to more."
    assert c.author["id"] == 88
    assert c.author["name"] == "CommenterName"
    assert c.author["avatar"] == "https://www.royalroadcdn.com/avatars/88.png"
    # relative "5 days ago" -> some epoch ms in the past
    assert isinstance(c.posted, int)


def test_chapter_id_helper():
    assert chapter._chapter_id_from_url("/fiction/12/s/chapter/100/c") == 100
    assert chapter._chapter_id_from_url("") == -1
    assert chapter._chapter_id_from_url("/a/b") == -1
