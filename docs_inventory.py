"""Four-way classification of docs/ for the ticket-bus sit.

Every ``*.md`` / ``*.jsonl`` under ``docs/`` is exactly one of
``live_kernel``, ``live_tape``, ``parked_archive``, ``leftover_migrated``.
Parked trees are not work-to-do. Tests import this module rather than
scraping a novel.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Iterator

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

DOC_CLASSES = (
    "live_kernel",
    "live_tape",
    "parked_archive",
    "leftover_migrated",
)

# Packet skim / default spawn-read must not name these as work.
FORBIDDEN_DISPATCH = (
    "docs/archive/",
    "docs/crew/niche/",
    "docs/program/improve/",
    "docs/archive/kerbin-lessons.md",
    "docs/lessons.md",
    "docs/program/lars-rsi.md",
    "docs/program/learn-rsi.md",
    "docs/program/feedback-plan.md",
    "docs/program/tickets/BOARD.md",
    "docs/program/sit-card.json",
    "docs/program/org-flow/",
    ".grok/agents/spotter.md",
    "docs/program/plan.md",
    "docs/program/briefing.md",
    "docs/program/science.md",
    "docs/program/vab.md",
    "docs/program/note-tech.md",
    "docs/program/loop.md",
    "docs/crew/builder.md",
)

GITIGNORED_OPTIONAL = frozenset(
    {
        "docs/last-flight.md",
        "docs/program/desk.md",
        "docs/program/ship.md",
    }
)

# I-012..I-020 and F-001..F-015 item files (any tree depth).
_IF_ITEM = re.compile(
    r"(?:^|/)(I-0(?:1[2-9]|20)|F-0(?:0[1-9]|1[0-5]))\.md$"
)

_ORG_NOVEL_NAMES = frozenset(
    {
        "NEXT-ORG.md",
        "SPEED.md",
        "ORG-INTERACTIONS.md",
        "ORG.md",
        "org-session-audit.md",
        "rsi-jump.md",
        "ticket-bus-cutover.md",
        "rescue.md",
        "RSI-JUMP.md",
        "feedback.md",
        "lars-rsi.md",
        "learn-rsi.md",
        "feedback-plan.md",
        "lessons.md",
        "plan.md",
        "briefing.md",
        "science.md",
        "vab.md",
        "note-tech.md",
        "loop.md",
        "builder.md",
    }
)

# Idempotent ticket twins. status inbox stays open; done/wont/verify
# are patched after open. I-013/I-017/I-018/I-019 live in tickets.SEED
# already — migrate skips on the id token so titles are not duplicated.
IF_TWINS: tuple[dict[str, str], ...] = (
    {
        "token": "I-012",
        "type": "org",
        "title": "I-012 Opportunities board sci vs desk",
        "reporter": "Gene Grokman, Launch / Flight Director",
        "desk": "mortimer",
        "severity": "S3",
        "priority": "P2",
        "status": "done",
        "why": "accepted: opportunities copy desk sci",
    },
    {
        "token": "I-014",
        "type": "ops",
        "title": "I-014 Desk stale after Gus capable",
        "reporter": "Linus Grokman, Director of Research",
        "desk": "hank",
        "severity": "S3",
        "priority": "P1",
        "status": "done",
        "why": "accepted: parent re-desks after capable: yes",
    },
    {
        "token": "I-015",
        "type": "control",
        "title": "I-015 Hop recover line hides situation",
        "reporter": "Jebediah Grokman, Commander",
        "desk": "lars",
        "severity": "S3",
        "priority": "P2",
        "status": "done",
        "why": "accepted: hop.py recover line names sit + recoverable",
    },
    {
        "token": "I-016",
        "type": "ops",
        "title": "I-016 Pad idle during Learn",
        "reporter": "Os (Founder)",
        "desk": "hank",
        "severity": "S2",
        "priority": "P1",
        "status": "done",
        "why": "accepted: uncrewed campaign re-fly last cli on clean 0",
    },
    {
        "token": "I-020",
        "type": "org",
        "title": "I-020 jsonl envelope is the flight tape",
        "reporter": "Mortimer Grokman, CEO",
        "desk": "mortimer",
        "severity": "S3",
        "priority": "P1",
        "status": "done",
        "why": "accepted: Learn/bind cite envelope; last-flight is abort/exit",
    },
    {
        "token": "F-001",
        "type": "science",
        "title": "F-001 Linus card must carry dwell and EC",
        "reporter": "Lars Grokman, Vehicle Systems Engineer",
        "desk": "linus",
        "severity": "S3",
        "priority": "P1",
        "status": "done",
        "why": "accepted: duration_s / ec_rate / recover_banks on bind",
    },
    {
        "token": "F-002",
        "type": "ops",
        "title": "F-002 Lars not after a clean recover",
        "reporter": "Gene Grokman, Launch / Flight Director",
        "desk": "hank",
        "severity": "S3",
        "priority": "P1",
        "status": "done",
        "why": "accepted: Lars only after a miss",
    },
    {
        "token": "F-003",
        "type": "systems",
        "title": "F-003 Tests must not write last-flight",
        "reporter": "Lars Grokman, Vehicle Systems Engineer",
        "desk": "wernher",
        "severity": "S3",
        "priority": "P2",
        "status": "done",
        "why": "accepted: unittest must not clobber last-flight",
    },
    {
        "token": "F-004",
        "type": "ops",
        "title": "F-004 Helm CLI is Gene recommended verbatim",
        "reporter": "Jebediah Grokman, Commander",
        "desk": "hank",
        "severity": "S2",
        "priority": "P0",
        "status": "done",
        "why": "accepted: Commander cli is fly payload.cli verbatim",
    },
    {
        "token": "F-005",
        "type": "science",
        "title": "F-005 Same pad card is not more science",
        "reporter": "Gene Grokman, Launch / Flight Director",
        "desk": "linus",
        "severity": "S3",
        "priority": "P1",
        "status": "done",
        "why": "accepted: same subject does not re-pay",
    },
    {
        "token": "F-006",
        "type": "systems",
        "title": "F-006 World disk vs live leftover hop",
        "reporter": "Gene Grokman, Launch / Flight Director",
        "desk": "wernher",
        "severity": "S2",
        "priority": "P1",
        "status": "done",
        "why": "accepted: desk leftover vs Tracking (I-017 pool)",
    },
    {
        "token": "F-007",
        "type": "control",
        "title": "F-007 Hop recover hung on crash dialog",
        "reporter": "Jebediah Grokman, Commander",
        "desk": "lars",
        "severity": "S2",
        "priority": "P1",
        "status": "done",
        "why": "patched: hop recover / Hank walk-home; crash UI is not a hang",
    },
    {
        "token": "F-008",
        "type": "control",
        "title": "F-008 Hop recovered before thermo dwell",
        "reporter": "Jebediah Grokman, Commander",
        "desk": "lars",
        "severity": "S2",
        "priority": "P1",
        "status": "done",
        "why": "patched: hang covers duration_s; do not skip start on a new hang",
    },
    {
        "token": "F-009",
        "type": "science",
        "title": "F-009 75 s hang cannot finish leftover thermo",
        "reporter": "Linus Grokman, Director of Research",
        "desk": "linus",
        "severity": "S3",
        "priority": "P2",
        "status": "done",
        "why": "patched history: 75 s is not finished leftover thermo",
    },
    {
        "token": "F-010",
        "type": "vehicle",
        "title": "F-010 Experiment id is not a part",
        "reporter": "Gus Grokman, Vehicle Engineering Lead",
        "desk": "gus",
        "severity": "S3",
        "priority": "P2",
        "status": "done",
        "why": "accepted: f013 uses instrument parts, not experiment id",
    },
    {
        "token": "F-011",
        "type": "systems",
        "title": "F-011 Disk kRPC settings were not what notes said",
        "reporter": "Wernher Grokman, Chief Systems Engineer",
        "desk": "wernher",
        "severity": "S3",
        "priority": "P2",
        "status": "done",
        "why": "accepted: krpc.md is the briefing; never write GameData",
    },
    {
        "token": "F-012",
        "type": "control",
        "title": "F-012 Pad unpause does not start MET",
        "reporter": "Jebediah Grokman, Commander",
        "desk": "lars",
        "severity": "S2",
        "priority": "P1",
        "status": "done",
        "why": "patched: pad clock is rem/running/UT; unpause physics",
    },
    {
        "token": "F-013",
        "type": "ops",
        "title": "F-013 Tree and parts never reached Lars (or a go:)",
        "reporter": "Os (Founder)",
        "desk": "hank",
        "severity": "S2",
        "priority": "P0",
        "status": "done",
        "why": "accepted: missing f013 on bind / capable / go is wait",
    },
    {
        "token": "F-014",
        "type": "systems",
        "title": "F-014 load persistent autosaves RAM first",
        "reporter": "Mortimer Grokman, CEO",
        "desk": "wernher",
        "severity": "S2",
        "priority": "P1",
        "status": "verify",
        "why": "still true: never load persistent; named rd-<node> then ksc",
    },
    {
        "token": "F-015",
        "type": "systems",
        "title": "F-015 RD load can seat an RSS asteroid",
        "reporter": "Mortimer Grokman, CEO",
        "desk": "wernher",
        "severity": "S3",
        "priority": "P2",
        "status": "verify",
        "why": "still true: after named RD load, ksc if Flight is asteroid",
    },
)

_SEEDED_IF_TOKENS = ("I-013", "I-017", "I-018", "I-019")


def lesson_headings(text: str | None = None) -> list[str]:
    """Parked ``##`` parser. Not a live bus. Pass ``text``; default empty."""
    raw = text or ""
    out: list[str] = []
    for line in raw.splitlines():
        if line.startswith("## "):
            out.append(line[3:].strip())
    return out


