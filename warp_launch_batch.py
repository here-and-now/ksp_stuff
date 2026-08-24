"""Warp × launch batch. Os 2026-08-23: revert_to_launch is allowed here only.

Hangar once, then short burns. Revert to that launch between cases.
Never WarpTo. Rails stay 0. Full factory hop is not this file.
"""

from __future__ import annotations

import time
from typing import Any, Callable

from hangar import run_physics, wait_vessel_ready
from hop import install_and_launch
from pad import arm_chutes, deploy_chutes
from physics_warp import set_factor, set_rate
from session import SessionError
from telem import chute_state

_CHUTE_OPEN = frozenset({"deployed", "semi_deployed", "semideployed"})

_AIRBORNE_M = 250.0


def _log(msg: str) -> None:
    print(msg, flush=True)


def _sit(vessel: object) -> str:
    raw = getattr(vessel, "situation", None)
    name = getattr(raw, "name", None)
    if isinstance(name, str):
        return name.lower()
    return str(raw or "?").lower()


def _factors(sc: object) -> tuple[int, int]:
    try:
        phys = int(getattr(sc, "physics_warp_factor", 0) or 0)
    except Exception:
        phys = -1
    try:
        rails = int(getattr(sc, "rails_warp_factor", 0) or 0)
    except Exception:
        rails = -1
    return phys, rails


def _paused(session: object) -> bool:
    for obj in (
        getattr(getattr(session, "conn", None), "krpc", None),
        getattr(session, "space_center", None),
    ):
        if obj is None:
            continue
        try:
            return bool(getattr(obj, "paused", False))
        except Exception:
            continue
    return False


def _stage(vessel: object) -> int:
    try:
        return int(getattr(vessel.control, "current_stage", -1))
    except Exception:
        return -1


def _engines(vessel: object) -> tuple[int, int]:
    try:
        eng = list(getattr(getattr(vessel, "parts", None), "engines", ()) or ())
    except Exception:
        return 0, 0
    on = 0
    for e in eng:
        try:
            if bool(getattr(e, "active", False)):
                on += 1
        except Exception:
            continue
    return len(eng), on


def _parts_n(vessel: object) -> int:
    try:
        return len(list(getattr(getattr(vessel, "parts", None), "all", ()) or ()))
    except Exception:
        return 0


def _read(session: object, vessel: object) -> dict[str, Any]:
    sc = session.space_center
    phys, rails = _factors(sc)
    alt = float("nan")
    apo = float("nan")
    try:
        body = vessel.orbit.body
        fl = vessel.flight(body.reference_frame)
        alt = float(fl.mean_altitude)
        apo = float(vessel.orbit.apoapsis_altitude)
    except Exception:
        pass
    try:
        throttle = float(vessel.control.throttle)
    except Exception:
        throttle = float("nan")
    try:
        met = float(vessel.met)
    except Exception:
        met = float("nan")
    try:
        mass = float(vessel.mass)
    except Exception:
        mass = float("nan")
    n_eng, n_on = _engines(vessel)
    try:
        chute = str(chute_state(vessel) or "none")
    except Exception:
        chute = "?"
    return {
        "sit": _sit(vessel),
        "met": met,
        "alt": alt,
        "apo": apo,
        "throttle": throttle,
        "mass": mass,
        "phys": phys,
        "rails": rails,
        "paused": _paused(session),
        "stage": _stage(vessel),
        "parts": _parts_n(vessel),
        "engines": n_eng,
        "eng_on": n_on,
        "chute": chute,
    }


def _fmt(row: dict[str, Any]) -> str:
    return (
        f"sit={row['sit']} met={row['met']:.2f} alt={row['alt']:.0f} "
        f"apo={row['apo']:.0f} thr={row['throttle']:.2f} mass={row['mass']:.0f} "
        f"stage={row['stage']} chute={row.get('chute', '?')} "
        f"parts={row['parts']} eng={row['eng_on']}/{row['engines']} "
        f"phys={row['phys']} rails={row['rails']} paused={int(row['paused'])}"
    )


def _active(session: object) -> object:
    v = session.space_center.active_vessel
    if v is None:
        raise SessionError("no active vessel")
    return v


def _pad_matches(row: dict[str, Any], snap: dict[str, Any]) -> bool:
    if row["sit"] not in {"pre_launch", "prelaunch"}:
        return False
    if int(row["parts"] or 0) < 20:
        return False
    want = float(snap.get("mass") or 0.0)
    got = float(row.get("mass") or 0.0)
    if want > 0 and not (0.7 * want <= got <= 1.3 * want):
        return False
    return True


