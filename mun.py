"""Pad compose: Hangar + ascent + Mun transfer/land.

Leftover crew flies ``python main.py phase``, not this. VAB ``capable: yes``
required for Hangar (L-039). One FlightWatch lives inside ``run_from_lko``.
"""

from __future__ import annotations

import logging
import time
from typing import Callable

from land import run_from_lko
from session import Session
from watch import MissionAbort, freeze, heartbeat

log = logging.getLogger("kspstuff")


def _say(msg: str, on_log: Callable[[str], None] | None) -> None:
    log.info(msg)
    if on_log:
        on_log(msg)


def run_mission(
    session: Session,
    *,
    recover: bool = True,
    on_log: Callable[[str], None] | None = None,
    abort: Callable[[], bool] | None = None,
    from_orbit: bool = False,
) -> None:
    """Pad → LKO → Mun, or continue the active vessel (from_orbit)."""
    from crew import apply_ascent, current_pilot
    from hangar import discover_hangar
    from launch import Ascent, AscentConfig
    from missions import pad_craft_name
    from session import SessionError
    from uplink import desk as _desk, save_plan

    person = current_pilot()
    style = person.style
    _say(
        f"Crew {person.name}  apo={style.target_altitude:.0f} "
        f"cap={style.energy_cap}",
        on_log,
    )
    _desk.plan["suicide_start"] = style.suicide_start_alt
    _desk.plan["parking_apo"] = style.target_altitude
    save_plan()

    if from_orbit:
        if session.active_vessel is None:
            raise MissionAbort("from-orbit: no active vessel")
        _say(f"Continue from orbit as {person.name}", on_log)
        heartbeat(session, on_log, tag="cont ")
        try:
            run_from_lko(
                session,
                on_log=on_log,
                abort=abort,
                suicide_start_alt=style.suicide_start_alt,
                from_orbit=True,
            )
        except MissionAbort:
            freeze(session)
            heartbeat(session, on_log, tag="abort ")
            raise
        return

    try:
        wanted = pad_craft_name()
    except SessionError:
        raise
    hangar = discover_hangar()
    if hangar is None:
        raise MissionAbort("KSP install not found (KSPSTUFF_KSP or ~/Games/KSP-rss)")
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
    seats = [person.kerbal] if person.kerbal else None
    hangar.launch(session, craft.name, recover=recover, crew=seats)
    time.sleep(2.0)
    heartbeat(session, on_log, tag="pad ")

    cfg = apply_ascent(
        AscentConfig(
            target_altitude=style.target_altitude,
            turn_start_altitude=style.turn_start_altitude,
            turn_end_altitude=style.turn_end_altitude,
            end_stage=1,
            circularize=True,
            max_q=style.max_q,
            energy_cap=style.energy_cap,
        ),
        style,
    )
    Ascent(session, cfg, on_log=on_log, abort=abort or (lambda: False)).run()
    try:
        run_from_lko(
            session,
            on_log=on_log,
            abort=abort,
            suicide_start_alt=style.suicide_start_alt,
        )
    except MissionAbort:
        freeze(session)
        heartbeat(session, on_log, tag="abort ")
        raise
