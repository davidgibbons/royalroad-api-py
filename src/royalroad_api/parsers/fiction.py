"""Parsers for a single fiction page and its reviews.

Port of FictionParser in services/fiction.ts.
"""

from __future__ import annotations

from selectolax.parser import HTMLParser, Node

from .._parsing import (
    attr,
    node_text,
    parse_number,
    parse_rating,
    time_to_epoch_ms,
)
from ..models import (
    Fiction,
    FictionAuthor,
    FictionChapter,
    FictionDetailStats,
    FictionScore,
    FictionViews,
    Review,
)


def _nth(nodes: list[Node], i: int) -> Node | None:
    return nodes[i] if 0 <= i < len(nodes) else None


def _rating_content(li: Node | None) -> str | None:
    """getContent(): the rating value lives in a span's data-content attr."""
    if li is None:
        return None
    return attr(li.css_first("span"), "data-content")


def parse_fiction(html: str) -> Fiction:
    """Port of FictionParser.parseFiction."""
    tree = HTMLParser(html)

    fic_title = tree.css_first("div.fic-title")
    title = node_text(fic_title.css_first("h1")) if fic_title else ""

    fic_header = tree.css_first("div.fic-header")
    image = (attr(fic_header.css_first("img"), "src") or "") if fic_header else ""

    labels = tree.css("span.bg-blue-hoki")
    type_ = node_text(_nth(labels, 0))
    status = node_text(_nth(labels, 1)).strip()

    tags_container = tree.css_first("span.tags")
    tags = (
        [node_text(el).strip() for el in tags_container.css("a.label")]
        if tags_container
        else []
    )

    # Warnings live in the list under the red "Warning" heading. The TS lib
    # used a bare `ul.list-inline`, which on current RR matches an earlier,
    # empty list — so we target the warning container precisely instead.
    warnings_container = tree.css_first("div.font-red-sunglo ul.list-inline")
    warnings = (
        [
            text
            for el in warnings_container.css("li")
            if (text := node_text(el).strip())
        ]
        if warnings_container
        else []
    )

    description = node_text(
        tree.css_first("div.description > div.hidden-content")
    ).strip()

    author = _parse_author(tree)
    stats = _parse_stats(tree)
    chapters = _parse_chapters(tree)

    return Fiction(
        type=type_,
        title=title,
        image=image,
        status=status,
        description=description,
        tags=tags,
        warnings=warnings,
        stats=stats,
        author=author,
        chapters=chapters,
    )


def _parse_author(tree: HTMLParser) -> FictionAuthor:
    author_el = tree.css_first(".portlet-body")
    if author_el is None:
        return FictionAuthor(id=0, name="", title="", avatar="")

    link = author_el.css_first(".mt-card-content a")
    name = node_text(link).strip()
    title = node_text(author_el.css_first(".mt-card-desc"))
    avatar = attr(author_el.css_first('img[data-type="avatar"]'), "src") or ""

    href = attr(link, "href") or ""
    parts = href.split("/")
    try:
        author_id = int(parts[2])
    except (IndexError, ValueError):
        author_id = 0

    return FictionAuthor(id=author_id, name=name, title=title, avatar=avatar)


def _parse_stats(tree: HTMLParser) -> FictionDetailStats:
    stats_content = tree.css_first("div.stats-content")
    if stats_content is None:
        return FictionDetailStats()

    unstyled = stats_content.css(".list-unstyled")
    ul_rating = _nth(unstyled, 0)
    ul_stats = _nth(unstyled, 1)
    rating_list = ul_rating.css("li") if ul_rating else []
    stats_list = ul_stats.css("li") if ul_stats else []

    def stat(i: int) -> int:
        return parse_number(node_text(_nth(stats_list, i)))

    def score(i: int) -> float:
        return parse_rating(_rating_content(_nth(rating_list, i)))

    return FictionDetailStats(
        pages=stat(11),
        ratings=stat(9),
        followers=stat(5),
        favorites=stat(7),
        views=FictionViews(total=stat(1), average=stat(3)),
        score=FictionScore(
            style=score(3),
            story=score(5),
            grammar=score(9),
            overall=score(1),
            character=score(7),
        ),
    )


def _parse_chapters(tree: HTMLParser) -> list[FictionChapter]:
    chapters: list[FictionChapter] = []
    tbody = tree.css_first("tbody")
    if tbody is None:
        return chapters

    for row in tbody.css("tr"):
        cells = row.css("td")
        title_cell = _nth(cells, 0)
        link = title_cell.css_first("a") if title_cell else None
        chapter_title = node_text(link).strip()

        href = attr(link, "href") or ""
        parts = href.split("/")
        try:
            chapter_id = int(parts[5])
        except (IndexError, ValueError):
            chapter_id = 0

        time_cell = _nth(cells, 1)
        time_node = time_cell.css_first("time") if time_cell else None
        release = time_to_epoch_ms(time_node)

        chapters.append(
            FictionChapter(id=chapter_id, title=chapter_title, release=release)
        )

    return chapters


def parse_reviews(html: str) -> list[Review]:
    """Port of FictionParser.parseReviews."""
    tree = HTMLParser(html)
    reviews: list[Review] = []

    for el in tree.css("div.review"):
        posted_raw = attr(el.css_first("time"), "unixtime")
        try:
            posted = int(posted_raw) if posted_raw else 0
        except ValueError:
            posted = 0

        content = ""
        for p in el.css("div.review-content"):
            content += node_text(p) + "\n"
        content = content.strip()

        meta = el.css_first("div.review-meta")
        author_link = meta.css_first("a") if meta else None
        author = {
            "name": node_text(author_link),
            "avatar": attr(el.css_first("img"), "src") or "",
            "id": _id_from_parts(attr(author_link, "href"), 2),
        }

        overall = 0.0
        container = el.css_first("div.overall-score-container")
        if container is not None:
            for child in container.iter(include_text=False):
                label = attr(child, "aria-label")
                if label and "stars" in label:
                    try:
                        overall = float(label.replace("stars", "").strip())
                    except ValueError:
                        overall = 0.0
                    break

        # TODO: advanced (per-axis) review scores; TS leaves these at 0 too.
        score = {
            "style": 0,
            "story": 0,
            "overall": overall,
            "grammar": 0,
            "character": 0,
        }

        reviews.append(
            Review(score=score, author=author, content=content, posted=posted)
        )

    return reviews


def _id_from_parts(href: str | None, index: int) -> int:
    if not href:
        return 0
    parts = href.split("/")
    try:
        return int(parts[index])
    except (IndexError, ValueError):
        return 0
