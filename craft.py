"""``.craft`` ships: parse, write, stack along part nodes.

kRPC cannot place parts in the VAB. A craft file in
``saves/<save>/Ships/VAB/`` *can* be launched. This module is that file.

Part tokens in the file use dots for underscores: ``mk1pod_v2`` →
``mk1pod.v2_<uid>``. Procedural/RO modules belong in ``modules`` later;
stock reconstructs MODULE blocks from ``part.cfg`` on load.
"""

from __future__ import annotations

import argparse
import math
import random
from dataclasses import dataclass, field
from pathlib import Path

from catalog import Catalog, load_catalog
from cfg import CfgNode, dump, load, loads


def _uid() -> int:
    return random.randint(1_000_000_000, 2_000_000_000)


def part_token(name: str, uid: int) -> str:
    return f"{name.replace('_', '.')}_{uid}"


def split_token(token: str) -> tuple[str, int]:
    base, _, rest = token.rpartition("_")
    try:
        return base.replace(".", "_"), int(rest.split("|")[0])
    except ValueError:
        return token.replace(".", "_"), 0


def _vec3(text: str) -> tuple[float, float, float]:
    a, b, c = (p.strip() for p in text.split(",")[:3])
    return float(a), float(b), float(c)


def _fmt3(v: tuple[float, float, float]) -> str:
    return f"{v[0]},{v[1]},{v[2]}"


def _fmt4(v: tuple[float, float, float, float]) -> str:
    return f"{v[0]},{v[1]},{v[2]},{v[3]}"


@dataclass
class CraftPart:
    name: str
    uid: int = field(default_factory=_uid)
    pos: tuple[float, float, float] = (0.0, 15.0, 0.0)
    rot: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0)
    links: list[str] = field(default_factory=list)
    att_n: dict[str, str] = field(default_factory=dict)
    attm: int = 0
    srf_n: str = ""
    att_pos0: tuple[float, float, float] | None = None
    istg: int = -1
    dstg: int = 0
    sidx: int = -1
    sqor: int = -1
    sep_i: int = -1
    autostrut_mode: str = "Off"
    rigid_attachment: str = "False"
    persistent_id: int = field(default_factory=_uid)
    modules: list[CfgNode] = field(default_factory=list)
    resources: list[CfgNode] = field(default_factory=list)
    extra: list[tuple[str, str]] = field(default_factory=list)

    @property
    def token(self) -> str:
        return part_token(self.name, self.uid)

    def to_node(self) -> CfgNode:
        n = CfgNode(name="PART")
        n.add("part", self.token)
        n.add("partName", "Part")
        n.add("persistentId", str(self.persistent_id))
        n.add("pos", _fmt3(self.pos))
        n.add("attPos", "0,0,0")
        n.add("attPos0", _fmt3(self.att_pos0 if self.att_pos0 is not None else self.pos))
        n.add("rot", _fmt4(self.rot))
        n.add("attRot", "0,0,0,1")
        n.add("attRot0", _fmt4(self.rot) if self.attm else "0,0,0,1")
        n.add("mir", "1,1,1")
        n.add("symMethod", "Radial")
        n.add("autostrutMode", self.autostrut_mode)
        n.add("rigidAttachment", self.rigid_attachment)
        n.add("istg", str(self.istg))
        n.add("resPri", "0")
        n.add("dstg", str(self.dstg))
        n.add("sidx", str(self.sidx))
        n.add("sqor", str(self.sqor))
        n.add("sepI", str(self.sep_i))
        n.add("attm", str(self.attm))
        n.add("modCost", "0")
        n.add("modMass", "0")
        n.add("modSize", "0,0,0")
        for link in self.links:
            n.add("link", link)
        for node_name, other in self.att_n.items():
            n.add("attN", f"{node_name},{other}" if other else f"{node_name},Null")
        if self.srf_n:
            n.add("srfN", self.srf_n)
        for key, value in self.extra:
            n.add(key, value)
        n.children.append(CfgNode(name="EVENTS"))
        n.children.append(CfgNode(name="ACTIONS"))
        n.children.append(CfgNode(name="PARTDATA"))
        n.children.extend(self.modules)
        n.children.extend(self.resources)
        return n

    @classmethod
    def from_node(cls, node: CfgNode) -> CraftPart:
        token = node.get("part") or ""
        name, uid = split_token(token)
        att: dict[str, str] = {}
        for raw in node.get_all("attN"):
            node_name, _, rest = raw.partition(",")
            att[node_name.strip()] = rest.strip()
        pos = _vec3(node.get("pos") or "0,0,0")
        rot_s = node.get("rot") or "0,0,0,1"
        r = [float(x) for x in rot_s.split(",")[:4]]
        while len(r) < 4:
            r.append(0.0)
        extra_skip = {
            "part",
            "partName",
            "persistentId",
            "pos",
            "attPos",
            "attPos0",
            "rot",
            "attRot",
            "attRot0",
            "mir",
            "symMethod",
            "autostrutMode",
            "rigidAttachment",
            "istg",
            "resPri",
            "dstg",
            "sidx",
            "sqor",
            "sepI",
            "attm",
            "modCost",
            "modMass",
            "modSize",
            "link",
            "attN",
            "srfN",
        }
        extra = [(k, v) for k, v in node.values if k not in extra_skip]
        return cls(
            name=name,
            uid=uid,
            pos=pos,
            rot=(r[0], r[1], r[2], r[3]),
            links=list(node.get_all("link")),
            att_n=att,
            attm=int(node.get("attm") or 0),
            srf_n=node.get("srfN") or "",
            att_pos0=_vec3(node.get("attPos0") or node.get("pos") or "0,0,0"),
            istg=int(node.get("istg") or -1),
            dstg=int(node.get("dstg") or 0),
            sidx=int(node.get("sidx") or -1),
            sqor=int(node.get("sqor") or -1),
            sep_i=int(node.get("sepI") or -1),
            autostrut_mode=node.get("autostrutMode") or "Off",
            rigid_attachment=node.get("rigidAttachment") or "False",
            persistent_id=int(node.get("persistentId") or _uid()),
            modules=[c for c in node.children if c.name == "MODULE"],
            resources=[c for c in node.children if c.name == "RESOURCE"],
            extra=extra,
        )


