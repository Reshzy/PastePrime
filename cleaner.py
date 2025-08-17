"""
==============================================================

        ██████  ███████ ███████ ██   ██ ███████ ██    ██ 
        ██   ██ ██      ██      ██   ██    ███   ██  ██  
        ██████  █████   ███████ ███████   ███     ████   
        ██   ██ ██           ██ ██   ██  ███       ██    
        ██   ██ ███████ ███████ ██   ██ ███████    ██    
                                                              
                  Paste Prime – by Reshzy                     
==============================================================
"""

import re
import unicodedata


ZERO_WIDTH_PATTERN = re.compile(r"[\u200B-\u200D\uFEFF]")
NON_BREAKING_SPACES_PATTERN = re.compile(r"[\u00A0\u202F\u2007]")
WHITESPACE_PATTERN = re.compile(r"\s+")


SMART_QUOTES = {
    "": "",  # SUB char sometimes appears in weird copies
    "": "",
    "": "",
    # Curly quotes
    "": "'",
    "": "'",
    "": '"',
    "": '"',
    "": '"',
    "‘": "'",
    "’": "'",
    "‚": ",",
    "“": '"',
    "”": '"',
    "„": ",",
}

CHAR_REPLACEMENTS = {
    "–": "-",
    "—": "-",
    "−": "-",
    "…": "...",
}


def strip_diacritics(text: str) -> str:
    """Remove diacritics by decomposing and dropping combining chars."""
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def clean_text(text: str, *, ascii_only: bool = False, single_line: bool = True) -> str:
    """Clean text for reliable pasting into Warframe chat.

    Steps:
    - Normalize Unicode (NFKC)
    - Remove zero-width chars and BOM
    - Replace non-breaking spaces with regular spaces
    - Replace smart quotes/dashes/ellipsis with ASCII equivalents
    - Collapse whitespace
    - Optionally force ASCII (strip diacritics and drop non-ASCII)
    - Optionally enforce single line
    """
    if not text:
        return ""

    # Normalize
    text = unicodedata.normalize("NFKC", text)

    # Remove zero width and BOM-like characters
    text = ZERO_WIDTH_PATTERN.sub("", text)

    # Replace non-breaking spaces with normal space
    text = NON_BREAKING_SPACES_PATTERN.sub(" ", text)

    # Replace common smart punctuation
    for src, dst in {**SMART_QUOTES, **CHAR_REPLACEMENTS}.items():
        text = text.replace(src, dst)

    # Normalize newlines to spaces if single line requested
    if single_line:
        text = text.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")

    # Collapse whitespace runs
    text = WHITESPACE_PATTERN.sub(" ", text).strip()

    if ascii_only:
        # Remove diacritics and drop any remaining non-ASCII
        text = strip_diacritics(text)
        text = text.encode("ascii", errors="ignore").decode("ascii")

    return text


