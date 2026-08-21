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
not Hangar a second stack. Unmatched leftover (PRELAUNCH Flea vs
seated Valiant) recovers without lighting, then Hangars the seated
craft. Leftover is the live kRPC pool, not save
FLYING debris. A dead kRPC GUID (``No such vessel``) is not leftover
— scan tracking; empty Tracking Hangars. ``… Debris`` is not a hop
leftover. Ballistic peri is negative. No chute.
MET-still + q=0 while flying is down now (lithobrake / crash UI) —
do not wait the wreck-dialog wall. Low flying (≤250 m) calls
``vessel.recover()`` only when ``recoverable`` — last living hop
banked at ~199 m. Frozen MET + flying + q=0 + low alt is Catastrophic
Flight Results: log sit/recoverable/met/alt/q, ``recover()`` if
``recoverable``, else ``go_space_center`` (Close / Space Center, not
revert) and abort. Do not wait ``sit=landed`` that never comes
(12-04-13Z). Dismiss is not a living recover; post-dismiss
``pre_launch`` recoverable is not recovery@EarthFlew. 1 Hz recover
line names sit + recoverable. Splash goo is not a hop start. Do not
light a pad geiger.
"""

from __future__ import annotations

import logging
import math
import time
from pathlib import Path
from typing import Callable

from card import NO_BOUND_CARD, card_flying_ids, parse_card
from emergencies import Ctx, call
from hangar import (
    discover_hangar,
    game_scene,
    go_flight,
    go_space_center,
    run_physics,
    wait_vessel_ready,
)
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
_NOT_HOP = (PAD_CRAFT, GEIGER_CRAFT)
_DEBRIS_SUFFIX = " debris"
REPO_CRAFTS = Path(__file__).resolve().parent / "crafts"
HOP_APO_DEFAULT = 15_000.0
HOP_APO_CLAMP = (8_000.0, 18_000.0)
# hop_apo is a cut. Solids ignore it. FlyingLow clamp 8–18 km.
# FlyingHigh card unclamps to Space (RSS Earth atmosphere_depth).
HOP_APO_MAX = 18_000.0
FLYING_LOW_M = 50_000.0
FLYING_HIGH_M = 140_000.0
_HOP_PREFIX = "kspstuff-hop-"
DEFAULT_HOP_S = 600.0
_AIRBORNE_M = 250.0
_PULSE_S = 1.0
_STILL_N = 5
_STILL_MET = 0.2
_AIR = frozenset({"flying", "sub_orbital", "suborbital", "escaping", "orbiting"})
_GROUND = frozenset({"landed", "splashed", "wrecked", "wreck"})
_PAD_SIT = frozenset({"pre_launch", "prelaunch"})
_LIGHT_SIT = frozenset({"pre_launch", "prelaunch", "landed"})
_ABORT_UPLINK = frozenset({"abort_pad", "abort", "hold", "freeze", "recover"})
_UPLINK_SKIP = frozenset({"science", "stage"})


def _say(msg: str, on_log: Callable[[str], None] | None) -> None:
    log.info(msg)
    if on_log:
        on_log(msg)


def hop_wants_flying_high() -> bool:
    """Bound flying card names FlyingHigh. Missing card is FlyingLow."""
    try:
        from missions import seated_science_path

        path = seated_science_path()
        if not path.is_file():
            return False
        text = path.read_text(encoding="utf-8")
    except Exception:
        return False
    for row in parse_card(text):
        sit = (row.situation or "").lower().replace(" ", "").replace("_", "")
        sec = (row.section or "").lower().replace(" ", "").replace("_", "")
        if "flyinghigh" in sit or "flyinghigh" in sec:
            return True
    return False


def hop_offplan_apo() -> float:
    """OffPlan apo lid. FlyingLow 50 km; FlyingHigh is Space (140 km)."""
    return FLYING_HIGH_M if hop_wants_flying_high() else FLYING_LOW_M


def hop_target_apo() -> float:
    """Gene ``hop_apo`` (m). FlyingLow clamp 8–18 km; FlyingHigh to Space."""
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
    lo, hi = HOP_APO_CLAMP
    if hop_wants_flying_high():
        hi = hop_offplan_apo()
    return min(hi, max(lo, apo))


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
    try:
        return str(getattr(vessel, "name", "") or "")
    except Exception:
        return ""


def _craft_token(name: str) -> str:
    """Vessel/craft name without KSP `` Debris`` suffix."""
    low = (name or "").strip().lower()
    if low.endswith(_DEBRIS_SUFFIX):
        return low[: -len(_DEBRIS_SUFFIX)].rstrip()
    return low


def _is_debris_name(name: str) -> bool:
    return (name or "").strip().lower().endswith(_DEBRIS_SUFFIX)


def _is_not_hop_name(name: str) -> bool:
    """Exact pad/geiger craft names (plus Debris suffix), not a substring."""
    return _craft_token(name) in {PAD_CRAFT.lower(), GEIGER_CRAFT.lower()}


def _is_pad_motor(vessel: object) -> bool:
    return _is_not_hop_name(_vessel_name(vessel))


def _is_hop_motor(vessel: object) -> bool:
    """Living hop stack (Flea/Hammer/Valiant). Not pad, geiger, or Debris."""
    name = _vessel_name(vessel)
    if not name or _is_not_hop_name(name) or _is_debris_name(name):
        return False
    token = _craft_token(name)
    wanted = hop_match_name().lower()
    if wanted and wanted in name.lower():
        return True
    return _HOP_PREFIX in token


def _is_hop_craft(vessel: object) -> bool:
    """Living hop ship matching the seated name. Debris is not leftover."""
    name = _vessel_name(vessel)
    if not name or _is_not_hop_name(name) or _is_debris_name(name):
        return False
    wanted = hop_match_name().lower()
    return bool(wanted) and wanted in name.lower()


def _is_unmatched_hop(vessel: object) -> bool:
    """Hop motor in the pool that is not the seated/VAB craft."""
    return _is_hop_motor(vessel) and not _is_hop_craft(vessel)


def _vessel_live(vessel: object | None) -> bool:
    """False if the kRPC proxy GUID is already gone."""
    if vessel is None:
        return False
    try:
        getattr(vessel, "name")
    except Exception:
        return False
    return True


def _active_vessel(session: object) -> object | None:
    try:
        vessel = session.active_vessel  # type: ignore[attr-defined]
    except Exception:
        return None
    if not _vessel_live(vessel):
        return None
    return vessel


def _find_hop_vessel(session: object) -> object | None:
    """Active leftover, else live tracking pool. Not Debris, not save ghosts.

    Dead GUID (``No such vessel``) is not leftover — scan tracking.
    Empty live pool Hangars. Disk FLYING debris is not leftover.
    """
    active = _active_vessel(session)
    if active is not None and _is_hop_craft(active):
        return active
    for other in _pool(session, active):
        if other is not None and other is not active and _is_hop_craft(other):
            return other
    return None


def _find_unmatched_leftover(session: object) -> object | None:
    """Live unmatched hop motor. Flea vs seated Valiant. Not Debris."""
    active = _active_vessel(session)
    if active is not None and _is_unmatched_hop(active):
        return active
    for other in _pool(session, active):
        if other is not None and other is not active and _is_unmatched_hop(other):
            return other
    return None


def _recover_unmatched_leftover(
    session: object,
    vessel: object,
    on_log: Callable[[str], None] | None,
) -> str:
    """Recover unmatched leftover. Do not light. Do not Hangar over it."""
    name = _vessel_name(vessel) or "?"
    sit = _vessel_sit(vessel)
    rec = "yes" if _recoverable(vessel) else "no"
    _say(
        f"hop leftover unmatched {name} sit={sit} recoverable={rec} "
        "— recover, do not light",
        on_log,
    )
    if not _recoverable(vessel):
        raise MissionAbort("unmatched leftover not recoverable")
    try:
        getattr(vessel, "recover")()
    except Exception as exc:
        raise MissionAbort(f"unmatched leftover recover failed: {exc}") from exc
    _say(f"recovered unmatched leftover sit={sit} recoverable=yes", on_log)
    mission_event("recover")
    try:
        go_space_center(session)
    except Exception:
        pass
    return "recovered"


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

    Byte-copy the repo file — never Hangar pad/geiger. Exact names, not
    a substring (hop-*-geiger-pbc may carry the part). Same pointer as pad.
    """
    from session import SessionError

    try:
        name = hop_craft_name()
    except SessionError as exc:
        raise MissionAbort(str(exc)) from exc
    if _is_not_hop_name(name):
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


