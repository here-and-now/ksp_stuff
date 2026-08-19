"""Career / RP-1 facing snapshot.

There is no kRPC RP-1 service. Funds, science, reputation, and contracts
still come through SpaceCenter. Avionics, KCT, and program points are
listed as future hooks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from session import Session


@dataclass(slots=True)
class ContractSnapshot:
    title: str
    state: str
    active: bool
    failed: bool
    seen: bool
    read: bool


@dataclass(slots=True)
class CareerSnapshot:
    game_mode: str
    funds: float | None
    science: float | None
    reputation: float | None
    contracts: list[ContractSnapshot]
    notes: tuple[str, ...]


RP1_NOTES = (
    "RP-1 has no dedicated kRPC API. This tab only sees stock career fields.",
    "Comms in RP-1 are RealAntennas on CommNet, not RemoteTech.",
    "kRPC has no RA service: we read ModuleRealAntenna fields and vessel.comms.",
    "Dish pointing is in-game only (Antenna Targeting). Omnis need none.",
    "Avionics (control range, EC, unlocked tech) are not exposed — fly that in-game.",
    "KCT build times, unlock points, and program slots are future work.",
    "RO engines may need ullage (see parts.ullage) before ignition.",
)


def _enum_name(value: Any) -> str:
    return getattr(value, "name", str(value))


def snapshot_career(session: Session) -> CareerSnapshot:
    session.require_connected()
    sc = session.space_center
    mode = "?"
    funds = science = reputation = None
    try:
        mode = _enum_name(sc.game_mode)
    except Exception:
        pass
    try:
        funds = float(sc.funds)
    except Exception:
        pass
    try:
        science = float(sc.science)
    except Exception:
        pass
    try:
        reputation = float(sc.reputation)
    except Exception:
        pass

    contracts: list[ContractSnapshot] = []
    try:
        manager = sc.contract_manager
        pool = []
        for attr in ("active_contracts", "all_contracts"):
            try:
                pool = list(getattr(manager, attr))
                if pool:
                    break
            except Exception:
                continue
        for contract in pool:
            try:
                contracts.append(
                    ContractSnapshot(
                        title=str(contract.title),
                        state=_enum_name(getattr(contract, "state", "")),
                        active=bool(getattr(contract, "active", False)),
                        failed=bool(getattr(contract, "failed", False)),
                        seen=bool(getattr(contract, "seen", False)),
                        read=bool(getattr(contract, "read", False)),
                    )
                )
            except Exception:
                continue
    except Exception:
        pass

    return CareerSnapshot(
        game_mode=mode,
        funds=funds,
        science=science,
        reputation=reputation,
        contracts=contracts,
        notes=RP1_NOTES,
    )
