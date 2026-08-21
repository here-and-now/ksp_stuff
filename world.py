"""Disk world desk: tech tree, parts, save unlocks. No kRPC.

Queries are the environment memory. Do not snapshot Start parts into docs.
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from catalog import Catalog, PartDef, cfg_name, load_catalog
from hangar import DEFAULT_SAVE, Hangar, discover_ksp

log = logging.getLogger("kspstuff")


class WorldError(RuntimeError):
    """KSP root, save, or GameData missing / unreadable."""


@dataclass(slots=True)
class TechNode:
    id: str
    title: str
    cost: int
    parents: tuple[str, ...] = ()


@dataclass(slots=True)
class ScienceSubject:
    id: str
    sci: float
    cap: float
    scv: float = 0.0

    @property
    def leftover(self) -> float:
        if self.cap <= 0:
            return 0.0
        return max(0.0, self.cap - self.sci)


@dataclass(slots=True)
class SaveVessel:
    name: str
    sit: str
    type: str
    landed: bool


@dataclass(slots=True)
class Research:
    science: float | None = None
    unlocked: tuple[str, ...] = ()
    parts_by_node: dict[str, tuple[str, ...]] = field(default_factory=dict)
    subjects: tuple[ScienceSubject, ...] = ()


@dataclass
class World:
    ksp_root: Path
    save: str
    mode: str
    tree_url: str
    home_hint: str
    research: Research
    catalog: Catalog
    tree: dict[str, TechNode]
    save_path: Path | None = None
    vessels: tuple[SaveVessel, ...] = ()

    @property
    def hangar(self) -> Hangar:
        return Hangar(ksp_root=self.ksp_root, save=self.save)


def load_world(
    ksp_root: str | Path | None = None,
    save: str | None = None,
) -> World:
    if ksp_root is not None:
        root = Path(ksp_root)
    else:
        found = discover_ksp()
        if found is None:
            raise WorldError(
                "no KSP root (set KSPSTUFF_KSP or install RSS at ~/Games/KSP-rss)"
            )
        root = found
    if not root.is_dir():
        raise WorldError(f"KSP root is not a directory: {root}")

    hangar = Hangar(
        ksp_root=root,
        save=save or os.environ.get("KSPSTUFF_SAVE") or DEFAULT_SAVE,
    )

    save_path = hangar.save_dir / "persistent.sfs"
    mode = "unknown"
    tree_url = ""
    home_hint = "unknown"
    research = Research()
    vessels: tuple[SaveVessel, ...] = ()
    if save_path.is_file():
        text = save_path.read_text(encoding="utf-8", errors="replace")
        mode = _game_mode(text)
        tree_url = _tech_tree_url(text)
        home_hint = _home_hint(text)
        research = parse_research(text)
        vessels = tuple(parse_vessels(text))
    else:
        log.warning("no persistent.sfs at %s", save_path)

    tree_path = _resolve_tree(root, tree_url)
    tree = parse_tech_tree(tree_path) if tree_path is not None else {}
    catalog = load_catalog(root)
    return World(
        ksp_root=root,
        save=hangar.save,
        mode=mode,
        tree_url=tree_url or (str(tree_path.relative_to(root)) if tree_path else ""),
        home_hint=home_hint,
        research=research,
        catalog=catalog,
        tree=tree,
        save_path=save_path if save_path.is_file() else None,
        vessels=vessels,
    )


def _resolve_tree(root: Path, tree_url: str) -> Path | None:
    candidates: list[Path] = []
    if tree_url:
        candidates.append(root / tree_url)
        if not tree_url.startswith("GameData/"):
            candidates.append(root / "GameData" / tree_url)
    candidates.extend(
        [
            root / "GameData" / "HideEmptyTechTreeNodes" / "Resources" / "HETTN.TechTree",
            root / "GameData" / "ModuleManager.TechTree",
            root / "GameData" / "Squad" / "Resources" / "TechTree.cfg",
        ]
    )
    for path in candidates:
        if path.is_file():
            return path
    return None


def _game_mode(text: str) -> str:
    match = re.search(r"(?m)^\s*Mode = (\S+)", text)
    return match.group(1) if match else "unknown"


def _tech_tree_url(text: str) -> str:
    match = re.search(r"(?m)^\s*TechTreeUrl = (\S+)", text)
    return match.group(1) if match else ""


def _home_hint(text: str) -> str:
    if re.search(r"\bBodyName = Earth\b", text) or re.search(
        r"(?m)^\s*name = Earth\s*$", text
    ):
        return "Earth"
    if re.search(r"\bBodyName = Kerbin\b", text) or re.search(
        r"(?m)^\s*name = Kerbin\s*$", text
    ):
        return "Kerbin"
    if "Earth" in text and "Kerbin" not in text:
        return "Earth"
    if "Kerbin" in text and "Earth" not in text:
        return "Kerbin"
    return "unknown"


def parse_tech_tree(path: str | Path) -> dict[str, TechNode]:
    """RDNode list from HETTN / ModuleManager.TechTree / Squad TechTree.cfg."""
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    nodes: dict[str, TechNode] = {}
    chunks = text.split("RDNode")
    for chunk in chunks[1:]:
        nid = title = ""
        cost = 0
        parents: list[str] = []
        seen_cost = False
        for line in chunk.splitlines():
            s = line.strip()
            if s.startswith("id =") and not nid:
                nid = s.split("=", 1)[1].strip()
            elif s.startswith("title =") and not title:
                title = s.split("=", 1)[1].strip()
            elif s.startswith("cost =") and not seen_cost:
                seen_cost = True
                raw = s.split("=", 1)[1].strip().split("//", 1)[0].strip()
                try:
                    cost = int(float(raw))
                except ValueError:
                    cost = 0
            elif s.startswith("parentID"):
                parents.append(s.split("=", 1)[1].strip())
        if nid:
            nodes[nid] = TechNode(
                id=nid, title=title or nid, cost=cost, parents=tuple(parents)
            )
    return nodes


def parse_research(text: str) -> Research:
    """``SCENARIO name = ResearchAndDevelopment`` from persistent.sfs."""
    marker = "name = ResearchAndDevelopment"
    idx = text.find(marker)
    if idx < 0:
        return Research()
    start = text.rfind("SCENARIO", 0, idx)
    if start < 0:
        start = idx
    nxt = text.find("\n\tSCENARIO", idx + len(marker))
    if nxt < 0:
        nxt = text.find("\nSCENARIO", idx + len(marker))
    block = text[start:] if nxt < 0 else text[start:nxt]

    sci: float | None = None
    match = re.search(r"(?m)^\s*sci = (\S+)", block)
    if match:
        try:
            sci = float(match.group(1))
        except ValueError:
            sci = None

    unlocked: list[str] = []
    parts_by_node: dict[str, list[str]] = {}
    current: str | None = None
    in_tech = False
    tech_depth = 0
    for line in block.splitlines():
        s = line.strip()
        if s == "Tech":
            in_tech = True
            current = None
            tech_depth = 0
            continue
        if in_tech:
            if s == "{":
                tech_depth += 1
                continue
            if s == "}":
                tech_depth -= 1
                if tech_depth <= 0:
                    in_tech = False
                    current = None
                continue
            if s.startswith("id =") and current is None:
                current = s.split("=", 1)[1].strip()
                parts_by_node.setdefault(current, [])
            elif s.startswith("state =") and current:
                state = s.split("=", 1)[1].strip().lower()
                if state in {"available", "owned", "purchased"}:
                    if current not in unlocked:
                        unlocked.append(current)
            elif s.startswith("part =") and current:
                part = cfg_name(s.split("=", 1)[1].strip())
                parts_by_node[current].append(part)
    return Research(
        science=sci,
        unlocked=tuple(unlocked),
        parts_by_node={k: tuple(v) for k, v in parts_by_node.items()},
        subjects=tuple(parse_science_subjects(block)),
    )


def parse_science_subjects(block: str) -> list[ScienceSubject]:
    """R&D ``Science { id sci cap scv }`` — leftover = cap − sci."""
    out: list[ScienceSubject] = []
    current: dict[str, str] = {}
    in_sci = False
    depth = 0
    for line in block.splitlines():
        s = line.strip()
        if s == "Science":
            in_sci = True
            current = {}
            depth = 0
            continue
        if not in_sci:
            continue
        if s == "{":
            depth += 1
            continue
        if s == "}":
            depth -= 1
            if depth <= 0:
                in_sci = False
                sid = current.get("id", "")
                if sid:
                    out.append(
                        ScienceSubject(
                            id=sid,
                            sci=_sf(current.get("sci"), 0.0),
                            cap=_sf(current.get("cap"), 0.0),
                            scv=_sf(current.get("scv"), 0.0),
                        )
                    )
                current = {}
            continue
        if "=" in s:
            key, _, val = s.partition("=")
            current[key.strip()] = val.strip()
    return out


def _sf(raw: str | None, default: float) -> float:
    if not raw:
        return default
    try:
        return float(raw.split("//", 1)[0].strip())
    except ValueError:
        return default


def parse_vessels(text: str) -> list[SaveVessel]:
    """FLIGHTSTATE vessels. Skip RSS asteroids (type SpaceObject). F-006."""
    idx = text.find("FLIGHTSTATE")
    chunk = text[idx:] if idx >= 0 else text
    out: list[SaveVessel] = []
    current: dict[str, str] = {}
    in_v = False
    depth = 0
    for line in chunk.splitlines():
        s = line.strip()
        if s == "VESSEL":
            in_v = True
            current = {}
            depth = 0
            continue
        if not in_v:
            continue
        if s == "{":
            depth += 1
            continue
        if s == "}":
            depth -= 1
            if depth <= 0:
                in_v = False
                typ = current.get("type", "")
                if typ.lower() not in {"spaceobject", "flag", "eva"}:
                    name = current.get("name", "")
                    if name:
                        out.append(
                            SaveVessel(
                                name=name,
                                sit=current.get("sit", "?"),
                                type=typ or "?",
                                landed=current.get("landed", "").lower()
                                in {"true", "1"},
                            )
                        )
                current = {}
            continue
        if depth == 1 and "=" in s:
            key, _, val = s.partition("=")
            k = key.strip()
            if k in {"name", "sit", "type", "landed"} and k not in current:
                current[k] = val.strip()
    return out


def unlocked_parts(world: World) -> list[PartDef]:
    nodes = set(world.research.unlocked)
    if not nodes:
        return []
    out = [p for p in world.catalog.parts.values() if p.tech in nodes]
    out.sort(key=lambda p: (p.tech, p.category, p.name))
    return out


def filter_parts(
    world: World,
    *,
    unlocked: bool = False,
    node: str | None = None,
    search: str | None = None,
    module: str | None = None,
) -> list[PartDef]:
    parts: list[PartDef]
    if unlocked:
        parts = unlocked_parts(world)
    elif node:
        parts = [p for p in world.catalog.parts.values() if p.tech == node]
        parts.sort(key=lambda p: (p.category, p.name))
    else:
        parts = sorted(
            world.catalog.parts.values(), key=lambda p: (p.tech, p.category, p.name)
        )
    if search:
        q = search.lower()
        parts = [
            p
            for p in parts
            if q in p.name.lower()
            or q in p.title.lower()
            or q in p.tech.lower()
            or q in p.category.lower()
        ]
    if module:
        m = module.lower()
        parts = [
            p
            for p in parts
            if any(m == x.lower() or m in x.lower() for x in p.modules)
        ]
    return parts


def format_world(world: World) -> str:
    sci = world.research.science
    sci_s = "?" if sci is None else (str(int(sci)) if sci == int(sci) else str(sci))
    unlocked = ",".join(world.research.unlocked) or "(none)"
    save_ok = "yes" if world.save_path else "missing"
    lines = [
        f"ksp: {world.ksp_root}",
        f"save: {world.save} persistent={save_ok}",
        f"mode: {world.mode}",
        f"home: {world.home_hint}",
        f"tree: {world.tree_url or '?'}",
        f"sci: {sci_s}",
        f"unlocked: {unlocked}",
        f"parts: {len(world.catalog.parts)} source={world.catalog.source}",
        f"nodes: {len(world.tree)}",
    ]
    return "\n".join(lines) + "\n"


def format_tech(world: World, node_id: str | None = None) -> str:
    if node_id:
        return _format_one_node(world, node_id)
    lines = []
    unlocked = set(world.research.unlocked)
    ordered = sorted(world.tree.values(), key=lambda n: (n.cost, n.id))
    for node in ordered:
        mark = "*" if node.id in unlocked else " "
        parents = ",".join(node.parents) if node.parents else ""
        extra = f"  ← {parents}" if parents else ""
        nparts = sum(1 for p in world.catalog.parts.values() if p.tech == node.id)
        lines.append(
            f"{mark} {node.id:32} {node.cost:5}  {node.title}  parts={nparts}{extra}"
        )
    if not lines:
        return "tech: (no tree file)\n"
    lines.append("# * = unlocked in save. python main.py tech <id> for parts.")
    return "\n".join(lines) + "\n"


def _format_one_node(world: World, node_id: str) -> str:
    node = world.tree.get(node_id)
    if node is None:
        parts = filter_parts(world, node=node_id)
        if not parts:
            return f"tech: unknown node {node_id}\n"
        node = TechNode(id=node_id, title=node_id, cost=-1, parents=())
    unlocked = node_id in world.research.unlocked
    lines = [
        f"id: {node.id}",
        f"title: {node.title}",
        f"cost: {node.cost}",
        f"parents: {','.join(node.parents) or '(root)'}",
        f"unlocked: {'yes' if unlocked else 'no'}",
        "parts:",
    ]
    parts = filter_parts(world, node=node_id)
    if not parts:
        save_parts = world.research.parts_by_node.get(node_id, ())
        if save_parts:
            lines.append("  # catalog empty; save lists:")
            for name in save_parts:
                lines.append(f"  {name}")
        else:
            lines.append("  (none in catalog)")
    else:
        for part in parts:
            lines.append(_format_part_line(part))
    return "\n".join(lines) + "\n"


def _format_part_line(part: PartDef) -> str:
    proc = " proc" if part.procedural else ""
    mass = "" if part.mass is None else f" m={part.mass:g}"
    mods = ",".join(part.modules[:8])
    if len(part.modules) > 8:
        mods += ",…"
    res = f" res={','.join(part.resources)}" if part.resources else ""
    n_host = len(part.experiments)
    host = f" hosts={n_host}" if n_host else ""
    return (
        f"  {part.name:36} {part.tech:28} {part.category:14}"
        f"{mass}{proc}{host}  {part.title}{res}"
        + (f"  [{mods}]" if mods else "")
    )


def instrument_parts(world: World, eid: str) -> list[PartDef]:
    """Science-category parts that *are* this experiment (Goo, 2HOT, Geiger)."""
    out = [
        p
        for p in world.catalog.parts.values()
        if p.category.lower() == "science" and eid in p.experiments
    ]
    unlocked = set(world.research.unlocked)
    out.sort(key=lambda p: (0 if p.tech in unlocked else 1, p.tech, p.name))
    return out


def _host_parts(world: World, eid: str, *, among: list[PartDef] | None = None) -> list[PartDef]:
    pool = among if among is not None else list(world.catalog.parts.values())
    out = [
        p
        for p in pool
        if eid in p.experiments and p.category.lower() != "science"
    ]
    out.sort(key=lambda p: (p.tech, p.name))
    return out


def format_hosted(world: World, parts: list[PartDef]) -> str:
    """PAW experiments on these parts — not extra VAB parts."""
    unlocked = set(world.research.unlocked)
    eids: list[str] = []
    seen: set[str] = set()
    for part in parts:
        for eid in part.experiments:
            if eid not in seen:
                seen.add(eid)
                eids.append(eid)
    if not eids:
        return ""
    lines = [
        "# hosted experiments (PAW on a part). Not extra parts. Do not sign these as hardware.",
    ]
    for eid in eids:
        hosts = [p for p in parts if eid in p.experiments and p.category.lower() != "science"]
        instruments = instrument_parts(world, eid)
        host_s = ",".join(f"{p.name}({p.title})" for p in hosts) or "(none in this list)"
        if instruments:
            on_stack = [p for p in instruments if p.name in {x.name for x in parts}]
            unlocked_inst = [p for p in instruments if p.tech in unlocked]
            inst = (on_stack or unlocked_inst or instruments)[0]
            lock = "UNLOCKED" if inst.tech in unlocked else f"LOCKED tech={inst.tech}"
            inst_s = f" part={inst.name} ({inst.title}) {lock}"
        else:
            inst_s = " no Science-category part"
        lines.append(f"  {eid:28} hosted_on={host_s}{inst_s}")
    return "\n".join(lines) + "\n"


def format_parts(
    world: World,
    parts: list[PartDef],
    *,
    search: str | None = None,
    unlocked: bool = False,
) -> str:
    lines = [
        "# placeable parts (VAB). hosts=N means PAW experiment slots, not extra parts.",
    ]
    if parts:
        lines.extend(_format_part_line(p).lstrip() for p in parts)
        lines.append(f"# {len(parts)} parts")
        hosted = format_hosted(world, parts)
        if hosted:
            lines.append(hosted.rstrip())
    else:
        lines.append("parts: (none)")
    if search:
        q = search.lower()
        extra = _format_search_hosted(world, q, unlocked=unlocked)
        if extra:
            lines.append(extra.rstrip())
    return "\n".join(lines) + "\n"


def _format_search_hosted(world: World, q: str, *, unlocked: bool) -> str:
    """When the query is an experiment (geiger), say who hosts it and which part is locked."""
    hits: list[str] = []
    for p in world.catalog.parts.values():
        for eid in p.experiments:
            if q in eid.lower():
                hits.append(eid)
    eids = sorted(set(hits))
    if not eids:
        return ""
    unlocked_nodes = set(world.research.unlocked)
    lines = [f"# search {q!r}: experiment ids (not parts unless Science-category)"]
    for eid in eids:
        hosts = _host_parts(world, eid)
        if unlocked:
            hosts = [p for p in hosts if p.tech in unlocked_nodes]
        inst = instrument_parts(world, eid)
        joined = ",".join(p.name for p in hosts[:8])
        host_s = joined or ("(none unlocked)" if unlocked else "(none)")
        lines.append(f"  {eid:28} hosted_on={host_s}")
        for part in inst:
            mark = "UNLOCKED" if part.tech in unlocked_nodes else f"LOCKED tech={part.tech}"
            lines.append(f"    instrument {part.name}  {part.title}  {mark}")
    return "\n".join(lines) + "\n"


def craft_part_names(text: str) -> list[str]:
    """Unique cfg part names from a .craft file or craft.md ``parts:`` list."""
    names: list[str] = []
    seen: set[str] = set()
    in_list = False
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("part ="):
            token = line.split("=", 1)[1].strip()
            if "_" in token and token.rsplit("_", 1)[-1].isdigit():
                token = token.rsplit("_", 1)[0]
            name = cfg_name(token)
            if name not in seen:
                seen.add(name)
                names.append(name)
            continue
        if line == "parts:":
            in_list = True
            continue
        if in_list:
            if line.startswith("- "):
                name = cfg_name(line[2:].strip())
                if name not in seen:
                    seen.add(name)
                    names.append(name)
            elif line and not line.startswith("#"):
                in_list = False
    return names


def format_stack(world: World, names: list[str], *, label: str = "stack") -> str:
    """Honest stack: parts on the craft, then PAW experiments those parts host."""
    lines = [f"# {label}: parts on the vehicle (what you see)", "parts:"]
    found: list[PartDef] = []
    for name in names:
        part = world.catalog.get(name)
        if part is None:
            lines.append(f"  {name}  MISSING from catalog")
            continue
        if any(p.name == name for p in found):
            continue
        found.append(part)
        count = sum(1 for x in names if x == name)
        qty = f" x{count}" if count > 1 else ""
        lines.append(
            f"  {part.name}{qty}  {part.title}  tech={part.tech}  {part.category}"
        )
    hosted = format_hosted(world, found)
    if hosted:
        lines.append(hosted.rstrip())
    return "\n".join(lines) + "\n"
