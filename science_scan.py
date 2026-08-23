"""Open science at this tree. GameData + save. Linus owns the scan. No kRPC.

Kerbalism ``Situation =`` lines plus R&D leftovers. Reach is Cape Shores
pad / FlyingLow hop / FlyingHigh 50 km lid — not splash, not space.
"""

from __future__ import annotations

from world import World, instrument_parts

# RSS Earth ScienceValues (Earth.cfg). LEO is InSpaceLow only; high is GEO.
_SIT_SCALE = {
    "surface": 0.3,
    "srf": 0.3,
    "landed": 0.3,
    "splash": 0.4,
    "flyinglow": 0.7,
    "flyinghigh": 0.9,
    "inspacelow": 1.0,
    "inspacehigh": 1.5,
    "space": 1.0,
}

_REACH = {
    "surface": "pad Shores (Cape); other biomes no site",
    "flyinglow": "hop FlyingLow <50 km — hang-limited",
    "flyinghigh": "50 km lid / OffPlan",
    "space": "LEO / not this hop",
    "inspacelow": "LEO — not this hop",
    "inspacehigh": "GEO 35786 km — not this hop",
    "splash": "splash leftover Water only",
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
    if "inspacehigh" in t or "spacehigh" in t:
        return "inspacehigh"
    if "inspacelow" in t or "spacelow" in t:
        return "inspacelow"
    if "space" in t:
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


def format_live_defs(world: World) -> str:
    """Post-MM experiment table. House patch last-writes baro/Jr/atmo."""
    lines = [
        "# live experiment defs (ModuleManager.ConfigCache last write)",
        "# GameData/zzzzkspstuffScience after Kerbalism. Do not read StockExperiments.cfg.",
        "# sample = recover the can (no radio). file = credits while recording onto HD.",
        "# id  kind  cap  size_Mb  duration_s  ec_rate  slots  situations",
    ]
    for eid, cfg in sorted(world.catalog.experiments.items()):
        dur = f"{cfg.duration_s:.0f}" if cfg.duration_s else "-"
        cap = f"{cfg.science_cap:.3g}" if cfg.science_cap is not None else "-"
        size = f"{cfg.size_mb:.3g}" if cfg.size_mb is not None else "-"
        ec = f"{cfg.ec_rate:.4g}" if cfg.ec_rate is not None else "-"
        slots = f"{cfg.sample_amount:g}" if cfg.sample_amount else "-"
        sits = ",".join(cfg.situations) if cfg.situations else "-"
        lines.append(
            f"{eid:28} {cfg.kind:6} cap={cap:6} size={size:8} t={dur:6} "
            f"ec={ec:8} slots={slots:4} {sits}"
        )
    return "\n".join(lines) + "\n"


def format_comms(world: World) -> str:
    """Live RA antennas + command-module HD from MM cache. Gus / Linus disk sit."""
    lines = [
        "# live RA + probe HD (ModuleManager.ConfigCache). No kRPC.",
        "# TL2 (survivability) MaxDataRate=64 bps on every ModuleRealAntenna.",
        "# 16-S omni L gain=2. Dishes start basicScience (HG-5 0.5m). Goo/Jr are samples.",
        "# part  tech  title  gain  diam_m  band  HD_Mb  samples",
    ]
    owned = set(world.research.unlocked)
    rows: list[tuple[str, object]] = []
    for part in world.catalog.parts.values():
        if "ModuleRealAntenna" not in part.modules and part.data_capacity is None:
            continue
        rows.append((part.name, part))
    for _name, part in sorted(rows, key=lambda r: ((r[1].tech or "zzz"), r[0])):
        lock = "UNLOCKED" if (not part.tech or part.tech in owned) else "LOCKED"
        gain = f"{part.antenna_gain:g}" if part.antenna_gain is not None else "-"
        diam = f"{part.antenna_diameter:g}" if part.antenna_diameter is not None else "-"
        band = part.antenna_band or "-"
        hd = f"{part.data_capacity:g}" if part.data_capacity is not None else "-"
        sm = f"{part.sample_capacity:g}" if part.sample_capacity is not None else "-"
        title = (part.title or part.name)[:36]
        lines.append(
            f"{part.name:36} {part.tech or '-':22} {lock:8} "
            f"gain={gain:6} D={diam:6} {band:4} HD={hd:6} samp={sm:4}  {title}"
        )
    return "\n".join(lines) + "\n"


def format_science_scan(world: World) -> str:
    owned_ids = unlocked_experiment_ids(world)
    by_id: dict[str, list] = {}
    for sub in world.research.subjects:
        eid = sub.id.split("@", 1)[0]
        by_id.setdefault(eid, []).append(sub)

    lines = [
        "# open science at this tree (live MM defs + save leftovers)",
        "# kRPC has get_Science only — no subject list. Disk is the scan.",
        "# python main.py science-scan   # this table",
        "# python main.py comms          # RA + HD",
        f"# unlocked experiments n={len(owned_ids)}",
    ]
    lines.extend(format_live_defs(world).splitlines())
    lines.append("# leftover / reach")
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
                or (key == "inspacelow" and "InSpaceLow" in s.id)
                or (key == "inspacehigh" and "InSpaceHigh" in s.id)
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
                if key not in {"space", "splash", "inspacelow", "inspacehigh"}:
                    opens += 1
            else:
                status = "unstarted"
                if key not in {"space", "splash", "inspacelow", "inspacehigh"}:
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
