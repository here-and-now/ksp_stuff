"""Time warp helpers.

Do not call ``SpaceCenter.warp_to`` in a loop. Each call ramps 1× → max
and drops to 1× when it returns, so 20 min chunks look like a warp cycle
(L-020). Hold ``rails_warp_factor`` at the altitude cap, heartbeat on
wall-clock, step down so we do not overshoot the UT.

Rails rate is also altitude-capped (observed stock Kerbin: 194 km →
factor 4 / 100×; 250 km → 5 / 1000×; 800 km → 7).
"""

from __future__ import annotations

import logging
import math
import time
from typing import Any, Callable

from session import Session

log = logging.getLogger("kspstuff")

# Observed stock Kerbin: maximum_rails_warp_factor vs mean altitude.
# Wiki bands differ slightly; trust these until re-measured.
KERBIN_RAILS_ALTITUDE: tuple[tuple[float, int], ...] = (
    (0.0, 3),
    (100_000.0, 4),
    (250_000.0, 5),
    (750_000.0, 6),
    (1_500_000.0, 7),
)

# Stock on-rails multipliers for factor 0..7.
_RAILS_RATE = (1.0, 5.0, 10.0, 50.0, 100.0, 1_000.0, 10_000.0, 100_000.0)


def in_atmosphere(vessel: Any) -> bool:
    body = vessel.orbit.body
    try:
        if not body.has_atmosphere:
            return False
        return float(vessel.flight().mean_altitude) < float(body.atmosphere_depth)
    except Exception:
        return False


def drop_warp(session: Session) -> None:
    sc = session.space_center
    try:
        sc.rails_warp_factor = 0
        sc.physics_warp_factor = 0
    except Exception:
        pass


def _factor_for(remaining: float, max_factor: int) -> int:
    """Highest rails factor that leaves ~2 s wall-clock before ``remaining``."""
    want = 0
    cap = max(0, min(int(max_factor), 7))
    for factor in range(0, cap + 1):
        if remaining > _RAILS_RATE[factor] * 2.0:
            want = factor
    return want


def warp_to_ut(
    session: Session,
    ut: float,
    *,
    abort: Callable[[], bool] | None = None,
    chunk_s: float = 1_200.0,
    on_tick: Callable[[], None] | None = None,
    watch: Any | None = None,
    stop_if: Callable[[], bool] | None = None,
) -> None:
    """Hold max legal rails until near ``ut``. Heartbeat each wall-clock second.

    ``chunk_s`` is unused (L-020); kept so callers do not break.

    Rails are illegal while *currently* in atmosphere (L-005/L-012).
    Coast at 1× until out, then warp — do not abort a future node just
    because the ship is in the air at peri (L-019).

    Airless close peri: cap rails at 50× (L-023). High warp toward a Mun
    Pe punches the patched conic through the surface. ``stop_if`` returns
    early so the caller can burn; a frozen UT is a wreck.
    """
    del chunk_s
    from watch import MissionAbort, heartbeat

    sc = session.space_center
    target = float(ut)
    last_hb = 0.0
    last_factor: int | None = None
    last_ut = float(sc.ut)
    stuck_since = time.monotonic()

    def tick() -> None:
        nonlocal last_hb
        now = time.monotonic()
        if now - last_hb < 1.0:
            return
        last_hb = now
        if on_tick is not None:
            on_tick()
            return
        try:
            heartbeat(session, tag="warp ", watch=watch)
        except MissionAbort:
            raise
        except Exception:
            log.info("warp UT+%.0f s", target - sc.ut)

    try:
        while sc.ut < target - 1.0:
            if abort and abort():
                raise MissionAbort("warp aborted")
            from uplink import holding, skip_warp as uplink_skip_warp

            if holding():
                drop_warp(session)
                last_factor = 0
                tick()
                time.sleep(0.5)
                continue
            if uplink_skip_warp():
                drop_warp(session)
                return
            if stop_if is not None:
                try:
                    if stop_if():
                        return
                except MissionAbort:
                    raise
                except Exception:
                    pass
            in_atmo = False
            peri = float("nan")
            airless = False
            alt = float("nan")
            try:
                vessel = session.active_vessel
                in_atmo = in_atmosphere(vessel)
                body = vessel.orbit.body
                airless = not bool(body.has_atmosphere)
                peri = float(vessel.orbit.periapsis_altitude)
                alt = float(vessel.flight().mean_altitude)
            except Exception:
                in_atmo = False
            # L-023: rails through an airless lithobrake peri.
            if airless and math.isfinite(peri) and peri < 0.0:
                drop_warp(session)
                if math.isfinite(alt) and alt < 25_000:
                    raise MissionAbort(f"lithobrake peri={peri:.0f} alt={alt:.0f}")
                return
            if in_atmo:
                if last_factor != 0:
                    drop_warp(session)
                    last_factor = 0
                try:
                    heartbeat(session, tag="warp-atmo ", watch=watch)
                except Exception:
                    log.info("warp waiting out atmosphere")
                time.sleep(1.0)
                continue

            now_ut = float(sc.ut)
            if now_ut > last_ut + 0.05:
                last_ut = now_ut
                stuck_since = time.monotonic()
            elif time.monotonic() - stuck_since > 8.0:
                drop_warp(session)
                raise MissionAbort(f"warp UT frozen at {now_ut:.0f}")

            remaining = target - now_ut
            try:
                cap = int(sc.maximum_rails_warp_factor)
            except Exception:
                cap = 4
            if airless and math.isfinite(peri) and peri < 80_000:
                cap = min(cap, 3)
            want = _factor_for(remaining, cap)
            if want != last_factor:
                try:
                    if want > 0 and hasattr(sc, "can_rails_warp_at"):
                        while want > 0 and not sc.can_rails_warp_at(want):
                            want -= 1
                    sc.rails_warp_factor = want
                    last_factor = want
                except Exception:
                    log.debug("rails_warp_factor=%s failed", want, exc_info=True)
                    last_factor = None

            tick()
            time.sleep(0.25 if want <= 3 else 1.0)
    finally:
        drop_warp(session)
