"""RealAntennas through stock kRPC — there is no RA service.

CommNet still owns routing. RA adds RF band, gain, transmit power, tech
level, and (for dishes) a pointing target stored as a nested ConfigNode
that kRPC cannot write. We can:

* read every PAW field on ``ModuleRealAntenna``
* deploy stock/RA antennas and refuse to permanently shut them down
* compare dish aim strings against a policy (home body, DSN, peer)

We cannot set dish targets from Python until someone ships a tiny
kRPC.RealAntennas plugin. Dishes default to the home-body centre, which
is the right first-order aim for an Earth GEO relay.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable, Iterable

from parts import deploy_antennas
from session import Session

log = logging.getLogger("kspstuff")

MODULE = "ModuleRealAntenna"

# RSS Deep Space Network. S/X/K only live here; VHF/UHF are everywhere.
DSN = (
    ("Goldstone", 35.4267, -116.8900),
    ("Madrid", 40.4314, -4.2480),
    ("Canberra", -35.4014, 148.9817),
)


def _fields(module: Any) -> dict[str, str]:
    try:
        return {str(k): str(v) for k, v in dict(module.fields).items()}
    except Exception:
        pass
    out: dict[str, str] = {}
    try:
        for field in module.field_list:
            name = getattr(field, "gui_name", None) or getattr(field, "name", "")
            if name:
                out[str(name)] = str(getattr(field, "value", ""))
    except Exception:
        pass
    return out


def _pick(fields: dict[str, str], *names: str) -> str:
    lower = {k.lower(): v for k, v in fields.items()}
    for name in names:
        if name.lower() in lower:
            return lower[name.lower()]
    for key, value in fields.items():
        for name in names:
            if name.lower() in key.lower():
                return value
    return ""


@dataclass(slots=True)
class RealAntenna:
    part_name: str
    title: str
    condition: str
    band: str
    gain_dbi: str
    tx_dbm: str
    tech_level: str
    target: str
    idle_power: str
    active_power: str
    deployable: bool
    deployed: bool
    is_dish: bool

    def as_row(self) -> tuple[str, ...]:
        shape = "dish" if self.is_dish else "omni"
        deployed = "yes" if self.deployed else ("no" if self.deployable else "fixed")
        return (
            self.part_name,
            self.band or "—",
            self.gain_dbi or "—",
            self.tx_dbm or "—",
            self.tech_level or "—",
            shape,
            self.target or "(default / omni)",
            self.condition or "—",
            deployed,
        )


def present(session: Session, vessel: Any | None = None) -> bool:
    """True if this vessel (or the active one) has ModuleRealAntenna."""
    session.require_connected()
    vessel = vessel or session.active_vessel
    try:
        return bool(vessel.parts.with_module(MODULE))
    except Exception:
        return False


def inspect(vessel: Any) -> list[RealAntenna]:
    found: list[RealAntenna] = []
    try:
        parts = list(vessel.parts.with_module(MODULE))
    except Exception:
        parts = []
    for part in parts:
        module = next((m for m in part.modules if m.name == MODULE), None)
        if module is None:
            continue
        fields = _fields(module)
        gain = _pick(fields, "Gain")
        target = _pick(fields, "Antenna Target")
        deployable = False
        deployed = True
        try:
            stock = part.antenna
            if stock is not None:
                deployable = bool(getattr(stock, "deployable", False))
                deployed = bool(getattr(stock, "deployed", True)) or not deployable
        except Exception:
            pass
        is_dish = bool(target) and target.lower() not in ("", "none", "n/a")
        if not is_dish:
            try:
                is_dish = float(gain.split()[0]) > 8.0
            except (TypeError, ValueError, IndexError):
                is_dish = "dish" in part.name.lower() or "dish" in getattr(
                    part, "title", ""
                ).lower()
        found.append(
            RealAntenna(
                part_name=part.name,
                title=getattr(part, "title", part.name),
                condition=_pick(fields, "Condition") or "Enabled",
                band=_pick(fields, "RF Band"),
                gain_dbi=gain,
                tx_dbm=_pick(fields, "Transmit Power (dBm)", "Transmit Power"),
                tech_level=_pick(fields, "Tech Level"),
                target=target,
                idle_power=_pick(fields, "Power (Idle)"),
                active_power=_pick(fields, "Power (Active)"),
                deployable=deployable,
                deployed=deployed,
                is_dish=is_dish,
            )
        )
    return found


def commission(
    session: Session,
    vessels: Iterable[Any],
    *,
    on_log: Callable[[str], None] | None = None,
) -> list[RealAntenna]:
    """Deploy antennas on each vessel and inventory RA modules.

    Does not permanently shut anything down. Dish pointing is not written
    (no kRPC setter); defaults already aim at the home-body centre.
    """
    say = on_log or (lambda msg: log.info(msg))
    inventory: list[RealAntenna] = []
    for vessel in vessels:
        session.switch_to(vessel)
        n = deploy_antennas(vessel)
        say(f"{vessel.name}: deployed {n} antenna action(s)")
        ants = inspect(vessel)
        if not ants:
            say(f"{vessel.name}: no ModuleRealAntenna (stock CommNet only?)")
        for ant in ants:
            if "shutdown" in ant.condition.lower():
                say(f"{vessel.name}: {ant.part_name} is {ant.condition} — skip")
                continue
            if ant.deployable and not ant.deployed:
                say(f"{vessel.name}: {ant.part_name} still stowed")
            inventory.append(ant)
            say(
                f"{vessel.name}: {ant.part_name}  {ant.band or '?'}  "
                f"gain {ant.gain_dbi or '?'}  tx {ant.tx_dbm or '?'}  "
                f"→ {ant.target or 'default/omni'}"
            )
    return inventory


def dish_policy_report(
    antennas: Iterable[RealAntenna],
    *,
    home_body: str = "Earth",
) -> list[str]:
    """What the dishes are doing vs what a GEO relay usually wants."""
    notes: list[str] = []
    dishes = [a for a in antennas if a.is_dish]
    if not dishes:
        notes.append(
            "Omni-only. Fine for early RP-1 VHF/UHF MEO. No pointing to manage."
        )
        return notes
    notes.append(
        "Dish targets are read-only over kRPC (RA stores them as a ConfigNode). "
        "Change them in-game: part menu → Antenna Targeting."
    )
    for ant in dishes:
        target = ant.target.lower()
        if home_body.lower() in target or target in ("", "none"):
            notes.append(
                f"{ant.part_name}: aimed near {home_body} (default centre is OK "
                f"for a GEO-to-DSN hop; Goldstone/Madrid/Canberra is tighter)."
            )
        else:
            notes.append(f"{ant.part_name}: currently → {ant.target}")
    notes.append(
        "Duplicate dishes on the same band do nothing unless they point at "
        "different targets. Extra copies are for extra aims, not extra gain."
    )
    return notes
