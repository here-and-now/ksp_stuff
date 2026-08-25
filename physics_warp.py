"""Physics warp only. Rails always 0. Never WarpTo.

kRPC ``physics_warp_factor``: 0=1×, 1=2×, 2=3×, 3=4×.
Warp is a clock on sits, not a new flight. Lars composes
``hop_factory`` from these blocks. Forest / Grasslands: same function.

Sits:

- 1×: burn, chute_arm_sit, chute_deploy_sit, silk, recover, high q,
  thick air (≤18 km lid).
- Arm: descending (vz<0 / pitch down), lofted, thick air (≤18 km).
  Not light, not only 2 km, not 200 km vacuum (silk ~15 km). Clock is
  already 1× in thick air (15-10-47Z silk at 4× sheared 28→18).
- Deploy canopy: still ≤2 km or already semi.
- 4×: lofted coast after real burnout AND q actually low (≤1 kPa) AND
  not thick air. Quiet descent above thick air honors uplink. Not arm
  sit. Not silk.
- Never rails. Never WarpTo.
- Timeout budget is MET / down, not wall seconds while 1×.
- Airborne cannot-pay is a sit flag, not a dwell.
- Timeout leftover: recover() if recoverable else ksc leftover.
  Never revert.

Hangar ``run_physics`` is unpause + 1×. Living loft uses
``unpause_clock`` then ``apply_coast`` / ``apply_sit_warp``.
``pre_launch`` MET does not tick. Do not drive ``rails_warp_factor``
other than 0. Do not call ``WarpTo``.
"""

from __future__ import annotations

import math
import os
from typing import Callable

COAST_RATE = 4
PAD_RATE = 3
_MAX_RATE = 4
LOFT_ALT_M = 250.0
CHUTE_DEPLOY_ALT_M = 2_000.0
# 10-31-47Z 4× at burnout q≈29.5 kPa FAR-sheared. 17-26-04Z 4× at
# q≈4.7 kPa after FlyingHigh wait sheared 28→1. 47 km loft is q≈0.4 kPa.
# 06-57-16Z 4× after 18 km lid at ~3 km q=2.67 kPa sheared. 18 km is
# RSS FlyingHigh sit start, still thick.
COAST_Q_MAX_PA = 1_000.0
THICK_AIR_ALT_M = 18_000.0
CHUTE_OPEN = frozenset({"deployed", "semi_deployed", "semideployed"})
_SEMI = frozenset({"semi_deployed", "semideployed"})
_SILK = "deployed"


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


def unpause_clock(session: object) -> None:
    """paused=False. Do not touch physics_warp_factor — coast owns that.

    Hangar ``run_physics`` is unpause + 1×. A living loft after airborne
    cannot-pay must keep 2–4× after burnout.
    """
    krpc = getattr(getattr(session, "conn", None), "krpc", None)
    sc = _sc(session)
    for obj in (krpc, sc):
        if obj is None:
            continue
        try:
            obj.paused = False
        except Exception:
            pass
    rails_zero(session)


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


def _finite(snap: object, name: str) -> float:
    try:
        val = float(getattr(snap, name, float("nan")))
    except (TypeError, ValueError):
        return float("nan")
    return val if math.isfinite(val) else float("nan")


def chute_name(snap: object) -> str:
    raw = str(getattr(snap, "chute", "") or "").lower().replace("-", "_")
    return raw


def lofted_sit(snap: object) -> bool:
    """Alt well above the pad. sit=flying at pad alt is still boost."""
    alt = _finite(snap, "alt")
    return math.isfinite(alt) and alt > LOFT_ALT_M


def high_q_sit(snap: object) -> bool:
    """q above coast-safe (1 kPa). 1×. NaN is high (fail closed)."""
    q = _finite(snap, "q")
    if not math.isfinite(q):
        return True
    return q > COAST_Q_MAX_PA


def thick_air_sit(snap: object) -> bool:
    """18 km lid is still thick. 4× only above. Vacuum is not this sit.

    Unknown alt is thick (fail closed). ``in_atmo`` False (Mun) is not.
    """
    alt = _finite(snap, "alt")
    if not math.isfinite(alt):
        return True
    if alt > THICK_AIR_ALT_M:
        return False
    in_atmo = getattr(snap, "in_atmo", None)
    if in_atmo is False:
        return False
    return True


def _descending(snap: object) -> bool:
    """vz<0. If vz unknown, pitch down. Climbing is not this sit."""
    vz = _finite(snap, "v_vert")
    if math.isfinite(vz):
        return vz < 0.0
    pitch = _finite(snap, "pitch")
    return math.isfinite(pitch) and pitch < 0.0


def chute_arm_sit(snap: object) -> bool:
    """Arm on descent after loft in thick air. Not light. Not only 2 km.

    11-11-37Z lithobrake 2.9 km q=5.7 kPa still stowed: deploy sit is
    2 km, so Arm never ran. T-338 whoosh is first-airborne Arm.
    T-442 200 km vacuum descent is not Arm (silk ~15 km).
    """
    alt = _finite(snap, "alt")
    if not math.isfinite(alt) or alt <= LOFT_ALT_M:
        return False
    if not thick_air_sit(snap):
        return False
    return _descending(snap)


