#!/usr/bin/env python3
"""Small GB/T 7714-2015 formatter for manually supplied metadata.

This helper does not search the web and does not validate journal quality.
Use it only for preliminary formatting; manually verify final references.
"""

from __future__ import annotations

from typing import Dict, Iterable, List


def _clean(value) -> str:
    return "" if value is None else str(value).strip()


def format_authors(authors: Iterable[str], lang: str = "zh") -> str:
    names = [_clean(a) for a in authors if _clean(a)]
    if not names:
        return ""
    if lang == "zh":
        return ", ".join(names[:3]) + (", 等" if len(names) > 3 else "")
    return ", ".join(names[:3]) + (", et al" if len(names) > 3 else "")


def format_article(paper: Dict, index: int | str = 1) -> str:
    lang = paper.get("language", "zh")
    authors = format_authors(paper.get("authors", []), lang)
    title = _clean(paper.get("title"))
    journal = _clean(paper.get("journal"))
    year = _clean(paper.get("year"))
    volume = _clean(paper.get("volume"))
    issue = _clean(paper.get("issue"))
    pages = _clean(paper.get("pages"))
    doi = _clean(paper.get("doi"))

    vol_issue = ""
    if volume and issue:
        vol_issue = f", {volume}({issue})"
    elif volume:
        vol_issue = f", {volume}"
    elif issue:
        vol_issue = f"({issue})"
    if pages:
        vol_issue += f": {pages}" if vol_issue else f": {pages}"

    ref = f"[{index}] {authors}. {title}[J]. {journal}"
    if year:
        ref += f", {year}"
    ref += vol_issue
    if doi:
        ref += f". DOI:{doi}"
    return ref + "."


def format_reference_list(papers: List[Dict]) -> str:
    return "\n".join(format_article(p, i) for i, p in enumerate(papers, 1))
