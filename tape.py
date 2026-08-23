"""Disk telemetry query. Agents never read jsonl into a prompt.

The run tape stays on disk. Packet skim is :func:`format_envelope`.
Windows return a handful of compact rows (pad, first airborne, apex by
peak **alt**, **burnout** attitude (min pitch while throttled through
first cutoff), descent ladder, last airborne / impact, kind=event).
Apex is not max apo (07-21-05Z max apo at 10.8 km hid 14 km→412 m).
Apex is also not burnout (09-28-59Z peak alt 297/86 hid MET 49 heading
209 pitch 3). ``python main.py telem <jsonl>`` is the CLI.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from telem import classify_impact, format_landing, impact_speed, stack_shear

_PAD = frozenset({"pre_launch", "prelaunch"})
_DOWN = frozenset({"landed", "splashed"})
_AIR = frozenset({"flying", "sub_orbital", "suborbital", "escaping", "orbiting"})
_COMPACT = (
    "t",
    "met",
    "kind",
    "situation",
    "heading",
    "horiz",
    "pitch",
    "apo",
    "alt",
    "v_vert",
    "throttle",
    "fuel",
    "biome",
    "lat",
    "lon",
    "downrange",
    "hz",
    "q",
    "ec",
    "g",
    "stage",
    "broken",
    "wreck",
    "recoverable",
    "chute",
    "sci_run",
    "sci_rem",
    "sci_bank",
    "mass",
    "parts_n",
    "root",
    "debris_n",
    "shear",
    "landing",
)
WINDOWS = ("pad", "airborne", "apex", "burnout", "descent", "impact", "events")
_BURN_THROTTLE = 0.05


def _finite(value: Any, default: float = float("nan")) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def _fmt(val: Any, spec: str = ".0f") -> str:
    n = _finite(val)
    if not math.isfinite(n):
        return "?"
    return format(n, spec)


def _round(val: Any, nd: int = 3) -> float | None:
    n = _finite(val)
    if not math.isfinite(n):
        return None
    return round(float(n), nd)


def _sit(row: dict[str, Any]) -> str:
    return str(row.get("situation") or "").lower()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.is_file():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def _compact(row: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key in _COMPACT:
        if key not in row:
            continue
        val = row[key]
        if isinstance(val, float):
            out[key] = None if not math.isfinite(val) else round(val, 3)
        else:
            out[key] = val
    return out


def _apex_row(states: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Peak altitude while flying. Max apo is still climbing during burn."""
    best: dict[str, Any] | None = None
    best_alt = float("-inf")
    apo_fallback: dict[str, Any] | None = None
    apo_max = float("-inf")
    for row in states:
        apo = _finite(row.get("apo"))
        if math.isfinite(apo) and apo > apo_max:
            apo_max = apo
            apo_fallback = row
        if _sit(row) not in _AIR:
            continue
        alt = _finite(row.get("alt"))
        if math.isfinite(alt) and alt > best_alt:
            best_alt = alt
            best = row
    return best or apo_fallback


def _throttled(row: dict[str, Any]) -> bool:
    thr = _finite(row.get("throttle"))
    return math.isfinite(thr) and thr > _BURN_THROTTLE


