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
    "probeCoreOcto_v2": {
        "top": (0.0, 0.0785, 0.0),
        "bottom": (0.0, -0.27448, 0.0),
    },
    "sasModule": {
        "top": (0.0, 0.09111, 0.0),
        "bottom": (0.0, -0.09111, 0.0),
    },
    "proceduralTankRealFuels": {
        "top": (0.0, 0.3125, 0.0),
        "bottom": (0.0, -0.3125, 0.0),
    },
    "proceduralHeatshield": {
        # Heatshield.cfg MODEL nodes (±0.5), not length/2. PP cache matches.
        "top": (0.0, 0.5, 0.0),
        "bottom": (0.0, -0.5, 0.0),
    },
    "restock-engine-125-valiant": {"top": (0.0, 0.45, 0.0)},
    "RC_cone": {"bottom": (0.0, -0.1963, 0.0)},
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
    data_capacity: float | None = None
    sample_capacity: float | None = None
    antenna_gain: float | None = None
    antenna_diameter: float | None = None
    antenna_band: str = ""
    fuel_cross_feed: bool | None = None


@dataclass(slots=True)
class ExperimentCfg:
    """Live MM-cache experiment (post kspstuffScience). Not tweak-file gospel."""

    id: str
    data_rate: float | None = None
    sample_amount: float | None = None
    ec_rate: float | None = None
    size_mb: float | None = None
    science_cap: float | None = None
    base_value: float | None = None
    situations: tuple[str, ...] = ()
    sample_mass: float | None = None
    sample_collecting: bool = False

    @property
    def kind(self) -> str:
        if (self.sample_amount and self.sample_amount > 0) or (
            self.sample_mass and self.sample_mass > 0
        ) or self.sample_collecting:
            return "sample"
        return "file"

    @property
    def duration_s(self) -> float | None:
        if self.data_rate and self.data_rate > 0 and self.size_mb:
            return self.size_mb / self.data_rate
        return None