@dataclass
class Craft:
    name: str
    kind: str = "VAB"
    version: str = "1.12.5"
    description: str = ""
    parts: list[CraftPart] = field(default_factory=list)
    vessel_type: str = "Ship"
    flag: str = "Squad/Flags/default"
    size: str = "2,12,2"
    persistent_id: int = field(default_factory=_uid)

    def to_node(self) -> CfgNode:
        n = CfgNode(name="")
        n.add("ship", self.name)
        n.add("version", self.version)
        n.add("description", self.description)
        n.add("type", self.kind)
        n.add("size", self.size)
        n.add("steamPublishedFileId", "0")
        n.add("persistentId", str(self.persistent_id))
        n.add("rot", "0,0,0,1")
        n.add("missionFlag", self.flag)
        n.add("vesselType", self.vessel_type)
        for part in self.parts:
            n.children.append(part.to_node())
        return n

    def dumps(self) -> str:
        return self.to_node().dumps(root=True)

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        dump(self.to_node(), path, root=True)
        return path

    @classmethod
    def from_node(cls, node: CfgNode) -> Craft:
        name = node.get("ship") or "unnamed"
        if "//" in name:
            name = name.split("//")[-1].split("=", 1)[-1].strip() or name
        return cls(
            name=name,
            kind=node.get("type") or "VAB",
            version=node.get("version") or "1.12.5",
            description=node.get("description") or "",
            parts=[CraftPart.from_node(p) for p in node.of("PART")],
            vessel_type=node.get("vesselType") or "Ship",
            flag=node.get("missionFlag") or "Squad/Flags/default",
            size=node.get("size") or "2,12,2",
            persistent_id=int(node.get("persistentId") or _uid()),
        )

    @classmethod
    def loads(cls, text: str) -> Craft:
        return cls.from_node(loads(text))

    @classmethod
    def load(cls, path: str | Path) -> Craft:
        return cls.from_node(load(path))

    def summary(self) -> str:
        names = ", ".join(p.name for p in self.parts[:12])
        extra = "" if len(self.parts) <= 12 else f" +{len(self.parts) - 12}"
        return f"{self.name}  {self.kind}  {len(self.parts)} parts  ({names}{extra})"


class StackBuilder:
    """Attach parts along stack nodes. Positions from a :class:`Catalog`."""

    def __init__(self, name: str, catalog: Catalog | None = None) -> None:
        self.craft = Craft(name=name)
        self.catalog = catalog or Catalog.stock()
        self._bottom: CraftPart | None = None

    def root(self, part_name: str, *, y: float = 15.0) -> CraftPart:
        part = CraftPart(name=part_name, pos=(0.0, y, 0.0), istg=-1, dstg=0)
        self.craft.parts.append(part)
        self._bottom = part
        return part

    def attach(
        self,
        parent: CraftPart,
        parent_node: str,
        child_name: str,
        child_node: str = "top",
        *,
        istg: int | None = None,
        dstg: int | None = None,
        sidx: int = -1,
    ) -> CraftPart:
        p_off = self.catalog.node(parent.name, parent_node)
        c_off = self.catalog.node(child_name, child_node)
        pos = (
            parent.pos[0] + p_off[0] - c_off[0],
            parent.pos[1] + p_off[1] - c_off[1],
            parent.pos[2] + p_off[2] - c_off[2],
        )
        child = CraftPart(
            name=child_name,
            pos=pos,
            istg=parent.istg if istg is None else istg,
            dstg=parent.dstg if dstg is None else dstg,
            sidx=sidx,
        )
        parent.links.append(child.token)
        parent.att_n[parent_node] = child.token
        child.att_n[child_node] = parent.token
        self.craft.parts.append(child)
        if parent_node == "bottom":
            self._bottom = child
        return child

    def srf_attach(
        self,
        parent: CraftPart,
        child_name: str,
        offset: tuple[float, float, float],
        rot: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0),
        *,
        istg: int | None = None,
        dstg: int | None = None,
        sidx: int = -1,
    ) -> CraftPart:
        """Surface-attach (Goo, fins). Offset is parent-relative."""
        pos = (
            parent.pos[0] + offset[0],
            parent.pos[1] + offset[1],
            parent.pos[2] + offset[2],
        )
        child = CraftPart(
            name=child_name,
            pos=pos,
            rot=rot,
            attm=1,
            srf_n=f"srfAttach,{parent.token}",
            att_pos0=offset,
            istg=parent.istg if istg is None else istg,
            dstg=parent.dstg if dstg is None else dstg,
            sidx=sidx,
        )
        parent.links.append(child.token)
        self.craft.parts.append(child)
        return child

    def stack(self, child_name: str, **kwargs: int) -> CraftPart:
        if self._bottom is None:
            raise RuntimeError("Call root() before stack()")
        return self.attach(self._bottom, "bottom", child_name, "top", **kwargs)


def procedural_cylinder(
    diameter: float,
    length: float,
    *,
    tank_type: str = "SolidFuel",
) -> list[CfgNode]:
    """MODULE blocks for a ProceduralParts cylinder (meters).

    Default ``tank_type=SolidFuel`` is pad_pbc SRB. Liquid Valiant tanks
    use :func:`liquid_cylinder` (Default Kero/LOx) — do not reuse this.
    """
    part = CfgNode(name="MODULE")
    part.add("name", "ProceduralPart")
    part.add("isEnabled", "True")
    part.add("shapeName", "Cylinder")
    cyl = CfgNode(name="MODULE")
    cyl.add("name", "ProceduralShapeCylinder")
    cyl.add("isEnabled", "True")
    cyl.add("diameter", f"{diameter:g}")
    cyl.add("length", f"{length:g}")
    tanks = CfgNode(name="MODULE")
    tanks.add("name", "ModuleFuelTanks")
    tanks.add("type", tank_type)
    tanks.add("volume", f"{max(diameter, 0.01) * max(length, 0.01) * 1000:g}")
    return [part, cyl, tanks]


def set_cylinder(part: CraftPart, *, diameter: float, length: float) -> CraftPart:
    part.modules.extend(procedural_cylinder(diameter, length))
    return part


