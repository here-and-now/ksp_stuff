"""After-flight rollup. Facts from jsonl; Gene writes the learn line."""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

from flightlog import FLIGHTS


def load_rows(jsonl: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not jsonl.is_file():
        return rows
    for line in jsonl.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    states = [r for r in rows if r.get("kind") == "state"]
    events = [r for r in rows if r.get("kind") != "state"]
    flags_seen: Counter[str] = Counter()
    transitions: list[str] = []
    prev_flags: tuple[str, ...] = ()
    bodies: list[str] = []
    tags: Counter[str] = Counter()

    def _f(row: dict[str, Any], key: str) -> float:
        val = row.get(key)
        try:
            num = float(val)
        except (TypeError, ValueError):
            return float("nan")
        return num

    alt_min = peri_min = lf_min = fuel_min = ec_min = float("inf")
    apo_max = warp_max = met_max = horiz_max = -float("inf")
    lf0 = lf1 = fuel0 = fuel1 = ec0 = ec1 = float("nan")
    hdg0 = hdg1 = pitch0 = pitch1 = float("nan")
    t_esc = t_atmo = t_dip = 0.0
    prev_t = 0.0
    first_line = last_line = ""

    for row in states:
        t = float(row.get("t") or 0.0)
        dt = max(0.0, t - prev_t)
        prev_t = t
        flags = tuple(row.get("flags") or [])
        flags_seen.update(flags)
        if flags != prev_flags:
            extra = " ".join(flags) if flags else "(clear)"
            transitions.append(f"T+{t:.0f}s {row.get('tag','')} {extra}".strip())
            prev_flags = flags
        body = str(row.get("body") or "")
        if body and (not bodies or bodies[-1] != body):
            bodies.append(body)
        tag = str(row.get("tag") or "")
        if tag:
            tags[tag] += 1
        alt, peri, apo = _f(row, "alt"), _f(row, "peri"), _f(row, "apo")
        lf, warp = _f(row, "lf"), _f(row, "warp")
        fuel, ec, met = _f(row, "fuel"), _f(row, "ec"), _f(row, "met")
        hdg, horiz, pitch = _f(row, "heading"), _f(row, "horiz"), _f(row, "pitch")
        if math.isfinite(hdg):
            if not math.isfinite(hdg0):
                hdg0 = hdg
            hdg1 = hdg
        if math.isfinite(horiz):
            horiz_max = max(horiz_max, horiz)
        if math.isfinite(pitch):
            if not math.isfinite(pitch0):
                pitch0 = pitch
            pitch1 = pitch
        if not math.isfinite(lf):
            lf = fuel
        if math.isfinite(alt):
            alt_min = min(alt_min, alt)
        if math.isfinite(peri):
            peri_min = min(peri_min, peri)
        if math.isfinite(apo):
            apo_max = max(apo_max, apo)
        if math.isfinite(met):
            met_max = max(met_max, met)
        if math.isfinite(lf):
            lf_min = min(lf_min, lf)
            if not math.isfinite(lf0):
                lf0 = lf
            lf1 = lf
        if math.isfinite(fuel):
            fuel_min = min(fuel_min, fuel)
            if not math.isfinite(fuel0):
                fuel0 = fuel
            fuel1 = fuel
        if math.isfinite(ec):
            ec_min = min(ec_min, ec)
            if not math.isfinite(ec0):
                ec0 = ec
            ec1 = ec
        if math.isfinite(warp):
            warp_max = max(warp_max, warp)
        if "ESC" in flags:
            t_esc += dt
        if "ATMO" in flags:
            t_atmo += dt
        if "DIP" in flags:
            t_dip += dt
        last_line = _line(row)
        if not first_line:
            first_line = last_line

    dur = float(states[-1]["t"]) if states else 0.0
    return {
        "samples": len(states),
        "events": len(events),
        "duration_s": round(dur, 1),
        "bodies": bodies,
        "tags": dict(tags),
        "alt_min": _fin(alt_min),
        "peri_min": _fin(peri_min),
        "apo_max": _fin(apo_max),
        "met_max": _fin(met_max),
        "lf_start": _fin(lf0),
        "lf_end": _fin(lf1),
        "lf_min": _fin(lf_min),
        "fuel_start": _fin(fuel0),
        "fuel_end": _fin(fuel1),
        "fuel_min": _fin(fuel_min),
        "ec_start": _fin(ec0),
        "ec_end": _fin(ec1),
        "ec_min": _fin(ec_min),
        "warp_max": _fin(warp_max),
        "t_esc_s": round(t_esc, 1),
        "t_atmo_s": round(t_atmo, 1),
        "t_dip_s": round(t_dip, 1),
        "flag_counts": dict(flags_seen),
        "transitions": transitions[:40],
        "event_lines": [
            f"T+{e.get('t', 0):.0f}s {e.get('kind')} {e.get('msg', '')}".strip()
            for e in events
        ][:40],
        "first": first_line,
        "last": last_line,
        "heading_first": _fin(hdg0),
        "heading_last": _fin(hdg1),
        "horiz_max": _fin(horiz_max),
        "pitch_first": _fin(pitch0),
        "pitch_last": _fin(pitch1),
    }


def write_review(
    jsonl: Path,
    *,
    command: str,
    exit_code: int,
    abort: str | None,
    handoff: Path | None = None,
) -> Path:
    rows = load_rows(jsonl)
    stats = summarize(rows)
    start = next((r for r in rows if r.get("kind") == "start"), {})
    earth = str(start.get("earth_utc") or "")
    kut = str(start.get("kerbal_ut") or "")
    kmet = str(start.get("kerbal_met") or "")
    out = jsonl.with_name(jsonl.stem + "-review.md")
    lines = [
        f"# Review {jsonl.stem}",
        "",
        f"command: {command}",
        f"exit: {exit_code}",
        f"abort: {abort or ''}",
        f"log: {jsonl.as_posix()}",
        f"earth: {earth or '?'}",
        f"kerbal_ut: {kut or '?'}",
        f"kerbal_met: {kmet or '?'}",
        f"samples: {stats['samples']} (~1 Hz)",
        f"duration: {stats['duration_s']} s wall",
        f"bodies: {', '.join(stats['bodies']) or '?'}",
        f"tags: {stats['tags']}",
        "",
        "## Envelope",
        "",
        f"- alt min {stats['alt_min']}",
        f"- peri min {stats['peri_min']}",
        f"- apo max {stats['apo_max']}",
        f"- met max {stats['met_max']}",
        f"- EC {stats['ec_start']} → {stats['ec_end']} (min {stats['ec_min']})",
        f"- fuel {stats['fuel_start']} → {stats['fuel_end']} (min {stats['fuel_min']})",
        f"- LF {stats['lf_start']} → {stats['lf_end']} (min {stats['lf_min']})",
        f"- warp max {stats['warp_max']}x",
        f"- time ATMO {stats['t_atmo_s']}s  DIP {stats['t_dip_s']}s  ESC {stats['t_esc_s']}s",
        f"- flags {stats['flag_counts']}",
        "",
        "## First / last",
        "",
        f"- {stats['first']}",
        f"- {stats['last']}",
        "",
        "## Flag changes",
        "",
    ]
    lines.extend(f"- {x}" for x in stats["transitions"] or ["(none)"])
    lines.extend(["", "## Events", ""])
    lines.extend(f"- {x}" for x in stats["event_lines"] or ["(none)"])
    if handoff and handoff.is_file():
        lines.extend(["", "## Handoff", "", "```", handoff.read_text(encoding="utf-8")[:4000], "```"])
    lines.extend(learn_block(command, exit_code, abort, stats))
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


_HYGIENE = frozenset({"ksc", "load", "recover-probe"})


def _env_num(val: float | None) -> str:
    if val is None:
        return "?"
    return str(int(round(val)))


def learn_block(
    command: str,
    exit_code: int,
    abort: str | None,
    stats: dict[str, Any],
) -> list[str]:
    """Envelope Learn from jsonl stats. Hygiene commands skip the Gene blank."""
    env: list[str] = []
    h0, h1 = stats.get("heading_first"), stats.get("heading_last")
    if h0 is not None or h1 is not None:
        env.append(f"heading {_env_num(h0)}→{_env_num(h1)}")
    if stats.get("horiz_max") is not None:
        env.append(f"horiz max {_env_num(stats.get('horiz_max'))}")
    p0, p1 = stats.get("pitch_first"), stats.get("pitch_last")
    if p0 is not None or p1 is not None:
        env.append(f"pitch {_env_num(p0)}→{_env_num(p1)}")
    env_s = ", ".join(env) if env else "none"
    cmd = (command or "").strip().lower()
    if cmd in _HYGIENE:
        body = f"hygiene {cmd} exit={exit_code} envelope {env_s}."
    else:
        body = (
            f"exit={exit_code} abort={abort or 'none'}. envelope {env_s}. "
            "Stamp payload.learn on the fly ticket."
        )
    return ["", "## Learn", "", body, ""]


def latest_jsonl(flight_id: str | None = None) -> Path | None:
    from missions import seated_id, seated_logs_dir

    fid = flight_id or seated_id()
    dest = seated_logs_dir(fid)
    files = sorted(dest.glob("*.jsonl")) if dest.is_dir() else []
    if not files:
        files = sorted(FLIGHTS.glob("*.jsonl"))
    return files[-1] if files else None


def _fin(val: float) -> float | None:
    if not math.isfinite(val) or abs(val) == float("inf"):
        return None
    return round(val, 1)


def _line(row: dict[str, Any]) -> str:
    flag = row.get("flags") or []
    flag_s = (" [" + " ".join(flag) + "]") if flag else ""
    fuel = row.get("fuel")
    if fuel is None:
        fuel = row.get("lf")
    return (
        f"{row.get('tag','')}{row.get('body','?')} {row.get('situation','?')} "
        f"alt={row.get('alt')} peri={row.get('peri')} apo={row.get('apo')} "
        f"met={row.get('met')} ec={row.get('ec')} fuel={fuel} "
        f"warp={row.get('warp')}x{flag_s}"
    ).strip()
