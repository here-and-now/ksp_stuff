"""Persistent program staff. Markdown in docs/crew/, not a package.

Style keys actually change the next flight, then get clamped so a
personality cannot disable FlightWatch or lithobrake gates.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, fields, replace
from pathlib import Path
from typing import Any

log = logging.getLogger("kspstuff")

CREW_DIR = Path("docs/crew")
CURRENT_PATH = Path("docs/program/current.md")

# House is Grokman. Stock KSP roster may still say Kerman — both slug.
_SLUG: dict[str, str] = {}
for _first, _slug in (
    ("Jebediah", "jebediah"),
    ("Valentina", "valentina"),
    ("Bill", "bill"),
    ("Bob", "bob"),
    ("Grok", "grok"),
    ("Mortimer", "mortimer"),
    ("Gene", "gene"),
    ("Walt", "walt"),
    ("Wernher", "wernher"),
    ("Linus", "linus"),
    ("Gus", "gus"),
    ("Lars", "lars"),
    ("Verena", "verena"),
):
    _SLUG[f"{_first} Grokman"] = _slug
    _SLUG[f"{_first} Kerman"] = _slug
_SLUG["Wernher von Kerman"] = "wernher"
_SLUG["Wernher von Grokman"] = "wernher"

# Library defaults, then clamp. Matches mun.py / L-015 / L-008.
_STYLE_CLAMP: dict[str, tuple[float, float]] = {
    "target_altitude": (80_000.0, 400_000.0),
    "max_q": (8_000.0, 50_000.0),
    "energy_cap": (1.05, 1.45),
    "suicide_start_alt": (20_000.0, 40_000.0),
    "turn_start_altitude": (800.0, 5_000.0),
    "turn_end_altitude": (50_000.0, 80_000.0),
}


@dataclass(slots=True)
class Style:
    target_altitude: float = 250_000.0
    max_q: float = 40_000.0
    energy_cap: float = 1.4
    suicide_start_alt: float = 25_000.0
    turn_start_altitude: float = 1_200.0
    turn_end_altitude: float = 70_000.0


@dataclass(slots=True)
class Person:
    slug: str
    name: str
    duty: str
    kerbal: str | None
    path: Path
    style: Style
    body: str


def _parse_kv(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip().lower()
        val = val.strip()
        if key:
            out[key] = val
    return out


def _style_from(kv: dict[str, str]) -> Style:
    kwargs: dict[str, float] = {}
    for f in fields(Style):
        if f.name not in kv:
            continue
        try:
            value = float(kv[f.name])
        except ValueError:
            continue
        lo, hi = _STYLE_CLAMP[f.name]
        kwargs[f.name] = min(hi, max(lo, value))
    return Style(**kwargs)


def slug_for(name: str) -> str:
    if name in _SLUG:
        return _SLUG[name]
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def load_person(name_or_slug: str) -> Person:
    slug = slug_for(name_or_slug)
    path = CREW_DIR / f"{slug}.md"
    if not path.is_file() and "grok" in slug:
        path = CREW_DIR / "grok.md"
    if not path.is_file():
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8")
    title = slug
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    kv = _parse_kv(text)
    kerbal = kv.get("kerbal", "").strip()
    if not kerbal or kerbal.lower() in {"none", "-", "n/a"}:
        kerbal_name = None
    else:
        kerbal_name = kerbal
    display = name_or_slug if name_or_slug[0].isupper() else title
    if kerbal_name and slug.startswith("grok") and " " in name_or_slug:
        kerbal_name = name_or_slug
        display = name_or_slug
    return Person(
        slug=slug,
        name=display,
        duty=kv.get("duty", "pilot"),
        kerbal=kerbal_name,
        path=path,
        style=_style_from(kv),
        body=text,
    )


def current_assignment() -> dict[str, str]:
    if not CURRENT_PATH.is_file():
        return {"pilot": "Jebediah Grokman", "capcom": "Valentina Grokman"}
    kv = _parse_kv(CURRENT_PATH.read_text(encoding="utf-8"))
    out = {
        "pilot": kv.get("pilot", "Jebediah Grokman"),
        "capcom": kv.get("capcom", "Valentina Grokman"),
    }
    if kv.get("flight"):
        out["flight"] = kv["flight"]
    return out


def current_pilot() -> Person:
    return load_person(current_assignment()["pilot"])


def apply_ascent(cfg: Any, style: Style) -> Any:
    """Copy style onto an AscentConfig. Unknown fields stay as the caller set."""
    return replace(
        cfg,
        target_altitude=style.target_altitude,
        max_q=style.max_q,
        energy_cap=style.energy_cap,
        turn_start_altitude=style.turn_start_altitude,
        turn_end_altitude=style.turn_end_altitude,
    )


def append_log(person: Person, line: str) -> None:
    text = person.path.read_text(encoding="utf-8")
    if not text.endswith("\n"):
        text += "\n"
    person.path.write_text(f"{text}- {line.rstrip()}\n", encoding="utf-8")