def pad_pbc(
    name: str = "kspstuff-pad-pbc",
    *,
    diameter: float = 0.625,
    length: float = 1.2,
    catalog: Catalog | None = None,
) -> Craft:
    """PBC Start probe: Stayputnik + 3×Z-100 + omni + Goo + thermometer + SRB.

    No Mk1, no chute. Procedural SRB meters in the craft text.
    proceduralBattery is basicScience, not Start — stack Z-100s instead.
    """
    b = StackBuilder(name, catalog or Catalog.stock())
    b.craft.description = (
        f"kspstuff PBC pad. Stayputnik + 3xZ-100 + Goo + thermometer + "
        f"procedural SRB {diameter:g}x{length:g} m."
    )
    b.craft.vessel_type = "Probe"
    probe = b.root("probeCoreSphere_v2")
    # 3× Z-100 on +X (300 EC + Stayputnik 10). One pack died at T+483 s.
    b.srf_attach(probe, "batteryPack", (0.13, 0.12, 0.0))
    b.srf_attach(probe, "batteryPack", (0.13, 0.0, 0.0))
    b.srf_attach(probe, "batteryPack", (0.13, -0.12, 0.0))
    b.srf_attach(probe, "SurfAntenna", (-0.12, 0.0, 0.0))
    b.srf_attach(probe, "GooExperiment", (0.0, 0.05, 0.14))
    b.srf_attach(probe, "sensorThermometer", (0.0, 0.05, -0.14))
    srb = b.attach(
        probe,
        "bottom",
        "proceduralSRBRealFuels",
        "top",
        istg=0,
        dstg=0,
        sidx=0,
    )
    set_cylinder(srb, diameter=diameter, length=length)
    return b.craft


TEMPLATES = {
    "pad-pbc": pad_pbc,
}

CRAFTS_DIR = Path(__file__).resolve().parent / "crafts"

TANK_NAMES = frozenset({"fuelTankSmallFlat", "proceduralTankRealFuels"})
CHUTE_NAMES = frozenset({"parachuteSingle", "RC_cone", "parachuteRadial"})
ENGINE_PREFIXES = (
    "restock-engine",
    "liquidEngine",
    "nuclearEngine",
    "solidBooster",
    "proceduralSRB",
)
PROBE_NAMES = frozenset(
    {"probeCoreSphere_v2", "probeCoreOcto_v2", "probeCoreHex_v2", "probeCoreCube"}
)
DONOR_MK16 = "kspstuff-hop-valiant-t7-chute-pbc"
DONOR_CONE = "kspstuff-hop-valiant-t7-chute-cone-pbc"
T100_VOLUME = 500
T100_HEIGHT = 0.625
PRESMAT_OFFSET = (0.16, 0.05, 0.12)


class CraftError(ValueError):
    """Gus-facing VAB helper error (no Hangar, no kRPC)."""


def _copy_node(node: CfgNode) -> CfgNode:
    return CfgNode(
        name=node.name,
        values=list(node.values),
        children=[_copy_node(c) for c in node.children],
    )


def _mod(part: CraftPart, name: str) -> CfgNode | None:
    for mod in part.modules:
        if mod.get("name") == name:
            return mod
    return None


def _tank(parent: CfgNode, name: str, amount: int) -> None:
    n = CfgNode(name="TANK")
    n.add("name", name)
    n.add("amount", str(amount))
    n.add("maxAmount", str(amount))
    parent.children.append(n)


def _resource(name: str, amount: int) -> CfgNode:
    n = CfgNode(name="RESOURCE")
    n.add("name", name)
    n.add("amount", str(amount))
    n.add("maxAmount", str(amount))
    return n


def kero_lox_amounts(volume: int) -> tuple[int, int]:
    """RF Default mix used on signed hangs: 45% Kerosene / 55% LqdOxygen."""
    kero = int(round(volume * 0.45))
    return kero, volume - kero


def proc_volume(diameter: float, length: float) -> int:
    """Liters for a cylinder. 1.25×0.625 → 767; 1.25×0.65 snaps to 800."""
    raw = math.pi * (diameter * 0.5) ** 2 * length * 1000.0
    if abs(raw - 800.0) < 5.0:
        return 800
    return max(1, int(round(raw)))


def rf_fuel_module(volume: int, *, tank_type: str = "Default") -> CfgNode:
    kero, lox = kero_lox_amounts(volume)
    tanks = CfgNode(name="MODULE")
    tanks.add("name", "ModuleFuelTanks")
    tanks.add("volume", str(volume))
    tanks.add("type", tank_type)
    _tank(tanks, "Kerosene", kero)
    _tank(tanks, "LqdOxygen", lox)
    return tanks


def rf_fuel_resources(volume: int) -> list[CfgNode]:
    kero, lox = kero_lox_amounts(volume)
    return [_resource("Kerosene", kero), _resource("LqdOxygen", lox)]


def liquid_cylinder(diameter: float, length: float) -> tuple[list[CfgNode], list[CfgNode]]:
    """Procedural tank MODULE+RESOURCE: Default Kero/LOx, never SolidFuel.

    volumeMax on signed hangs is 0.8 kL (1500 L is generalRocketry).
    """
    volume = proc_volume(diameter, length)
    shape = CfgNode(name="MODULE")
    shape.add("name", "ProceduralPart")
    shape.add("shapeName", "Cylinder")
    shape.add("textureSet", "PlainWhite")
    cyl = CfgNode(name="MODULE")
    cyl.add("name", "ProceduralShapeCylinder")
    cyl.add("diameter", f"{diameter:g}")
    cyl.add("length", f"{length:g}")
    return [shape, cyl, rf_fuel_module(volume)], rf_fuel_resources(volume)


def t100_fuel() -> tuple[list[CfgNode], list[CfgNode]]:
    return [rf_fuel_module(T100_VOLUME)], rf_fuel_resources(T100_VOLUME)


def mk16_chute_modules() -> list[CfgNode]:
    """Nylon Mk16 5/35. minIsPressure false; minDeployment 2500; deployAlt 700."""
    chute = CfgNode(name="PARACHUTE")
    chute.add("material", "Nylon")
    chute.add("preDeployedDiameter", "5")
    chute.add("deployedDiameter", "35")
    chute.add("minIsPressure", "false")
    chute.add("minDeployment", "2500")
    chute.add("minPressure", "0.01")
    chute.add("deploymentAlt", "700")
    chute.add("cutAlt", "-1")
    chute.add("preDeploymentSpeed", "2")
    chute.add("deploymentSpeed", "6")
    chute.add("preDeploymentAnimation", "semiDeployLarge")
    chute.add("deploymentAnimation", "fullyDeployLarge")
    chute.add("parachuteName", "B_ParachuteRoot004")
    chute.add("capName", "SmallChuteCap")
    chute.add("referenceDiameter", "11.268")
    real = CfgNode(name="MODULE")
    real.add("name", "RealChuteModule")
    real.add("caseMass", "0.075")
    real.add("timer", "0")
    real.add("mustGoDown", "True")
    real.add("cutSpeed", "0.5")
    real.add("spareChutes", "5")
    real.add("stagingEnabled", "True")
    real.children.append(chute)
    proc = CfgNode(name="MODULE")
    proc.add("name", "ProceduralChute")
    proc.add("textureLibrary", "StockReplacement")
    proc.add("currentCanopies", "Main chute")
    proc.add("currentCanopyModels", "Single chute")
    return [real, proc]