def chute_deploy_sit(snap: object) -> bool:
    """Canopy: descending below 2 km, or already semi. Independent of skip."""
    if chute_name(snap) in _SEMI:
        return True
    alt = _finite(snap, "alt")
    return (
        _descending(snap)
        and math.isfinite(alt)
        and 0.0 < alt <= CHUTE_DEPLOY_ALT_M
    )


def airborne_cannot_pay(
    *,
    lofted: bool,
    down: bool,
    started: list[str] | tuple[str, ...],
    science_attempted: bool,
    waiting_hd: bool,
) -> bool:
    """Airborne skip is a sit flag, not a dwell. Same inland hop as paying loft.

    Keep lofting until down; then land leftover starts. Not hop-down
    while still flying.
    """
    return bool(
        science_attempted
        and not started
        and lofted
        and not down
        and not waiting_hd
    )


def want_coast(
    snap: object,
    *,
    left_pad: bool,
    down: bool,
    burning: bool,
) -> bool:
    """4× lofted coast after real burnout AND q actually low (≤1 kPa)
    AND not thick air (≤18 km).

    1×: pad, burn, chute_arm_sit, chute_deploy_sit, silk, recover,
    high q, thick air. Unknown q is not coast-safe. 18 km lid is still
    thick. Climbing armed may still 4× above thick air. Quiet descent
    above thick air honors uplink (T-442). Never rails.
    """
    if not left_pad or down or burning:
        return False
    if not lofted_sit(snap):
        return False
    if thick_air_sit(snap):
        return False
    if high_q_sit(snap):
        return False
    if chute_arm_sit(snap) or chute_deploy_sit(snap):
        return False
    st = chute_name(snap)
    if st == _SILK or st in _SEMI:
        return False
    return True


def apply_sit_warp(
    session: object,
    snap: object,
    *,
    left_pad: bool,
    down: bool,
    burning: bool,
    on_log: Callable[[str], None] | None = None,
    last: list[str] | None = None,
    default_rate: int | None = None,
    uplink_rate: int | None = None,
) -> int:
    """Keep the clock; 4× only when ``want_coast``. Unpause is not 1×.

    Skip or paying loft: same path. Do not Hangar ``run_physics`` here.
    """
    unpause_clock(session)
    rate = coast_rate() if default_rate is None else int(default_rate)
    return apply_coast(
        session,
        coast=want_coast(
            snap, left_pad=left_pad, down=down, burning=burning
        ),
        on_log=on_log,
        last=last,
        default_rate=rate,
        uplink_rate=uplink_rate,
    )


def met_elapsed(met: float | None, met0: float | None) -> float:
    """Physics seconds since ``met0`` (light). NaN if unknown."""
    if met is None or met0 is None:
        return float("nan")
    try:
        now = float(met)
        start = float(met0)
    except (TypeError, ValueError):
        return float("nan")
    if not (math.isfinite(now) and math.isfinite(start)):
        return float("nan")
    return max(0.0, now - start)


def timeout_hit(
    *,
    met: float | None,
    met0: float | None,
    budget: float,
    down: bool,
) -> bool:
    """MET budget gone and not already down. Wall at 1× while MET is frozen does not count."""
    if down:
        return False
    elapsed = met_elapsed(met, met0)
    try:
        cap = float(budget)
    except (TypeError, ValueError):
        return False
    if not math.isfinite(elapsed) or not math.isfinite(cap):
        return False
    return elapsed >= cap


def leftover_call(*, recoverable: bool) -> str:
    """Timeout leftover. Never revert."""
    if recoverable:
        return "recover"
    return "ksc leftover"


def leftover_ksc_call(recoverable: bool) -> str:
    """Hank leftover CLI. Never leftover-ksc load. Never revert."""
    if recoverable:
        return "python main.py recover-probe --recover"
    return "python main.py recover-probe --space-center"


def leftover_abort_kv(*, sit: str, recoverable: bool) -> tuple[str, str, str, str]:
    """Four kv lines hop abort prints. Recover is Hank's, not the pulse."""
    rec_s = "yes" if recoverable else "no"
    call = leftover_ksc_call(recoverable)
    return (
        "ksc: leftover",
        f"sit: {sit or '?'}",
        f"recoverable: {rec_s}",
        f"call: {call}",
    )


def leftover_abort_why(*, sit: str, recoverable: bool, why: str = "") -> str:
    """MissionAbort text. Never revert."""
    rec_s = "yes" if recoverable else "no"
    call = leftover_ksc_call(recoverable)
    extra = f" {why}" if why else ""
    return f"ksc leftover sit={sit or '?'} recoverable={rec_s} call: {call}{extra}"
