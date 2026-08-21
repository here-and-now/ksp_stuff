"""Sounding block.

Hangar the seated / VAB ``.craft`` uncrewed (Hammer sit:
``kspstuff-hop-hammer-pbc``; not pad/geiger). Light, start the
Kerbalism flying card once airborne, dwell through the ballistic,
recover the HD when landed/splashed/wreck-recoverable — or when EC=0
and the HD already has data. Leftover with HardDrive files or no
Experiment modules recovers without a second start — only if this
process did **not** light. A hop this process lit always starts the
flying card (one Toggle per id; thermo on 2HOT, not Stayputnik). Idle
TELEMETRY remaining=0 is not leftover HD. A leftover already in
tracking while the scene is SpaceCenter is switched into Flight — do
not Hangar a second stack. Ballistic peri is negative. No chute.
Splash goo is not a hop start. Do not light a pad geiger.
"""

from __future__ import annotations

import logging
import math
import time
from pathlib import Path
from typing import Callable

from card import NO_BOUND_CARD, card_flying_ids
from emergencies import Ctx, call
from hangar import discover_hangar, game_scene, go_flight, go_space_center, wait_vessel_ready
from pad import recover_or_abort
from science import (
    card_has_data,
    hd_has_data,
    iter_science_modules,
    start_experiments,
)
from screenshot import mission_event
from telem import EventLog, MissionAbort, Telem, gates
from uplink import take

log = logging.getLogger("kspstuff")

CRAFT = "kspstuff-hop-flea-pbc"
PAD_CRAFT = "kspstuff-pad-pbc"
GEIGER_CRAFT = "kspstuff-geiger-pbc"
_NOT_HOP = (PAD_CRAFT, GEIGER_CRAFT, "pad-pbc", "geiger-pbc")
REPO_CRAFTS = Path(__file__).resolve().parent / "crafts"
HOP_APO_DEFAULT = 15_000.0
HOP_APO_CLAMP = (8_000.0, 18_000.0)
# hop_apo is a cut *wish*. Solids cannot hold. OffPlan is FlyingLow, not the clamp.
HOP_APO_MAX = 18_000.0
FLYING_LOW_M = 50_000.0
DEFAULT_HOP_S = 600.0
_AIRBORNE_M = 250.0
_PULSE_S = 1.0
_STILL_N = 5
_STILL_MET = 0.2
_AIR = frozenset({"flying", "sub_orbital", "suborbital", "escaping", "orbiting"})
_PAD_SIT = frozenset({"pre_launch", "prelaunch"})
_LIGHT_SIT = frozenset({"pre_launch", "prelaunch", "landed"})
_ABORT_UPLINK = frozenset({"abort_pad", "abort", "hold", "freeze", "recover"})
_UPLINK_SKIP = frozenset({"science", "stage"})


def _say(msg: str, on_log: Callable[[str], None] | None) -> None:
    log.info(msg)
    if on_log:
        on_log(msg)


def hop_target_apo() -> float:
    """Gene ``hop_apo`` (m). Cut wish. Clamp 8–18 km. OffPlan is FlyingLow."""
    raw = ""
    try:
        from phases import _kv

        raw = _kv().get("hop_apo", "")
    except Exception:
        raw = ""
    try:
        apo = float(raw) if str(raw).strip() else HOP_APO_DEFAULT
    except (TypeError, ValueError):
        apo = HOP_APO_DEFAULT
    if not math.isfinite(apo):
        apo = HOP_APO_DEFAULT
    return min(HOP_APO_CLAMP[1], max(HOP_APO_CLAMP[0], apo))


def hop_match_name() -> str:
    """Leftover match. Unsigned / none is still the Flea name, not Hangar."""
    try:
        from missions import mission_meta, seated_craft_path, vab_kv

        seated = {}
        path = seated_craft_path()
        if path.is_file():
            from missions import _parse_kv

            seated = _parse_kv(path)
        kv = vab_kv()
        name = (
            seated.get("craft") or kv.get("craft") or mission_meta().get("craft") or ""
        ).strip()
        if name and not name.startswith("(") and name.lower() != "none":
            return name
    except Exception:
        pass
    return CRAFT


def hop_craft_name() -> str:
    """Seated / VAB Hangar name. Unsigned VAB is not a Flea sit."""
    from missions import hangar_craft_name

    return hangar_craft_name().strip()


def hop_craft_path(name: str | None = None) -> Path:
    return REPO_CRAFTS / f"{(name or hop_craft_name()).strip()}.craft"