def rc_cone_chute_modules() -> list[CfgNode]:
    """Nylon RC_cone 50 m / pre 2.5 m. Same deploy envelope as Mk16."""
    chute = CfgNode(name="PARACHUTE")
    chute.add("material", "Nylon")
    chute.add("capName", "cone")
    chute.add("parachuteName", "RC_triple_canopy")
    chute.add("preDeploymentAnimation", "RC_triple_chute_semi_deploy")
    chute.add("deploymentAnimation", "RC_triple_chute_full_deploy")
    chute.add("preDeployedDiameter", "2.5")
    chute.add("deployedDiameter", "50")
    chute.add("minIsPressure", "false")
    chute.add("minDeployment", "2500")
    chute.add("deploymentAlt", "700")
    chute.add("cutAlt", "-1")
    chute.add("preDeploymentSpeed", "2")
    chute.add("deploymentSpeed", "6")
    real = CfgNode(name="MODULE")
    real.add("name", "RealChuteModule")
    real.add("caseMass", "0.04")
    real.add("timer", "0")
    real.add("mustGoDown", "True")
    real.add("cutSpeed", "0.5")
    real.add("spareChutes", "5")
    real.add("stagingEnabled", "True")
    real.children.append(chute)
    proc = CfgNode(name="MODULE")
    proc.add("name", "ProceduralChute")
    proc.add("size", "2")
    proc.add("lastSize", "2")
    proc.add("originalSize", "0.425,0.4,0.425")
    proc.add("textureLibrary", "RealChute")
    proc.add("type", "Cone")
    proc.add("currentCase", "Main")
    proc.add("currentCanopies", "Main chute")
    return [real, proc]


def heatshield_modules(
    *,
    top: float,
    bottom: float,
    length: float,
    ablator: int = 80,
) -> tuple[list[CfgNode], list[CfgNode]]:
    part = CfgNode(name="MODULE")
    part.add("name", "ProceduralPart")
    part.add("textureSet", "Ablative")
    part.add("shapeName", "Smooth Cone")
    part.add("capTextureIndex", "1")
    cone = CfgNode(name="MODULE")
    cone.add("name", "ProceduralShapeBezierCone")
    cone.add("selectedShape", "Round3")
    cone.add("topDiameter", f"{top:g}")
    cone.add("bottomDiameter", f"{bottom:g}")
    cone.add("length", f"{length:g}")
    hs = CfgNode(name="MODULE")
    hs.add("name", "ProceduralHeatshield")
    hs.add("ablativeResource", "Ablator")
    res = CfgNode(name="RESOURCE")
    res.add("name", "Ablator")
    res.add("amount", str(ablator))
    res.add("maxAmount", str(ablator))
    return [part, cone, hs], [res]


def _chute_parachute(part: CraftPart) -> CfgNode | None:
    real = _mod(part, "RealChuteModule")
    if real is None:
        return None
    kids = real.of("PARACHUTE")
    return kids[0] if kids else None


def chute_is_nylon_good(part: CraftPart) -> bool:
    """Reject empty / inherited 0.04 atm / 0.8 m templates (T-155/T-156)."""
    para = _chute_parachute(part)
    if para is None:
        return False
    if (para.get("material") or "") != "Nylon":
        return False
    if (para.get("minIsPressure") or "").lower() not in {"false", "0"}:
        return False
    try:
        deployed = float(para.get("deployedDiameter") or "0")
    except ValueError:
        return False
    return deployed >= 5.0


def resolve_craft_path(name: str | Path) -> Path:
    raw = Path(name)
    if raw.suffix.lower() != ".craft":
        raw = raw.with_suffix(".craft") if raw.suffix == "" else raw
    if raw.is_file():
        return raw
    cand = CRAFTS_DIR / raw.name
    if cand.is_file():
        return cand
    raise CraftError(f"no craft at {name}")


def _by_token(craft: Craft) -> dict[str, CraftPart]:
    return {p.token: p for p in craft.parts}


def _find_named(craft: Craft, name: str) -> list[CraftPart]:
    return [p for p in craft.parts if p.name == name]


def axial_tanks(craft: Craft) -> list[CraftPart]:
    tanks = [p for p in craft.parts if p.name in TANK_NAMES and p.attm == 0]
    tanks.sort(key=lambda p: p.pos[1], reverse=True)
    return tanks


def find_engine(craft: Craft) -> CraftPart | None:
    for p in craft.parts:
        if any(p.name.startswith(pref) for pref in ENGINE_PREFIXES):
            return p
    return None


def find_core(craft: Craft) -> CraftPart | None:
    for name in ("probeCoreSphere_v2", "probeCoreOcto_v2", "probeCoreHex_v2"):
        found = _find_named(craft, name)
        if found:
            return found[0]
    return None


def find_chutes(craft: Craft) -> list[CraftPart]:
    return [p for p in craft.parts if p.name in CHUTE_NAMES]


def retarget(craft: Craft, old: str, new: str) -> None:
    if old == new:
        return
    for p in craft.parts:
        p.links = [new if t == old else t for t in p.links]
        p.att_n = {k: (new if v == old else v) for k, v in p.att_n.items()}
        if p.srf_n:
            kind, sep, rest = p.srf_n.partition(",")
            if sep and rest == old:
                p.srf_n = f"{kind},{new}"


def _shift_part(part: CraftPart, dy: float) -> None:
    if abs(dy) < 1e-9:
        return
    part.pos = (part.pos[0], part.pos[1] + dy, part.pos[2])
    if part.attm == 0:
        part.att_pos0 = part.pos


def _node_off(
    catalog: Catalog,
    part_name: str,
    node: str,
    *,
    half: float | None = None,
) -> tuple[float, float, float]:
    if half is not None:
        if node == "top":
            return (0.0, half, 0.0)
        if node == "bottom":
            return (0.0, -half, 0.0)
    try:
        return catalog.node(part_name, node)
    except KeyError:
        if half is None:
            raise
        return (0.0, half if node == "top" else -half, 0.0)