def _rel(path: Path, repo: Path) -> str:
    return path.resolve().relative_to(repo).as_posix()


def classify(rel: str) -> str:
    """Return exactly one DOC_CLASSES member for a repo-relative path."""
    rel = rel.replace("\\", "/")
    name = rel.rsplit("/", 1)[-1]
    if rel.startswith("docs/archive/"):
        return "parked_archive"
    if _IF_ITEM.search(rel):
        return "leftover_migrated"
    if "/niche/" in f"/{rel}" or rel.startswith("docs/crew/niche/"):
        return "parked_archive"
    if rel.startswith("docs/program/improve/"):
        return "parked_archive"
    if rel.startswith("docs/program/feedback/"):
        return "parked_archive"
    if rel.endswith("-review.md"):
        return "parked_archive"
    if "/missions/" in rel and rel.endswith("/mission.md"):
        return "parked_archive"
    if rel == "docs/program/log.md" or rel.endswith("/program/log.md"):
        return "parked_archive"
    if rel.endswith(".jsonl"):
        return "live_tape"
    if rel.startswith("docs/crew/log/"):
        return "live_tape"
    if rel == "docs/last-flight.md":
        return "live_tape"
    if rel == "docs/program/ship.md":
        return "live_tape"
    if "/missions/" in rel and "/logs/" in rel:
        return "live_tape"
    if "/missions/" in rel and rel.endswith("/craft.md"):
        return "live_tape"
    if "/missions/" in rel and rel.endswith("/loop.md"):
        return "live_tape"
    if "/missions/" in rel and rel.endswith(
        ("/plan.md", "/science.md", "/briefing.md")
    ):
        return "live_kernel"
    if name in _ORG_NOVEL_NAMES:
        return "parked_archive"
    return "live_kernel"


