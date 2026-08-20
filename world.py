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
class Research:
    science: float | None = None
    unlocked: tuple[str, ...] = ()
    parts_by_node: dict[str, tuple[str, ...]] = field(default_factory=dict)


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
    if save_path.is_file():
        text = save_path.read_text(encoding="utf-8", errors="replace")
        mode = _game_mode(text)
        tree_url = _tech_tree_url(text)
        home_hint = _home_hint(text)
        research = parse_research(text)
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
    )


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
    exp = f" exp={','.join(part.experiments)}" if part.experiments else ""
    res = f" res={','.join(part.resources)}" if part.resources else ""
    return (
        f"  {part.name:36} {part.tech:28} {part.category:14}"
        f"{mass}{proc}  {part.title}{exp}{res}"
        + (f"  [{mods}]" if mods else "")
    )


def format_parts(world: World, parts: list[PartDef]) -> str:
    if not parts:
        return "parts: (none)\n"
    lines = [_format_part_line(p).lstrip() for p in parts]
    lines.append(f"# {len(parts)} parts")
    return "\n".join(lines) + "\n"
