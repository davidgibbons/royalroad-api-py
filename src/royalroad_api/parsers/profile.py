"""Parser for a user profile page. Port of ProfileParser in profile.ts."""

from __future__ import annotations

from selectolax.parser import HTMLParser, Node

from .._parsing import attr, node_text, parse_number
from ..models import ProfileAuthorStats, ProfileOverview


def _nth(nodes: list[Node], i: int) -> Node | None:
    return nodes[i] if 0 <= i < len(nodes) else None


def parse_profile(html: str) -> ProfileOverview:
    """Port of ProfileParser.parseProfile."""
    tree = HTMLParser(html)

    avatar = ""
    pic = tree.css_first("div.profile-picture-container")
    if pic is not None:
        avatar = attr(pic.css_first("img"), "src") or ""

    stats_el = tree.css_first("div.profile-stats")
    name = node_text(stats_el.css_first("h1")).strip() if stats_el else ""

    stat_values = stats_el.css("span.stat-value") if stats_el else []
    follows = parse_number(node_text(_nth(stat_values, 0)))
    favorites = parse_number(node_text(_nth(stat_values, 1)))
    ratings = parse_number(node_text(_nth(stat_values, 2)))
    fictions = parse_number(node_text(_nth(stat_values, 3)))

    tbodies = tree.css("tbody")

    # tbody[0]: personal info
    p_info = _nth(tbodies, 0)
    joined = active = None
    gender = location = biography = ""
    if p_info is not None:
        times = p_info.css("time")
        joined_attr = attr(_nth(times, 0), "unixtime")
        active_attr = attr(_nth(times, 1), "unixtime")
        joined = int(joined_attr) if joined_attr else None
        active = int(active_attr) if active_attr else None

        tds = p_info.css("td")
        gender = node_text(_nth(tds, 2)).strip()
        location = node_text(_nth(tds, 3)).strip()
        biography = node_text(_nth(tds, 4)).strip()

    # tbody[2]: author info
    author_stats = ProfileAuthorStats(fictions=fictions)
    a_info = _nth(tbodies, 2)
    if a_info is not None:
        a_tds = a_info.css("td")
        author_stats.words = parse_number(node_text(_nth(a_tds, 1)))
        author_stats.reviews = parse_number(node_text(_nth(a_tds, 2)))
        author_stats.followers = parse_number(node_text(_nth(a_tds, 3)))
        author_stats.favorites = parse_number(node_text(_nth(a_tds, 4)))

    return ProfileOverview(
        name=name,
        avatar=avatar,
        gender=gender,
        active=active,
        joined=joined,
        follows=follows,
        ratings=ratings,
        location=location,
        favorites=favorites,
        biography=biography,
        authorStats=author_stats,
    )