def tank_height(part: CraftPart) -> float:
    if part.name == "fuelTankSmallFlat":
        return T100_HEIGHT
    cyl = _mod(part, "ProceduralShapeCylinder")
    if cyl is not None:
        try:
            return float(cyl.get("length") or T100_HEIGHT)
        except ValueError:
            return T100_HEIGHT
    return T100_HEIGHT


def tank_diameter(part: CraftPart) -> float:
    cyl = _mod(part, "ProceduralShapeCylinder")
    if cyl is not None:
        try:
            return float(cyl.get("diameter") or 1.25)
        except ValueError:
            return 1.25
    return 1.25


def clone_craft(src: str | Path, name: str, dest: str | Path | None = None) -> Path:
    """Rename ship= and write crafts/<name>.craft. Does not Hangar."""
    path = resolve_craft_path(src)
    craft = Craft.load(path)
    craft.name = name
    craft.persistent_id = _uid()
    out = Path(dest) if dest else CRAFTS_DIR / f"{name}.craft"
    if out.exists() and out.resolve() != path.resolve():
        raise CraftError(f"refusing to overwrite {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    craft.save(out)
    return out


def surface_attach(
    craft: Craft,
    parent: CraftPart,
    child_name: str,
    offset: tuple[float, float, float],
    rot: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0),
    *,
    autostrut: str = "Off",
    rigid: str = "False",
) -> CraftPart:
    child = CraftPart(
        name=child_name,
        pos=(
            parent.pos[0] + offset[0],
            parent.pos[1] + offset[1],
            parent.pos[2] + offset[2],
        ),
        rot=rot,
        attm=1,
        srf_n=f"srfAttach,{parent.token}",
        att_pos0=offset,
        istg=parent.istg,
        dstg=parent.dstg,
        autostrut_mode=autostrut,
        rigid_attachment=rigid,
    )
    parent.links.append(child.token)
    craft.parts.append(child)
    return child


def insert_inline(
    craft: Craft,
    parent: CraftPart,
    child: CraftPart,
    new: CraftPart,
    *,
    catalog: Catalog | None = None,
    parent_node: str = "bottom",
    child_node: str = "top",
    new_top: str = "top",
    new_bottom: str = "bottom",
    new_half: float | None = None,
) -> CraftPart:
    """Splice ``new`` between stack ``parent`` and ``child``. Shift below."""
    cat = catalog or Catalog.stock()
    p_off = _node_off(cat, parent.name, parent_node)
    n_top = _node_off(cat, new.name, new_top, half=new_half)
    n_bot = _node_off(cat, new.name, new_bottom, half=new_half)
    if child.name in TANK_NAMES:
        c_off = _node_off(
            cat, child.name, child_node, half=tank_height(child) * 0.5
        )
    else:
        try:
            c_off = _node_off(cat, child.name, child_node)
        except KeyError:
            c_off = (0.0, tank_height(child) * 0.5, 0.0)
    new.pos = (
        parent.pos[0] + p_off[0] - n_top[0],
        parent.pos[1] + p_off[1] - n_top[1],
        parent.pos[2] + p_off[2] - n_top[2],
    )
    new.att_pos0 = new.pos
    new_child_y = new.pos[1] + n_bot[1] - c_off[1]
    dy = new_child_y - child.pos[1]
    y0 = child.pos[1]
    parent.links = [t for t in parent.links if t != child.token]
    parent.links.append(new.token)
    parent.att_n[parent_node] = new.token
    new.att_n[new_top] = parent.token
    new.att_n[new_bottom] = child.token
    new.links.append(child.token)
    child.att_n[child_node] = new.token
    if new not in craft.parts:
        # Keep stack order: insert just before the old child.
        idx = craft.parts.index(child)
        craft.parts.insert(idx, new)
    for p in craft.parts:
        if p is new:
            continue
        if p.pos[1] <= y0 + 1e-4:
            _shift_part(p, dy)
    return new


def _fill_tank(
    part: CraftPart,
    *,
    kind: str,
    diameter: float,
    length: float,
) -> None:
    if kind == "proc":
        part.name = "proceduralTankRealFuels"
        mods, res = liquid_cylinder(diameter, length)
    else:
        part.name = "fuelTankSmallFlat"
        mods, res = t100_fuel()
    part.modules = mods
    part.resources = res