def iter_docs(
    *,
    repo: Path | None = None,
    skip_missing_gitignored: bool = True,
) -> Iterator[tuple[str, str]]:
    """Walk ``docs/`` ``*.md`` / ``*.jsonl``. Yield ``(rel, class)``."""
    base = repo or ROOT
    docs = base / "docs"
    if not docs.is_dir():
        return
    seen: set[str] = set()
    for path in sorted(docs.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".md", ".jsonl"}:
            continue
        rel = _rel(path, base)
        if rel in seen:
            continue
        seen.add(rel)
        yield rel, classify(rel)
    if skip_missing_gitignored:
        return
    for rel in GITIGNORED_OPTIONAL:
        if rel not in seen:
            yield rel, classify(rel)


def classified_map(repo: Path | None = None) -> dict[str, str]:
    return dict(iter_docs(repo=repo))


def skim_mentions_forbidden(text: str) -> list[str]:
    """Forbidden dispatch prefixes that appear in packet/AGENTS text."""
    hits: list[str] = []
    for needle in FORBIDDEN_DISPATCH:
        if needle in text:
            hits.append(needle)
    return hits


def packet_read_paths(packet: str) -> list[str]:
    """Paths listed under the skim ``read:`` block (not ``deep:`` / tape)."""
    paths: list[str] = []
    in_read = False
    for line in packet.splitlines():
        if line.startswith("read:"):
            in_read = True
            continue
        if in_read:
            if line.startswith("  - "):
                body = line[4:].split("  #", 1)[0].strip()
                if body:
                    paths.append(body)
                continue
            if line.startswith("deep:") or not line.startswith(" "):
                break
    return paths


def if_tokens() -> list[str]:
    tokens = [spec["token"] for spec in IF_TWINS]
    tokens.extend(_SEEDED_IF_TOKENS)
    return tokens


def twin_title_hits(titles: Iterable[str], token: str) -> int:
    """I/F ids count as a twin only when the title starts with that id."""
    n = 0
    if_id = token.startswith("I-") or token.startswith("F-")
    for raw in titles:
        t = raw or ""
        if if_id:
            if t == token or t.startswith(token + " "):
                n += 1
        elif token in t:
            n += 1
    return n