def _burn_rows(states: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Flying from first throttle through first cutoff (inclusive)."""
    out: list[dict[str, Any]] = []
    seen_thr = False
    for row in states:
        if _sit(row) not in _AIR:
            if out:
                break
            continue
        if _throttled(row):
            seen_thr = True
            out.append(row)
            continue
        if seen_thr:
            out.append(row)
            break
    if out:
        return out
    climb: list[dict[str, Any]] = []
    for row in states:
        if _sit(row) not in _AIR:
            continue
        fuel = _finite(row.get("fuel"))
        vz = _finite(row.get("v_vert"))
        if math.isfinite(fuel) and fuel > 0 and math.isfinite(vz) and vz > 5.0:
            climb.append(row)
    return climb


def _burnout_row(states: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Most off-vertical sample through burnout — not peak alt (09-28-59Z)."""
    rows = _burn_rows(states)
    if not rows:
        return None
    best = rows[-1]
    best_def = float("-inf")
    for row in rows:
        pitch = _finite(row.get("pitch"))
        if not math.isfinite(pitch):
            continue
        deflect = abs(90.0 - pitch)
        if deflect > best_def:
            best_def = deflect
            best = row
    return best


def _gap_s(states: list[dict[str, Any]]) -> float | None:
    best = 0.0
    prev: float | None = None
    for row in states:
        met = _finite(row.get("met"))
        if not math.isfinite(met):
            continue
        if prev is not None and met > prev:
            best = max(best, met - prev)
        prev = met
    return round(best, 2) if best > 0 else None


def _subsample(rows: list[dict[str, Any]], n: int) -> list[dict[str, Any]]:
    if n <= 0 or len(rows) <= n:
        return rows
    if n == 1:
        return [rows[-1]]
    out: list[dict[str, Any]] = []
    last_i = len(rows) - 1
    seen: set[int] = set()
    for k in range(n):
        i = int(round(k * last_i / (n - 1)))
        if i in seen:
            continue
        seen.add(i)
        out.append(rows[i])
    return out


def _hz_median(states: list[dict[str, Any]]) -> float | None:
    dts: list[float] = []
    prev_t: float | None = None
    for row in states:
        tf = _finite(row.get("t"))
        if not math.isfinite(tf):
            continue
        if prev_t is not None and tf > prev_t:
            dts.append(tf - prev_t)
        prev_t = tf
    if not dts:
        return None
    dts.sort()
    med = dts[len(dts) // 2]
    return round(1.0 / med, 2) if med > 0 else None


def _kin(row: dict[str, Any] | None) -> dict[str, Any]:
    src = row or {}
    rec = src.get("recoverable")
    return {
        "heading": _round(src.get("heading")),
        "horiz": _round(src.get("horiz")),
        "pitch": _round(src.get("pitch")),
        "met": _round(src.get("met")),
        "apo": _round(src.get("apo")),
        "alt": _round(src.get("alt")),
        "sit": src.get("situation") or "",
        "q": _round(src.get("q")),
        "ec": _round(src.get("ec")),
        "g": _round(src.get("g"), 2),
        "stage": src.get("stage"),
        "broken": src.get("broken"),
        "recoverable": rec if rec is None else bool(rec),
        "chute": src.get("chute") or "",
        "sci_run": src.get("sci_run"),
        "sci_rem": _round(src.get("sci_rem")),
        "sci_bank": _round(src.get("sci_bank"), 4),
        "mass": _round(src.get("mass")),
        "parts_n": src.get("parts_n"),
        "root": src.get("root") or "",
        "shear": bool(src.get("shear")) if src.get("shear") is not None else None,
        "throttle": _round(src.get("throttle"), 2),
        "fuel": _round(src.get("fuel")),
        "biome": src.get("biome") or "",
        "lat": _round(src.get("lat"), 4),
        "lon": _round(src.get("lon"), 4),
        "downrange": _round(src.get("downrange"), 3),
    }


def _sci_bank(rows: list[dict[str, Any]], last: dict[str, Any] | None) -> float | None:
    """Recover credits RAM RD after last state. kind=sci_bank wins."""
    for row in reversed(rows):
        if str(row.get("kind") or "") != "sci_bank":
            continue
        n = _round(row.get("sci"), 4)
        if n is not None:
            return n
    return _round((last or {}).get("sci_bank"), 4)


def _max_key(states: list[dict[str, Any]], key: str) -> float | None:
    m = float("-inf")
    for row in states:
        n = _finite(row.get(key))
        if math.isfinite(n) and n > m:
            m = n
    return None if m == float("-inf") else round(m, 3)


class Tape:
    """Index one run jsonl. Load stays in-process — not a prompt."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._rows: list[dict[str, Any]] | None = None

    def load(self) -> list[dict[str, Any]]:
        if self._rows is None:
            self._rows = _read_jsonl(self.path)
        return self._rows

    def states(self) -> list[dict[str, Any]]:
        return [r for r in self.load() if r.get("kind") == "state"]

    def events(self, kind: str | None = None) -> list[dict[str, Any]]:
        rows = [r for r in self.load() if r.get("kind") and r.get("kind") != "state"]
        if kind:
            want = kind.lower()
            rows = [r for r in rows if str(r.get("kind") or "").lower() == want]
        return rows

    def envelope(self) -> dict[str, Any]:
        states = self.states()
        rows = self.load()
        pad = next((r for r in states if _sit(r) in _PAD), None)
        air0 = next((r for r in states if _sit(r) in _AIR), None)
        last_air: dict[str, Any] | None = None
        down: dict[str, Any] | None = None
        apex = _apex_row(states)
        burn_rows = _burn_rows(states)
        burnout = _burnout_row(states)
        apo_max = float("-inf")
        biomes: list[str] = []
        for r in states:
            sit = _sit(r)
            if sit in _AIR:
                last_air = r
            elif sit in _DOWN and down is None:
                down = r
            apo = _finite(r.get("apo"))
            if math.isfinite(apo) and apo > apo_max:
                apo_max = apo
            bio = str(r.get("biome") or "").strip()
            if bio and bio not in biomes:
                biomes.append(bio)
        descent_rows: list[dict[str, Any]] = []
        if apex is not None:
            seen_apex = False
            for r in states:
                if r is apex:
                    seen_apex = True
                if seen_apex and _sit(r) in _AIR:
                    descent_rows.append(r)
        landing_row = next((r for r in rows if r.get("kind") == "landing"), None)
        start = next((r for r in rows if r.get("kind") == "start"), None)
        last = states[-1] if states else None
        air = last_air or {}
        hit = down or {}
        v_vert = _finite(air.get("v_vert"))
        speed = _finite(air.get("speed"))
        horiz = _finite(air.get("horiz"))
        impact = impact_speed(v_vert=v_vert, speed=speed, horiz=horiz)
        landing = ""
        if landing_row and landing_row.get("landing"):
            landing = str(landing_row.get("landing") or "")
            impact = _finite(landing_row.get("impact_ms"), impact)
        if not landing:
            landing = classify_impact(impact) or "unknown"
        met_air = _finite(air.get("met"))
        met_down = _finite(hit.get("met"))
        dt_s = None
        if math.isfinite(met_air) and math.isfinite(met_down):
            dt_s = round(met_down - met_air, 3)
        mets = [_finite(r.get("met")) for r in states]
        mets = [m for m in mets if math.isfinite(m)]
        cmd = ""
        if start:
            msg = str(start.get("msg") or "")
            if msg.startswith("command="):
                cmd = msg.split("command=", 1)[1].split()[0]
        kinds: list[str] = []
        seen_k: set[str] = set()
        for r in rows:
            k = str(r.get("kind") or "")
            if not k or k == "state" or k in seen_k:
                continue
            seen_k.add(k)
            kinds.append(k)
        broken = next((r.get("broken") for r in states if r.get("broken")), None)
        shear = False
        for a, b in zip(states, states[1:]):
            if stack_shear(a, b) or b.get("shear"):
                shear = True
                break
        if not shear:
            shear = any(bool(r.get("shear")) for r in states)
        sit = (
            hit.get("situation")
            or (landing_row or {}).get("sit")
            or (last or {}).get("situation")
            or ""
        )
        pos = hit or air or last or {}
        lat = _round(pos.get("lat"), 4)
        lon = _round(pos.get("lon"), 4)
        down = _round(pos.get("downrange"), 3)
        if down is None and lat is not None and lon is not None:
            down = _downrange_from_ll(lat, lon)
        if lat is None:
            lat = _round((landing_row or {}).get("lat"), 4)
        if lon is None:
            lon = _round((landing_row or {}).get("lon"), 4)
        if down is None:
            down = _round((landing_row or {}).get("downrange"), 3)
        return {
            "run": self.path.name,
            "path": str(self.path),
            "command": cmd,
            "landing": landing,
            "impact_ms": _round(impact),
            "v_vert": _round(v_vert),
            "speed": _round(speed),
            "horiz": _round(air.get("horiz") if air else horiz),
            "heading": _round(air.get("heading")),
            "pitch": _round(air.get("pitch")),
            "alt_before": _round(air.get("alt")),
            "sit": sit,
            "biome": (hit.get("biome") or air.get("biome") or (biomes[0] if biomes else "")),
            "biomes": biomes,
            "lat": lat,
            "lon": lon,
            "downrange": down,
            "met": _round(met_down) if math.isfinite(met_down) else (_round(mets[-1]) if mets else None),
            "dt_s": dt_s,
            "samples": len(states),
            "hz_median": _hz_median(states),
            "met_start": _round(mets[0]) if mets else None,
            "met_end": _round(mets[-1]) if mets else None,
            "apo_max": None if not math.isfinite(apo_max) or apo_max == float("-inf") else round(apo_max, 3),
            "alt_max": _round((apex or {}).get("alt")),
            "gap_s": _gap_s(states),
            "descent_n": len(descent_rows),
            "burnout_n": len(burn_rows),
            "pad": _kin(pad),
            "airborne": _kin(air0),
            "apex": _kin(apex),
            "burnout": _kin(burnout),
            "last": _kin(last),
            "q_max": _max_key(states, "q"),
            "g_max": _max_key(states, "g"),
            "ec": _round((last or {}).get("ec")),
            "stage": (last or {}).get("stage"),
            "broken": broken,
            "recoverable": (last or {}).get("recoverable"),
            "chute": (last or {}).get("chute") or "",
            "sci_run": (last or {}).get("sci_run"),
            "sci_rem": _round((last or {}).get("sci_rem")),
            "sci_bank": _sci_bank(rows, last),
            "mass": _round((last or {}).get("mass")),
            "mass_pad": _round((pad or {}).get("mass")),
            "parts_n": (last or {}).get("parts_n"),
            "parts_pad": (pad or {}).get("parts_n"),
            "root": (last or {}).get("root") or "",
            "debris_n": (last or {}).get("debris_n"),
            "shear": shear,
            "events": kinds + (["shear"] if shear and "shear" not in kinds else []),
        }

    def window(
        self,
        name: str,
        *,
        before_s: float = 2.0,
        max_rows: int = 12,
    ) -> dict[str, Any]:
        """Named slice. Never the whole tape. ``max_rows`` caps prompt size."""
        want = (name or "").lower().strip()
        states = self.states()
        picked: list[dict[str, Any]] = []
        if want == "pad":
            picked = [r for r in states if _sit(r) in _PAD][:1]
        elif want == "airborne":
            picked = [r for r in states if _sit(r) in _AIR][:3]
        elif want == "apex":
            apex = _apex_row(states)
            if apex is not None:
                picked = [apex]
        elif want == "burnout":
            picked = _subsample(_burn_rows(states), max_rows)
        elif want == "descent":
            apex = _apex_row(states)
            if apex is not None:
                seen_apex = False
                for r in states:
                    if r is apex:
                        seen_apex = True
                    if seen_apex and _sit(r) in _AIR:
                        picked.append(r)
            picked = _subsample(picked, max_rows)
        elif want == "impact":
            env = self.envelope()
            met = _finite(env.get("met"))
            if not math.isfinite(met):
                down = next((r for r in states if _sit(r) in _DOWN), None)
                met = _finite((down or {}).get("met"))
            if math.isfinite(met):
                lo = met - before_s
                picked = [
                    r
                    for r in states
                    if math.isfinite(_finite(r.get("met"))) and lo <= _finite(r.get("met")) <= met + 0.05
                ]
            flying = [r for r in states if _sit(r) in _AIR]
            if len(picked) < 3 and flying:
                picked = flying[-max_rows:]
            picked.extend(self.events("landing"))
        elif want == "events":
            picked = self.events()
        else:
            raise ValueError(f"unknown window {name!r}; want {WINDOWS}")
        if max_rows > 0 and len(picked) > max_rows:
            picked = picked[:max_rows]
        return {
            "window": want,
            "path": str(self.path),
            "n": len(picked),
            "rows": [_compact(r) for r in picked],
        }

    def around(
        self,
        *,
        met: float,
        before_s: float = 2.0,
        after_s: float = 1.0,
        max_rows: int = 12,
    ) -> dict[str, Any]:
        lo, hi = met - before_s, met + after_s
        picked = [
            r
            for r in self.states()
            if lo <= _finite(r.get("met")) <= hi
        ]
        if max_rows > 0 and len(picked) > max_rows:
            picked = picked[:max_rows]
        return {
            "window": "around",
            "met": met,
            "path": str(self.path),
            "n": len(picked),
            "rows": [_compact(r) for r in picked],
        }


def _downrange_from_ll(lat: float, lon: float) -> float | None:
    try:
        from hangar import pad_ll
        from sites import downrange_km

        plat, plon = pad_ll()
        n = downrange_km(lat, lon, plat, plon)
    except Exception:
        return None
    return _round(n, 3)


def envelope(path: str | Path) -> dict[str, Any]:
    return Tape(path).envelope()


def format_envelope(row: dict[str, Any]) -> str:
    """Skim block. Landing line plus pad/last/apo — no state rows."""
    lines = [format_landing(row)]
    pad = row.get("pad") if isinstance(row.get("pad"), dict) else {}
    last = row.get("last") if isinstance(row.get("last"), dict) else {}
    if pad and any(pad.get(k) is not None for k in ("heading", "horiz", "pitch")):
        lines.append(
            f"pad: heading={_fmt(pad.get('heading'))} "
            f"horiz={_fmt(pad.get('horiz'), '.2f')} "
            f"pitch={_fmt(pad.get('pitch'))}"
        )
    if last and any(last.get(k) is not None for k in ("heading", "horiz", "pitch")):
        lines.append(
            f"last: heading={_fmt(last.get('heading'))} "
            f"horiz={_fmt(last.get('horiz'), '.2f')} "
            f"pitch={_fmt(last.get('pitch'))}"
        )
    burn = row.get("burnout") if isinstance(row.get("burnout"), dict) else {}
    if burn and any(burn.get(k) is not None for k in ("heading", "horiz", "pitch")):
        lines.append(
            f"burn: heading={_fmt(burn.get('heading'))} "
            f"pitch={_fmt(burn.get('pitch'))} "
            f"horiz={_fmt(burn.get('horiz'), '.0f')} "
            f"met={_fmt(burn.get('met'), '.0f')} "
            f"n={row.get('burnout_n') or 0}"
        )
    biomes = row.get("biomes") or []
    biome = ",".join(str(b) for b in biomes if b) or (row.get("biome") or "?")
    lines.append(
        f"where: lat={_fmt(row.get('lat'), '.4f')} "
        f"lon={_fmt(row.get('lon'), '.4f')} "
        f"down={_fmt(row.get('downrange'), '.2f')} km "
        f"biome={biome}"
    )
    lines.append(
        f"eyes: apo={_fmt(row.get('apo_max'))} m alt={_fmt(row.get('alt_max'))} m "
        f"samples={row.get('samples') or 0} "
        f"hz={_fmt(row.get('hz_median'), '.2f')} biome={biome} "
        f"met={_fmt(row.get('met_start'), '.1f')}–{_fmt(row.get('met_end'), '.1f')}"
    )
    apex = row.get("apex") if isinstance(row.get("apex"), dict) else {}
    last_alt = last.get("alt") if last else None
    peak = row.get("alt_max")
    if peak is None and apex:
        peak = apex.get("alt")
    if peak is not None and last_alt is not None:
        gap = row.get("gap_s")
        gap_s = f" gap={_fmt(gap, '.0f')}s" if gap is not None else ""
        lines.append(
            f"descent: {_fmt(peak)}→{_fmt(last_alt)} m "
            f"n={row.get('descent_n') or 0}{gap_s}"
        )
    rec = row.get("recoverable")
    if rec is True:
        rec_s = "yes"
    elif rec is False:
        rec_s = "no"
    else:
        rec_s = "?"
    sci_run = row.get("sci_run")
    run_s = "?" if sci_run is None else ("1" if sci_run else "0")
    bank = row.get("sci_bank")
    bank_s = _fmt(bank, ".2f") if bank is not None else "?"
    lines.append(
        f"tape: q={_fmt(row.get('q_max'))} g={_fmt(row.get('g_max'), '.2f')} "
        f"ec={_fmt(row.get('ec'))} stage={row.get('stage') if row.get('stage') is not None else '?'} "
        f"broken={row.get('broken') or 'none'} rec={rec_s} "
        f"chute={row.get('chute') or 'none'} sci=run={run_s} rem={_fmt(row.get('sci_rem'), 'g')} "
        f"bank={bank_s}"
    )
    mass_pad = row.get("mass_pad")
    mass_last = row.get("mass")
    parts_n = row.get("parts_n")
    shear_s = "yes" if row.get("shear") else "no"
    mass_s = _fmt(mass_last)
    if mass_pad is not None and mass_last is not None:
        mass_s = f"{_fmt(mass_pad)}→{_fmt(mass_last)}"
    parts_s = "?" if parts_n is None else str(parts_n)
    lines.append(f"stack: mass={mass_s} parts={parts_s} shear={shear_s}")
    kinds = row.get("events") or []
    if kinds:
        lines.append("events: " + ",".join(str(k) for k in kinds))
    return "\n".join(lines)


def cmd_telem(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="telem", description=__doc__)
    p.add_argument("path", help="run jsonl (disk; do not paste rows)")
    p.add_argument(
        "--window",
        default="",
        help="pad|airborne|apex|burnout|descent|impact|events",
    )
    p.add_argument("--kind", default="", help="non-state kind filter (start, landing, end)")
    p.add_argument("--around-met", type=float, default=None, dest="around_met")
    p.add_argument("--before", type=float, default=2.0)
    args = p.parse_args(argv)
    src = Path(args.path)
    if not src.is_file():
        print(f"telem: missing {src}", flush=True)
        return 1
    tape = Tape(src)
    if args.window:
        print(json.dumps(tape.window(args.window, before_s=args.before), indent=2, sort_keys=True))
        return 0
    if args.kind:
        rows = [_compact(r) for r in tape.events(args.kind)]
        print(json.dumps({"kind": args.kind, "n": len(rows), "rows": rows}, indent=2, sort_keys=True))
        return 0
    if args.around_met is not None:
        print(json.dumps(tape.around(met=args.around_met, before_s=args.before), indent=2, sort_keys=True))
        return 0
    env = tape.envelope()
    print(format_envelope(env))
    print(json.dumps(env, indent=2, sort_keys=True))
    return 0
