"""Part names and stack-node offsets from GameData (no ModuleManager).

RO/RP-1 parts often exist only after MM patches. This scan is the unpatched
``.cfg`` view — enough to stack stock, and a hook for later.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from cfg import CfgNode, load

log = logging.getLogger("kspstuff")

# Internal name → stack node local positions. Used when GameData is absent.
STOCK_NODES: dict[str, dict[str, tuple[float, float, float]]] = {
    "mk1pod_v2": {"top": (0.0, 0.6423756, 0.0), "bottom": (0.0, -0.4050379, 0.0)},
    "parachuteSingle": {"bottom": (0.0, -0.120649, 0.0)},
    "fuelTankSmallFlat": {"top": (0.0, 0.3125, 0.0), "bottom": (0.0, -0.3125, 0.0)},
    "fuelTank": {"top": (0.0, 0.981725, 0.0), "bottom": (0.0, -0.9125, 0.0)},
    "fuelTank_long": {"top": (0.0, 1.875, 0.0), "bottom": (0.0, -1.8875, 0.0)},
    "liquidEngine2_v2": {"top": (0.0, 0.0, 0.0), "bottom": (0.0, -1.63, 0.0)},
    "liquidEngine3_v2": {"top": (0.0, 0.0, 0.0), "bottom": (0.0, -0.83, 0.0)},
    "liquidEngine_v2": {"top": (0.0, 0.0, 0.0), "bottom": (0.0, -1.63, 0.0)},
    "Decoupler_1": {"top": (0.0, 0.05, 0.0), "bottom": (0.0, -0.05, 0.0)},
    "Decoupler_2": {"top": (0.0, 0.1, 0.0), "bottom": (0.0, -0.1, 0.0)},
    "probeCoreHex_v2": {"top": (0.0, 0.1875, 0.0), "bottom": (0.0, -0.1875, 0.0)},
    "adapterSize2-Size1": {"top": (0.0, 1.25, 0.0), "bottom": (0.0, -1.25, 0.0)},
    "Rockomax32_BW": {"top": (0.0, 1.86, 0.0), "bottom": (0.0, -1.86, 0.0)},
    "Rockomax16_BW": {"top": (0.0, 0.92, 0.0), "bottom": (0.0, -0.92, 0.0)},
    "engineLargeSkipper_v2": {"top": (0.0, 1.013, 0.0), "bottom": (0.0, -1.362, 0.0)},
}


@dataclass(slots=True)
class PartDef:
    name: str
    title: str
    nodes: dict[str, tuple[float, float, float]]
    cfg_path: str = ""
    author: str = ""


@dataclass
class Catalog:
    parts: dict[str, PartDef] = field(default_factory=dict)

    def node(self, part_name: str, node: str) -> tuple[float, float, float]:
        part = self.parts.get(part_name)
        if part and node in part.nodes:
            return part.nodes[node]
        fallback = STOCK_NODES.get(part_name, {})
        if node in fallback:
            return fallback[node]
        raise KeyError(f"No stack node {node!r} on {part_name}")

    def has(self, part_name: str) -> bool:
        return part_name in self.parts or part_name in STOCK_NODES

    @classmethod
    def stock(cls) -> Catalog:
        cat = cls()
        for name, nodes in STOCK_NODES.items():
            cat.parts[name] = PartDef(name=name, title=name, nodes=dict(nodes))
        return cat


def _parse_node_stack(value: str) -> tuple[float, float, float]:
    bits = [b.strip() for b in value.split(",")]
    return float(bits[0]), float(bits[1]), float(bits[2])


def scan_gamedata(ksp_root: str | Path) -> Catalog:
    """Walk ``GameData/**/*.cfg`` for ``PART { name = ... }``. Skips MM patches."""
    root = Path(ksp_root) / "GameData"
    cat = Catalog.stock()
    if not root.is_dir():
        log.warning("No GameData at %s", root)
        return cat
    for path in root.rglob("*.cfg"):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        stripped = text.lstrip("\ufeff").lstrip()
        if not stripped.startswith("PART"):
            continue
        try:
            node = load(path)
        except Exception:
            log.debug("cfg parse failed: %s", path, exc_info=True)
            continue
        for part in node.of("PART"):
            name = part.get("name")
            if not name:
                continue
            nodes: dict[str, tuple[float, float, float]] = {}
            for key, value in part.values:
                if key.startswith("node_stack_"):
                    nname = key[len("node_stack_") :]
                    try:
                        nodes[nname] = _parse_node_stack(value)
                    except (ValueError, IndexError):
                        continue
            title = part.get("title") or name
            if "//" in title:
                title = title.split("//", 1)[0].strip()
            cat.parts[name] = PartDef(
                name=name,
                title=title,
                nodes=nodes or cat.parts.get(name, PartDef(name, title, {})).nodes,
                cfg_path=str(path),
                author=part.get("author") or "",
            )
    log.info("Catalog: %d parts from %s", len(cat.parts), root)
    return cat
