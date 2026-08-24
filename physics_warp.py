"""Physics warp only. Rails always 0. Never WarpTo.

kRPC ``physics_warp_factor``: 0=1×, 1=2×, 2=3×, 3=4×.
Pad dwell and factory hop coast both call this. Do not drive
``rails_warp_factor`` other than 0. Do not call ``WarpTo``.

Launch laws (live 2026-08-23 warp-batch, revert-ok that sit only):

- Hangar / revert / light / pad boost / grim: **1×**, rails 0.
- ``run_physics`` after Hangar, after revert, and after light (unpause).
- Revert returns a ghost first (mass ~13 t). Wait until Hangar snapshot
  matches (mass/parts/stage) before staging. Stage 2→1 is the Valiant.
  A second ``activate_next_stage`` while stage already 1 is the chute.
- ``pre_launch`` MET does not tick. 3× on the clamps does not race MET.
- After loft, 4× coast. 1× through chute deploy (semi or below 2 km
  descending). 4× again once ``deployed``. Grim pins 1×. Recover is 1×.
- Valiant: stage 2→1 is the engine (chute stays stowed). A second
  ``activate_next_stage`` (1× or 3×) is RealChute **arm**, stage 0 —
  that is the whoosh. Arm/Deploy are module events; do not extra-stage.
  Revert restores stage 2; kRPC chute may stay ``armed``.
"""

from __future__ import annotations

import os
from typing import Callable

COAST_RATE = 4
PAD_RATE = 3
_MAX_RATE = 4


def coast_rate() -> int:
    """Coast × multiplier. ``KSPSTUFF_PHYS_WARP=1..4`` pins a test hop."""
    raw = (os.environ.get("KSPSTUFF_PHYS_WARP") or "").strip()
    if not raw:
        return COAST_RATE
    try:
        return min(max(int(raw), 1), _MAX_RATE)
    except ValueError:
        return COAST_RATE


def _sc(session: object) -> object | None:
    return getattr(session, "space_center", None)


def rails_zero(session: object) -> None:
    sc = _sc(session)
    if sc is None:
        return
    try:
        sc.rails_warp_factor = 0
    except Exception:
        pass


def set_factor(session: object, n: int) -> None:
    """``n`` is the kRPC factor (0=1× … 3=4×). Rails stay 0."""
    rails_zero(session)
    sc = _sc(session)
    if sc is None:
        return
    try:
        sc.physics_warp_factor = int(n)
    except Exception:
        pass


def set_rate(session: object, rate: int) -> int:
    """``rate`` is the × multiplier 1–4. Returns the kRPC factor."""
    rate = min(max(int(rate), 1), _MAX_RATE)
    factor = rate - 1
    set_factor(session, factor)
    return factor


def _say(msg: str, on_log: Callable[[str], None] | None) -> None:
    if on_log is not None:
        on_log(msg)


def apply_coast(
    session: object,
    *,
    coast: bool,
    on_log: Callable[[str], None] | None = None,
    last: list[str] | None = None,
    default_rate: int = COAST_RATE,
    uplink_rate: int | None = None,
) -> int:
    """Factory coast 2–4× after real burnout; 1× otherwise. Returns factor."""
    if not coast:
        set_factor(session, 0)
        _log_idle(on_log, last)
        return 0
    rate = default_rate if uplink_rate is None else int(uplink_rate)
    if rate <= 1:
        set_factor(session, 0)
        _log_idle(on_log, last)
        return 0
    rate = min(max(rate, 2), _MAX_RATE)
    factor = set_rate(session, rate)
    label = f"{rate}x"
    if last is not None and (not last or last[0] != label):
        _say(f"hop coast physics {rate}x rails=0", on_log)
        last[0] = label
    elif last is not None:
        last[0] = label
    return factor


def _log_idle(
    on_log: Callable[[str], None] | None, last: list[str] | None
) -> None:
    if last is None:
        return
    prev = last[0] if last else ""
    if prev and prev != "1x":
        _say("hop physics 1x", on_log)
    last[0] = "1x"