def replace_tanks(
    craft: Craft,
    *,
    count: int | None = None,
    kind: str | None = None,
    diameter: float = 1.25,
    length: float | None = None,
) -> Craft:
    """Swap FL-T100 ↔ proc and/or change stack count. Retarget link/attN.

    ``kind=proc`` writes Default Kero/LOx (T-418), not SolidFuel pad_pbc.
    """
    tanks = axial_tanks(craft)
    if not tanks:
        raise CraftError("no axial FL-T100 / proceduralTankRealFuels stack")
    current_kind = "proc" if tanks[0].name == "proceduralTankRealFuels" else "t100"
    kind_n = kind or current_kind
    if kind_n not in {"t100", "proc"}:
        raise CraftError("kind must be t100 or proc")
    n = int(count) if count is not None else len(tanks)
    if n < 1:
        raise CraftError("count must be >= 1")
    length_n = T100_HEIGHT if kind_n == "t100" else (length if length is not None else T100_HEIGHT)
    old_h = tank_height(tanks[0])
    old_half = old_h * 0.5
    new_h = length_n
    new_half = new_h * 0.5
    old_first = tanks[0]
    old_last = tanks[-1]
    above = old_first.att_n.get("top") or ""
    below = old_last.att_n.get("bottom") or ""
    old_tokens = [t.token for t in tanks]
    old_top_y = old_first.pos[1] + old_half
    new_y0 = old_top_y - new_half
    old_last_bottom = old_last.pos[1] - old_half

    radials_by_tank: dict[str, list[CraftPart]] = {t.token: [] for t in tanks}
    for p in craft.parts:
        if p.attm != 1 or not p.srf_n:
            continue
        _, _, rest = p.srf_n.partition(",")
        if rest in radials_by_tank:
            radials_by_tank[rest].append(p)

    keep = min(n, len(tanks))
    new_tanks: list[CraftPart] = []
    for i in range(n):
        if i < keep:
            part = tanks[i]
        else:
            src = tanks[-1]
            part = CraftPart(
                name=src.name,
                pos=src.pos,
                rot=src.rot,
                istg=src.istg,
                dstg=src.dstg,
                autostrut_mode=src.autostrut_mode,
                rigid_attachment=src.rigid_attachment,
            )
            craft.parts.append(part)
        old_token = part.token
        _fill_tank(part, kind=kind_n, diameter=diameter, length=length_n)
        part.pos = (old_first.pos[0], new_y0 - i * new_h, old_first.pos[2])
        part.att_pos0 = part.pos
        part.attm = 0
        if old_token != part.token:
            retarget(craft, old_token, part.token)
        new_tanks.append(part)

    drop = tanks[keep:]
    drop_tokens = {t.token for t in drop}
    for old in drop:
        craft.parts = [p for p in craft.parts if p is not old]

    for i, part in enumerate(new_tanks):
        part.att_n = dict(part.att_n)
        if i == 0:
            if above:
                part.att_n["top"] = above
        else:
            part.att_n["top"] = new_tanks[i - 1].token
        if i == n - 1:
            if below:
                part.att_n["bottom"] = below
            else:
                part.att_n.pop("bottom", None)
        else:
            part.att_n["bottom"] = new_tanks[i + 1].token
        child_tok = new_tanks[i + 1].token if i + 1 < n else below
        kept_links = [
            t
            for t in part.links
            if t not in old_tokens and t not in drop_tokens and t != below
        ]
        part.links = []
        if child_tok:
            part.links.append(child_tok)
        part.links.extend(kept_links)

    if above:
        host = _by_token(craft).get(above)
        if host is not None:
            host.att_n = {
                k: (new_tanks[0].token if v in set(old_tokens) else v)
                for k, v in host.att_n.items()
            }
            host.links = [
                new_tanks[0].token if t in set(old_tokens) else t for t in host.links
            ]
            if new_tanks[0].token not in host.links:
                host.links.append(new_tanks[0].token)
    if below:
        host = _by_token(craft).get(below)
        if host is not None:
            host.att_n = {
                k: (new_tanks[-1].token if v in set(old_tokens) else v)
                for k, v in host.att_n.items()
            }
            host.links = [
                new_tanks[-1].token if t in set(old_tokens) else t for t in host.links
            ]

    for i, old in enumerate(tanks):
        dest_i = i if i < n else n - 1
        dest = new_tanks[dest_i]
        dy = dest.pos[1] - old.pos[1]
        for radial in radials_by_tank.get(old.token, []):
            if dest.token != old.token:
                retarget(craft, old.token, dest.token)
                if dest.token not in dest.links:
                    pass
                if radial.token not in dest.links:
                    dest.links.append(radial.token)
            _shift_part(radial, dy)
            if radial.attm == 1:
                radial.pos = (
                    dest.pos[0] + (radial.att_pos0 or (0.0, 0.0, 0.0))[0],
                    dest.pos[1] + (radial.att_pos0 or (0.0, 0.0, 0.0))[1],
                    dest.pos[2] + (radial.att_pos0 or (0.0, 0.0, 0.0))[2],
                )
                radial.srf_n = f"srfAttach,{dest.token}"

    new_last_bottom = new_tanks[-1].pos[1] - new_half
    dy_below = new_last_bottom - old_last_bottom
    tank_ids = {id(t) for t in new_tanks}
    for p in craft.parts:
        if id(p) in tank_ids:
            continue
        if p.attm == 1:
            _, _, rest = (p.srf_n or "").partition(",")
            if rest in {t.token for t in new_tanks}:
                continue
        if p.pos[1] < old_last.pos[1] - 1e-4:
            _shift_part(p, dy_below)
    alive = {p.token for p in craft.parts}
    for p in craft.parts:
        p.links = [t for t in p.links if t in alive]
    return craft


def stage_engine_first(craft: Craft) -> None:
    """Valiant first activate_next_stage; chute last. Chute istg=0 is not empty."""
    engine = find_engine(craft)
    if engine is not None:
        engine.istg = 0
        engine.sidx = 0
        engine.sqor = 0
    for chute in find_chutes(craft):
        chute.istg = 1 if engine is not None else 0
        chute.sidx = 0
        chute.sqor = 0


def set_nylon_chute(craft: Craft, kind: str = "mk16") -> CraftPart:
    """Write RealChuteModule+ProceduralChute. Not an empty PARACHUTE.

    Engine is first fire (istg=0 sqor=0). Chute is the later queued stage.
    engine.istg=1 with sqor=-1 leaves chute sqor=0 as the only queued stage.
    """
    if kind not in {"mk16", "cone"}:
        raise CraftError("chute kind must be mk16 or cone")
    chutes = find_chutes(craft)
    if not chutes:
        raise CraftError(
            "no chute part; clone a chute hang or copy-chute --from "
            f"{DONOR_MK16 if kind == 'mk16' else DONOR_CONE}"
        )
    chute = chutes[0]
    if kind == "mk16":
        if chute.name != "parachuteSingle":
            old = chute.token
            chute.name = "parachuteSingle"
            retarget(craft, old, chute.token)
        chute.modules = mk16_chute_modules()
    else:
        if chute.name != "RC_cone":
            old = chute.token
            chute.name = "RC_cone"
            retarget(craft, old, chute.token)
        chute.modules = rc_cone_chute_modules()
    stage_engine_first(craft)
    return chute


def copy_chute(craft: Craft, donor: Craft) -> CraftPart:
    """Copy Nylon PARACHUTE+ProceduralChute from a known-good hang (T-419)."""
    srcs = find_chutes(donor)
    if not srcs:
        raise CraftError("donor has no chute part")
    src = srcs[0]
    if not chute_is_nylon_good(src):
        raise CraftError(
            "donor chute is empty or inherited 0.04 atm / 0.8 m; "
            f"use {DONOR_MK16} or {DONOR_CONE}"
        )
    dsts = find_chutes(craft)
    if not dsts:
        raise CraftError("target has no chute part to copy onto")
    dst = dsts[0]
    old = dst.token
    dst.name = src.name
    if old != dst.token:
        retarget(craft, old, dst.token)
    dst.modules = [_copy_node(m) for m in src.modules]
    stage_engine_first(craft)
    if not chute_is_nylon_good(dst):
        raise CraftError("copy produced a bad PARACHUTE")
    return dst


def girder_ring(
    craft: Craft,
    n: int = 3,
    *,
    on: str = "mid",
    radius: float | None = None,
) -> list[CraftPart]:
    """N× trussPiece1x Heaviest/rigid, even azimuth around a tank."""
    if n < 1:
        raise CraftError("girder count must be >= 1")
    tanks = axial_tanks(craft)
    if not tanks:
        raise CraftError("no tank to hang a girder ring on")
    tank = _pick_tank(tanks, on)
    diam = tank_diameter(tank)
    rad = 0.7 * (diam / 1.25) if radius is None else radius
    girders: list[CraftPart] = []
    for i in range(n):
        ang = 2.0 * math.pi * i / n
        offset = (rad * math.cos(ang), 0.0, rad * math.sin(ang))
        g = surface_attach(
            craft,
            tank,
            "trussPiece1x",
            offset,
            autostrut="Heaviest",
            rigid="True",
        )
        girders.append(g)
    return girders