def _snap_q(snap: object) -> float:
    try:
        q = float(getattr(snap, "q", float("nan")))
    except (TypeError, ValueError):
        return float("nan")
    return q if math.isfinite(q) else float("nan")


def _q_zero(snap: object) -> bool:
    q = _snap_q(snap)
    return math.isfinite(q) and q <= 0.0


def _fmt(val: float | None, digits: int) -> str:
    if val is None:
        return "?"
    try:
        num = float(val)
    except (TypeError, ValueError):
        return "?"
    if not math.isfinite(num):
        return "?"
    return f"{num:.{digits}f}"


def _vessel_sit(vessel: object | None) -> str:
    if vessel is None:
        return "?"
    try:
        raw = getattr(vessel, "situation", None)
    except Exception:
        return "?"
    name = getattr(raw, "name", None)
    if name:
        return str(name).lower()
    text = str(raw or "").strip()
    return text.lower() if text else "?"


def _met_still(
    met: float | None, prev: float | None, still: int
) -> tuple[int, bool]:
    """Count frozen MET. NaN MET is frozen now."""
    if met is not None and not math.isfinite(met):
        return still, True
    if (
        met is not None
        and prev is not None
        and abs(met - prev) < _STILL_MET
    ):
        n = still + 1
        return n, n >= _STILL_N
    return 0, False


