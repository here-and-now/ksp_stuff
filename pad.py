"""Pad science compose. Not hop.py.

Hangar the seated / VAB craft file (Gus-signed ``.craft``), start the
seated science.md pad card (not a hardcoded goo+thermo pair), dwell
until the HD has the card (or remaining EC is gone), recover or abort
honestly. Do not ``pad_pbc()`` a geiger sit — that template has no
Geiger Counter part (F-013). Pad EC=0 with data recovers; empty HD
aborts. Science clock is rem / running / UT, not vessel MET. Dry-launch
only when it will not light the motor. Pad dwell may physics-warp
2–4× (rails 0, never WarpTo); back to 1× after. Empty card aborts
(``no bound card``) before Hangar.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Callable

from card import NO_BOUND_CARD, card_pad_ids
from emergencies import Ctx, call
from hangar import discover_hangar, game_scene, go_flight, run_physics, wait_vessel_ready
from science import (
    card_complete,
    card_has_data,
    card_run_rem,
    card_wait_line,
    hd_has_data,
    pad_dwell_s,
    start_experiments,
)
from screenshot import mission_event
from telem import EventLog, MissionAbort, Telem, gates
from uplink import take

log = logging.getLogger("kspstuff")

TEMPLATE = "kspstuff-pad-pbc"
CRAFT = TEMPLATE
REPO_CRAFTS = Path(__file__).resolve().parent / "crafts"
_PULSE_S = 1.0
_STILL_N = 5
_STILL_MET = 0.2
_STILL_UT = 0.2
_PAD_SIT = frozenset(
    {"pre_launch", "prelaunch", "landed", "srf_landed", "srflanded"}
)
# kRPC physics_warp_factor: 0=1×, 1=2×, 2=3×, 3=4×. Never rails.
_PAD_PHYS_FACTOR = 2
_PAD_PHYS_MAX = 3
_DWELL_ABORT = frozenset({"abort_pad", "abort", "hold", "freeze", "recover"})
# Hop-era radio. Toggle starts *and* stops; the pad SRB is not a hop.
_PAD_UPLINK_SKIP = frozenset({"science", "stage"})


def _say(msg: str, on_log: Callable[[str], None] | None) -> None:
    log.info(msg)
    if on_log:
        on_log(msg)


def pad_science_ids() -> tuple[str, ...]:
    """Pad experiments. Science tickets first; science.md is fallback.

    Empty or missing card aborts. A bound geiger card is not F-005
    goo+thermo.
    """
    from tickets import science_ids_for

    ids = science_ids_for(situation="landed")
    if ids:
        return ids
    from missions import seated_science_path

    path = seated_science_path()
    if not path.is_file():
        raise MissionAbort(NO_BOUND_CARD)
    ids = card_pad_ids(path.read_text(encoding="utf-8"))
    if not ids:
        raise MissionAbort(NO_BOUND_CARD)
    return ids


def _uplink_tick(ctx: Ctx) -> None:
    """Take uplink. abort-class raises. Do not Toggle or stage."""
    cmd = take()
    if cmd is None:
        return
    verb = str(getattr(cmd, "verb", "") or "").lower().replace("-", "_")
    if verb in _PAD_UPLINK_SKIP:
        return
    try:
        call(cmd.verb, ctx)
    except KeyError:
        pass
    if verb in _DWELL_ABORT:
        raise MissionAbort(verb)


def _ec_has_science(
    vessel: object,
    science_ids: tuple[str, ...] | list[str],
    saw_running: dict[tuple, bool],
    pulses: int,
) -> bool:
    """Pad EC=0 is not a wreck if the HD already has data, or we already ran."""
    if card_has_data(vessel, science_ids):
        return True
    if pulses <= 1:
        return False
    return any(saw_running.values())


def _hd_stored(vessel: object, science_ids: tuple[str, ...] | list[str]) -> bool:
    """Stored files / Has Data — not idle remaining=0."""
    return bool(
        card_has_data(vessel, science_ids, remaining=False) or hd_has_data(vessel)
    )


def _launch_clock(
    vessel: object,
    on_log: Callable[[str], None] | None,
) -> None:
    """Leave pre_launch so MET can tick. Throttle 0. Do not hop.

    KSP does not increment ``vessel.met`` in PRELAUNCH. First stage is
    a dry launch if the SRB is already ``istg=0`` (stage 0 restage is a
    no-op). A Flea at ``istg=1`` would light — skip.
    """
    sit = str(getattr(vessel, "situation", "") or "").lower().replace("-", "_")
    if sit not in {"pre_launch", "prelaunch"}:
        return
    try:
        control = vessel.control
        stage = getattr(control, "current_stage", 0)
        try:
            stage_n = int(stage)
        except (TypeError, ValueError):
            stage_n = 0
        if stage_n != 0:
            _say(f"pad launch clock skip stage={stage_n} (would light)", on_log)
            return
        control.throttle = 0.0
        control.activate_next_stage()
        _say("pad launch clock", on_log)
    except Exception as exc:
        log.warning("pad launch clock: %s", exc)
        return
    try:
        vessel.situation = "landed"
    except Exception:
        pass


def _unpause_clock(
    session: object,
    vessel: object,
    on_log: Callable[[str], None] | None,
) -> None:
    """Always unpause. Hangar / Flight Results stop physics."""
    _say("pad unpause", on_log)
    run_physics(session)
    try:
        scene = game_scene(session)  # type: ignore[arg-type]
    except Exception:
        return
    if scene in {"flight", "?"}:
        return
    _say(f"pad enter flight ({scene})", on_log)
    try:
        go_flight(session, vessel)  # type: ignore[arg-type]
    except Exception as exc:
        log.warning("pad enter flight: %s", exc)


def _sc(session: object) -> object | None:
    return getattr(session, "space_center", None)


def _read_ut(session: object) -> float:
    try:
        return float(getattr(_sc(session), "ut"))
    except (TypeError, ValueError, AttributeError):
        return float("nan")


def _rails_zero(session: object) -> None:
    sc = _sc(session)
    if sc is None:
        return
    try:
        sc.rails_warp_factor = 0
    except Exception:
        pass


def _physics_factor(session: object, n: int) -> None:
    """Physics warp only. 0 is 1×. Never rails. Never WarpTo."""
    _rails_zero(session)
    sc = _sc(session)
    if sc is None:
        return
    try:
        sc.physics_warp_factor = int(n)
    except Exception:
        pass


def _sit_ok_for_warp(vessel: object, snap: object | None = None) -> bool:
    sit = ""
    if snap is not None:
        sit = str(getattr(snap, "situation", "") or "")
    if not sit:
        sit = str(getattr(vessel, "situation", "") or "")
    return sit.lower().replace("-", "_") in _PAD_SIT


def _pad_physics_warp(
    session: object,
    vessel: object,
    on_log: Callable[[str], None] | None,
    *,
    snap: object | None = None,
) -> None:
    """2–4× physics on the pad. Rails stay 0."""
    _rails_zero(session)
    if not _sit_ok_for_warp(vessel, snap):
        return
    n = min(max(_PAD_PHYS_FACTOR, 1), _PAD_PHYS_MAX)
    _physics_factor(session, n)
    _say(f"pad physics {n + 1}x rails=0", on_log)


def _pad_physics_1x(
    session: object, on_log: Callable[[str], None] | None
) -> None:
    _physics_factor(session, 0)
    _say("pad physics 1x", on_log)


def _load_catalog() -> object | None:
    try:
        from catalog import load_catalog

        hangar = discover_hangar()
        if hangar is None:
            return None
        return load_catalog(hangar.ksp_root)
    except Exception:
        return None


def dwell_for_card(
    session: object,
    vessel: object,
    *,
    science_ids: tuple[str, ...] | list[str],
    events: EventLog,
    on_log: Callable[[str], None] | None = None,
    ctx: Ctx,
    now: Callable[[], float] | None = None,
    sleep: Callable[[float], None] | None = None,
    timeout: float | None = None,
    abort: Callable[[], bool] | None = None,
    pulse: float = _PULSE_S,
) -> str:
    """Telem pulse until card HD is done, catalog duration, or honest abort.

    Does not Toggle. Science clock is rem / running / UT, not vessel MET.
    Unpause then pad physics-warp (rails 0) before the loop. Freeze
    retries unpause. Recording (run=1 or rem dropping) does not abort
    because MET is 0. Splash EC=0 (19-43-18Z snapshot lie) does not
    abort — return so TELEMETRY/goo can start. Empty HD after a timeout
    with nothing recording still aborts. Always 1× physics on the way out.
    """
    clock = now if now is not None else time.monotonic
    nap = sleep if sleep is not None else time.sleep
    budget = timeout
    t0 = clock()
    saw_running: dict[tuple, bool] = {}
    pulses = 0
    prev_rem: float | None = None
    rem_moved = False
    prev_ut: float | None = None
    ut_moved = False
    still = 0
    nudged = False
    _say("science dwell", on_log)
    events.emit("science_dwell", phase="start")
    _unpause_clock(session, vessel, on_log)
    _pad_physics_warp(session, vessel, on_log)
    try:
        with Telem(session, events=events) as telem:
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
                snap = telem.read()
                pulses += 1
                met = float(getattr(snap, "met", float("nan")))
                ut = _read_ut(session)
                sit = str(
                    getattr(snap, "situation", "")
                    or getattr(vessel, "situation", "")
                    or ""
                )
                running, rem = card_run_rem(vessel, science_ids)
                _say(
                    card_wait_line(
                        vessel,
                        science_ids,
                        met=met if met == met else None,
                        ut=ut if ut == ut else None,
                        sit=sit or None,
                        ec=getattr(snap, "ec", None),
                    ),
                    on_log,
                )
                if rem is not None:
                    if prev_rem is not None and rem < prev_rem - 1e-6:
                        rem_moved = True
                        still = 0
                    prev_rem = rem
                if ut == ut:
                    if prev_ut is not None and ut > prev_ut + _STILL_UT:
                        ut_moved = True
                        still = 0
                    elif prev_ut is not None and ut <= prev_ut + _STILL_UT:
                        still += 1
                        if still >= _STILL_N and not nudged:
                            _say("pad physics frozen", on_log)
                            events.emit("science_dwell", result="physics")
                            _unpause_clock(session, vessel, on_log)
                            _pad_physics_warp(session, vessel, on_log, snap=snap)
                            nudged = True
                    prev_ut = ut
                elif met == met and met <= _STILL_MET:
                    still += 1
                    if still >= _STILL_N and not nudged:
                        _say("pad physics frozen", on_log)
                        _unpause_clock(session, vessel, on_log)
                        _pad_physics_warp(session, vessel, on_log, snap=snap)
                        nudged = True
                recording = bool(running or rem_moved or any(saw_running.values()))
                for reason in gates(snap):
                    _say(f"gate {reason}", on_log)
                    if reason == "wreck" or reason.startswith("reliability"):
                        call("abort_pad", ctx)
                        raise MissionAbort(reason)
                    if reason == "ec=0":
                        card_complete(vessel, science_ids, saw_running)
                        if _ec_has_science(vessel, science_ids, saw_running, pulses):
                            _say("science dwell ec=0 with data", on_log)
                            events.emit("science_dwell", result="ec")
                            return "ec"
                        if recording:
                            continue
                        # 19-43-18Z: 24×Z-100 still 2401 EC at 68 m flying;
                        # first splashed sample is 0. Dwell must not abort.
                        if "splashed" in sit.lower():
                            _say("science dwell ec=0 splash", on_log)
                            events.emit("science_dwell", result="ec")
                            return "ec"
                        call("abort_pad", ctx)
                        raise MissionAbort(reason)
                if pulses > 1 and card_complete(vessel, science_ids, saw_running):
                    _say("science dwell done", on_log)
                    events.emit("science_dwell", result="done")
                    return "done"
                if pulses == 1:
                    card_complete(vessel, science_ids, saw_running)
                elapsed = clock() - t0
                if budget is None:
                    budget = pad_dwell_s(
                        science_ids,
                        vessel=vessel,
                        catalog=_load_catalog(),
                        ec=snap.ec,
                    )
                hard = float(budget) * 2.0 if budget else elapsed
                if pulses > 1 and elapsed >= budget:
                    if _hd_stored(vessel, science_ids):
                        _say(f"science dwell timeout {elapsed:.0f}s", on_log)
                        events.emit("science_dwell", result="timeout", s=elapsed)
                        return "timeout"
                    filing = bool(
                        rem is not None
                        and rem > 0
                        and (running or rem_moved)
                        and elapsed < hard
                    )
                    if filing:
                        nap(pulse)
                        continue
                    _say(f"science dwell timeout {elapsed:.0f}s", on_log)
                    events.emit("science_dwell", result="timeout", s=elapsed)
                    if recording:
                        return "timeout"
                    raise MissionAbort("dwell timeout empty HD")
                nap(pulse)
    finally:
        _pad_physics_1x(session, on_log)


_CHUTE_ARM_EVENTS = (
    "Arm parachute",
    "Arm parachuteS",
    "GUIArm",
)
_CHUTE_DEPLOY_EVENTS = (
    "Deploy chute",
    "Deploy ChuteS",
    "GUIDeploy",
)
_CHUTE_REPACK_EVENTS = (
    "Repack chuteS",
    "GUIRepack",
)
_CHUTE_OPEN = frozenset({"deployed", "semi_deployed", "semideployed"})


def _is_chute_mod(name: object) -> bool:
    n = str(name or "").lower()
    return n == "realchutemodule" or n.endswith("parachute")


def _trigger_chute_events(module: object, want_names: tuple[str, ...]) -> bool:
    want = {n.lower() for n in want_names}
    try:
        elist = list(getattr(module, "event_list", None) or [])
    except Exception:
        elist = []
    for ev in elist:
        try:
            gui = str(getattr(ev, "gui_name", "") or "")
            ident = str(getattr(ev, "name", "") or "")
        except Exception:
            continue
        if gui.lower() not in want and ident.lower() not in want:
            continue
        trig = getattr(ev, "trigger", None)
        if callable(trig):
            try:
                trig()
                return True
            except Exception:
                pass
    try:
        names = [str(x) for x in (getattr(module, "events", None) or [])]
    except Exception:
        names = []
    trigger = getattr(module, "trigger_event", None)
    by_id = getattr(module, "trigger_event_by_id", None)
    for ev_name in names:
        if ev_name.lower() not in want:
            continue
        if callable(trigger):
            try:
                trigger(ev_name)
                return True
            except Exception:
                pass
        if callable(by_id):
            try:
                by_id(ev_name)
                return True
            except Exception:
                pass
    for ev_name in want_names:
        if callable(trigger):
            try:
                trigger(ev_name)
                return True
            except Exception:
                pass
        if callable(by_id):
            try:
                by_id(ev_name)
                return True
            except Exception:
                pass
    return False


def _arm_krpc_chute(ch: object) -> bool:
    """kRPC Parachute: arm, do not immediate deploy (high-q shred)."""
    hit = False
    try:
        if not bool(getattr(ch, "armed", False)):
            ch.armed = True
            hit = True
        else:
            hit = True
    except Exception:
        pass
    arm = getattr(ch, "arm", None)
    if callable(arm):
        try:
            arm()
            hit = True
        except Exception:
            pass
    return hit


def _deploy_krpc_chute(ch: object) -> bool:
    dep = getattr(ch, "deploy", None)
    if callable(dep):
        try:
            dep()
            return True
        except Exception:
            pass
    try:
        ch.deployed = True
        return True
    except Exception:
        return False


def _each_chute(vessel: object):
    try:
        chutes = list(getattr(getattr(vessel, "parts", None), "parachutes", None) or [])
    except Exception:
        chutes = []
    for ch in chutes:
        yield ("krpc", ch)
    try:
        parts = list(getattr(getattr(vessel, "parts", None), "all", None) or [])
    except Exception:
        parts = []
    for part in parts:
        try:
            modules = list(getattr(part, "modules", None) or [])
        except Exception:
            continue
        for module in modules:
            try:
                mname = str(getattr(module, "name", "") or "")
            except Exception:
                continue
            if not _is_chute_mod(mname):
                continue
            yield ("mod", module)


def _chute_state_now(vessel: object) -> str:
    from telem import chute_state

    try:
        return str(chute_state(vessel) or "none")
    except Exception:
        return "none"


def arm_chutes(vessel: object, on_log: Callable[[str], None] | None = None) -> str:
    """Arm Mk16 / RealChute. Do not extra-stage. Do not Deploy here.

    00-10-20Z never armed. 06-53-50Z kRPC armed stayed packed to 154 m/s.
    """
    hit = False
    for kind, obj in _each_chute(vessel):
        if kind == "krpc":
            if _arm_krpc_chute(obj):
                hit = True
        elif _trigger_chute_events(obj, _CHUTE_ARM_EVENTS):
            hit = True
    st = _chute_state_now(vessel)
    if hit and st in {"none", "stowed", "cut"}:
        st = "armed"
    if hit or st not in {"", "none"}:
        _say(f"chute {st}", on_log)
    return st


def deploy_chutes(vessel: object, on_log: Callable[[str], None] | None = None) -> str:
    """Force RealChute ``Deploy chute`` on the way down. Do not extra-stage.

    06-53-50Z stayed armed through 206 m / 154 m/s, then none. Repack if
    cut, Arm, then Deploy. kRPC ``armed=True`` is not a canopy.
    """
    st = _chute_state_now(vessel)
    if st in _CHUTE_OPEN:
        return st
    if st == "cut":
        for kind, obj in _each_chute(vessel):
            if kind == "mod":
                _trigger_chute_events(obj, _CHUTE_REPACK_EVENTS)
    arm_chutes(vessel, on_log=None)
    hit = False
    for kind, obj in _each_chute(vessel):
        if kind == "krpc":
            if _deploy_krpc_chute(obj):
                hit = True
        elif _trigger_chute_events(obj, _CHUTE_DEPLOY_EVENTS):
            hit = True
    st = _chute_state_now(vessel)
    if hit and st not in _CHUTE_OPEN:
        st = "deployed"
    if hit or st not in {"", "none"}:
        _say(f"chute {st}", on_log)
    return st


def recover_or_abort(vessel: object) -> str:
    """Recover the HD if KSP will allow it; otherwise honest abort."""
    try:
        ok = bool(getattr(vessel, "recoverable", False))
    except Exception:
        ok = False
    if ok:
        getattr(vessel, "recover")()
        mission_event("recover")
        return "recovered"
    raise MissionAbort("not recoverable")


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
    """Science, dwell until HD has the card, recover/abort."""
    log_events = events if events is not None else EventLog()
    ids = science_ids if science_ids is not None else pad_science_ids()
    ctx = Ctx(
        session=session,
        vessel=vessel,
        events=log_events,
        science_ids=ids,
    )
    _uplink_tick(ctx)
    _launch_clock(vessel, on_log)
    started = start_experiments(vessel, names=ids, on_log=on_log)
    if started:
        _say("science " + ",".join(started), on_log)
        log_events.emit("science", ids=list(started))
        mission_event("science")
        dwell_for_card(
            session,
            vessel,
            science_ids=tuple(started),
            events=log_events,
            on_log=on_log,
            ctx=ctx,
            now=now,
            sleep=sleep,
            timeout=timeout,
            abort=abort,
            pulse=pulse,
        )
    else:
        _say("science (none)", on_log)
        if ids:
            wanted = ",".join(ids)
            call("abort_pad", ctx)
            raise MissionAbort(f"no science (wanted {wanted})")
        with Telem(session, events=log_events) as telem:
            snap = telem.read()
        for reason in gates(snap):
            _say(f"gate {reason}", on_log)
            if reason == "wreck" or reason.startswith("reliability") or reason == "ec=0":
                call("abort_pad", ctx)
                raise MissionAbort(reason)
    result = recover_or_abort(vessel)
    _say(result, on_log)
    return result


def pad_craft_path(name: str | None = None) -> Path:
    nid = (name or CRAFT).strip()
    return REPO_CRAFTS / f"{nid}.craft"


def install_and_launch(session: object, *, recover: bool = True) -> None:
    """Hangar the Gus-signed file. Never generate pad_pbc over a named sit.

    Byte-copy ``crafts/<name>.craft`` — ``pad_pbc()`` has no Geiger Counter
    part (F-013). Template generate only for ``kspstuff-pad-pbc``.
    """
    from missions import pad_craft_name

    wanted = pad_craft_name()
    src = pad_craft_path(wanted)
    hangar = discover_hangar()
    if hangar is None:
        raise MissionAbort("KSP install not found (KSPSTUFF_KSP or ~/Games/KSP-rss)")
    if src.is_file():
        from hangar import install_signed
        from session import SessionError

        try:
            install_signed(
                session,
                wanted,
                hangar=hangar,
                recover=recover,
                src=src,
            )
        except SessionError as exc:
            raise MissionAbort(str(exc)) from exc
        return
    if wanted != TEMPLATE and TEMPLATE not in wanted:
        raise MissionAbort(
            f"missing pad craft {src} — do not pad_pbc() a {wanted} sit (F-013)"
        )
    from catalog import load_catalog
    from craft import pad_pbc

    catalog = load_catalog(hangar.ksp_root)
    craft = pad_pbc(TEMPLATE, catalog=catalog)
    hangar.install(craft, overwrite=True)
    hangar.launch(session, craft.name, recover=recover, uncrewed=True)


def run_pad(
    session: object,
    *,
    recover: bool = True,
    on_log: Callable[[str], None] | None = None,
    abort: Callable[[], bool] | None = None,
    events: EventLog | None = None,
) -> str:
    """Hangar + Kerbalism pad science. Probes are uncrewed."""
    pad_science_ids()
    log_events = events if events is not None else EventLog()
    install_and_launch(session, recover=recover)
    try:
        msg = wait_vessel_ready(session)
    except Exception as exc:
        raise MissionAbort(f"no vessel after launch: {exc}") from exc
    _say(msg, on_log)
    try:
        vessel = session.active_vessel  # type: ignore[attr-defined]
    except Exception as exc:
        raise MissionAbort(f"no vessel after launch: {exc}") from exc
    if vessel is None:
        raise MissionAbort("no vessel after launch")
    return run_on_vessel(
        session, vessel, events=log_events, on_log=on_log, abort=abort
    )


def run_phase(
    session: object,
    *,
    on_log: Callable[[str], None] | None = None,
    abort: Callable[[], bool] | None = None,
) -> str:
    """``phase pad``: already launched. No Hangar."""
    try:
        vessel = session.active_vessel  # type: ignore[attr-defined]
    except Exception:
        vessel = None
    if vessel is None:
        raise MissionAbort("no active vessel — python main.py pad to Hangar")
    return run_on_vessel(session, vessel, on_log=on_log, abort=abort)
