"""Open science at this tree. GameData + save. Linus owns the scan. No kRPC.

Kerbalism ``Situation =`` lines plus R&D leftovers. Reach is Cape Shores
pad / FlyingLow hop / FlyingHigh 50 km lid — not splash, not space.
"""

from __future__ import annotations

from world import World, instrument_parts

# RSS Kerbin-scale body multipliers used on Earth subjects we already banked.
_SIT_SCALE = {
    "surface": 0.3,
    "srf": 0.3,
    "landed": 0.3,
    "splash": 0.4,
    "flyinglow": 0.7,
    "flyinghigh": 0.9,
    "space": 1.3,
}

_REACH = {
    "surface": "pad Shores (Cape); other biomes no site",
    "flyinglow": "hop FlyingLow <50 km — hang-limited",
    "flyinghigh": "50 km lid / OffPlan",
    "space": "not in reach",
    "splash": "splash refused (no Water leftover)",
}


def _sit_key(tag: str) -> str:
    t = tag.lower()
    if "splash" in t:
        return "splash"
    if "surface" in t or "landed" in t or t.startswith("srf"):
        return "surface"
    if "flyinglow" in t or "flying_low" in t:
        return "flyinglow"
    if "flyinghigh" in t or "flying_high" in t:
        return "flyinghigh"
    if "space" in t or "inspace" in t:
        return "space"
    return t.split("@", 1)[0]


def unlocked_experiment_ids(world: World) -> set[str]:
    owned = set(world.research.unlocked)
    out: set[str] = set()
    for part in world.catalog.parts.values():
        if part.tech and part.tech not in owned:
            continue
        out.update(part.experiments)
    return out


def format_science_scan(world: World) -> str:
    owned_ids = unlocked_experiment_ids(world)
    by_id: dict[str, list] = {}
    for sub in world.research.subjects:
        eid = sub.id.split("@", 1)[0]
        by_id.setdefault(eid, []).append(sub)

    lines = [
        "# open science at this tree (GameData Situation + save leftovers)",
        "# kRPC has get_Science only — no subject list. Disk is the scan.",
        f"# unlocked experiments n={len(owned_ids)}",
    ]
    opens = 0
    for eid in sorted(owned_ids):
        cfg = world.catalog.experiments.get(eid)
        sits = list(cfg.situations) if cfg and cfg.situations else ["Surface@Biomes"]
        inst = instrument_parts(world, eid)
        owned_nodes = set(world.research.unlocked)
        if inst and inst[0].tech not in owned_nodes:
            inst_s = f"{inst[0].name} tech={inst[0].tech} LOCKED"
        elif inst:
            inst_s = f"{inst[0].name} tech={inst[0].tech}"
        else:
            inst_s = "hosted PAW"
        cap = cfg.science_cap if cfg else None
        for tag in sits:
            key = _sit_key(tag)
            reach = _REACH.get(key, "unknown")
            scale = _SIT_SCALE.get(key, 0.0)
            full = (cap * scale) if cap and scale else None
            subs = [
                s
                for s in by_id.get(eid, [])
                if key in s.id.lower()
                or (
                    key == "surface"
                    and ("SrfLanded" in s.id or "Landed" in s.id)
                )
                or (key == "flyinglow" and "FlyingLow" in s.id)
                or (key == "flyinghigh" and "FlyingHigh" in s.id)
                or (key == "space" and "InSpace" in s.id)
                or (key == "splash" and "Splash" in s.id)
            ]
            left = sum(s.leftover for s in subs)
            if subs and left < 0.02:
                status = "capped"
            elif subs:
                status = f"left={left:.2f}"
                opens += 1
            elif full:
                status = f"unstarted ~{full:.2f}"
                if key not in {"space", "splash"}:
                    opens += 1
            else:
                status = "unstarted"
                if key not in {"space", "splash"}:
                    opens += 1
            locked_inst = bool(inst and inst[0].tech not in owned_nodes)
            in_reach = key in {"surface", "flyinglow"} and not locked_inst
            mark = "REACH" if in_reach and not status.startswith("capped") else "out"
            if locked_inst:
                mark = "locked"
            elif status.startswith("capped") and key in {"surface", "flyinglow"}:
                mark = "capped"
            lines.append(
                f"  {eid:22} {tag:22} {inst_s:42} {status:18} {mark}  ({reach})"
            )
    lines.append(f"# open-or-unstarted in pad/hop reach: see REACH rows")
    return "\n".join(lines) + "\n"