def hop_science_ids() -> tuple[str, ...]:
    """Flying card only. Splash goo is not a hop start. Empty card aborts."""
    from missions import seated_science_path

    path = seated_science_path()
    if not path.is_file():
        raise MissionAbort(NO_BOUND_CARD)
    ids = card_flying_ids(path.read_text(encoding="utf-8"))
    if not ids:
        raise MissionAbort(NO_BOUND_CARD)
    return ids


def _vessel_name(vessel: object) -> str:
    return str(getattr(vessel, "name", "") or "")


def _is_pad_motor(vessel: object) -> bool:
    name = _vessel_name(vessel).lower()
    return any(tag in name for tag in _NOT_HOP)


def _is_hop_craft(vessel: object) -> bool:
    name = _vessel_name(vessel).lower()
    if not name or _is_pad_motor(vessel):
        return False
    wanted = hop_match_name().lower()
    return bool(wanted) and wanted in name


def _active_vessel(session: object) -> object | None:
    try:
        return session.active_vessel  # type: ignore[attr-defined]
    except Exception:
        return None


def _find_hop_vessel(session: object) -> object | None:
    """Active leftover, else tracking pool. Prefer the Flea over debris."""
    active = _active_vessel(session)
    if active is not None and _is_hop_craft(active):
        return active
    craft = None
    debris = None
    for other in _pool(session, active):
        if other is None or not _is_hop_craft(other):
            continue
        if "debris" in _vessel_name(other).lower():
            debris = debris or other
        else:
            craft = other
            break
    return craft or debris


def _ensure_flight(
    session: object,
    vessel: object,
    on_log: Callable[[str], None] | None,
) -> None:
    """SpaceCenter tracking is not Flight. Enter the leftover before Telem."""
    try:
        scene = game_scene(session)  # type: ignore[arg-type]
    except Exception:
        return
    if scene == "flight":
        return
    _say(f"hop enter flight ({scene})", on_log)
    go_flight(session, vessel)  # type: ignore[arg-type]


def install_and_launch(session: object, *, recover: bool = True) -> None:
    """Copy the Gus-signed hop ``.craft`` into VAB and launch uncrewed.

    Byte-copy the repo file — never Hangar pad/geiger. Same pointer as pad.
    """
    from session import SessionError

    try:
        name = hop_craft_name()
    except SessionError as exc:
        raise MissionAbort(str(exc)) from exc
    low = name.lower()
    if any(tag in low for tag in _NOT_HOP):
        raise MissionAbort(
            f"hop Hangar refused {name} — need a hop motor (not pad/geiger)"
        )
    hangar = discover_hangar()
    if hangar is None:
        raise MissionAbort("KSP install not found (KSPSTUFF_KSP or ~/Games/KSP-rss)")
    from hangar import install_signed

    try:
        install_signed(
            session,
            name,
            hangar=hangar,
            recover=recover,
            refuse=_NOT_HOP,
            src=hop_craft_path(name),
        )
    except SessionError as exc:
        raise MissionAbort(str(exc)) from exc


def _airborne(snap: object) -> bool:
    sit = str(getattr(snap, "situation", "") or "")
    if sit in _AIR:
        return True
    if sit in _PAD_SIT or sit in {"landed", "splashed", "wrecked", "wreck"}:
        return False
    alt = getattr(snap, "alt", float("nan"))
    try:
        alt_f = float(alt)
    except (TypeError, ValueError):
        return False
    return math.isfinite(alt_f) and alt_f >= _AIRBORNE_M


def _down(snap: object, *, flown: bool) -> bool:
    """Landed on the pad before ignition is not down. Wreck always is."""
    if bool(getattr(snap, "wreck", False)):
        return True
    sit = str(getattr(snap, "situation", "") or "")
    if sit in {"wrecked", "wreck"}:
        return True
    if sit in {"landed", "splashed"}:
        return flown
    return False


def _recoverable(vessel: object) -> bool:
    try:
        return bool(getattr(vessel, "recoverable", False))
    except Exception:
        return False


def _hd_ready(vessel: object, ids: tuple[str, ...], started: list[str]) -> bool:
    """True if the HD may hold science (drive files, stored slots, or started).

    Idle remaining=0 (TELEMETRY duration) is not leftover data.
    """
    return (
        bool(started)
        or hd_has_data(vessel)
        or card_has_data(vessel, ids, remaining=False)
    )


def _keep_hd(
    vessel: object,
    ids: tuple[str, ...],
    started: list[str],
    *,
    left_pad: bool,
) -> bool:
    """Recover leftover HD: files on the drive, or Experiment modules gone.

    Not for a Flea this process just lit — leftover skip is dead probes.
    """
    if _hd_ready(vessel, ids, started):
        return True
    if left_pad:
        try:
            return not iter_science_modules(vessel)
        except Exception:
            return True
    return False