def _wait_pad(session: object, snap: dict[str, Any], *, timeout: float = 20.0) -> object:
    """Revert/Hangar often returns a ghost (mass 13 t, stage wrong). Wait for the hop."""
    deadline = time.monotonic() + timeout
    last = ""
    while time.monotonic() < deadline:
        run_physics(session)
        vessel = _active(session)
        row = _read(session, vessel)
        last = _fmt(row)
        if _pad_matches(row, snap) and int(row["stage"]) == int(snap["stage"]):
            _log("pad ready " + last)
            return vessel
        time.sleep(0.2)
    raise SessionError(f"pad snapshot not restored ({last})")


def _revert(session: object, snap: dict[str, Any]) -> object:
    sc = session.space_center
    can = getattr(sc, "can_revert_to_launch", None)
    ok = False
    try:
        ok = bool(can() if callable(can) else can)
    except Exception as exc:
        raise SessionError(f"can_revert_to_launch: {exc}") from exc
    if not ok:
        raise SessionError("can_revert_to_launch is false — enable reverting flights")
    _log("revert_to_launch")
    try:
        sc.revert_to_launch()
    except Exception as exc:
        raise SessionError(f"revert_to_launch: {exc}") from exc
    time.sleep(0.6)
    wait_vessel_ready(session, timeout=45.0)
    try:
        return _wait_pad(session, snap)
    except SessionError as exc:
        _log(f"revert dirty ({exc}) — Hangar fresh (whoosh ate a stage)")
        install_and_launch(session, recover=True)
        wait_vessel_ready(session, timeout=45.0)
        run_physics(session)
        return _wait_pad(session, snap)


def _ignite(session: object, vessel: object, snap: dict[str, Any]) -> object:
    """Stage only if revert restored Hangar's stage. Else the whoosh already fired it."""
    row = _read(session, vessel)
    hangar_stage = int(snap["stage"])
    now_stage = int(row["stage"])
    _log("ignite " + _fmt(row))
    try:
        control = vessel.control
        control.sas = True
        control.throttle = 1.0
    except Exception as exc:
        raise SessionError(f"ignite throttle: {exc}") from exc
    if row["sit"] not in {"pre_launch", "prelaunch"}:
        _log("ignite already flying — no stage")
        run_physics(session)
        return vessel
    if now_stage != hangar_stage:
        _log(
            f"ignite skip stage (hangar stage={hangar_stage} now={now_stage}) "
            "— whoosh would be chute"
        )
        run_physics(session)
        return vessel
    try:
        control.activate_next_stage()
    except Exception as exc:
        raise SessionError(f"ignite stage: {exc}") from exc
    _log("hop light")
    run_physics(session)
    return _active(session)


def _hold_boost(vessel: object, seconds: float) -> None:
    t0 = time.monotonic()
    while time.monotonic() - t0 < seconds:
        try:
            vessel.control.throttle = 1.0
        except Exception:
            pass
        time.sleep(0.05)


def _case(name: str, ok: bool, detail: str, rows: list[str]) -> None:
    mark = "PASS" if ok else "FAIL"
    line = f"{mark} {name} — {detail}"
    _log(line)
    rows.append(line)


def _boost_flying(session: object, snap: dict[str, Any], *, seconds: float = 5.0) -> object:
    vessel = _active(session)
    set_factor(session, 0)
    run_physics(session)
    vessel = _ignite(session, vessel, snap)
    _hold_boost(vessel, seconds)
    return _active(session)


def _extra_stage(vessel: object) -> None:
    try:
        vessel.control.activate_next_stage()
    except Exception as exc:
        raise SessionError(f"extra stage: {exc}") from exc
    _log("extra stage (chute)")


