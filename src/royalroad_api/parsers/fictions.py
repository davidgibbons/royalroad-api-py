"""Pure parsers for the public fiction lists.

Direct 1:1 port of the FictionsParser class in services/fictions.ts. Each
function takes raw HTML and returns dataclasses; no I/O happens here, so both
the sync and async services call straight into these.

cheerio -> selectolax cheat-sheet used throughout:
    $('.sel')                 tree.css('.sel')           (list)
    $(el).find('.sel')        el.css('.sel') / css_first
    $(el).children('a')       el.css('> a') (direct child)
    .text()                   node_text(node)
    .attr('x')                attr(node, 'x')
"""

from __future__ import annotations

from selectolax.parser import HTMLParser, Node

from .._parsing import STATS_KEYS, attr, node_text, to_epoch_ms
from ..models import (
    FictionBlurb,
    FictionStats,
    LatestBlurb,
    LatestItem,
    NewReleaseBlurb,
    PopularBlurb,
    SearchBlurb,
)


def _id_from_href(href: str | None) -> int:
    """Fiction id is the 3rd path segment: /fiction/12345/slug -> 12345."""
    if not href:
        return 0
    parts = href.split("/")
    try:
        return int(parts[2])
    except (IndexError, ValueError):
        return 0


def _parse_blurb(el: Node) -> FictionBlurb:
    """Port of FictionsParser.parseBlurb — the fields common to every list."""
    title_el = el.css_first(".fiction-title a")
    title = node_text(title_el)
    image = attr(el.css_first("img"), "src") or ""
    type_ = node_text(el.css_first("span.label.bg-blue-hoki"))
    id_ = _id_from_href(attr(title_el, "href"))
    tags = [node_text(tag) for tag in el.css("a.label.fiction-tag")]
    return FictionBlurb(id=id_, type=type_, title=title, image=image, tags=tags)


def parse_popular(html: str) -> list[PopularBlurb]:
    """Port of parsePopular — also used for best-rated (identical shape)."""
    tree = HTMLParser(html)
    fictions: list[PopularBlurb] = []

    for el in tree.css(".fiction-list-item"):
        description = ""
        desc_container = el.css_first(".margin-top-10.col-xs-12")
        if desc_container is not None:
            for para in desc_container.css("p"):
                description += node_text(para) + "\n"

        stats = FictionStats()
        stats.latest = to_epoch_ms(attr(el.css_first("time"), "datetime"))
        rating_title = attr(el.css_first(".star"), "title")
        try:
            stats.rating = float(rating_title) if rating_title else 0.0
        except ValueError:
            stats.rating = 0.0

        for stat in el.css("span"):
            text = node_text(stat).lower()
            parts = text.split(" ")
            if len(parts) < 2:
                continue
            key = parts[1]
            try:
                value = int(parts[0].replace(",", ""))
            except ValueError:
                continue
            if key in STATS_KEYS and key not in ("latest", "rating"):
                setattr(stats, key, value)

        blurb = _parse_blurb(el)
        fictions.append(
            PopularBlurb(
                id=blurb.id,
                type=blurb.type,
                title=blurb.title,
                image=blurb.image,
                tags=blurb.tags,
                description=description,
                stats=stats,
            )
        )

    return fictions


# best-rated is parsed exactly like active-popular
parse_best = parse_popular


def parse_latest(html: str) -> list[LatestBlurb]:
    """Port of parseLatest."""
    tree = HTMLParser(html)
    fictions: list[LatestBlurb] = []

    for el in tree.css(".fiction-list-item"):
        latest: list[LatestItem] = []
        for item in el.css("li.list-item"):
            latest.append(
                LatestItem(
                    link=attr(item.css_first("a"), "href") or "",
                    name=node_text(item.css_first("span.col-xs-8")),
                    created=to_epoch_ms(node_text(item.css_first("time"))),
                )
            )

        blurb = _parse_blurb(el)
        fictions.append(
            LatestBlurb(
                id=blurb.id,
                type=blurb.type,
                title=blurb.title,
                image=blurb.image,
                tags=blurb.tags,
                latest=latest,
            )
        )

    return fictions


def parse_new_releases(html: str) -> list[NewReleaseBlurb]:
    """Port of parseNewReleases."""
    tree = HTMLParser(html)
    fictions: list[NewReleaseBlurb] = []

    for el in tree.css("div.fiction-list-item"):
        description = ""
        hidden = el.css_first("div.hidden-content")
        if hidden is not None:
            for p in hidden.css("p"):
                description += node_text(p).strip() + "\n"
        description = description.strip()

        blurb = _parse_blurb(el)
        fictions.append(
            NewReleaseBlurb(
                id=blurb.id,
                type=blurb.type,
                title=blurb.title,
                image=blurb.image,
                tags=blurb.tags,
                description=description,
            )
        )

    return fictions


def parse_search(html: str) -> list[SearchBlurb]:
    """Port of parseSearch."""
    tree = HTMLParser(html)
    fictions: list[SearchBlurb] = []

    for el in tree.css(".fiction-list-item"):
        image = attr(el.css_first("img"), "src") or ""
        title_el = el.css_first("h2.fiction-title a")
        title = node_text(title_el)
        id_ = _id_from_href(attr(title_el, "href"))

        # cheerio: $(el).find('i.fa-book').next().text() -> the page count sits
        # in the element immediately after the book icon. selectolax has no
        # jQuery .next(), so read the icon's parent text and pull the number.
        pages = 0
        book = el.css_first("i.fa-book")
        if book is not None and book.parent is not None:
            raw = node_text(book.parent).replace("Pages", "")
            digits = "".join(c for c in raw if c.isdigit())
            pages = int(digits) if digits else 0

        description = ""
        desc_container = el.css_first("div.margin-top-10.col-xs-12")
        if desc_container is not None:
            for child in desc_container.iter(include_text=False):
                description += node_text(child)

        fictions.append(
            SearchBlurb(
                id=id_, title=title, pages=pages, image=image, description=description
            )
        )

    return fictions