def _recoverable(vessel: object | None) -> bool:
    if vessel is None:
        return False
    try:
        return bool(getattr(vessel, "recoverable", False))
    except Exception:
        return False


def _recover_tick(
    vessel: object | None, on_log: Callable[[str], None] | None
) -> None:
    rec = "yes" if _recoverable(vessel) else "no"
    _say(f"hop recover sit={_vessel_sit(vessel)} recoverable={rec}", on_log)


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
    sit = _vessel_sit(vessel)
    if not _recoverable(vessel):
        return None
    result = recover_or_abort(vessel)
    _say(f"{result} sit={sit} recoverable=yes", on_log)
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
    name = _vessel_name(vessel)
    if not name or _is_pad_motor(vessel):
        return False
    wanted = hop_match_name().lower()
    low = name.lower()
    return (wanted and wanted in low) or _is_debris_name(name)


def _try_recover(
    vessel: object | None, on_log: Callable[[str], None] | None
) -> str | None:
    sit = _vessel_sit(vessel)
    if vessel is None or sit in _PAD_SIT or not _recoverable(vessel):
        return None
    try:
        getattr(vessel, "recover")()
    except Exception as exc:
        log.debug("hop recover() sit=%s: %s", sit, exc)
        return None
    _say(f"recovered sit={sit} recoverable=yes", on_log)
    mission_event("recover")
    return "recovered"