def run_chute_batch(session: object, *, on_log: Callable[[str], None] | None = None) -> int:
    """Chute arm/deploy vs extra-stage, at 1× and 3×. Revert between."""
    del on_log
    rows: list[str] = []
    failed = 0
    _log("warp-batch chute: Os revert-ok. Extra stage is silk; Arm/Deploy are events.")
    install_and_launch(session, recover=True)
    wait_vessel_ready(session, timeout=45.0)
    run_physics(session)
    vessel = _active(session)
    snap = _read(session, vessel)
    _log("hangar " + _fmt(snap))

    row = _read(session, vessel)
    ok = (
        int(row["stage"]) == 2
        and row["chute"] in {"stowed", "none", "packed"}
        and row["phys"] == 0
    )
    _case("hangar_chute_stowed", ok, _fmt(row), rows)
    failed += int(not ok)

    vessel = _boost_flying(session, snap, seconds=5.0)
    row = _read(session, vessel)
    ok = (
        row["sit"] == "flying"
        and int(row["stage"]) == 1
        and row["chute"] not in _CHUTE_OPEN
        and int(row["eng_on"]) >= 1
    )
    _case("light_leaves_chute_packed", ok, _fmt(row), rows)
    failed += int(not ok)

    set_factor(session, 0)
    _extra_stage(vessel)
    time.sleep(0.8)
    run_physics(session)
    vessel = _active(session)
    row = _read(session, vessel)
    opened = row["chute"] in _CHUTE_OPEN or row["chute"] in {"armed", "deployed"}
    ok = opened and int(row["stage"]) <= 1
    _case("extra_stage_1x_is_chute", ok, _fmt(row), rows)
    failed += int(not ok)

    vessel = _revert(session, snap)
    row = _read(session, vessel)
    ok = (
        int(row["stage"]) == int(snap["stage"])
        and row["chute"] not in _CHUTE_OPEN
        and int(row["eng_on"]) == 0
    )
    _case("revert_repacks_chute", ok, _fmt(row), rows)
    failed += int(not ok)

    vessel = _boost_flying(session, snap, seconds=5.0)
    set_factor(session, 0)
    st = arm_chutes(vessel, on_log=_log)
    time.sleep(0.4)
    vessel = _active(session)
    row = _read(session, vessel)
    ok = int(row["stage"]) == 1 and row["chute"] not in _CHUTE_OPEN and st not in {""}
    _case("arm_event_1x_not_stage", ok, f"arm={st} " + _fmt(row), rows)
    failed += int(not ok)

    vessel = _revert(session, snap)
    vessel = _boost_flying(session, snap, seconds=5.0)
    set_rate(session, 3)
    st = arm_chutes(vessel, on_log=_log)
    time.sleep(0.4)
    vessel = _active(session)
    row = _read(session, vessel)
    ok = (
        int(row["stage"]) == 1
        and row["phys"] == 2
        and row["rails"] == 0
        and row["chute"] not in _CHUTE_OPEN
    )
    _case("arm_event_3x_not_stage", ok, f"arm={st} " + _fmt(row), rows)
    failed += int(not ok)

    vessel = _revert(session, snap)
    vessel = _boost_flying(session, snap, seconds=5.0)
    try:
        vessel.control.throttle = 0.0
    except Exception:
        pass
    set_factor(session, 0)
    st = deploy_chutes(vessel, on_log=_log)
    time.sleep(1.0)
    run_physics(session)
    vessel = _active(session)
    row = _read(session, vessel)
    ok = row["chute"] in _CHUTE_OPEN or st in _CHUTE_OPEN
    _case("deploy_event_1x", ok, f"deploy={st} " + _fmt(row), rows)
    failed += int(not ok)

    vessel = _revert(session, snap)
    vessel = _boost_flying(session, snap, seconds=5.0)
    try:
        vessel.control.throttle = 0.0
    except Exception:
        pass
    set_rate(session, 3)
    _extra_stage(vessel)
    time.sleep(0.8)
    vessel = _active(session)
    row = _read(session, vessel)
    ok = row["phys"] == 2 and (
        row["chute"] in _CHUTE_OPEN or row["chute"] in {"armed", "deployed"}
    )
    _case("extra_stage_3x_is_chute", ok, _fmt(row), rows)
    failed += int(not ok)

    vessel = _revert(session, snap)
    row = _read(session, vessel)
    ok = int(row["stage"]) == 2 and row["phys"] == 0 and row["chute"] not in _CHUTE_OPEN
    _case("revert_after_3x_chute", ok, _fmt(row), rows)
    failed += int(not ok)

    _log("---")
    for line in rows:
        _log(line)
    _log(f"warp-batch chute {len(rows) - failed}/{len(rows)} passed")
    return 0 if failed == 0 else 2


