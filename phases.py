"""One flight segment per process. Gene names only ``NAMES``.

Unknown names abort — Lars writes the block. Factory hop is ``hop``.
Orbit stacks are ``python main.py ascent`` (not a Gene ``NAMES`` phase).
``hop-to-water`` / ``hop-splash`` are retired Gene names; loops stay in
``hop.py`` and the matching ``python main.py`` commands.
"""

from __future__ import annotations

import math
from typing import Any, Callable

from session import Session
from telem import MissionAbort
from uplink import load_plan, plan_file, write_plan_file

NAMES = ("pad", "hop", "splash", "tech-unlock")
UNCREWED = frozenset(NAMES)


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
    return "pad"


def set_phase(name: str, *, next_name: str | None = None) -> None:
    load_plan()
    extra = {"phase": name}
    if next_name:
        extra["next"] = next_name
    write_plan_file(extra=extra)


def check_expect(
    state: Any, *, skip_peri: bool = False, skip_apo: bool = False
) -> None:
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
    if skip_apo:
        return
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
        raise MissionAbort(
            f"unknown phase {name} — not in blocks.md; Lars writes the block"
        )
    load_plan()
    if name == "pad":
        from pad import run_phase

        run_phase(session, on_log=on_log, abort=abort)
        return
    if name == "hop":
        from hop import run_phase as run_hop_phase

        run_hop_phase(session, on_log=on_log, abort=abort)
        return
    if name == "splash":
        from splash import run_phase as run_splash_phase

        run_splash_phase(session, on_log=on_log, abort=abort)
        return
    if name in {"tech-unlock", "tech_unlock"}:
        from tech_unlock import run_phase as run_tech_unlock

        run_tech_unlock(session, on_log=on_log, abort=abort)
        return
    raise MissionAbort(f"unwired phase {name}")
