"""One flight segment per process. Gene plans between phases (L-036)."""

from __future__ import annotations

import math
from typing import Any, Callable

from session import Session
from uplink import desk, load_plan, plan_file, write_plan_file
from telem import MissionAbort
from watch import FlightWatch, heartbeat

NAMES = ("recover", "circularize", "tli", "soi", "capture", "land", "hop", "pad")


class OffPlan(Exception):
    """Phase finished but the envelope is not what Gene expected."""


def _kv() -> dict[str, str]:
    try:
        path = plan_file()
    except FileNotFoundError:
        return {}
    if not path.is_file():
        return {}
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, _, v = line.partition(":")
        out[k.strip().lower()] = v.strip()
    return out


def current_phase() -> str:
    name = _kv().get("phase", "").lower()
    if name in NAMES:
        return name
    return "recover"


def set_phase(name: str, *, next_name: str | None = None) -> None:
    load_plan()
    extra = {"phase": name}
    if next_name:
        extra["next"] = next_name
    write_plan_file(extra=extra)


def check_expect(state: Any, *, skip_peri: bool = False) -> None:
    kv = _kv()
    body = kv.get("expect_body", "")
    if body and str(getattr(state, "body", "")).lower() != body.lower():
        raise OffPlan(f"body {state.body} != {body}")
    if not skip_peri:
        try:
            pmin = float(kv["expect_peri_min"])
            if math.isfinite(state.peri) and state.peri < pmin:
                raise OffPlan(f"peri {state.peri:.0f} < {pmin:.0f}")
        except (KeyError, ValueError):
            pass
    try:
        amax = float(kv["expect_apo_max"])
        if math.isfinite(state.apo) and state.apo > amax:
            raise OffPlan(f"apo {state.apo:.0f} > {amax:.0f}")
    except (KeyError, ValueError):
        pass


def run(
    name: str,
    session: Session,
    *,
    on_log: Callable[[str], None] | None = None,
    abort: Callable[[], bool] | None = None,
) -> None:
    name = name.lower().strip()
    if name not in NAMES:
        raise MissionAbort(f"unknown phase {name}")
    load_plan()
    if name == "pad":
        from pad import run_phase

        run_phase(session, on_log=on_log, abort=abort)
        return
    vessel = session.active_vessel
    if vessel is None:
        if name == "hop":
            raise MissionAbort("no active vessel — python main.py hop to Hangar")
        raise MissionAbort("no active vessel")
    from land import run_from_lko
    from transfer import (
        _finish_tli,
        capture_at_periapsis,
        plan_mun_encounter,
        warp_to_soi,
    )
    from nodes import execute_node, plan_circularize_at_apoapsis
    from watch import recover_periapsis

    def _say(msg: str) -> None:
        if on_log:
            on_log(msg)

    _say(f"phase {name}")
    with FlightWatch(session, on_log=on_log, uplink=True) as watch:
        if name == "recover":
            recover_periapsis(
                session, extra=10_000.0, on_log=on_log, abort=abort, watch=watch
            )
        elif name == "circularize":
            plan_circularize_at_apoapsis(session, vessel)
            execute_node(session, vessel, abort=abort, on_log=on_log, watch=watch)
        elif name == "tli":
            plan_mun_encounter(session, vessel, on_log=on_log)
            execute_node(session, vessel, abort=abort, on_log=on_log, watch=watch)
            _finish_tli(session, vessel, watch=watch, abort=abort, on_log=on_log)
        elif name == "soi":
            warp_to_soi(
                session, vessel, on_log=on_log, abort=abort, watch=watch
            )
        elif name == "capture":
            capture_at_periapsis(
                session, vessel, on_log=on_log, abort=abort, watch=watch
            )
        elif name == "land":
            start = desk.plan.get("suicide_start", 25_000.0)
            run_from_lko(
                session,
                on_log=on_log,
                abort=abort,
                suicide_start_alt=start,
                from_orbit=True,
                watch=watch,
            )
        elif name == "hop":
            from hop import run_from_vessel

            result = run_from_vessel(
                session, on_log=on_log, abort=abort, watch=watch
            )
            if result == "recovered":
                _say("hop recovered")
                return
        heartbeat(session, on_log, tag=f"{name}-done ", watch=watch)
        check_expect(
            watch.pulse(f"{name} ", force_log=True),
            skip_peri=(name == "hop"),
        )