def _force_recover(
    vessel: object | None, on_log: Callable[[str], None] | None
) -> str | None:
    """recover() in Flight on ground, or when recoverable. Flying no is crash UI."""
    if vessel is None:
        return None
    sit = _vessel_sit(vessel)
    if sit in _PAD_SIT:
        return None
    if not _recoverable(vessel) and sit not in _GROUND:
        return None
    try:
        getattr(vessel, "recover")()
    except Exception as exc:
        log.debug("hop recover() sit=%s: %s", sit, exc)
        return None
    _say(f"recovered sit={sit} recoverable=yes", on_log)
    mission_event("recover")
    return "recovered"


def _pool(session: object, vessel: object | None) -> list[object]:
    """Live kRPC vessels only. Dead GUID / save FLYING ghosts stay out."""
    out: list[object] = []
    if _vessel_live(vessel):
        out.append(vessel)
    try:
        extra = list(getattr(getattr(session, "space_center", None), "vessels", []) or [])
    except Exception:
        extra = []
    for other in extra:
        if other is not None and other not in out and _vessel_live(other):
            out.append(other)
    return out


def _unpause(
    session: object, on_log: Callable[[str], None] | None
) -> None:
    """Flight Results / Hangar often freeze MET. Unpause is not recover()."""
    _say("hop unpause", on_log)
    try:
        run_physics(session)
    except Exception as exc:
        log.warning("hop unpause: %s", exc)


def _snap_alt(snap: object) -> float:
    try:
        alt = float(getattr(snap, "alt", float("nan")))
    except (TypeError, ValueError):
        return float("nan")
    return alt if math.isfinite(alt) else float("nan")


def _low_flying(snap: object) -> bool:
    """Near-ground flying — last living hop recovered ~199 m, still Flight."""
    sit = str(getattr(snap, "situation", "") or "")
    if sit not in _AIR:
        return False
    alt = _snap_alt(snap)
    return math.isfinite(alt) and alt <= _AIRBORNE_M


def _crash_ui(snap: object, *, frozen: bool) -> bool:
    """Catastrophic Flight Results: MET frozen, flying, q=0, low."""
    if not frozen:
        return False
    return _low_flying(snap) and _q_zero(snap)


def _crash_line(
    vessel: object | None,
    snap: object,
    on_log: Callable[[str], None] | None,
) -> None:
    rec = "yes" if _recoverable(vessel) else "no"
    _say(
        "hop crash ui "
        f"sit={_vessel_sit(vessel)} recoverable={rec} "
        f"met={_fmt(_vessel_met(vessel), 2)} alt={_fmt(_snap_alt(snap), 1)} "
        f"q={_fmt(_snap_q(snap), 0)}",
        on_log,
    )


def _leave_crash_ui(
    session: object, on_log: Callable[[str], None] | None
) -> None:
    """Close / Space Center. Never revert."""
    try:
        go_space_center(session)
        _say("hop dismissed crash ui", on_log)
    except Exception as exc:
        log.warning("hop dismiss crash ui: %s", exc)


