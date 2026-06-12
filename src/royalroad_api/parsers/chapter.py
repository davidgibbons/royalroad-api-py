"""Parsers for a chapter and its comments. Port of ChapterParser in chapter.ts."""

from __future__ import annotations

from selectolax.parser import HTMLParser, Node

from .._parsing import (
    attr,
    inner_html,
    node_text,
    parse_relative_to_epoch_ms,
)
from ..models import Chapter, ChapterComment


def _nth(nodes: list[Node], i: int) -> Node | None:
    return nodes[i] if 0 <= i < len(nodes) else None


def _chapter_id_from_url(url: str) -> int:
    """Port of ChapterParser.getChapterID: split('/')[5], else -1."""
    split = url.split("/")
    if len(split) < 5:
        return -1
    try:
        return int(split[5])
    except (IndexError, ValueError):
        return -1


def parse_chapter(html: str) -> Chapter:
    """Port of ChapterParser.parseChapter."""
    tree = HTMLParser(html)

    notes = tree.css("div.author-note")
    pre_el = _nth(notes, 0)
    post_el = _nth(notes, 1)
    pre_note = node_text(pre_el.css_first("p")) if pre_el else ""
    post_note = node_text(post_el.css_first("p")) if post_el else ""

    content = inner_html(tree.css_first("div.chapter-inner.chapter-content")).strip()

    next_id = _link_chapter_id(tree, "i.fa-chevron-double-right")
    previous_id = _link_chapter_id(tree, "i.fa-chevron-double-left")

    return Chapter(
        content=content,
        preNote=pre_note,
        postNote=post_note,
        next=next_id,
        previous=previous_id,
    )


def _link_chapter_id(tree: HTMLParser, icon_selector: str) -> int:
    """The nav arrows are <a href=...><i class=icon></i></a>; read the parent."""
    icon = tree.css_first(icon_selector)
    if icon is None or icon.parent is None:
        return _chapter_id_from_url("")
    return _chapter_id_from_url(attr(icon.parent, "href") or "")


def parse_comments(html: str) -> list[ChapterComment]:
    """Port of ChapterParser.parseComments."""
    tree = HTMLParser(html)
    comments: list[ChapterComment] = []

    for el in tree.css("div.media.media-v2"):
        raw_id = attr(el, "id") or ""
        id_parts = raw_id.split("-")
        try:
            comment_id = int(id_parts[2])
        except (IndexError, ValueError):
            comment_id = 0

        # RR renders comment timestamps as relative text ("5 days") -> "... ago".
        posted = parse_relative_to_epoch_ms(node_text(el.css_first("time")) + " ago")

        content = ""
        body = el.css_first("div.media-body")
        if body is not None:
            for p in body.css("p"):
                text = node_text(p)
                if text:
                    content += text.strip() + "\n"
        content = content.strip()

        name_link = None
        name_span = el.css_first("span.name")
        if name_span is not None:
            name_link = name_span.css_first("a")
        author = {
            "avatar": attr(el.css_first("img"), "src") or "",
            "name": node_text(name_link).split("@")[0],
            "id": _id_from_parts(attr(name_link, "href"), 2),
        }

        comments.append(
            ChapterComment(
                id=comment_id, author=author, posted=posted, content=content
            )
        )

    return comments


def _id_from_parts(href: str | None, index: int) -> int:
    if not href:
        return 0
    parts = href.split("/")
    try:
        return int(parts[index])
    except (IndexError, ValueError):
        return 0
