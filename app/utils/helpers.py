# ─────────────────────────────────────────────────────────────────
#  app/utils/helpers.py
#  Veltrix – General-purpose helper / utility functions.
#
#  Import these anywhere in the app:
#      from app.utils.helpers import slugify, truncate, format_datetime
# ─────────────────────────────────────────────────────────────────

import re
from datetime import datetime


def format_datetime(dt, fmt: str = "%B %d, %Y at %I:%M %p") -> str:
    """
    Format a datetime object or string into a human-readable string.

    Args:
        dt  : A Python datetime object or a string representation of a datetime.
        fmt : strftime format string (default: "January 01, 2024 at 12:00 PM").

    Returns:
        Formatted date string, or "N/A" if dt is None.
    """
    if dt is None:
        return "N/A"
    
    if isinstance(dt, str):
        # SQLite occasionally returns datetime columns as strings.
        # Let's parse them safely.
        cleaned = dt.split(".")[0].replace("Z", "").replace("+00:00", "").strip()
        for pattern in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(cleaned, pattern)
                break
            except ValueError:
                continue
                
    if not hasattr(dt, "strftime"):
        return str(dt)
        
    return dt.strftime(fmt)



def slugify(text: str) -> str:
    """
    Convert a string into a URL-friendly slug.

    Steps:
        1. Lowercase the text.
        2. Replace spaces and underscores with hyphens.
        3. Strip any character that is not alphanumeric or a hyphen.
        4. Collapse multiple consecutive hyphens into one.
        5. Strip leading/trailing hyphens.

    Args:
        text : The input string (e.g. a page title).

    Returns:
        A clean slug string.

    Example:
        >>> slugify("Hello World! This is Veltrix.")
        'hello-world-this-is-veltrix'
    """
    text = text.lower()
    text = re.sub(r"[\s_]+", "-", text)          # spaces/underscores → hyphen
    text = re.sub(r"[^\w-]", "", text)            # remove non-word chars
    text = re.sub(r"-+", "-", text)               # collapse multiple hyphens
    return text.strip("-")


def truncate(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum number of characters.

    If the text is shorter than max_length it is returned unchanged.
    Otherwise it is cut at max_length and the suffix is appended.

    Args:
        text       : The input string.
        max_length : Maximum allowed length before truncation (default 100).
        suffix     : String appended after truncation (default "...").

    Returns:
        Original or truncated string.

    Example:
        >>> truncate("The quick brown fox jumps over the lazy dog", 20)
        'The quick brown fox ...'
    """
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + suffix