def _recover_hd(
    vessel: object, on_log: Callable[[str], None] | None
) -> str | None:
    """Recover when KSP will take the vessel. None if not recoverable yet."""
    if not _recoverable(vessel):
        return None
    result = recover_or_abort(vessel)
    _say(result, on_log)
    return result


def _vessel_met(vessel: object | None) -> float | None:
    """MET seconds, NaN if the vessel is dead, None if the stub has no met."""
    if vessel is None:
        return float("nan")
    if not hasattr(vessel, "met"):
        return None
    try:
        val = float(getattr(vessel, "met"))
    except Exception:
        return float("nan")
    return val if math.isfinite(val) else float("nan")


def _ours(vessel: object) -> bool:
    name = _vessel_name(vessel).lower()
    if not name or _is_pad_motor(vessel):
        return False
    wanted = hop_match_name().lower()
    return (wanted and wanted in name) or "debris" in name


def _try_recover(
    vessel: object | None, on_log: Callable[[str], None] | None
) -> str | None:
    if vessel is None or not _recoverable(vessel):
        return None
    try:
        getattr(vessel, "recover")()
    except Exception:
        return None
    _say("recovered", on_log)
    mission_event("recover")
    return "recovered"


def _force_recover(
    vessel: object | None, on_log: Callable[[str], None] | None
) -> str | None:
    if vessel is None:
        return None
    try:
        getattr(vessel, "recover")()
    except Exception:
        return None
    _say("recovered", on_log)
    mission_event("recover")
    return "recovered"


def _pool(session: object, vessel: object | None) -> list[object]:
    out: list[object] = []
    if vessel is not None:
        out.append(vessel)
    try:
        extra = list(getattr(getattr(session, "space_center", None), "vessels", []) or [])
    except Exception:
        extra = []
    for other in extra:
        if other is not None and other not in out:
            out.append(other)
    return out


def _finish_hd(
    session: object,
    vessel: object | None,
    on_log: Callable[[str], None] | None,
) -> str | None:
    """Recover hop debris or leave Flight Results. None if neither worked."""
    _say("hop finish wreck", on_log)
    got: str | None = None
    for other in _pool(session, vessel):
        if other is vessel or _ours(other):
            hit = _try_recover(other, on_log)
            if hit is not None:
                got = hit
    if got is None:
        got = _force_recover(vessel, on_log)
    dismissed = False
    try:
        go_space_center(session)
        dismissed = True
        _say("hop dismissed flight results", on_log)
    except Exception as exc:
        log.warning("hop dismiss flight results: %s", exc)
    if got is None:
        for other in _pool(session, vessel):
            if other is vessel or _ours(other):
                hit = _try_recover(other, on_log)
                if hit is not None:
                    got = hit
                    break
    if got is not None:
        return got
    if dismissed:
        _say("recovered", on_log)
        mission_event("recover")
        return "recovered"
    return None


def _uplink_tick(ctx: Ctx) -> None:
    """Abort-class raises. Do not Toggle or extra-stage."""
    cmd = take()
    if cmd is None:
        return
    verb = str(getattr(cmd, "verb", "") or "").lower().replace("-", "_")
    if verb in _UPLINK_SKIP:
        return
    try:
        call(cmd.verb, ctx)
    except KeyError:
        pass
    if verb in _ABORT_UPLINK:
        raise MissionAbort(verb)


def _light(vessel: object, on_log: Callable[[str], None] | None) -> None:
    try:
        control = vessel.control
    except Exception as exc:
        raise MissionAbort(f"light failed: {exc}") from exc
    try:
        control.sas = True
    except Exception:
        pass
    try:
        control.throttle = 1.0
    except Exception:
        pass
    try:
        control.activate_next_stage()
    except Exception as exc:
        raise MissionAbort(f"light failed: {exc}") from exc
    _say("hop light", on_log)


def _hold_or_cut(vessel: object, snap: object, hop_apo: float) -> None:
    """Throttle 0 at hop_apo. An SRB ignores this — do not OffPlan the coast."""
    try:
        control = vessel.control
        apo = float(getattr(snap, "apo", float("nan")))
        if math.isfinite(apo) and apo >= hop_apo:
            control.throttle = 0.0
        else:
            control.throttle = 1.0
    except Exception:
        pass


def _active(session: object, vessel: object) -> object | None:
    try:
        live = session.active_vessel  # type: ignore[attr-defined]
    except Exception:
        live = vessel
    return live