def _finish_hd(
    session: object,
    vessel: object | None,
    on_log: Callable[[str], None] | None,
) -> str | None:
    """recover() while still Flight. Do not dismiss flying recoverable=no."""
    _say("hop finish wreck", on_log)
    got: str | None = None
    _recover_tick(vessel, on_log)
    got = _force_recover(vessel, on_log)
    if got is None:
        for other in _pool(session, vessel):
            if other is vessel or not _ours(other):
                continue
            hit = _try_recover(other, on_log)
            if hit is not None:
                got = hit
                break
    if got is None:
        return None
    try:
        go_space_center(session)
        _say("hop dismissed flight results", on_log)
    except Exception as exc:
        log.warning("hop dismiss flight results: %s", exc)
    return got


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
    MET-still + q=0 flying is down now. Low flying (≤250 m) calls
    recover() only when recoverable. Frozen MET + flying + q=0 + low
    alt is crash UI: recover() if recoverable, else Space Center and
    abort. Do not wait landed. Post-dismiss pre_launch is not the HD.
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
    unpaused = False
    litho = False
    said_crash = False
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
            down = _down(snap, flown=left_pad) or litho

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
            lid = hop_offplan_apo()
            label = "Space" if hop_wants_flying_high() else "FlyingLow"
            if hop_wants_flying_high():
                atm = getattr(snap, "atm_depth", float("nan"))
                try:
                    atm_f = float(atm)
                except (TypeError, ValueError):
                    atm_f = float("nan")
                if math.isfinite(atm_f) and atm_f > 0.0:
                    lid = atm_f
            if (
                left_pad
                and not down
                and not waiting_hd
                and math.isfinite(apo_f)
                and apo_f > lid
            ):
                raise OffPlan(f"apo {apo_f:.0f} > {lid:.0f} {label}")
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
                _recover_tick(vessel, on_log)
                got = _recover_hd(vessel, on_log)
                if got is not None:
                    return got
            elif left_pad:
                for other in _pool(session, vessel):
                    if other is vessel or not _ours(other):
                        continue
                    hit = _try_recover(other, on_log)
                    if hit is None:
                        continue
                    try:
                        go_space_center(session)
                        _say("hop dismissed flight results", on_log)
                    except Exception as exc:
                        log.warning("hop dismiss flight results: %s", exc)
                    return hit

            met = _vessel_met(vessel)
            frozen = False
            if left_pad and not _recoverable(vessel):
                still, frozen = _met_still(met, prev_met, still)
            else:
                still = 0
            sit_now = str(getattr(snap, "situation", "") or "")
            if frozen and sit_now in _AIR and _q_zero(snap):
                litho = True
                down = True

            if down and left_pad:
                if not said_down:
                    _say("hop down", on_log)
                    said_down = True

            if left_pad and (down or _low_flying(snap)):
                got = _force_recover(vessel, on_log)
                if got is not None:
                    return got

            if down and not left_pad:
                call("abort_pad", ctx)
                raise MissionAbort("wreck")

            if left_pad and (waiting_hd or down or still > 0) and not _recoverable(
                vessel
            ):
                _recover_tick(vessel, on_log)

            if frozen:
                sit_v = _vessel_sit(vessel)
                if _crash_ui(snap, frozen=True):
                    if not said_crash:
                        _crash_line(vessel, snap, on_log)
                        said_crash = True
                    got = _force_recover(vessel, on_log)
                    if got is not None:
                        return got
                    if not unpaused:
                        _unpause(session, on_log)
                        unpaused = True
                        still = 0
                    else:
                        _leave_crash_ui(session, on_log)
                        raise MissionAbort("not recoverable")
                elif sit_v in _AIR:
                    if not unpaused:
                        _unpause(session, on_log)
                        unpaused = True
                    still = 0
                elif not unpaused:
                    _unpause(session, on_log)
                    unpaused = True
                    still = 0
                else:
                    _say("hop paused wreck", on_log)
                    log_events.emit("hop", result="paused")
                    mission_event("paused", snap)
                    got = _finish_hd(session, vessel, on_log)
                    if got is not None:
                        return got
                    raise MissionAbort("not recoverable")
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
    leftover = _find_unmatched_leftover(session)
    if leftover is not None:
        _recover_unmatched_leftover(session, leftover, on_log)
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
    a second hop on that pad. Unmatched leftover recovers without lighting
    (PRELAUNCH Flea vs seated Valiant), then Hangars the seated craft.
    Do not fly leftover pad/geiger as a hop.
    Live kRPC hop ship only — FLYING Debris is not leftover.
    """
    leftover = _find_unmatched_leftover(session)
    if leftover is not None:
        _recover_unmatched_leftover(session, leftover, on_log)
        return run_hop(session, on_log=on_log, abort=abort)
    vessel = _find_hop_vessel(session)
    if vessel is None or _is_pad_motor(vessel):
        return run_hop(session, on_log=on_log, abort=abort)
    _ensure_flight(session, vessel, on_log)
    live = _active_vessel(session)
    if live is not None and _is_hop_craft(live):
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
