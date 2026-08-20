"""Part catalog from GameData.

Prefer ModuleManager.ConfigCache (post-MM: TechRequired, modules, resources).
The unpatched ``PART {`` walk is a fallback when no cache exists (stock Steam).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from cfg import load

log = logging.getLogger("kspstuff")

# Internal name → stack node local positions. Used when GameData is absent
# and by stock-era templates. Not the RSS source of truth.
STOCK_NODES: dict[str, dict[str, tuple[float, float, float]]] = {
    "mk1pod_v2": {"top": (0.0, 0.6423756, 0.0), "bottom": (0.0, -0.4050379, 0.0)},
    "parachuteSingle": {"bottom": (0.0, -0.120649, 0.0)},
    "solidBooster_sm_v2": {
        "top": (0.0, 0.7575, 0.0),
        "bottom": (0.0, -0.9975, 0.0),
    },
    "GooExperiment": {},
    "basicFin": {},
    "fuelTankSmallFlat": {"top": (0.0, 0.3125, 0.0), "bottom": (0.0, -0.3125, 0.0)},
    "fuelTank": {"top": (0.0, 0.981725, 0.0), "bottom": (0.0, -0.9125, 0.0)},
    "fuelTank_long": {"top": (0.0, 1.875, 0.0), "bottom": (0.0, -1.8875, 0.0)},
    "liquidEngine2_v2": {"top": (0.0, 0.0, 0.0), "bottom": (0.0, -1.63, 0.0)},
    "liquidEngine3_v2": {"top": (0.0, 0.0, 0.0), "bottom": (0.0, -0.83, 0.0)},
    "liquidEngine_v2": {"top": (0.0, 0.0, 0.0), "bottom": (0.0, -1.63, 0.0)},
    "Decoupler_1": {"top": (0.0, 0.05, 0.0), "bottom": (0.0, -0.05, 0.0)},
    "Decoupler_2": {"top": (0.0, 0.1, 0.0), "bottom": (0.0, -0.1, 0.0)},
    "probeCoreHex_v2": {"top": (0.0, 0.1875, 0.0), "bottom": (0.0, -0.1875, 0.0)},
    "probeCoreSphere_v2": {"bottom": (0.0, -0.27448, 0.0)},
    "proceduralSRBRealFuels": {
        "top": (0.0, 0.5, 0.0),
        "bottom": (0.0, -0.5, 0.0),
    },
    "batteryPack": {},
    "SurfAntenna": {},
    "sensorThermometer": {},
    "adapterSize2-Size1": {"top": (0.0, 1.25, 0.0), "bottom": (0.0, -1.25, 0.0)},
    "Rockomax32_BW": {"top": (0.0, 1.86, 0.0), "bottom": (0.0, -1.86, 0.0)},
    "Rockomax16_BW": {"top": (0.0, 0.92, 0.0), "bottom": (0.0, -0.92, 0.0)},
    "engineLargeSkipper_v2": {"top": (0.0, 1.013, 0.0), "bottom": (0.0, -1.362, 0.0)},
}


def cfg_name(token: str) -> str:
    """Save/craft dots → part.cfg underscores."""
    return token.replace(".", "_")


def craft_name(name: str) -> str:
    """part.cfg underscores → save/craft dots."""
    return name.replace("_", ".")


@dataclass(slots=True)
class PartDef:
    name: str
    title: str
    nodes: dict[str, tuple[float, float, float]]
    cfg_path: str = ""
    author: str = ""
    tech: str = ""
    category: str = ""
    mass: float | None = None
    modules: tuple[str, ...] = ()
    resources: tuple[str, ...] = ()
    experiments: tuple[str, ...] = ()
    procedural: bool = False


@dataclass(slots=True)
class ExperimentCfg:
    """Kerbalism MODULE Experiment + ScienceDefs size (MB)."""

    id: str
    data_rate: float | None = None
    sample_amount: float | None = None
    ec_rate: float | None = None
    size_mb: float | None = None


def merge_experiment_cfg(
    store: dict[str, ExperimentCfg],
    eid: str,
    *,
    data_rate: float | None = None,
    sample_amount: float | None = None,
    ec_rate: float | None = None,
    size_mb: float | None = None,
) -> None:
    token = (eid or "").strip()
    if not token:
        return
    cur = store.get(token)
    if cur is None:
        store[token] = ExperimentCfg(
            id=token,
            data_rate=data_rate,
            sample_amount=sample_amount,
            ec_rate=ec_rate,
            size_mb=size_mb,
        )
        return
    if data_rate is not None and data_rate > 0:
        if cur.data_rate is None or data_rate < cur.data_rate:
            cur.data_rate = data_rate
    if sample_amount is not None:
        if cur.sample_amount is None or sample_amount > cur.sample_amount:
            cur.sample_amount = sample_amount
    if ec_rate is not None and ec_rate > 0:
        if cur.ec_rate is None or ec_rate < cur.ec_rate:
            cur.ec_rate = ec_rate
    if size_mb is not None:
        if cur.size_mb is None or size_mb > cur.size_mb:
            cur.size_mb = size_mb


def _cfg_float(value: str) -> float | None:
    raw = value.split("//", 1)[0].strip().split()[0] if value else ""
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


@dataclass
class Catalog:
    parts: dict[str, PartDef] = field(default_factory=dict)
    source: str = ""
    experiments: dict[str, ExperimentCfg] = field(default_factory=dict)

    def node(self, part_name: str, node: str) -> tuple[float, float, float]:
        key = cfg_name(part_name)
        part = self.parts.get(key) or self.parts.get(part_name)
        if part and node in part.nodes:
            return part.nodes[node]
        fallback = STOCK_NODES.get(key, {}) or STOCK_NODES.get(part_name, {})
        if node in fallback:
            return fallback[node]
        raise KeyError(f"No stack node {node!r} on {part_name}")

    def has(self, part_name: str) -> bool:
        key = cfg_name(part_name)
        return key in self.parts or part_name in self.parts or key in STOCK_NODES

    def get(self, part_name: str) -> PartDef | None:
        key = cfg_name(part_name)
        return self.parts.get(key) or self.parts.get(part_name)

    def by_tech(self, node_id: str) -> list[PartDef]:
        return [p for p in self.parts.values() if p.tech == node_id]

    @classmethod
    def stock(cls) -> Catalog:
        cat = cls(source="stock-nodes")
        for name, nodes in STOCK_NODES.items():
            cat.parts[name] = PartDef(name=name, title=name, nodes=dict(nodes))
        return cat


def _parse_node_stack(value: str) -> tuple[float, float, float]:
    bits = [b.strip() for b in value.split(",")]
    return float(bits[0]), float(bits[1]), float(bits[2])


def _parse_mass(value: str) -> float | None:
    raw = value.split("//", 1)[0].strip()
    try:
        return float(raw)
    except ValueError:
        return None


def _part_from_fields(
    *,
    name: str,
    title: str,
    tech: str,
    category: str,
    mass: str,
    nodes: dict[str, tuple[float, float, float]],
    modules: list[str],
    resources: list[str],
    experiments: list[str],
    cfg_path: str,
    author: str,
) -> PartDef:
    mods = tuple(modules)
    return PartDef(
        name=name,
        title=title or name,
        nodes=nodes,
        cfg_path=cfg_path,
        author=author,
        tech=tech,
        category=category,
        mass=_parse_mass(mass) if mass else None,
        modules=mods,
        resources=tuple(resources),
        experiments=tuple(experiments),
        procedural="ProceduralPart" in mods,
    )


def scan_config_cache(path: str | Path) -> Catalog:
    """Stream ``ModuleManager.ConfigCache`` for patched ``PART`` blocks."""
    cache = Path(path)
    cat = Catalog(source=str(cache))
    if not cache.is_file():
        log.warning("No ConfigCache at %s", cache)
        return cat

    in_part = False
    in_expdef = False
    depth = 0
    kind = ""  # MODULE / RESOURCE while depth >= 2
    kind_depth = 0
    name = title = tech = category = mass = author = ""
    nodes: dict[str, tuple[float, float, float]] = {}
    modules: list[str] = []
    resources: list[str] = []
    experiments: list[str] = []
    module_name = ""
    module_eid = ""
    url = ""
    exp_id = ""
    exp_base: float | None = None
    exp_scale: float | None = None
    exp_depth = 0

    def _commit() -> None:
        nonlocal name, title, tech, category, mass, author, nodes
        nonlocal modules, resources, experiments, url
        if name:
            cat.parts[name] = _part_from_fields(
                name=name,
                title=title,
                tech=tech,
                category=category,
                mass=mass,
                nodes=dict(nodes),
                modules=list(modules),
                resources=list(resources),
                experiments=list(experiments),
                cfg_path=url or str(cache),
                author=author,
            )

    def _reset() -> None:
        nonlocal name, title, tech, category, mass, author, nodes
        nonlocal modules, resources, experiments, module_name, module_eid
        nonlocal kind, kind_depth
        name = title = tech = category = mass = author = ""
        nodes = {}
        modules = []
        resources = []
        experiments = []
        module_name = ""
        module_eid = ""
        kind = ""
        kind_depth = 0

    def _reset_expdef() -> None:
        nonlocal exp_id, exp_base, exp_scale, exp_depth
        exp_id = ""
        exp_base = None
        exp_scale = None
        exp_depth = 0

    def _commit_expdef() -> None:
        if not exp_id:
            return
        size = None
        if exp_base is not None and exp_scale is not None:
            size = exp_base * exp_scale
        merge_experiment_cfg(cat.experiments, exp_id, size_mb=size)

    with cache.open(encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            s = raw.strip()
            if not s or s.startswith("//"):
                continue
            if not in_part and not in_expdef:
                if s.startswith("url ="):
                    url = s.split("=", 1)[1].strip()
                elif s == "PART":
                    in_part = True
                    depth = 0
                    _reset()
                elif s == "EXPERIMENT_DEFINITION":
                    in_expdef = True
                    _reset_expdef()
                continue
            if in_expdef:
                if s == "{":
                    exp_depth += 1
                    continue
                if s == "}":
                    exp_depth -= 1
                    if exp_depth <= 0:
                        _commit_expdef()
                        in_expdef = False
                    continue
                if exp_depth != 1 or "=" not in s:
                    continue
                key, _, rest = s.partition("=")
                key = key.strip()
                value = rest.strip()
                if key == "id" and not exp_id:
                    exp_id = value
                elif key == "baseValue" and exp_base is None:
                    exp_base = _cfg_float(value)
                elif key == "dataScale" and exp_scale is None:
                    exp_scale = _cfg_float(value)
                continue
            if s == "{":
                depth += 1
                continue
            if s == "}":
                if kind and depth == kind_depth:
                    kind = ""
                    module_name = ""
                    module_eid = ""
                depth -= 1
                if depth <= 0:
                    _commit()
                    in_part = False
                    url = ""
                continue
            if s in ("MODULE", "RESOURCE", "EFFECTS", "DRAG_CUBE", "MODEL"):
                kind = s
                kind_depth = depth + 1
                module_name = ""
                module_eid = ""
                continue
            if "=" not in s:
                continue
            key, _, rest = s.partition("=")
            key = key.strip()
            value = rest.strip()
            if depth == 1:
                if key == "name" and not name:
                    name = value
                elif key == "title" and not title:
                    title = value.split("//", 1)[0].strip()
                elif key == "TechRequired":
                    tech = value
                elif key == "category" and not category:
                    category = value
                elif key == "mass" and not mass:
                    mass = value
                elif key == "author" and not author:
                    author = value
                elif key.startswith("node_stack_"):
                    nname = key[len("node_stack_") :]
                    try:
                        nodes[nname] = _parse_node_stack(value)
                    except (ValueError, IndexError):
                        pass
                continue
            if kind == "MODULE" and depth == kind_depth:
                if key == "name" and not module_name:
                    module_name = value
                    modules.append(value)
                    module_eid = ""
                elif key in ("experiment_id", "experimentID") and value:
                    module_eid = value
                    if value not in experiments:
                        experiments.append(value)
                    merge_experiment_cfg(cat.experiments, value)
                elif module_eid and key == "data_rate":
                    merge_experiment_cfg(
                        cat.experiments, module_eid, data_rate=_cfg_float(value)
                    )
                elif module_eid and key == "sample_amount":
                    merge_experiment_cfg(
                        cat.experiments, module_eid, sample_amount=_cfg_float(value)
                    )
                elif module_eid and key == "ec_rate":
                    merge_experiment_cfg(
                        cat.experiments, module_eid, ec_rate=_cfg_float(value)
                    )
            elif kind == "RESOURCE" and depth == kind_depth:
                if key == "name" and value and value not in resources:
                    resources.append(value)

    log.debug("Catalog: %d parts from cache %s", len(cat.parts), cache)
    return cat


def scan_gamedata(ksp_root: str | Path) -> Catalog:
    """Walk ``GameData/**/*.cfg`` for unpatched ``PART { name = ... }``."""
    root = Path(ksp_root) / "GameData"
    cat = Catalog.stock()
    cat.source = str(root)
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
            modules = []
            experiments = []
            resources = []
            for mod in part.of("MODULE"):
                mname = mod.get("name") or ""
                if mname:
                    modules.append(mname)
                eid = mod.get("experiment_id") or mod.get("experimentID") or ""
                if eid and eid not in experiments:
                    experiments.append(eid)
                if eid:
                    merge_experiment_cfg(
                        cat.experiments,
                        eid,
                        data_rate=_cfg_float(mod.get("data_rate") or ""),
                        sample_amount=_cfg_float(mod.get("sample_amount") or ""),
                        ec_rate=_cfg_float(mod.get("ec_rate") or ""),
                    )
            for res in part.of("RESOURCE"):
                rname = res.get("name") or ""
                if rname and rname not in resources:
                    resources.append(rname)
            cat.parts[name] = _part_from_fields(
                name=name,
                title=title,
                tech=part.get("TechRequired") or "",
                category=part.get("category") or "",
                mass=part.get("mass") or "",
                nodes=nodes or cat.parts.get(name, PartDef(name, title, {})).nodes,
                modules=modules,
                resources=resources,
                experiments=experiments,
                cfg_path=str(path),
                author=part.get("author") or "",
            )
    log.debug("Catalog: %d parts from %s", len(cat.parts), root)
    return cat


def load_catalog(ksp_root: str | Path) -> Catalog:
    """ConfigCache if present, else unpatched GameData walk."""
    root = Path(ksp_root)
    cache = root / "GameData" / "ModuleManager.ConfigCache"
    if cache.is_file():
        return scan_config_cache(cache)
    return scan_gamedata(root)