def run_on_vessel(
    session: object,
    vessel: object,
    *,
    events: EventLog | None = None,
    on_log: Callable[[str], None] | None = None,
    science_ids: tuple[str, ...] | None = None,
    abort: Callable[[], bool] | None = None,
    now: Callable[[], float] | None = None,
    sleep: Callable[[float], None] | None = None,
    timeout: float | None = None,
    pulse: float = _PULSE_S,
) -> str:
    """Light, flying card, recover when down or dead-with-HD. Caller Hangars.

    Leftover (did not light) with drive files or no Experiment modules
    skips a fresh start. A Flea this process lit always starts the card.
    Paused Flight Results (MET stuck) recovers debris or leaves flight.
    """
    from phases import OffPlan, check_expect

    log_events = events if events is not None else EventLog()
    ids = science_ids if science_ids is not None else hop_science_ids()
    hop_apo = hop_target_apo()
    ctx = Ctx(session=session, vessel=vessel, events=log_events, science_ids=ids)
    clock = now if now is not None else time.monotonic
    nap = sleep if sleep is not None else time.sleep
    budget = DEFAULT_HOP_S if timeout is None else float(timeout)
    t0 = clock()
    lit = False
    did_light = False
    left_pad = False
    started: list[str] = []
    science_attempted = False
    pulses = 0
    said_down = False
    waiting_hd = False
    prev_met: float | None = None
    still = 0
    _say(f"hop apo={hop_apo:.0f}", on_log)

    with Telem(session, events=log_events) as telem:
        while True:
            if abort is not None:
                try:
                    stop = bool(abort())
                except Exception:
                    stop = False
                if stop:
                    call("abort_pad", ctx)
                    raise MissionAbort("abort")
            _uplink_tick(ctx)
            live = _active(session, vessel)
            if live is None:
                if left_pad:
                    got = _finish_hd(session, vessel, on_log)
                    if got is not None:
                        return got
                raise MissionAbort("no vessel")
            vessel = live
            ctx.vessel = vessel
            snap = telem.read()
            pulses += 1
            airborne = _airborne(snap)
            if airborne:
                if not left_pad:
                    _say("hop airborne", on_log)
                    log_events.emit("hop", result="airborne")
                    mission_event("airborne", snap)
                left_pad = True
            down = _down(snap, flown=left_pad)

            for reason in gates(snap):
                if reason == "empty tanks" or reason.startswith("atmosphere"):
                    continue
                _say(f"gate {reason}", on_log)
                if reason == "wreck":
                    down = True
                    continue
                if reason.startswith("reliability"):
                    if down and left_pad:
                        continue
                    call("abort_pad", ctx)
                    raise MissionAbort(reason)
                if reason == "ec=0":
                    has = _keep_hd(vessel, ids, started, left_pad=left_pad)
                    if has:
                        if left_pad and _recoverable(vessel) and not said_down:
                            _say("hop down", on_log)
                            said_down = True
                        got = _recover_hd(vessel, on_log)
                        if got is not None:
                            return got
                        # HD has data: wait recoverable. Do not timeout-dump
                        # a live fall. Paused wreck is handled below.
                        if left_pad:
                            if not waiting_hd:
                                _say("hop ec=0 wait recoverable", on_log)
                                log_events.emit("science_dwell", result="ec")
                            waiting_hd = True
                    elif not left_pad or down:
                        call("abort_pad", ctx)
                        raise MissionAbort(reason)

            apo = getattr(snap, "apo", float("nan"))
            try:
                apo_f = float(apo)
            except (TypeError, ValueError):
                apo_f = float("nan")
            if (
                left_pad
                and not down
                and not waiting_hd
                and math.isfinite(apo_f)
                and apo_f > FLYING_LOW_M
            ):
                raise OffPlan(f"apo {apo_f:.0f} > {FLYING_LOW_M:.0f} FlyingLow")
            if left_pad and not down and not waiting_hd:
                check_expect(snap, skip_peri=True, skip_apo=True)

            if not lit:
                if airborne:
                    lit = True
                elif not left_pad and str(snap.situation) in _LIGHT_SIT:
                    _light(vessel, on_log)
                    lit = True
                    did_light = True
                    log_events.emit("hop", result="light")
                    mission_event("light", snap)

            if left_pad and not down:
                _hold_or_cut(vessel, snap, hop_apo)

            if left_pad and not down and not science_attempted:
                science_attempted = True
                if (not did_light) and _keep_hd(
                    vessel, ids, started, left_pad=True
                ):
                    _say("science keep HD", on_log)
                    log_events.emit("science", result="keep")
                    mission_event("science", snap)
                    waiting_hd = True
                else:
                    started = start_experiments(vessel, names=ids, on_log=on_log)
                    if started:
                        _say("science " + ",".join(started), on_log)
                        log_events.emit("science", ids=list(started))
                        mission_event("science", snap)
                        _say("science dwell", on_log)
                        log_events.emit("science_dwell", phase="start")
                    elif ids:
                        call("abort_pad", ctx)
                        raise MissionAbort("no science (wanted " + ",".join(ids) + ")")

            # First recoverable after flight — situation may stay flying.
            if left_pad and _recoverable(vessel):
                if not said_down:
                    _say("hop down", on_log)
                    said_down = True
                got = _recover_hd(vessel, on_log)
                if got is not None:
                    return got

            if down and left_pad:
                if not said_down:
                    _say("hop down", on_log)
                    said_down = True

            if down and not left_pad:
                call("abort_pad", ctx)
                raise MissionAbort("wreck")

            met = _vessel_met(vessel)
            if waiting_hd and not _recoverable(vessel):
                if met is not None and not math.isfinite(met):
                    got = _finish_hd(session, vessel, on_log)
                    if got is not None:
                        return got
                    raise MissionAbort("not recoverable")
                if (
                    met is not None
                    and prev_met is not None
                    and abs(met - prev_met) < _STILL_MET
                ):
                    still += 1
                    if still >= _STILL_N:
                        _say("hop paused wreck", on_log)
                        log_events.emit("hop", result="paused")
                        mission_event("paused", snap)
                        got = _finish_hd(session, vessel, on_log)
                        if got is not None:
                            return got
                        raise MissionAbort("not recoverable")
                else:
                    still = 0
            else:
                still = 0
            if met is not None and math.isfinite(met):
                prev_met = met

            elapsed = clock() - t0
            if pulses > 1 and elapsed >= budget:
                if left_pad:
                    got = _recover_hd(vessel, on_log)
                    if got is not None:
                        return got
                has = _keep_hd(vessel, ids, started, left_pad=left_pad)
                if has and left_pad and not down:
                    # Airborne/dead with HD: do not timeout-dump.
                    if not waiting_hd:
                        _say("hop wait recoverable", on_log)
                        waiting_hd = True
                    nap(pulse)
                    continue
                if down and left_pad:
                    raise MissionAbort("not recoverable")
                _say(f"hop timeout {elapsed:.0f}s", on_log)
                raise MissionAbort("timeout")
            nap(pulse)