def merge_experiment_cfg(
    store: dict[str, ExperimentCfg],
    eid: str,
    *,
    data_rate: float | None = None,
    sample_amount: float | None = None,
    ec_rate: float | None = None,
    size_mb: float | None = None,
    science_cap: float | None = None,
    base_value: float | None = None,
    situations: tuple[str, ...] | None = None,
    sample_mass: float | None = None,
    sample_collecting: bool | None = None,
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
            science_cap=science_cap,
            base_value=base_value,
            situations=situations or (),
            sample_mass=sample_mass,
            sample_collecting=bool(sample_collecting),
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
    # Last write wins for defs (kspstuffScience after Kerbalism).
    if size_mb is not None:
        cur.size_mb = size_mb
    if science_cap is not None:
        cur.science_cap = science_cap
    if base_value is not None:
        cur.base_value = base_value
    if sample_mass is not None:
        cur.sample_mass = sample_mass
    if sample_collecting:
        cur.sample_collecting = True
    if situations:
        cur.situations = tuple(dict.fromkeys([*cur.situations, *situations]))


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
            # PP/stock heatshields do not cross-feed (Heatshield.cfg).
            cf = False if name == "proceduralHeatshield" else None
            cat.parts[name] = PartDef(
                name=name,
                title=name,
                nodes=dict(nodes),
                fuel_cross_feed=cf,
            )
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


def _parse_bool(value: str) -> bool | None:
    raw = value.split("//", 1)[0].strip().lower()
    if raw in {"true", "1", "yes"}:
        return True
    if raw in {"false", "0", "no"}:
        return False
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
    data_capacity: float | None = None,
    sample_capacity: float | None = None,
    antenna_gain: float | None = None,
    antenna_diameter: float | None = None,
    antenna_band: str = "",
    fuel_cross_feed: bool | None = None,
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
        data_capacity=data_capacity,
        sample_capacity=sample_capacity,
        antenna_gain=antenna_gain,
        antenna_diameter=antenna_diameter,
        antenna_band=antenna_band,
        fuel_cross_feed=fuel_cross_feed,
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
    fuel_cf: bool | None = None
    module_name = ""
    module_eid = ""
    url = ""
    hd_eid = ""
    hd_data: float | None = None
    hd_samples: float | None = None
    ra_gain: float | None = None
    ra_diam: float | None = None
    ra_band = ""
    part_hd_data: float | None = None
    part_hd_samples: float | None = None
    part_ra_gain: float | None = None
    part_ra_diam: float | None = None
    part_ra_band = ""
    exp_id = ""
    exp_base: float | None = None
    exp_scale: float | None = None
    exp_cap: float | None = None
    exp_mass: float | None = None
    exp_sits: list[str] = []
    exp_depth = 0

    def _commit() -> None:
        nonlocal name, title, tech, category, mass, author, nodes
        nonlocal modules, resources, experiments, url, fuel_cf
        nonlocal part_hd_data, part_hd_samples, part_ra_gain, part_ra_diam, part_ra_band
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
                data_capacity=part_hd_data,
                sample_capacity=part_hd_samples,
                antenna_gain=part_ra_gain,
                antenna_diameter=part_ra_diam,
                antenna_band=part_ra_band,
                fuel_cross_feed=fuel_cf,
            )

    def _reset() -> None:
        nonlocal name, title, tech, category, mass, author, nodes
        nonlocal modules, resources, experiments, module_name, module_eid
        nonlocal kind, kind_depth, fuel_cf
        nonlocal hd_eid, hd_data, hd_samples, ra_gain, ra_diam, ra_band
        nonlocal part_hd_data, part_hd_samples, part_ra_gain, part_ra_diam, part_ra_band
        name = title = tech = category = mass = author = ""
        nodes = {}
        modules = []
        resources = []
        experiments = []
        fuel_cf = None
        module_name = ""
        module_eid = ""
        hd_eid = ""
        hd_data = hd_samples = ra_gain = ra_diam = None
        ra_band = ""
        part_hd_data = part_hd_samples = part_ra_gain = part_ra_diam = None
        part_ra_band = ""
        kind = ""
        kind_depth = 0

    def _reset_expdef() -> None:
        nonlocal exp_id, exp_base, exp_scale, exp_depth
        nonlocal exp_cap, exp_sits, exp_mass
        exp_id = ""
        exp_base = None
        exp_scale = None
        exp_cap = None
        exp_mass = None
        exp_sits = []
        exp_depth = 0

    def _commit_expdef() -> None:
        if not exp_id:
            return
        size = None
        if exp_base is not None and exp_scale is not None:
            size = exp_base * exp_scale
        merge_experiment_cfg(
            cat.experiments,
            exp_id,
            size_mb=size,
            science_cap=exp_cap,
            base_value=exp_base,
            situations=tuple(exp_sits),
            sample_mass=exp_mass,
        )

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
                if "=" not in s:
                    continue
                key, _, rest = s.partition("=")
                key = key.strip()
                value = rest.strip()
                if key == "Situation":
                    exp_sits.append(value)
                    continue
                if key == "SampleMass":
                    exp_mass = _cfg_float(value)
                    continue
                if exp_depth != 1:
                    continue
                if key == "id" and not exp_id:
                    exp_id = value
                elif key == "baseValue":
                    exp_base = _cfg_float(value)
                elif key == "scienceCap":
                    exp_cap = _cfg_float(value)
                elif key == "dataScale":
                    exp_scale = _cfg_float(value)
                continue
            if s == "{":
                depth += 1
                continue
            if s == "}":
                if kind and depth == kind_depth:
                    if module_name == "HardDrive" and not hd_eid:
                        if hd_data is not None:
                            part_hd_data = hd_data
                        if hd_samples is not None:
                            part_hd_samples = hd_samples
                    if module_name == "ModuleRealAntenna":
                        if ra_gain is not None:
                            part_ra_gain = ra_gain
                        if ra_diam is not None:
                            part_ra_diam = ra_diam
                        if ra_band:
                            part_ra_band = ra_band
                    kind = ""
                    module_name = ""
                    module_eid = ""
                    hd_eid = ""
                    hd_data = hd_samples = ra_gain = ra_diam = None
                    ra_band = ""
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
                hd_eid = ""
                hd_data = hd_samples = ra_gain = ra_diam = None
                ra_band = ""
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
                elif key == "fuelCrossFeed":
                    parsed = _parse_bool(value)
                    if parsed is not None:
                        fuel_cf = parsed
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
                elif module_eid and key == "sample_collecting" and value.lower() in {
                    "true",
                    "1",
                }:
                    merge_experiment_cfg(
                        cat.experiments, module_eid, sample_collecting=True
                    )
                elif module_name == "HardDrive":
                    if key in ("experiment_id", "experimentID") and value:
                        hd_eid = value
                    elif key == "dataCapacity":
                        hd_data = _cfg_float(value)
                    elif key == "sampleCapacity":
                        hd_samples = _cfg_float(value)
                elif module_name == "ModuleRealAntenna":
                    if key == "referenceGain":
                        ra_gain = _cfg_float(value)
                    elif key == "antennaDiameter":
                        ra_diam = _cfg_float(value)
                    elif key == "RFBand":
                        ra_band = value
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
            raw_cf = part.get("fuelCrossFeed")
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
                fuel_cross_feed=_parse_bool(raw_cf) if raw_cf else None,
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
