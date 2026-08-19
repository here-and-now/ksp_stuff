"""Pad compose: Hangar + Kerbin sounding. Not Mun.

``python main.py hop`` Hangars (VAB ``capable: yes``). Leftover crew
flies ``python main.py phase hop``. One FlightWatch. EVA is briefing only.
"""

from __future__ import annotations

import logging
import math
import time
from typing import Callable

from launch import Ascent, AscentConfig
from science import HOP_EXPERIMENTS, run_ready
from session import Session
from watch import FlightWatch, MissionAbort, apply_hold, freeze

log = logging.getLogger("kspstuff")

HOP_APO_DEFAULT = 15_000.0
HOP_APO_CLAMP = (8_000.0, 25_000.0)
_PAD = frozenset({"pre_launch", "prelaunch"})
_DOWN = frozenset({"landed", "splashed"})
_AIR = frozenset({"flying", "sub_orbital", "suborbital"})


def _say(msg: str, on_log: Callable[[str], None] | None) -> None:
    log.info(msg)
    if on_log:
        on_log(msg)


def _sit(vessel) -> str:
    try:
        value = vessel.situation
        name = getattr(value, "name", None)
        if isinstance(name, str):
            return name.lower().replace("-", "_")
        return str(value).rsplit(".", 1)[-1].lower().replace("-", "_")
    except Exception:
        return "?"


def hop_target_apo() -> float:
    lo, hi = HOP_APO_CLAMP
    raw = ""
    try:
        from phases import _kv

        raw = _kv().get("hop_apo", "")
    except Exception:
        raw = ""
    try:
        value = float(raw)
    except (TypeError, ValueError):
        value = HOP_APO_DEFAULT
    return min(hi, max(lo, value))


def hop_ascent_config() -> AscentConfig:
    apo = hop_target_apo()
    max_q = 40_000.0
    try:
        from crew import current_pilot

        max_q = current_pilot().style.max_q
    except Exception:
        pass
    return AscentConfig(
        target_altitude=apo,
        turn_start_altitude=8_000.0,
        turn_end_altitude=max(18_000.0, apo),
        end_stage=0,
        circularize=False,
        max_q=max_q,
        energy_cap=1.15,
    )


def _install_pad_craft(
    session: Session,
    on_log: Callable[[str], None] | None,
    *,
    recover: bool = True,
) -> None:
    import os

    from hangar import Hangar, discover_ksp
    from missions import pad_craft_name

    wanted = pad_craft_name()
    root = discover_ksp()
    if root is None:
        raise MissionAbort("KSP install not found (KSPSTUFF_KSP / Steam path)")
    hangar = Hangar(ksp_root=root, save=os.environ.get("KSPSTUFF_SAVE") or "Grok")
    from craft import TEMPLATES

    key = wanted.replace("kspstuff-", "").replace("_", "-")
    factory = TEMPLATES.get(key) or TEMPLATES.get(wanted)
    if factory is not None:
        craft = factory()
        if wanted.startswith("kspstuff-") or wanted != craft.name:
            craft.name = wanted if wanted.startswith("kspstuff-") else craft.name
    else:
        try:
            craft = hangar.load_craft(wanted)
        except Exception as exc:
            raise MissionAbort(f"no craft {wanted}: {exc}") from exc
    hangar.install(craft, overwrite=True)
    _say(f"Installed {craft.name} ({len(craft.parts)} parts)", on_log)
    from crew import current_pilot

    person = current_pilot()
    seats = [person.kerbal] if person.kerbal else None
    hangar.launch(session, craft.name, recover=recover, crew=seats)
    time.sleep(2.0)


def _arm_chutes(vessel) -> int:
    n = 0
    try:
        chutes = list(vessel.parts.parachutes)
    except Exception:
        return 0
    for chute in chutes:
        try:
            chute.arm()
            n += 1
        except Exception:
            continue
    return n


def _deploy_chutes(vessel) -> int:
    n = 0
    try:
        chutes = list(vessel.parts.parachutes)
    except Exception:
        return 0
    for chute in chutes:
        try:
            if not chute.deployed:
                chute.deploy()
                n += 1
        except Exception:
            try:
                chute.arm()
                n += 1
            except Exception:
                continue
    return n