def _pick_tank(tanks: list[CraftPart], on: str) -> CraftPart:
    key = (on or "mid").strip().lower()
    if key in {"first", "top", "0"}:
        return tanks[0]
    if key in {"last", "bottom"}:
        return tanks[-1]
    if key in {"mid", "middle"}:
        return tanks[len(tanks) // 2]
    for t in tanks:
        if t.token == on or t.name == on or str(t.uid) == on:
            return t
    try:
        idx = int(key)
    except ValueError:
        raise CraftError(f"unknown tank {on!r} (first|mid|last|token)") from None
    if idx < 0 or idx >= len(tanks):
        raise CraftError(f"tank index {idx} out of range 0..{len(tanks) - 1}")
    return tanks[idx]


def _resource_names(part: CraftPart) -> list[str]:
    names: list[str] = []
    for res in part.resources:
        n = res.get("name")
        if n and n not in names:
            names.append(n)
    fuel = _mod(part, "ModuleFuelTanks")
    if fuel is not None:
        for tank in fuel.of("TANK"):
            n = tank.get("name")
            if n and n not in names:
                names.append(n)
    return names


def _catalog_for_feed(
    catalog: Catalog | None = None,
    ksp_root: Path | None = None,
) -> Catalog:
    if catalog is not None:
        return catalog
    root = ksp_root
    if root is None:
        from hangar import discover_ksp

        root = discover_ksp()
    if root is not None:
        return load_catalog(root)
    return Catalog.stock()


def part_fuel_cross_feed(part_name: str, catalog: Catalog | None = None) -> bool | None:
    """PART fuelCrossFeed from catalog/cfg. None if the field is absent (KSP default True)."""
    cat = catalog or Catalog.stock()
    part = cat.get(part_name)
    if part is None:
        return None
    return part.fuel_cross_feed


def _cross_feed_label(part_name: str, catalog: Catalog | None) -> str:
    val = part_fuel_cross_feed(part_name, catalog)
    if val is True:
        return "fuelCrossFeed=True"
    if val is False:
        return "fuelCrossFeed=False"
    return "fuelCrossFeed=default"


def dump_attach_fuel(
    craft: Craft,
    *,
    catalog: Catalog | None = None,
    ksp_root: Path | None = None,
) -> str:
    """Attach tree + fuelCrossFeed path tank→engine from .craft+cfg. No Hangar.

    proceduralHeatshield and stock HeatShield* are fuelCrossFeed=False, so an
    inline dish between last tank and engine starves the engine (Ablator only).
    """
    cat = _catalog_for_feed(catalog, ksp_root)
    lines = [f"ship: {craft.name}", f"cfg: {cat.source or 'stock-nodes'}", "attach:"]
    by = _by_token(craft)
    for p in craft.parts:
        att = " ".join(f"{k}={v}" for k, v in p.att_n.items()) or "-"
        res = ",".join(_resource_names(p)) or "-"
        cfg_bit = ""
        part_def = cat.get(p.name)
        if (
            part_fuel_cross_feed(p.name, cat) is False
            and part_def is not None
            and part_def.cfg_path
        ):
            cfg_bit = f"  cfg={part_def.cfg_path}"
        extra = f"  srfN {p.srf_n}" if p.srf_n else ""
        lines.append(
            f"  {p.token}  {_cross_feed_label(p.name, cat)}  res={res}  "
            f"attN {att}{cfg_bit}{extra}"
        )
    tanks = axial_tanks(craft)
    engine = find_engine(craft)
    lines.append("fuel:")
    if not tanks or engine is None:
        lines.append("  (no tank/engine)")
        return "\n".join(lines) + "\n"
    last = tanks[-1]
    path: list[CraftPart] = []
    seen: set[str] = set()
    cur: CraftPart | None = last
    while cur is not None and cur.token not in seen:
        seen.add(cur.token)
        path.append(cur)
        if cur.token == engine.token:
            break
        nxt = cur.att_n.get("bottom") or ""
        cur = by.get(nxt)
    lines.append("  " + " -> ".join(p.token for p in path))
    for p in path:
        res = ",".join(_resource_names(p)) or "-"
        lines.append(f"  {p.token}  {_cross_feed_label(p.name, cat)}  res={res}")
    blocked = [p for p in path if part_fuel_cross_feed(p.name, cat) is False]
    if engine.token not in {p.token for p in path}:
        lines.append("  (engine not on attN bottom chain from last tank)")
    if blocked:
        names = " ".join(p.name for p in blocked)
        lines.append(
            f"BLOCKED  {names} fuelCrossFeed=False  Ablator only; engine starved"
        )
    else:
        lines.append("FED  last tank reaches engine")
    return "\n".join(lines) + "\n"


def insert_wheel(craft: Craft, *, catalog: Catalog | None = None) -> Craft:
    """sasModule between core and first tank; PresMat radial on the core."""
    cat = catalog or Catalog.stock()
    core = find_core(craft)
    if core is None:
        raise CraftError("no probe core to splice a wheel under")
    tanks = axial_tanks(craft)
    if not tanks:
        raise CraftError("no tank under the core")
    first = tanks[0]
    if not _find_named(craft, "sasModule"):
        wheel = CraftPart(name="sasModule", istg=core.istg, dstg=core.dstg)
        insert_inline(craft, core, first, wheel, catalog=cat)
    if not _find_named(craft, "sensorBarometer"):
        surface_attach(craft, core, "sensorBarometer", PRESMAT_OFFSET)
    return craft


def insert_heatshield(
    craft: Craft,
    *,
    kind: str = "disc",
    top: float | None = None,
    bottom: float = 1.25,
    length: float = 0.2,
    ablator: int = 80,
    catalog: Catalog | None = None,
) -> CraftPart:
    """Splice proceduralHeatshield between last tank and engine. No silk.

    Disc is a VAB dish (bottomDiameter=0), not a 1.25 puck. Engine child
    uses catalog top (Valiant 0.45), not tank half 0.3125.

    Refuse fuelCrossFeed=False (PP HS / stock HeatShield*). An inline
    dish starves the engine (Ablator only; pad Δv 0/0). Tank stays on
    the engine. Do not write GameData to flip the part.
    """
    if kind not in {"disc", "adapter"}:
        raise CraftError("heatshield kind must be disc or adapter")
    tanks = axial_tanks(craft)
    engine = find_engine(craft)
    if not tanks or engine is None:
        raise CraftError("need last tank and engine to insert a heatshield")
    last = tanks[-1]
    cat = catalog or _catalog_for_feed(None)
    if part_fuel_cross_feed("proceduralHeatshield", cat) is not True:
        raise CraftError(
            "refusing fuelCrossFeed=False splice: proceduralHeatshield "
            "would starve the engine (Ablator only). Tank stays on engine. "
            "Do not write GameData."
        )
    if last.att_n.get("bottom") != engine.token and engine.att_n.get("top") != last.token:
        if any(p.name == "proceduralHeatshield" for p in craft.parts):
            raise CraftError("heatshield already between tank and engine")
    top_d = 1.25 if kind == "disc" else 1.427
    if top is not None:
        top_d = top
    if kind == "disc":
        bottom = 0.0
    mods, res = heatshield_modules(
        top=top_d, bottom=bottom, length=length, ablator=ablator
    )
    hs = CraftPart(name="proceduralHeatshield", istg=-1, dstg=0)
    hs.modules = mods
    hs.resources = res
    insert_inline(
        craft,
        last,
        engine,
        hs,
        catalog=cat,
        new_half=length * 0.5,
    )
    stage_engine_first(craft)
    return hs


def _write(craft: Craft, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    craft.save(path)
    return path


def _load_named(src: str) -> tuple[Craft, Path]:
    path = resolve_craft_path(src)
    return Craft.load(path), path


def cmd_craft(argv: list[str] | None = None) -> int:
    """Gus CLI: clone / tanks / chute / girders / wheel / heatshield / fuel. No Hangar."""
    p = argparse.ArgumentParser(
        prog="craft",
        description="VAB helpers on crafts/*.craft. kRPC cannot place parts.",
    )
    sub = p.add_subparsers(dest="act", required=True)
    cl = sub.add_parser("clone", help="Copy a signed hang under a new ship=")
    cl.add_argument("src")
    cl.add_argument("--name", required=True)
    cl.add_argument("--out", default="")
    tk = sub.add_parser("tanks", help="Swap FL-T100↔proc and/or change count")
    tk.add_argument("src")
    tk.add_argument("--count", type=int, default=None)
    tk.add_argument("--kind", choices=("t100", "proc"), default=None)
    tk.add_argument("--diameter", type=float, default=1.25)
    tk.add_argument("--length", type=float, default=None)
    tk.add_argument("--out", default="")
    liq = sub.add_parser(
        "liquid",
        help="Replace tank stack with proc Default Kero/LOx (not SolidFuel)",
    )
    liq.add_argument("src")
    liq.add_argument("--count", type=int, default=None)
    liq.add_argument("--diameter", type=float, default=1.25)
    liq.add_argument("--length", type=float, default=0.625)
    liq.add_argument("--out", default="")
    ch = sub.add_parser("chute", help="Write Nylon Mk16 5/35 or RC_cone 50m MODULE")
    ch.add_argument("src")
    ch.add_argument("--kind", choices=("mk16", "cone"), default="mk16")
    ch.add_argument("--out", default="")
    cc = sub.add_parser("copy-chute", help="Copy Nylon PARACHUTE from a known-good hang")
    cc.add_argument("src")
    cc.add_argument("--from", dest="donor", default="")
    cc.add_argument("--out", default="")
    gd = sub.add_parser("girders", help="N× trussPiece1x Heaviest/rigid around a tank")
    gd.add_argument("src")
    gd.add_argument("-n", "--n", type=int, default=3)
    gd.add_argument("--on", default="mid")
    gd.add_argument("--radius", type=float, default=None)
    gd.add_argument("--out", default="")
    wh = sub.add_parser("wheel", help="Insert sasModule inline + PresMat on the core")
    wh.add_argument("src")
    wh.add_argument("--out", default="")
    hs = sub.add_parser(
        "heatshield",
        help="Insert proc HS disc or 1.427-to-1.25 adapter above the engine",
    )
    hs.add_argument("src")
    hs.add_argument("--kind", choices=("disc", "adapter"), default="disc")
    hs.add_argument("--top", type=float, default=None)
    hs.add_argument("--bottom", type=float, default=1.25)
    hs.add_argument("--length", type=float, default=0.2)
    hs.add_argument("--ablator", type=int, default=80)
    hs.add_argument("--out", default="")
    fu = sub.add_parser(
        "fuel",
        help="Dump attach tree + fuelCrossFeed path through an inline HS (disk)",
    )
    fu.add_argument("src")
    args = p.parse_args(argv)
    try:
        if args.act == "clone":
            out = clone_craft(args.src, args.name, args.out or None)
            craft = Craft.load(out)
            print(f"wrote {out}  {craft.summary()}")
            return 0
        craft, src_path = _load_named(args.src)
        if args.act == "fuel":
            text = dump_attach_fuel(craft)
            print(text, end="")
            return 2 if "BLOCKED" in text else 0
        out = Path(args.out) if args.out else src_path
        if args.act == "tanks":
            replace_tanks(
                craft,
                count=args.count,
                kind=args.kind,
                diameter=args.diameter,
                length=args.length,
            )
        elif args.act == "liquid":
            replace_tanks(
                craft,
                count=args.count,
                kind="proc",
                diameter=args.diameter,
                length=args.length,
            )
        elif args.act == "chute":
            set_nylon_chute(craft, args.kind)
        elif args.act == "copy-chute":
            donor_name = args.donor or (
                DONOR_CONE
                if find_chutes(craft) and find_chutes(craft)[0].name == "RC_cone"
                else DONOR_MK16
            )
            donor, _ = _load_named(donor_name)
            copy_chute(craft, donor)
        elif args.act == "girders":
            girder_ring(craft, args.n, on=args.on, radius=args.radius)
        elif args.act == "wheel":
            insert_wheel(craft)
        elif args.act == "heatshield":
            insert_heatshield(
                craft,
                kind=args.kind,
                top=args.top,
                bottom=args.bottom,
                length=args.length,
                ablator=args.ablator,
            )
        _write(craft, out)
        print(f"wrote {out}  {craft.summary()}")
        return 0
    except CraftError as exc:
        print(str(exc), flush=True)
        return 2
