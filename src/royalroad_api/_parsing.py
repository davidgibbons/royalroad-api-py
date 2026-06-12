"""Pure HTML/parsing helpers shared by sync and async paths.

Everything here operates on HTML strings (or selectolax nodes) and has no I/O,
so both the sync and async stacks import the same functions. This is the seam
that lets us support both styles without duplicating any scraping logic.
"""

from __future__ import annotations

import re
import time

from selectolax.parser import HTMLParser, Node

from dateutil import parser as _dateparser

# Maps the lowercase RR stat label -> FictionStats attribute name.
STATS_KEYS = ("pages", "latest", "rating", "chapters", "followers")

_RELATIVE_RE = re.compile(
    r"(\d+)\s+(second|minute|hour|day|week|month|year)s?\s+ago"
)
_UNIT_SECONDS = {
    "second": 1,
    "minute": 60,
    "hour": 3600,
    "day": 86400,
    "week": 604800,
    "month": 2592000,
    "year": 31536000,
}


def to_epoch_ms(value: str | None) -> int | None:
    """Parse a date string into epoch milliseconds, matching the TS use of
    ``date.js(...).getTime()``.

    Handles ISO-8601 ``datetime`` attributes cleanly. Relative strings like
    "5 days ago" (used by the latest-updates list) are not handled by dateutil;
    they return None for now.

    TODO: port date.js relative-time parsing for the latest-updates list.
    """
    if not value:
        return None
    try:
        dt = _dateparser.parse(value)
    except (ValueError, OverflowError, TypeError):
        return None
    return int(dt.timestamp() * 1000)


def node_text(node: Node | None) -> str:
    """cheerio ``.text()`` equivalent: combined text of all descendants."""
    if node is None:
        return ""
    return node.text(deep=True, separator="", strip=False)


def attr(node: Node | None, name: str) -> str | None:
    if node is None:
        return None
    return node.attributes.get(name)


def get_last_page(html: str) -> int:
    """Port of utils.ts getLastPage."""
    tree = HTMLParser(html)
    pagination = tree.css_first("ul.pagination")
    if pagination is None:
        return -1
    items = pagination.css("li")
    if not items:
        return -1
    link = items[-1].css_first("a")
    href = attr(link, "href")
    if not href or href == "javascript:;":
        return -1
    try:
        return int(href.split("#")[0].split("=")[1])
    except (IndexError, ValueError):
        return -1


def _catch_generic_error_legacy(tree: HTMLParser) -> str | None:
    # Usually 4xx, mostly 404 and 403.
    page404 = tree.css_first("div.page-404")
    error = node_text(page404.css_first("h3")).strip() if page404 else ""
    # These often are a result of invalid POSTs.
    alerts = tree.css("div.alert.alert-danger")
    alert = node_text(alerts[0]).strip() if alerts else ""
    return error or alert or None


def catch_generic_error(html: str) -> str | None:
    """Port of Requester.catchGenericError.

    RR returns 200 even for 404/403 and validation failures, so we sniff the
    body for the error containers and surface the message.
    """
    tree = HTMLParser(html)
    danger = tree.css_first("div.text-danger")
    error = None
    if danger is not None:
        li = danger.css_first("li")
        error = node_text(li).strip() or None
    legacy = _catch_generic_error_legacy(tree)
    return error or legacy


def find_token(html: str) -> str | None:
    """Extract the hidden __RequestVerificationToken (for POST/auth flows)."""
    tree = HTMLParser(html)
    node = tree.css_first('input[name="__RequestVerificationToken"]')
    value = attr(node, "value")
    return value or None


def parse_relative_to_epoch_ms(text: str | None, now_ms: int | None = None) -> int | None:
    """Parse a relative "5 days ago" string into epoch milliseconds.

    Equivalent to the TS use of ``date('... ago').getTime()``. ``now_ms`` is
    injectable so tests can be deterministic; otherwise the wall clock is used.
    """
    if not text:
        return None
    match = _RELATIVE_RE.search(text.lower())
    if not match:
        return None
    amount = int(match.group(1))
    unit = match.group(2)
    base = now_ms if now_ms is not None else int(time.time() * 1000)
    return base - amount * _UNIT_SECONDS[unit] * 1000


def time_to_epoch_ms(node: Node | None, now_ms: int | None = None) -> int | None:
    """Best-effort epoch-ms from a ``<time>`` node.

    RR <time> elements variously carry a ``datetime`` (ISO) or ``unixtime``
    (seconds) attribute, with relative text like "5 days ago" as the body. We
    prefer the machine-readable attributes and fall back to the text.
    """
    if node is None:
        return None
    iso = to_epoch_ms(attr(node, "datetime"))
    if iso is not None:
        return iso
    unixtime = attr(node, "unixtime")
    if unixtime:
        try:
            return int(unixtime) * 1000
        except ValueError:
            pass
    text = node_text(node).strip()
    relative = parse_relative_to_epoch_ms(text, now_ms)
    if relative is not None:
        return relative
    return to_epoch_ms(text)


def parse_number(raw: str | None) -> int:
    """parseInt with commas stripped; 0 on failure (cf. TS parseNumber)."""
    if not raw:
        return 0
    digits = re.sub(r"[^\d-]", "", raw)
    try:
        return int(digits)
    except ValueError:
        return 0


def parse_rating(raw: str | None) -> float:
    """Parse a "4.5 / 5" rating string into a float; -1 if absent (cf. TS)."""
    if not raw:
        return -1.0
    try:
        return float(raw.split("/")[0].strip())
    except ValueError:
        return -1.0


def inner_html(node: Node | None) -> str:
    """cheerio ``.html()`` equivalent: the node's inner HTML (children only)."""
    if node is None:
        return ""
    parts = []
    for child in node.iter(include_text=True):
        html = child.html
        if html:
            parts.append(html)
    return "".join(parts)