def _refuse_orbit(vessel) -> None:
    sit = _sit(vessel)
    if sit in _PAD | _DOWN | _AIR:
        return
    try:
        peri = float(vessel.orbit.periapsis_altitude)
        atm = float(vessel.orbit.body.atmosphere_depth)
    except Exception:
        return
    if math.isfinite(peri) and math.isfinite(atm) and peri > atm:
        raise MissionAbort("hop is Kerbin sounding, not orbit")


def _science(vessel, on_log: Callable[[str], None] | None, tag: str) -> None:
    ran = run_ready(vessel, names=HOP_EXPERIMENTS, on_log=on_log)
    if ran:
        _say(f"hop {tag} {','.join(ran)}", on_log)
    else:
        _say(f"hop {tag} (none)", on_log)


def _wait_down(
    session: Session,
    watch: FlightWatch,
    *,
    abort: Callable[[], bool] | None,
    on_log: Callable[[str], None] | None,
) -> None:
    from uplink import holding

    vessel = session.active_vessel
    if vessel is None:
        raise MissionAbort("no active vessel")
    watch.enable_landing()
    armed = False
    opened = False
    while not (abort and abort()):
        state = watch.pulse("hop ")
        if holding():
            apply_hold(session)
            continue
        sit = (state.situation or "").lower().replace("-", "_")
        if sit in _DOWN:
            return
        if not armed:
            n = _arm_chutes(vessel)
            armed = True
            _say(f"chutes armed {n}", on_log)
        falling = state.heading_to_peri or (
            math.isfinite(state.vs) and state.vs < 0.0
        )
        low = math.isfinite(state.surf) and state.surf < 5_000.0
        if falling and low and not opened:
            n = _deploy_chutes(vessel)
            opened = True
            _say(f"chutes deploy {n}", on_log)
    raise MissionAbort("hop descent aborted")


def _recover_or_freeze(
    session: Session,
    *,
    on_log: Callable[[str], None] | None,
) -> str:
    vessel = session.active_vessel
    if vessel is None:
        return "recovered"
    rec = False
    try:
        rec = bool(vessel.recoverable)
    except Exception:
        rec = False
    if rec:
        _say("recover pod", on_log)
        try:
            vessel.recover()
            time.sleep(1.0)
            return "recovered"
        except Exception as exc:
            _say(f"recover failed: {exc}", on_log)
    freeze(session)
    _say("hop freeze", on_log)
    return "freeze"


def run_from_vessel(
    session: Session,
    *,
    on_log: Callable[[str], None] | None = None,
    abort: Callable[[], bool] | None = None,
    watch: FlightWatch | None = None,
) -> str:
    """Sounding on the active vessel. No Hangar."""
    vessel = session.active_vessel
    if vessel is None:
        raise MissionAbort("no active vessel — python main.py hop to Hangar")
    _refuse_orbit(vessel)
    sit = _sit(vessel)
    _say(f"hop sit={sit} apo={hop_target_apo():.0f}", on_log)
    own = watch is None
    if own:
        watch = FlightWatch(session, extra=5_000.0, on_log=on_log, uplink=True)
    try:
        if sit in _DOWN:
            return _recover_or_freeze(session, on_log=on_log)
        if sit in _PAD:
            _science(vessel, on_log, "pad")
        if sit in _PAD | _AIR:
            Ascent(
                session,
                hop_ascent_config(),
                on_log=on_log,
                abort=abort or (lambda: False),
                watch=watch,
            ).run()
            vessel = session.active_vessel
            if vessel is not None:
                _science(vessel, on_log, "fly")
            _wait_down(session, watch, abort=abort, on_log=on_log)
        return _recover_or_freeze(session, on_log=on_log)
    finally:
        if own and watch is not None:
            watch.close()


def run_pad(
    session: Session,
    *,
    recover: bool = True,
    on_log: Callable[[str], None] | None = None,
    abort: Callable[[], bool] | None = None,
) -> str:
    """Hangar + sounding. VAB capable. Do not Hangar over leftover crew."""
    from crew import current_pilot
    from missions import pad_kerbal_available
    from watch import heartbeat

    person = current_pilot()
    _say(f"Crew {person.name} hop apo={hop_target_apo():.0f}", on_log)
    pad_kerbal_available(session)
    _install_pad_craft(session, on_log, recover=recover)
    from missions import assert_seated

    assert_seated(session)
    heartbeat(session, on_log, tag="pad ")
    with FlightWatch(session, extra=5_000.0, on_log=on_log, uplink=True) as watch:
        return run_from_vessel(
            session, on_log=on_log, abort=abort, watch=watch
        )
