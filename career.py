"""Career snapshot (kRPC stock fields).

Science sandbox has science, not funds/contracts. Tree unlocks are disk
(`world.py`), not this module. No RP-1 / KCT service.
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
    "kRPC sees stock career fields only. Tree/parts: python main.py world.",
    "Science sandbox: funds/contracts are none. Unlocks are on disk R&D.",
    "Comms are RealAntennas on CommNet, not RemoteTech. No RA kRPC service.",
    "Kerbalism science/LS/reliability are part.modules, not this snapshot.",
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