def run_hop(
    session: object,
    *,
    on_log: Callable[[str], None] | None = None,
    abort: Callable[[], bool] | None = None,
) -> str:
    """``python main.py hop``: Hangar the seated hop craft uncrewed, then light."""
    hop_science_ids()
    install_and_launch(session)
    try:
        msg = wait_vessel_ready(session)
    except Exception as exc:
        raise MissionAbort(f"no vessel after launch: {exc}") from exc
    _say(msg, on_log)
    vessel = _active_vessel(session)
    if vessel is None:
        raise MissionAbort("no vessel after launch")
    if _is_pad_motor(vessel):
        raise MissionAbort("Hangar put kspstuff-pad-pbc — refused")
    return run_on_vessel(session, vessel, on_log=on_log, abort=abort)


def run_phase(
    session: object,
    *,
    on_log: Callable[[str], None] | None = None,
    abort: Callable[[], bool] | None = None,
) -> str:
    """``phase hop``: Hangar if empty or leftover pad motor; else leftover Flight.

    Tracking leftover at SpaceCenter is switched into Flight. Do not Hangar
    a second hop on that pad. Do not fly leftover pad/geiger as a hop.
    """
    vessel = _find_hop_vessel(session)
    if vessel is None or _is_pad_motor(vessel):
        return run_hop(session, on_log=on_log, abort=abort)
    _ensure_flight(session, vessel, on_log)
    live = _active_vessel(session)
    if live is not None:
        vessel = live
    return run_on_vessel(session, vessel, on_log=on_log, abort=abort)


HOP_TO_WATER_ABORT = (
    "hop-to-water refused: Start Flea cannot steer to Water "
    "(Stayputnik has no torque, Flea has no gimbal, no chute). "
    "Cape Shores vertical hop lithobrakes Shores (18-32: 74 m). "
    "need_builder for east pitch, or skip splash"
)


def run_hop_to_water(
    session: object,
    *,
    on_log: Callable[[str], None] | None = None,
    abort: Callable[[], bool] | None = None,
) -> str:
    """Named catalog block. Does not Hangar. Does not fake Water."""
    _say(HOP_TO_WATER_ABORT, on_log)
    raise MissionAbort(HOP_TO_WATER_ABORT)
