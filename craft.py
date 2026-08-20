"""``.craft`` ships: parse, write, stack along part nodes.

kRPC cannot place parts in the VAB. A craft file in
``saves/<save>/Ships/VAB/`` *can* be launched. This module is that file.

Part tokens in the file use dots for underscores: ``mk1pod_v2`` →
``mk1pod.v2_<uid>``. Procedural/RO modules belong in ``modules`` later;
stock reconstructs MODULE blocks from ``part.cfg`` on load.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from pathlib import Path

from catalog import Catalog
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
    persistent_id: int = field(default_factory=_uid)
    modules: list[CfgNode] = field(default_factory=list)
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
        n.add("autostrutMode", "Off")
        n.add("rigidAttachment", "False")
        n.add("istg", str(self.istg))
        n.add("resPri", "0")
        n.add("dstg", str(self.dstg))
        n.add("sidx", str(self.sidx))
        n.add("sqor", "-1")
        n.add("sepI", "-1")
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
            persistent_id=int(node.get("persistentId") or _uid()),
            modules=[c for c in node.children if c.name == "MODULE"],
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
    persistent_id: int = field(default_factory=_uid)

    def to_node(self) -> CfgNode:
        n = CfgNode(name="")
        n.add("ship", self.name)
        n.add("version", self.version)
        n.add("description", self.description)
        n.add("type", self.kind)
        n.add("size", "2,12,2")
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


def simple_orbiter(name: str = "kspstuff-simple-orbiter") -> Craft:
    """Mk1 pod + chute + FL-T400 + Swivel. Stock-only, one liquid stage."""
    b = StackBuilder(name, Catalog.stock())
    b.craft.description = "Generated by kspstuff. Stock Mk1 + T400 + Swivel."
    pod = b.root("mk1pod_v2")
    b.attach(pod, "top", "parachuteSingle", "bottom", istg=0, dstg=0, sidx=0)
    tank = b.stack("fuelTank", istg=-1, dstg=0)
    b.attach(tank, "bottom", "liquidEngine2_v2", "top", istg=1, dstg=0, sidx=0)
    return b.craft


def hop_flea(name: str = "kspstuff-hop-flea") -> Craft:
    """Mk1 + Mk16 + 2×Goo + Flea. Start-only pad hop."""
    b = StackBuilder(name, Catalog.stock())
    b.craft.description = (
        "Generated by kspstuff. Start hop: Mk1 + chute + Goo + Flea."
    )
    pod = b.root("mk1pod_v2")
    b.attach(pod, "top", "parachuteSingle", "bottom", istg=0, dstg=0, sidx=0)
    b.attach(pod, "bottom", "solidBooster_sm_v2", "top", istg=1, dstg=0, sidx=0)
    # Surface poses from stock Jumping Flea (pod at 0,15,0).
    b.srf_attach(
        pod,
        "GooExperiment",
        (-0.313173443, 0.314465523, 0.0),
        rot=(0.0988500565, 0.700163364, -0.098850064, 0.700163305),
    )
    b.srf_attach(
        pod,
        "GooExperiment",
        (0.313173443, 0.314465523, 0.0),
        rot=(-0.0988500714, 0.700163245, -0.0988500491, -0.700163424),
    )
    return b.craft


def hecs_sounding(name: str = "kspstuff-hecs-sounding") -> Craft:
    """HECS probe + T100 + Terrier. Tiny stock probe for pad tests."""
    b = StackBuilder(name, Catalog.stock())
    b.craft.description = "Generated by kspstuff. HECS + T100 + Terrier."
    b.root("probeCoreHex_v2")
    tank = b.stack("fuelTankSmallFlat", istg=-1, dstg=0)
    b.attach(tank, "bottom", "liquidEngine3_v2", "top", istg=1, dstg=0, sidx=0)
    return b.craft


def two_stage_orbiter(name: str = "kspstuff-twostage") -> Craft:
    """Mk1 + T400/Terrier upper, two T800s + Swivel first stage.

    Enough vacuum Δv for a stock Kerbin parking orbit; the one-tank
    ``simple_orbiter`` is not.
    """
    b = StackBuilder(name, Catalog.stock())
    b.craft.description = "Generated by kspstuff. Swivel + 2×T800, Terrier upper."
    pod = b.root("mk1pod_v2")
    b.attach(pod, "top", "parachuteSingle", "bottom", istg=0, dstg=0, sidx=0)
    upper = b.stack("fuelTank", istg=-1, dstg=0)
    terrier = b.attach(upper, "bottom", "liquidEngine3_v2", "top", istg=1, dstg=0, sidx=0)
    b.attach(terrier, "bottom", "Decoupler_1", "top", istg=1, dstg=1, sidx=0)
    b.stack("fuelTank_long", istg=-1, dstg=1)
    lower = b.stack("fuelTank_long", istg=-1, dstg=1)
    b.attach(lower, "bottom", "liquidEngine2_v2", "top", istg=2, dstg=1, sidx=0)
    return b.craft


def mun_lander(name: str = "kspstuff-mun-lander") -> Craft:
    """One-way Mun stack: Skipper + X200-32, Terrier transfer, Terrier lander.

    Inline 1.25 m upper on a 2.5 m booster via ``adapterSize2-Size1``.
    Ascent should use ``end_stage=1`` so the transfer stage is not dumped
    in Kerbin orbit. Stage 0 (lander) is fired manually before the
    suicide burn.
    """
    b = StackBuilder(name, Catalog.stock())
    b.craft.description = (
        "Generated by kspstuff. Skipper booster, Terrier transfer, Terrier lander."
    )
    pod = b.root("mk1pod_v2")
    pod.dstg = -1
    lander_tank = b.stack("fuelTank_long", istg=-1, dstg=-1)
    b.attach(
        lander_tank, "bottom", "liquidEngine3_v2", "top", istg=0, dstg=-1, sidx=0
    )
    b.stack("Decoupler_1", istg=0, dstg=0, sidx=0)
    b.stack("fuelTank_long", istg=-1, dstg=0)
    xfer_tank = b.stack("fuelTank_long", istg=-1, dstg=0)
    b.attach(
        xfer_tank, "bottom", "liquidEngine3_v2", "top", istg=1, dstg=0, sidx=0
    )
    b.stack("Decoupler_1", istg=1, dstg=1, sidx=0)
    b.stack("adapterSize2-Size1", istg=-1, dstg=1)
    b.stack("Rockomax16_BW", istg=-1, dstg=1)
    rocko = b.stack("Rockomax32_BW", istg=-1, dstg=1)
    b.attach(
        rocko, "bottom", "engineLargeSkipper_v2", "top", istg=2, dstg=1, sidx=0
    )
    return b.craft


def procedural_cylinder(diameter: float, length: float) -> list[CfgNode]:
    """MODULE blocks for a ProceduralParts cylinder (meters)."""
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
    tanks.add("type", "SolidFuel")
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
        istg=1,
        dstg=0,
        sidx=0,
    )
    set_cylinder(srb, diameter=diameter, length=length)
    return b.craft


TEMPLATES = {
    "simple-orbiter": simple_orbiter,
    "hop-flea": hop_flea,
    "hecs-sounding": hecs_sounding,
    "twostage": two_stage_orbiter,
    "mun-lander": mun_lander,
    "pad-pbc": pad_pbc,
}