def run_batch(session: object, *, on_log: Callable[[str], None] | None = None) -> int:
    """Hangar, then revert-between cases. Returns 0 if every case passed."""
    del on_log
    rows: list[str] = []
    failed = 0

    _log("warp-batch: Os revert-ok 2026-08-23. Hangar once, revert between.")
    install_and_launch(session, recover=True)
    wait_vessel_ready(session, timeout=45.0)
    run_physics(session)
    vessel = _active(session)
    snap = _read(session, vessel)
    _log("hangar " + _fmt(snap))

    row = _read(session, vessel)
    ok = row["phys"] == 0 and row["rails"] == 0 and not row["paused"]
    _case("hangar_1x", ok, _fmt(row), rows)
    failed += int(not ok)

    set_rate(session, 3)
    run_physics(session)
    vessel = _active(session)
    row = _read(session, vessel)
    ok = row["phys"] == 0 and row["rails"] == 0
    _case("run_physics_clears_3x", ok, _fmt(row), rows)
    failed += int(not ok)

    vessel = _active(session)
    set_factor(session, 0)
    run_physics(session)
    vessel = _ignite(session, vessel, snap)
    t_wall = time.monotonic()
    _hold_boost(vessel, 8.0)
    wall = time.monotonic() - t_wall
    vessel = _active(session)
    row = _read(session, vessel)
    climbed = row["alt"] > _AIRBORNE_M or row["apo"] > 500.0
    ok = climbed and row["phys"] == 0 and row["rails"] == 0
    _case(
        "light_1x_climbs",
        ok,
        f"wall={wall:.1f}s " + _fmt(row),
        rows,
    )
    failed += int(not ok)

    vessel = _revert(session, snap)
    set_rate(session, 3)
    row = _read(session, vessel)
    left_on = row["phys"]
    vessel = _revert(session, snap)
    row = _read(session, vessel)
    ok = row["phys"] == 0 and row["rails"] == 0
    _case(
        "revert_clears_3x",
        ok,
        f"before_phys={left_on} after " + _fmt(row),
        rows,
    )
    failed += int(not ok)

    vessel = _active(session)
    run_physics(session)
    vessel = _ignite(session, vessel, snap)
    _hold_boost(vessel, 6.0)
    vessel = _active(session)
    set_rate(session, 3)
    row0 = _read(session, vessel)
    t0 = time.monotonic()
    time.sleep(2.0)
    wall = time.monotonic() - t0
    vessel = _active(session)
    row = _read(session, vessel)
    dmet = float(row["met"]) - float(row0["met"])
    flying = row["sit"] not in {"pre_launch", "prelaunch"}
    raced = flying and row["phys"] == 2 and dmet > wall * 1.8
    _case(
        "sleep_at_3x_races_met",
        raced,
        f"dmet={dmet:.2f} wall={wall:.2f} from={row0['sit']} " + _fmt(row),
        rows,
    )
    failed += int(not raced)

    vessel = _revert(session, snap)
    run_physics(session)
    vessel = _ignite(session, vessel, snap)
    _hold_boost(vessel, 6.0)
    vessel = _active(session)
    set_factor(session, 0)
    row0 = _read(session, vessel)
    t0 = time.monotonic()
    time.sleep(2.0)
    wall = time.monotonic() - t0
    vessel = _active(session)
    row = _read(session, vessel)
    dmet = float(row["met"]) - float(row0["met"])
    flying = row["sit"] not in {"pre_launch", "prelaunch"}
    ok = flying and row["phys"] == 0 and 0.5 * wall < dmet < wall * 1.8
    _case(
        "sleep_at_1x_tracks_wall",
        ok,
        f"dmet={dmet:.2f} wall={wall:.2f} " + _fmt(row),
        rows,
    )
    failed += int(not ok)

    vessel = _revert(session, snap)
    run_physics(session)
    vessel = _ignite(session, vessel, snap)
    t0 = time.monotonic()
    lofted = False
    while time.monotonic() - t0 < 20.0:
        _hold_boost(vessel, 0.4)
        vessel = _active(session)
        row = _read(session, vessel)
        if row["alt"] > _AIRBORNE_M:
            lofted = True
            break
    if not lofted:
        _case("coast_3x_after_loft", False, "never lofted " + _fmt(row), rows)
        failed += 1
    else:
        try:
            vessel.control.throttle = 0.0
        except Exception:
            pass
        set_rate(session, 3)
        time.sleep(1.5)
        vessel = _active(session)
        row = _read(session, vessel)
        ok = row["phys"] == 2 and row["rails"] == 0 and row["alt"] > _AIRBORNE_M
        _case("coast_3x_after_loft", ok, _fmt(row), rows)
        failed += int(not ok)

    vessel = _revert(session, snap)
    run_physics(session)
    row = _read(session, vessel)
    ok = row["phys"] == 0 and row["rails"] == 0 and row["sit"] in {
        "pre_launch",
        "prelaunch",
        "landed",
    }
    _case("revert_pad_1x", ok, _fmt(row), rows)
    failed += int(not ok)

    _log("---")
    for line in rows:
        _log(line)
    _log(f"warp-batch {len(rows) - failed}/{len(rows)} passed")
    return 0 if failed == 0 else 2
