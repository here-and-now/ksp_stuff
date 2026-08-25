"""Sounding block: shared helpers + parked hop-to-water / hop-splash.

Factory inland (``python main.py hop``) lives in hop_factory. Coast
physics 2–4× lives in physics_warp. Sit/biome Toggle lives in science.

Helpers name sit: lofted, burning, landed, splashed, recoverable.
Unmanned deaf (known no radio) zeros the stick; pad-light aborts.
Burnout is fuel gone, or throttle 0 after loft well above the pad.
A 0-tick on the pad with a full tank is still burning — do not hop-down
that pad boost. Hold AP through burnout; do not rewrite fuel=0.

Hangar the seated / VAB ``.craft`` uncrewed (Hammer sit:
``kspstuff-hop-hammer-pbc``; not pad/geiger). Light, start the
Kerbalism **bound** flying card once airborne (FlyingLow) or at alt ≥50 km
(FlyingHigh — one Toggle). After ``left_pad``, yaw **10°** off zenith
heading **270**, then **25°** inland. Point ``set_direction_and_up``
north up; engage once off zenith; re-point if flipped while burning;
write ``target_direction``. Recover when landed/splashed/wreck-recoverable
— or EC=0 with HD data. Unmatched leftover aborts ``ksc leftover``.
Empty pad still Hangars. Disk PRELAUNCH is a lie — gate live sit/fuel/
recoverable before light.

Parked ``hop-to-water``: slew 25° east after pad at throttle 0.4; latch
``hop_apo``; leftover LF is a suicide burn near Water (watch TTI ≤12,
light at 3.5, kill until vz ≥ −10, hover TWR≈1 until coast ≤ Goo 12).
Parked ``hop-splash``: vertical, no east slew, ``hop_apo`` stays cut,
wait ``sit=splashed``. Mk16: ``arm_chutes`` airborne, ``deploy_chutes``
on descent below 2 km (vz < 0). FAR mass/parts drop beyond propellant
is shear. parts/mass 0 after loft is kRPC death. Frozen MET + flying
q=0 is crash UI.
"""

from __future__ import annotations

import logging
import math
import time
from pathlib import Path
from typing import Callable, NoReturn

from card import NO_BOUND_CARD, card_flying_ids, card_splash_ids, parse_card
from emergencies import Ctx, call
from hangar import (
    discover_hangar,
    game_scene,
    go_flight,
    go_space_center,
    run_physics,
    wait_vessel_ready,
)
from pad import arm_chutes, deploy_chutes, recover_or_abort
from physics_warp import (
    CHUTE_DEPLOY_ALT_M,
    CHUTE_OPEN as _CHUTE_OPEN,
    COAST_RATE,
    apply_coast,
    chute_deploy_sit,
    coast_rate,
    leftover_abort_kv,
    leftover_abort_why,
    leftover_ksc_call,
    set_factor as _physics_factor,
    want_coast,
)
from science import (
    card_has_data,
    card_slots,
    ground_card_done,
    hd_has_data,
    iter_science_modules,
    paying_eids,
    sit_matches,
    start_experiments,
    stop_experiments,
)
from screenshot import mission_event
from telem import EventLog, MissionAbort, Telem, gates, pulse_s as telem_pulse_s
from uplink import phys_warp_rate, take

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
# Mk16: arm airborne. Deploy / silk / coast clock live in physics_warp.
# kRPC armed is not a canopy.
# kRPC physics_warp_factor: 0=1×, 1=2×, 2=3×, 3=4×. Never rails. Never WarpTo.
# Coast and silk cruise default 4× (1× through deploy). Pin with KSPSTUFF_PHYS_WARP.
HOP_COAST_PHYS_RATE = COAST_RATE
# Structure gone, not propellant: mass drop ≥40% well beyond fuel burned.
SHEAR_MASS_FRAC = 0.40
SHEAR_MASS_SLACK_KG = 80.0
SHEAR_FUEL_KG = 2.5
_PULSE_S = 1.0
# Splash still counts pulses. Hop recover uses wall seconds (20 Hz
# near-ground Close can land in a fraction of a cruise pulse).
_STILL_N = 5
_STILL_S = 5.0
_UNPAUSE_SETTLE_S = 2.0
_STILL_MET = 0.2
_AIR = frozenset({"flying", "sub_orbital", "suborbital", "escaping", "orbiting"})
_GROUND = frozenset({"landed", "splashed", "wrecked", "wreck"})
_PAD_SIT = frozenset({"pre_launch", "prelaunch"})
_LIGHT_SIT = frozenset({"pre_launch", "prelaunch", "landed"})
_ABORT_UPLINK = frozenset({"abort_pad", "abort", "hold", "freeze", "recover"})
# Extra-stage is hop's. Science/transmit are Gene radio (Kerbalism events).
_UPLINK_SKIP = frozenset({"stage"})
# After left_pad: yaw 10° off zenith heading 270, then 25° inland.
# Do not slam 65 at light. Point set_direction_and_up (north up).
# Engage once off zenith. Re-point if flipped while burning; write
# target_direction. Do not rewrite fuel=0. Not hop-to-water 090.
# Hop-to-water slews 25° east after pad at throttle 0.4.
WATER_PITCH_FROM_UP = 25.0
WATER_PITCH_UP = 90.0
WATER_PITCH_DEG = WATER_PITCH_UP - WATER_PITCH_FROM_UP
WATER_PITCH_SLEW_DPS = 10.0
WATER_SLEW_THROTTLE = 0.4
WATER_HEADING_DEG = 90.0
INLAND_HEADING_DEG = 270.0
INLAND_PITCH_FROM_UP = WATER_PITCH_FROM_UP
INLAND_PITCH_DEG = WATER_PITCH_UP - INLAND_PITCH_FROM_UP
INLAND_YAW_FROM_UP = 10.0
INLAND_YAW_PITCH_DEG = WATER_PITCH_UP - INLAND_YAW_FROM_UP
INLAND_HEADING_CAPTURE_DEG = 20.0
INLAND_YAW_MET_S = 6.0
# Surface frame x=up y=north z=east. North is off the 270/090 path,
# so roll stays defined through the vertical (kRPC 0.6).
SURFACE_NORTH = (0.0, 1.0, 0.0)
# Latch hop_apo. Leftover LF is a suicide burn near Water, not apo-1 recut.
# Watch TTI ≤12; first throttle 1 at live TTI ≤ ~3.5. Kill until vz ≥ −10
# is seen. Hover TWR≈1 until coast ≤ Goo 12. TTI rising is not recut.
# Crumbs (fuel ≤2) are not a relight. spent only if coast impact ≤12.
GOO_CRASH_MS = 12.0
WATER_BRAKE_G = 9.81
WATER_BRAKE_TTI_S = 12.0
WATER_BRAKE_LIGHT_TTI_S = 3.5
WATER_BRAKE_LIGHT_PAD_M = 40.0
WATER_BRAKE_ALT_MAX_M = 8_000.0
WATER_BRAKE_SPEED_M = 40.0
WATER_BRAKE_VZ_CUT = -10.0
WATER_BRAKE_HOVER_THROTTLE = 0.25
WATER_BRAKE_FUEL_MIN = 2.0
WATER_BRAKE_HZ = 20.0
WATER_BRAKE_GATE_S = 60.0
WATER_CRAFT = "kspstuff-hop-valiant-east-pbc"


def _say(msg: str, on_log: Callable[[str], None] | None) -> None:
    log.info(msg)
    if on_log:
        on_log(msg)


def _nap_dt(
    requested: float | None,
    snap: object,
    *,
    braking: bool = False,
) -> float:
    """``pulse=None`` (production) follows telem.pulse_s; tests pass 1.0.

    Braking stays 20 Hz while leftover LF is still on.
    """
    if requested is not None:
        return requested
    if braking:
        return 1.0 / WATER_BRAKE_HZ
    try:
        return float(telem_pulse_s(snap))
    except Exception:
        return _PULSE_S


def bound_card_is_flying_high(
    tickets: list[object],
    *,
    flying_ids: tuple[str, ...] = (),
) -> bool | None:
    """True if a bound flying ticket is FlyingHigh.

    Unbound leftover High (``wait_experiment_id``, no ``experiment_id``)
    is not a 50 km lid. None if there is no bound flying card.
    """
    want = {str(e).strip() for e in flying_ids if str(e).strip()}
    if not want:
        return None
    for raw in tickets:
        if not isinstance(raw, dict):
            continue
        t = raw
        if t.get("type") != "science" and t.get("category") != "science_opportunity":
            continue
        pl = t.get("payload") or {}
        if not isinstance(pl, dict):
            continue
        eid = str(pl.get("experiment_id") or pl.get("eid") or "").strip()
        if eid not in want:
            continue
        sit = str(pl.get("situation") or "").lower().replace(" ", "").replace("_", "")
        if "flyinghigh" in sit:
            return True
    return False


def hop_wants_flying_high() -> bool:
    """Bound flying card is FlyingHigh. Missing / FlyingLow is airborne Toggle."""
    try:
        import sys

        from tickets import list_tickets, science_ids_for

        if "unittest" not in sys.modules:
            ids = science_ids_for(situation="flying")
            got = bound_card_is_flying_high(
                list_tickets(open_only=True), flying_ids=ids
            )
            if got is not None:
                return got
    except Exception:
        pass
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


def hop_science_alt() -> float:
    """Toggle lid (m). FlyingLow airborne (0); FlyingHigh ≥50 km."""
    return FLYING_LOW_M if hop_wants_flying_high() else 0.0


def hop_target_apo(*, space: bool | None = None) -> float:
    """Gene ``hop_apo`` (m). FlyingLow clamp 8–18 km; FlyingHigh / hop-splash to Space."""
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
    loft = hop_wants_flying_high() if space is None else bool(space)
    lo, hi = HOP_APO_CLAMP
    if loft:
        hi = FLYING_HIGH_M
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
    """Flying experiments. Bound tickets union fly science_ids; science.md legacy."""
    from tickets import card_science_ids, seated_fly_ticket

    try:
        fly = seated_fly_ticket()
    except Exception:
        fly = None
    ids = card_science_ids(situation="flying", ticket=fly)
    if ids:
        return ids
    from missions import seated_science_path

    path = seated_science_path()
    if not path.is_file():
        raise MissionAbort(NO_BOUND_CARD)
    ids = card_flying_ids(path.read_text(encoding="utf-8"))
    if not ids:
        raise MissionAbort(NO_BOUND_CARD)
    return ids


def hop_landed_science_ids(
    live_sit: str = "",
    live_biome: str = "",
) -> tuple[str, ...]:
    """Bound SrfLanded / SrfSplashed leftover. Empty is not a miss — flying card may still pay.

    Live sit keeps Forest land vs splash: SrfLanded@Forest pays landed, not flying.
    """
    from tickets import science_ids_for, union_science_ids

    try:
        ids = union_science_ids(
            science_ids_for(situation="landed"),
            science_ids_for(situation="splash"),
        )
    except Exception:
        return ()
    if not ids or not (live_sit or live_biome):
        return ids
    need = bound_science_need(live_sit=live_sit, live_biome=live_biome)
    return tuple(
        eid
        for eid in ids
        if sit_matches(live_sit, live_biome, *(need.get(eid, ("", ""))))
    )


def bound_science_need(
    live_sit: str = "",
    live_biome: str = "",
    *,
    alt: float = float("nan"),
) -> dict[str, tuple[str, str]]:
    """eid → (situation, biome) from bound science tickets.

    Prefer the bound ticket that can pay live sit (land vs splash).
    First seq is a reject sentinel when live sit is empty or no ticket
    matches (airborne skip still cannot-pay a SrfLanded pin).
    FlyingHigh vs live flying uses alt ≥50 km.
    """
    out: dict[str, tuple[str, str]] = {}
    rows: list[tuple[int, str, str, str]] = []
    try:
        from tickets import list_tickets, science_is_catalog

        for raw in list_tickets(open_only=True):
            if not isinstance(raw, dict):
                continue
            if raw.get("type") != "science" and raw.get("category") != "science_opportunity":
                continue
            if science_is_catalog(raw):
                continue
            pl = raw.get("payload") or {}
            if not isinstance(pl, dict):
                continue
            eid = str(pl.get("experiment_id") or pl.get("eid") or "").strip()
            if not eid:
                continue
            sit = str(pl.get("situation") or "").strip()
            biome = str(pl.get("biome") or "").strip()
            if not biome and "@" in sit:
                biome = sit.split("@", 1)[1].strip()
            try:
                seq = int(pl.get("seq", 100))
            except (TypeError, ValueError):
                seq = 100
            rows.append((seq, eid, sit, biome))
    except Exception:
        return out
    rows.sort()
    first: dict[str, tuple[str, str]] = {}
    match: dict[str, tuple[str, str]] = {}
    for _seq, eid, sit, biome in rows:
        if eid not in first:
            first[eid] = (sit, biome)
        if eid in match:
            continue
        if (live_sit or live_biome) and sit_matches(
            live_sit, live_biome, sit, biome, alt=alt
        ):
            match[eid] = (sit, biome)
    first.update(match)
    return first


def _snap_biome(snap: object, vessel: object | None) -> str:
    bio = str(getattr(snap, "biome", "") or "")
    if bio:
        return bio
    if vessel is None:
        return ""
    return str(getattr(vessel, "biome", "") or "")


def _live_sit(vessel: object, snap: object) -> str:
    """kRPC vessel sit wins over snap (land vs splash).

    Ground snap beats a lagging flying vessel so splash leftover still
    sit-matches before recover.
    """
    sit = _vessel_sit(vessel)
    snap_sit = str(getattr(snap, "situation", "") or "")
    snap_l = snap_sit.lower()
    sit_l = sit.lower()
    snap_ground = "landed" in snap_l or "splash" in snap_l
    sit_ground = "landed" in sit_l or "splash" in sit_l
    if snap_ground and not sit_ground:
        return snap_sit
    if sit not in {"", "?"}:
        return sit
    return snap_sit


def _start_paying(
    vessel: object,
    names: tuple[str, ...] | list[str],
    snap: object,
    on_log: Callable[[str], None] | None,
    need: dict[str, tuple[str, str]],
) -> list[str]:
    """Start only slots that can pay this sit/biome. Empty = skip, not abort."""
    sit = _live_sit(vessel, snap)
    biome = _snap_biome(snap, vessel)
    alt = _snap_alt(snap)
    paying = paying_eids(vessel, names, sit=sit, biome=biome, need=need, alt=alt)
    if not paying:
        return []
    return start_experiments(
        vessel,
        names=paying,
        on_log=on_log,
        sit=sit,
        biome=biome,
        need=need,
        alt=alt,
    )


def water_can_steer(name: str | None = None) -> bool:
    """Valiant gimbal can pitch east. Flea/Hammer cannot."""
    token = _craft_token(name if name is not None else hop_craft_name())
    return "valiant" in token


def hop_to_water_science() -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Flying + splash ids. Tickets first; science.md is legacy fallback."""
    from tickets import science_ids_for

    flying = science_ids_for(situation="flying")
    splash = science_ids_for(situation="splash")
    if flying or splash:
        return flying, splash
    from missions import seated_science_path

    path = seated_science_path()
    if not path.is_file():
        raise MissionAbort(NO_BOUND_CARD)
    text = path.read_text(encoding="utf-8")
    flying = card_flying_ids(text)
    splash = card_splash_ids(text)
    if not flying and not splash:
        raise MissionAbort(NO_BOUND_CARD)
    return flying, splash


def hop_splash_science() -> tuple[str, ...]:
    """Splash ids only. Tickets first; science.md is legacy fallback."""
    from tickets import science_ids_for

    ids = science_ids_for(situation="splash")
    if ids:
        return ids
    from missions import seated_science_path

    path = seated_science_path()
    if not path.is_file():
        raise MissionAbort(NO_BOUND_CARD)
    ids = card_splash_ids(path.read_text(encoding="utf-8"))
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


def abort_ksc_leftover(
    vessel: object | None,
    on_log: Callable[[str], None] | None,
    *,
    why: str = "",
) -> NoReturn:
    """Print Hank's leftover call, then abort. Do not recover. Do not KSC."""
    sit = _vessel_sit(vessel)
    rec = _recoverable(vessel)
    for line in leftover_abort_kv(sit=sit, recoverable=rec):
        print(line, flush=True)
        _say(line, on_log)
    raise MissionAbort(leftover_abort_why(sit=sit, recoverable=rec, why=why))


def _recover_unmatched_leftover(
    session: object,
    vessel: object,
    on_log: Callable[[str], None] | None,
) -> NoReturn:
    """Unmatched leftover is Hank's. Do not light. Do not recover here."""
    name = _vessel_name(vessel) or "?"
    sit = _vessel_sit(vessel)
    rec = "yes" if _recoverable(vessel) else "no"
    _say(
        f"hop leftover unmatched {name} sit={sit} recoverable={rec} "
        "— ksc leftover, do not light",
        on_log,
    )
    abort_ksc_leftover(vessel, on_log, why="unmatched leftover")


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


def _science_ready(snap: object) -> bool:
    """FlyingLow: airborne. FlyingHigh: alt ≥50 km. Not a second Toggle."""
    if not _airborne(snap):
        return False
    lid = hop_science_alt()
    if lid <= 0.0:
        return True
    alt = _snap_alt(snap)
    return math.isfinite(alt) and alt >= lid


def _reached_high_lid(snap: object) -> bool:
    """FlyingHigh Toggle sit. Pad loft (250 m) is not the lid."""
    return hop_wants_flying_high() and _science_ready(snap)


def _abort_high_lid(
    *,
    lit: bool,
    started: list[str] | tuple[str, ...],
    left_pad: bool,
    down: bool,
    reached_lid: bool,
) -> bool:
    """Abort FlyingHigh only after the Toggle sit with nothing started.

    A hop that never reached 50 km is not a lid miss. Land leftover still
    pays. Pad loft is not the lid.
    """
    if not hop_wants_flying_high():
        return False
    return bool(lit and not started and left_pad and down and reached_lid)


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


def _parts_n(vessel: object | None) -> int | None:
    if vessel is None:
        return None
    try:
        return len(list(getattr(getattr(vessel, "parts", None), "all", None) or []))
    except Exception:
        return None


def _snap_mass(snap: object) -> float:
    try:
        mass = float(getattr(snap, "mass", float("nan")))
    except (TypeError, ValueError):
        return float("nan")
    return mass if math.isfinite(mass) else float("nan")


def stack_sheared(
    prev_mass: float,
    mass: float,
    prev_fuel: float,
    fuel: float,
    prev_parts: int | None,
    parts_n: int | None,
) -> str | None:
    """Structure gone, not propellant.

    ``parts_n`` drop wins. Mass drop ≥40% of previous and well beyond
    fuel burned is tank/engine shear. parts/mass 0 is kRPC death, not shear.
    """
    if parts_n is not None and parts_n <= 0:
        return None
    if math.isfinite(mass) and mass <= 0.0:
        return None
    if (
        prev_parts is not None
        and parts_n is not None
        and parts_n < prev_parts
    ):
        return f"parts {prev_parts}->{parts_n}"
    if not (
        math.isfinite(prev_mass)
        and math.isfinite(mass)
        and prev_mass > 0.0
        and mass >= 0.0
    ):
        return None
    drop = prev_mass - mass
    if drop <= SHEAR_MASS_SLACK_KG:
        return None
    if drop < SHEAR_MASS_FRAC * prev_mass:
        return None
    fuel_drop = 0.0
    if math.isfinite(prev_fuel) and math.isfinite(fuel):
        fuel_drop = max(0.0, prev_fuel - fuel)
    if drop <= SHEAR_FUEL_KG * fuel_drop + SHEAR_MASS_SLACK_KG:
        return None
    return f"mass {prev_mass:.0f}->{mass:.0f}"


def _vessel_gone(snap: object, vessel: object | None) -> bool:
    """kRPC death at impact: parts/mass 0. Not shear."""
    n = _parts_n(vessel)
    if n is not None and n <= 0:
        return True
    mass = _snap_mass(snap)
    return math.isfinite(mass) and mass <= 0.0


def _snap_fuel(snap: object) -> float:
    raw = getattr(snap, "fuel", float("nan"))
    if raw is None:
        return float("nan")
    try:
        fuel = float(raw)
    except (TypeError, ValueError):
        return float("nan")
    return fuel if math.isfinite(fuel) else float("nan")


def _snap_speed(snap: object) -> float:
    try:
        speed = float(getattr(snap, "speed", float("nan")))
    except (TypeError, ValueError):
        return float("nan")
    return speed if math.isfinite(speed) else float("nan")


def _snap_heading(snap: object) -> float:
    try:
        hdg = float(getattr(snap, "heading", float("nan")))
    except (TypeError, ValueError):
        return float("nan")
    return hdg if math.isfinite(hdg) else float("nan")


def _snap_pitch(snap: object) -> float:
    try:
        pitch = float(getattr(snap, "pitch", float("nan")))
    except (TypeError, ValueError):
        return float("nan")
    return pitch if math.isfinite(pitch) else float("nan")


def _snap_v_vert(snap: object) -> float:
    try:
        vz = float(getattr(snap, "v_vert", float("nan")))
    except (TypeError, ValueError):
        return float("nan")
    return vz if math.isfinite(vz) else float("nan")


def _experiment_count(vessel: object | None) -> int:
    """Kerbalism Experiment modules still on the stack. 0 = science wreck."""
    if vessel is None:
        return 0
    try:
        parts = list(getattr(getattr(vessel, "parts", None), "all", []) or [])
    except Exception:
        return 0
    n = 0
    for part in parts:
        try:
            mods = list(getattr(part, "modules", []) or [])
        except Exception:
            continue
        for mod in mods:
            if getattr(mod, "name", "") in {"Experiment", "ModuleScienceExperiment"}:
                n += 1
    return n


def leftover_wreck_before_light(snap: object, vessel: object | None) -> bool:
    """Refuse light on a leftover wreck. Disk PRELAUNCH is not this gate.

    Pad leftover may light only with fuel. Dry flying q=0 / still is
    crash UI — do not start science. Living ballistic empty tanks is
    not this. ``sit=splashed`` leftover may start the splash card.
    """
    sit = str(getattr(snap, "situation", "") or "").lower()
    if not sit or sit == "?":
        sit = _vessel_sit(vessel)
    fuel = _snap_fuel(snap)
    dry = math.isfinite(fuel) and fuel <= 0.0
    if sit in _LIGHT_SIT:
        return dry
    if sit not in _AIR and sit not in _GROUND:
        return False
    if not dry:
        return False
    if _recoverable(vessel):
        return True
    speed = _snap_speed(snap)
    still = not math.isfinite(speed) or speed <= 0.5
    return _q_zero(snap) and still


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


def _vessel_fuel(vessel: object | None) -> float:
    """LF/SF on the live vessel. Tests use ``resources.fuel``."""
    if vessel is None:
        return float("nan")
    res = getattr(vessel, "resources", None)
    if res is None:
        return float("nan")
    raw = getattr(res, "fuel", None)
    if raw is not None:
        try:
            fuel = float(raw)
        except (TypeError, ValueError):
            fuel = float("nan")
        else:
            if math.isfinite(fuel):
                return fuel
    total = 0.0
    found = False
    for name in ("LiquidFuel", "SolidFuel", "Oxidizer"):
        try:
            amt = float(res.amount(name))  # type: ignore[union-attr]
        except Exception:
            continue
        if math.isfinite(amt):
            total += amt
            found = True
    return total if found else float("nan")


def leftover_should_hangar_new(vessel: object | None) -> bool:
    """Matching leftover is last loft's wreck. Abort ksc leftover.

    Living Water leftover is not Hangar-new. Unrecoverable flying wreck
    is crash UI — do not Hangar over it.
    """
    if vessel is None or not _recoverable(vessel):
        return False
    sit = _vessel_sit(vessel)
    if sit in _GROUND:
        return True
    if _experiment_count(vessel) == 0:
        return True
    fuel = _vessel_fuel(vessel)
    dry = math.isfinite(fuel) and fuel <= 0.0
    if sit in _PAD_SIT or sit in _LIGHT_SIT or sit in _AIR:
        return dry
    return False


def _recover_wreck_then_clear(
    session: object,
    vessel: object,
    on_log: Callable[[str], None] | None,
) -> NoReturn:
    """Matching wreck leftover is Hank's. Do not recover. Do not Hangar."""
    sit = _vessel_sit(vessel)
    rec = "yes" if _recoverable(vessel) else "no"
    n_exp = _experiment_count(vessel)
    _say(
        f"hop leftover wreck sit={sit} recoverable={rec} "
        f"experiments={n_exp} — ksc leftover, do not Hangar",
        on_log,
    )
    abort_ksc_leftover(vessel, on_log, why="leftover wreck")


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
    met: float | None,
    prev: float | None,
    still_t0: float | None,
    now: float,
) -> tuple[float | None, bool]:
    """Frozen MET for ``_STILL_S`` wall seconds. Pulse count is Hz-blind."""
    if met is not None and not math.isfinite(met):
        t0 = now if still_t0 is None else still_t0
        return t0, True
    if (
        met is not None
        and prev is not None
        and abs(met - prev) < _STILL_MET
    ):
        t0 = now if still_t0 is None else still_t0
        return t0, (now - t0) >= _STILL_S
    return None, False


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
    lit: bool = False,
) -> bool:
    """Recover leftover HD: files on the drive, or Experiment modules gone.

    Not for a hop this process just lit — empty modules after light is a
    wreck, not leftover skip.
    """
    if _hd_ready(vessel, ids, started):
        return True
    if lit:
        return False
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


def _hold_ground_card(
    vessel: object,
    started: list[str],
    ids: tuple[str, ...],
    snap: object,
    *,
    wait_splash: bool = False,
) -> bool:
    """Living landed dwell: leftover rem still recording. Wreck recovers now.

    Sit-matched leftover stays in the card: airborne rem=0 (goo/geiger dwell)
    is not splash leftover done. File rem=0 idle still holds.
    """
    if wait_splash:
        return False
    if bool(getattr(snap, "wreck", False)):
        return False
    sit = _live_sit(vessel, snap)
    sit_l = sit.lower()
    if "landed" not in sit_l and "splash" not in sit_l:
        return False
    biome = _snap_biome(snap, vessel)
    try:
        leftover = hop_landed_science_ids(live_sit=sit, live_biome=biome)
    except Exception:
        leftover = ()
    names = tuple(dict.fromkeys([*(started or ()), *leftover]))
    if not names:
        names = tuple(ids)
    if not names:
        return False
    try:
        return not ground_card_done(vessel, names)
    except Exception:
        return False


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
        stop_experiments(vessel, on_log=on_log)
    except Exception:
        log.debug("science stop before recover failed", exc_info=True)
    mission_event("recover", beauty=True, pose="recover")
    try:
        from flightlog import record_recover_vessel

        record_recover_vessel(vessel)
    except Exception:
        log.debug("kind=recover tape failed", exc_info=True)
    try:
        getattr(vessel, "recover")()
    except Exception as exc:
        log.debug("hop recover() sit=%s: %s", sit, exc)
        return None
    _say(f"recovered sit={sit} recoverable=yes", on_log)
    return "recovered"


def _force_recover(
    vessel: object | None, on_log: Callable[[str], None] | None
) -> str | None:
    """recover() in Flight when recoverable. Do not invent recover() if no."""
    if vessel is None:
        return None
    sit = _vessel_sit(vessel)
    if sit in _PAD_SIT:
        return None
    if not _recoverable(vessel):
        return None
    try:
        stop_experiments(vessel, on_log=on_log)
    except Exception:
        log.debug("science stop before recover failed", exc_info=True)
    mission_event("recover", beauty=True, pose="recover")
    try:
        from flightlog import record_recover_vessel

        record_recover_vessel(vessel)
    except Exception:
        log.debug("kind=recover tape failed", exc_info=True)
    try:
        getattr(vessel, "recover")()
    except Exception as exc:
        log.debug("hop recover() sit=%s: %s", sit, exc)
        return None
    _say(f"recovered sit={sit} recoverable=yes", on_log)
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
    """Near-ground flying — recover in Flight when recoverable."""
    sit = str(getattr(snap, "situation", "") or "")
    if sit not in _AIR:
        return False
    alt = _snap_alt(snap)
    return math.isfinite(alt) and alt <= _AIRBORNE_M


def _lofted(snap: object) -> bool:
    """Alt well above the pad. sit=flying at pad alt is still pad boost."""
    alt = _snap_alt(snap)
    return math.isfinite(alt) and alt > _AIRBORNE_M


def _crash_ui(
    snap: object, vessel: object | None, *, frozen: bool
) -> bool:
    """Catastrophic Flight Results: MET frozen, no Recover button.

    Flying q=0 low, or landed/splashed recoverable=no.
    """
    if not frozen:
        return False
    if _low_flying(snap) and _q_zero(snap):
        return True
    sit = str(getattr(snap, "situation", "") or "").lower()
    if not sit or sit == "?":
        sit = _vessel_sit(vessel)
    return sit in _GROUND and not _recoverable(vessel)


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


def _wait_vessel_gone(
    session: object,
    vessel: object | None,
    on_log: Callable[[str], None] | None,
    *,
    timeout: float = 8.0,
) -> None:
    """recover() returns before KSP drops the ship (recover-sit probe)."""
    name = _vessel_name(vessel) if vessel is not None else ""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        live = _vessel_live(vessel) if vessel is not None else False
        pool = _pool(session, None)
        named = [
            other
            for other in pool
            if name and (_vessel_name(other) or "") == name
        ]
        if (not live) and not named:
            _say("hop recover gone", on_log)
            return
        time.sleep(0.3)
    _say("hop recover still listed after recover()", on_log)


def _leave_crash_ui(
    session: object,
    on_log: Callable[[str], None] | None,
    *,
    total_wreck: bool = False,
) -> None:
    """Leave Catastrophic Flight Results.

    Total wreck: do not go_space_center (overlay is not leftover-clean).
    Caller aborts ``ksc leftover``. Never revert_to_launch.
    """
    if total_wreck:
        _say("hop crash ui total wreck — ksc leftover (not space_center)", on_log)
        return
    try:
        krpc = getattr(getattr(session, "conn", None), "krpc", None)
        gs = getattr(krpc, "GameScene", None) if krpc is not None else None
        ts = getattr(gs, "tracking_station", None) if gs is not None else None
        if krpc is not None and ts is not None:
            krpc.game_scene = ts
            _say("hop crash ui tracking (not pad reload)", on_log)
            return
    except Exception as exc:
        log.warning("hop crash ui tracking: %s", exc)
    _say("hop crash ui abort in flight (not space_center)", on_log)


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
    _wait_vessel_gone(session, vessel, on_log)
    try:
        go_space_center(session, reload_save=False)
        _say("hop dismissed flight results", on_log)
    except Exception as exc:
        log.warning("hop dismiss flight results: %s", exc)
    return got


def _uplink_tick(ctx: Ctx) -> None:
    """Abort-class raises. Science/transmit run. Do not extra-stage."""
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


def _command_ok(snap: object | None, vessel: object | None = None) -> bool:
    """False only when we know the unmanned probe is deaf.

    snap.link is True/False/None (Wernher). None or missing → try
    vessel.comms.can_communicate; unreadable → True (Hangar/KSC).
    Crewed: True.
    """
    if vessel is not None:
        try:
            n = int(getattr(vessel, "crew_count", 0) or 0)
        except Exception:
            n = 0
        if n > 0:
            return True
    link = getattr(snap, "link", None) if snap is not None else None
    if link is False:
        return False
    if link is True:
        return True
    if vessel is None:
        return True
    try:
        can = getattr(vessel.comms, "can_communicate")
    except Exception:
        return True
    if can is None:
        return True
    return bool(can)


def _zero_stick_if_deaf(vessel: object, snap: object | None) -> bool:
    """If not _command_ok: throttle 0, SAS off. Return True if deaf.

    Do not stage. Do not abort here.
    """
    if _command_ok(snap, vessel):
        return False
    try:
        control = vessel.control
        control.throttle = 0.0
        control.sas = False
    except Exception:
        pass
    return True


def _link_edge(
    events: EventLog | None, ok: bool, was: bool | None
) -> None:
    """kind=link on yes↔no only. Not 5 Hz."""
    if events is None or was is None or bool(ok) == bool(was):
        return
    events.emit(
        "link",
        link=int(bool(ok)),
        msg="link yes" if ok else "link no",
    )


def _light(
    vessel: object,
    on_log: Callable[[str], None] | None,
    snap: object | None = None,
) -> None:
    if _zero_stick_if_deaf(vessel, snap):
        raise MissionAbort("no signal (pad)")
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


def _burning(vessel: object, snap: object, *, lofted: bool = False) -> bool:
    """Throttle on with fuel. A 0-tick after light is not cutoff.

    Real burnout is fuel gone, or throttle 0 after a real loft.
    Stayputnik cannot steer after cutoff.
    """
    try:
        fuel = float(getattr(snap, "fuel", float("nan")))
    except (TypeError, ValueError):
        fuel = float("nan")
    if math.isfinite(fuel) and fuel <= 0.0:
        return False
    try:
        throttle = float(getattr(vessel.control, "throttle", 0.0) or 0.0)
    except Exception:
        throttle = 0.0
    if throttle > 0.05:
        return True
    return not lofted


def _pad_boosting(
    *,
    lit: bool,
    left_pad: bool,
    lofted: bool,
    down: bool,
    burning: bool,
) -> bool:
    """Lit, left pad, flying, still burning, not lofted — not recover, not coast.

    ``down`` (landed/splashed) is not boost: do not throttle into dirt.
    sit=flying below loft with fuel is still 1× boost. Warp does not change this.
    """
    return bool(lit and left_pad and not lofted and not down and burning)


def _chute_fully_open(snap: object) -> bool:
    st = str(getattr(snap, "chute", "") or "").lower().replace("-", "_")
    return st == "deployed"


def _want_coast_phys(
    snap: object,
    *,
    left_pad: bool,
    down: bool,
    chute_open: bool,
    burning: bool,
) -> bool:
    """Warp clock is ``physics_warp.want_coast``. ``chute_open`` is snap.chute."""
    del chute_open
    return want_coast(snap, left_pad=left_pad, down=down, burning=burning)


def _apply_hop_physics(
    session: object,
    *,
    coast: bool,
    on_log: Callable[[str], None] | None = None,
    last: list[str] | None = None,
) -> int:
    """Physics warp only. Rails 0. Never WarpTo. Returns kRPC factor."""
    return apply_coast(
        session,
        coast=coast,
        on_log=on_log,
        last=last,
        default_rate=coast_rate(),
        uplink_rate=phys_warp_rate(),
    )


def _slew_pitch(cmd: float, dt: float, target: float) -> tuple[float, bool]:
    """Step target_pitch from vertical toward ``target``.

    True while still slewing. Do not slam 65 at light.
    """
    step = WATER_PITCH_SLEW_DPS * (dt if dt > 0.0 else _PULSE_S)
    nxt = cmd - step
    if nxt <= target:
        return target, False
    return nxt, True


def _slew_east_pitch(cmd: float, dt: float) -> tuple[float, bool]:
    """Step target_pitch from vertical toward WATER_PITCH_DEG."""
    return _slew_pitch(cmd, dt, WATER_PITCH_DEG)


def surface_direction(
    pitch_deg: float, heading_deg: float
) -> tuple[float, float, float]:
    """Surface-frame unit vector: pitch from horizon, heading from north.

    kRPC vessel.surface_reference_frame: x=up, y=north, z=east.
    Pitch 90 is zenith (1,0,0) — heading is not a rotation there.
    """
    pitch = math.radians(float(pitch_deg))
    heading = math.radians(float(heading_deg))
    cy = math.cos(pitch)
    return (
        math.sin(pitch),
        cy * math.cos(heading),
        cy * math.sin(heading),
    )


def east_direction(pitch_deg: float) -> tuple[float, float, float]:
    """Surface-frame unit vector: pitch from horizon, heading 90 east."""
    return surface_direction(pitch_deg, WATER_HEADING_DEG)


def inland_direction(pitch_deg: float) -> tuple[float, float, float]:
    """Surface-frame unit vector: pitch from horizon, heading 270 west."""
    return surface_direction(pitch_deg, INLAND_HEADING_DEG)


def _point_surface(ap: object, direction: tuple[float, float, float], *, why: str) -> None:
    """Nose along ``direction``, north up — defined through vertical.

    Write ``target_direction`` then ``set_direction_and_up``. Do not set
    ``target_roll=0`` vs zenith (heading undefined near vertical).
    """
    if hasattr(ap, "target_direction"):
        ap.target_direction = direction
        try:
            ap.up_reference = SURFACE_NORTH
        except Exception:
            pass
    if hasattr(ap, "set_direction_and_up"):
        ap.set_direction_and_up(direction, SURFACE_NORTH, 0.0)
        return
    if not hasattr(ap, "target_direction"):
        raise MissionAbort(f"{why} failed: no target_direction")
    try:
        ap.target_roll = float("nan")
    except Exception:
        pass


def _pitch_has_heading(pitch: float) -> bool:
    """Heading exists 10° off zenith. Do not engage at ~90."""
    try:
        p = float(pitch)
    except (TypeError, ValueError):
        return False
    return math.isfinite(p) and p <= INLAND_YAW_PITCH_DEG + 1e-9


def _heading_err_deg(flown: float, want: float) -> float:
    if not math.isfinite(flown) or not math.isfinite(want):
        return 0.0
    return abs((float(flown) - float(want) + 180.0) % 360.0 - 180.0)


def _inland_cmd_pitch(
    yawed: bool,
    yaw_n: int,
    flown_pitch: float,
    flown_heading: float,
    met: float,
) -> tuple[float, bool]:
    """Yaw 10° off zenith until heading captured, then 25° inland."""
    if yawed:
        return INLAND_PITCH_DEG, True
    captured = (
        math.isfinite(flown_heading)
        and _heading_err_deg(flown_heading, INLAND_HEADING_DEG)
        <= INLAND_HEADING_CAPTURE_DEG
        and math.isfinite(flown_pitch)
        and float(flown_pitch) <= INLAND_YAW_PITCH_DEG + 5.0
    )
    timed_out = math.isfinite(met) and float(met) >= INLAND_YAW_MET_S
    unseen = not math.isfinite(flown_heading) and int(yaw_n) >= 2
    if captured or timed_out or unseen:
        return INLAND_PITCH_DEG, True
    return INLAND_YAW_PITCH_DEG, False


def _hold_flipped(
    flown_pitch: float,
    flown_heading: float,
    want_heading: float,
    want_pitch: float = INLAND_PITCH_DEG,
    *,
    burning: bool = True,
) -> bool:
    """True when the commanded hold is not on the vessel.

    Pitch past horizon, or heading error >45° while burning. After
    burnout, heading weathercock is not a rewrite.
    """
    if math.isfinite(flown_pitch):
        p = float(flown_pitch)
        if p < 0.0:
            return True
        if (
            burning
            and math.isfinite(want_pitch)
            and p < float(want_pitch) - 20.0
        ):
            return True
    if not burning:
        return False
    return _heading_err_deg(flown_heading, want_heading) > 45.0


def _ap_engage_once(ap: object) -> None:
    """Engage only from disengaged. Re-engage restarts 0.6 soft-start."""
    if getattr(ap, "engaged", False):
        return
    ap.engaged = True


_STEER_HELD: dict[int, tuple[float, float, float]] = {}


def _steer_heading(
    vessel: object,
    pitch: float,
    heading: float,
    *,
    why: str,
    flown_pitch: float = float("nan"),
    flown_heading: float = float("nan"),
    burning: bool = True,
) -> None:
    """Point surface heading. Caller slews pitch; hold through burnout.

    ``set_direction_and_up`` north up. Engage once off zenith. Latch
    the vector; re-point if flipped while burning; write
    ``target_direction``. Do not re-engage. Do not rewrite fuel=0.
    """
    try:
        vessel.control.sas = False
    except Exception:
        pass
    ap = getattr(vessel, "auto_pilot", None)
    if ap is None:
        raise MissionAbort(f"{why} failed: no auto_pilot")
    try:
        cmd = float(pitch)
        want_hdg = float(heading)
        direction = surface_direction(cmd, want_hdg)
        key = id(ap)
        same = _STEER_HELD.get(key) == direction
        flipped = _hold_flipped(
            flown_pitch,
            flown_heading,
            want_hdg,
            cmd,
            burning=burning,
        )
        if getattr(ap, "engaged", False) and same and not flipped:
            return
        frame = getattr(vessel, "surface_reference_frame", None)
        if frame is not None and hasattr(ap, "reference_frame"):
            ap.reference_frame = frame
        _point_surface(ap, direction, why=why)
        if _pitch_has_heading(cmd):
            _ap_engage_once(ap)
        _point_surface(ap, direction, why=why)
        _STEER_HELD[key] = direction
    except Exception as exc:
        raise MissionAbort(f"{why} failed: {exc}") from exc


def _steer_east(
    vessel: object,
    pitch: float = WATER_PITCH_DEG,
    *,
    flown_pitch: float = float("nan"),
    flown_heading: float = float("nan"),
    burning: bool = True,
) -> None:
    """Point east (heading 90). Caller slews pitch; hold through burnout."""
    _steer_heading(
        vessel,
        pitch,
        WATER_HEADING_DEG,
        why="east pitch",
        flown_pitch=flown_pitch,
        flown_heading=flown_heading,
        burning=burning,
    )


def _steer_inland(
    vessel: object,
    pitch: float = INLAND_PITCH_DEG,
    *,
    flown_pitch: float = float("nan"),
    flown_heading: float = float("nan"),
    burning: bool = True,
) -> None:
    """Point west (heading 270). Caller slews pitch; hold through burnout."""
    _steer_heading(
        vessel,
        pitch,
        INLAND_HEADING_DEG,
        why="inland pitch",
        flown_pitch=flown_pitch,
        flown_heading=flown_heading,
        burning=burning,
    )


def _release_steer(vessel: object) -> None:
    ap = getattr(vessel, "auto_pilot", None)
    if ap is None:
        return
    try:
        if hasattr(ap, "disengage"):
            ap.disengage()
        else:
            ap.engaged = False
    except Exception:
        pass


def _coast_impact_ms(snap: object) -> float:
    """Vacuum splash speed from this alt/vz. Drag only helps.

    GooExperiment crashTolerance is 12. This is v_vert impact.
    """
    alt = _snap_alt(snap)
    vz = _snap_v_vert(snap)
    speed = _snap_speed(snap)
    if math.isfinite(alt) and alt <= 0.0:
        if math.isfinite(speed):
            return speed
        if math.isfinite(vz):
            return abs(vz)
        return 0.0
    if not math.isfinite(alt) or alt > WATER_BRAKE_ALT_MAX_M:
        return float("inf")
    if math.isfinite(vz) and vz > 0.0:
        return float("inf")
    sink = (
        -vz
        if math.isfinite(vz) and vz < 0.0
        else (speed if math.isfinite(speed) else float("nan"))
    )
    if not math.isfinite(sink):
        return float("inf")
    return math.sqrt(sink * sink + 2.0 * WATER_BRAKE_G * max(alt, 0.0))


def _coast_ok(snap: object) -> bool:
    """True when leftover LF may stay cut: coast ≤ Goo crashTolerance."""
    impact = _coast_impact_ms(snap)
    return math.isfinite(impact) and impact <= GOO_CRASH_MS


def _suicide_tti(snap: object) -> float:
    """Seconds to surface at current sink. inf if not falling."""
    alt = _snap_alt(snap)
    if not math.isfinite(alt) or alt <= 0.0:
        return float("inf")
    vz = _snap_v_vert(snap)
    speed = _snap_speed(snap)
    sink = -vz if math.isfinite(vz) and vz < 0.0 else speed
    if not math.isfinite(sink) or sink <= 0.0:
        return float("inf")
    return alt / max(sink, 1.0)


def _brake_accel(vessel: object | None) -> float:
    """Throttle-1 accel (m/s²). NaN when mass/thrust is unbound (tests)."""
    if vessel is None:
        return float("nan")
    try:
        thrust = float(getattr(vessel, "available_thrust", 0.0) or 0.0)
    except (TypeError, ValueError):
        thrust = 0.0
    if not math.isfinite(thrust) or thrust <= 1.0:
        try:
            thrust = float(getattr(vessel, "max_thrust", 0.0) or 0.0)
        except (TypeError, ValueError):
            thrust = 0.0
    try:
        mass = float(getattr(vessel, "mass", 0.0) or 0.0)
    except (TypeError, ValueError):
        mass = 0.0
    if (
        not math.isfinite(thrust)
        or not math.isfinite(mass)
        or thrust <= 1.0
        or mass <= 0.1
    ):
        return float("nan")
    return thrust / mass


def _hover_throttle(vessel: object | None) -> float:
    """TWR≈1 after the kill. Throttle 1 at leftover TWR dumps crumbs."""
    a = _brake_accel(vessel)
    if math.isfinite(a) and a > WATER_BRAKE_G * 1.05:
        return min(1.0, max(0.08, WATER_BRAKE_G / a))
    return WATER_BRAKE_HOVER_THROTTLE


def _suicide_light(snap: object, vessel: object | None = None) -> bool:
    """First throttle 1: live TTI ≤ ~3.5, not the TTI≤12 watch.

    When mass/thrust is bound, light at burn-distance + pad.
    """
    tti = _suicide_tti(snap)
    if not math.isfinite(tti):
        return False
    a = _brake_accel(vessel)
    vz = _snap_v_vert(snap)
    sink = -vz if math.isfinite(vz) and vz < 0.0 else _snap_speed(snap)
    alt = _snap_alt(snap)
    if (
        math.isfinite(a)
        and a > WATER_BRAKE_G + 1.0
        and math.isfinite(sink)
        and sink > GOO_CRASH_MS
        and math.isfinite(alt)
        and alt > 0.0
    ):
        anet = a - WATER_BRAKE_G
        t_burn = (sink - GOO_CRASH_MS) / anet
        s_burn = sink * t_burn - 0.5 * anet * t_burn * t_burn
        if math.isfinite(s_burn) and s_burn > 0.0:
            return alt <= s_burn + WATER_BRAKE_LIGHT_PAD_M
    return tti <= WATER_BRAKE_LIGHT_TTI_S


def _suicide_need(snap: object) -> bool:
    """Leftover brake still required: coast > Goo 12 and not loft/crumbs."""
    fuel = _snap_fuel(snap)
    if not math.isfinite(fuel) or fuel <= WATER_BRAKE_FUEL_MIN:
        return False
    alt = _snap_alt(snap)
    if not math.isfinite(alt) or alt <= 0.0:
        return False
    vz = _snap_v_vert(snap)
    if math.isfinite(vz) and vz >= 0.0:
        return False
    return not _coast_ok(snap)


def _suicide_now(
    snap: object, *, spent: bool = False, hover: bool = False
) -> bool:
    """Arm leftover-LF watch. TTI / alt cap enter the gate, not throttle 1.

    ``spent`` is leftover after a vz-cut whose coast is already ≤12
    (or crumbs). ``hover`` stays on until coast ≤12 — do not wait
    TTI≤12 and do not drop out at vz ≥ −10. First throttle 1 is
    ``_suicide_light``.
    """
    if spent:
        return False
    fuel = _snap_fuel(snap)
    if not math.isfinite(fuel) or fuel <= WATER_BRAKE_FUEL_MIN:
        return False
    alt = _snap_alt(snap)
    if not math.isfinite(alt) or alt <= 0.0 or alt > WATER_BRAKE_ALT_MAX_M:
        return False
    vz = _snap_v_vert(snap)
    if hover:
        return _suicide_need(snap)
    speed = _snap_speed(snap)
    if not math.isfinite(speed):
        return False
    if speed <= WATER_BRAKE_SPEED_M:
        return False
    if math.isfinite(vz) and vz >= -WATER_BRAKE_SPEED_M:
        return False
    tti = _suicide_tti(snap)
    return math.isfinite(tti) and tti <= WATER_BRAKE_TTI_S


def _suicide_hold(
    snap: object,
    *,
    prev_vz: float | None = None,
    dt: float | None = None,
) -> bool:
    """Kill band: vz still faster than −10. TTI rising is not a cut.

    Do not predict-cut. ``prev_vz`` / ``dt`` are ignored — 20 Hz gate.
    After vz ≥ −10 leftover is spent only if coast ≤12; else TWR≈1 hover.
    """
    del prev_vz, dt
    fuel = _snap_fuel(snap)
    if not math.isfinite(fuel) or fuel <= WATER_BRAKE_FUEL_MIN:
        return False
    alt = _snap_alt(snap)
    if not math.isfinite(alt) or alt <= 0.0:
        return False
    vz = _snap_v_vert(snap)
    if math.isfinite(vz):
        return vz < WATER_BRAKE_VZ_CUT
    speed = _snap_speed(snap)
    if not math.isfinite(speed):
        return False
    return speed > WATER_BRAKE_SPEED_M


def _suicide_throttle(
    vessel: object,
    snap: object,
    *,
    lit: bool = False,
    hover: bool = False,
) -> float:
    """0 / TWR≈1 / 1. Do not dump leftover at vz-cut."""
    if not _suicide_need(snap):
        return 0.0
    armed = lit or hover or _suicide_light(snap, vessel)
    if _suicide_hold(snap):
        if armed:
            return 1.0
        return 0.0
    if armed:
        return _hover_throttle(vessel)
    return 0.0


def _stream_float(telem: object | None, key: str) -> float:
    streams = getattr(telem, "_streams", None) or {}
    stream = streams.get(key) if isinstance(streams, dict) else None
    if stream is None:
        return float("nan")
    try:
        val = float(stream())
    except Exception:
        return float("nan")
    return val if math.isfinite(val) else float("nan")


def _live_v_vert(vessel: object, telem: object | None = None) -> float:
    vz = _stream_float(telem, "kin.vertical_speed")
    if math.isfinite(vz):
        return vz
    try:
        orbit = getattr(vessel, "orbit", None)
        body = getattr(orbit, "body", None)
        rf = getattr(body, "reference_frame", None)
        kin = vessel.flight(rf) if rf is not None else vessel.flight()
        vz = float(getattr(kin, "vertical_speed", float("nan")))
        if math.isfinite(vz):
            return vz
    except Exception:
        pass
    try:
        vz = float(getattr(vessel.flight(), "vertical_speed", float("nan")))
    except Exception:
        return float("nan")
    return vz if math.isfinite(vz) else float("nan")


def _live_alt(vessel: object, telem: object | None = None) -> float:
    alt = _stream_float(telem, "flight.mean_altitude")
    if math.isfinite(alt):
        return alt
    try:
        alt = float(getattr(vessel.flight(), "mean_altitude", float("nan")))
    except Exception:
        return float("nan")
    return alt if math.isfinite(alt) else float("nan")


def _live_fuel(vessel: object) -> float:
    from telem import resource_amount

    total = 0.0
    seen = False
    for name in ("LiquidFuel", "SolidFuel", "Kerosene"):
        amt = resource_amount(vessel, name)
        if amt is None:
            continue
        try:
            fuel = float(amt)
        except (TypeError, ValueError):
            continue
        if math.isfinite(fuel):
            total += fuel
            seen = True
    return total if seen else float("nan")


def _suicide_gate(
    vessel: object,
    snap: object,
    *,
    sleep: Callable[[float], None],
    now: Callable[[], float],
    telem: object | None = None,
    abort: Callable[[], bool] | None = None,
    budget_s: float = WATER_BRAKE_GATE_S,
    hover: bool = False,
) -> bool:
    """20 Hz leftover-LF. Telem.read is ~1.5 s — 1 Hz never saw throttle 1.

    Watch at TTI≤12; throttle 1 only at live TTI ≤ 3.5 or TWR burn
    distance. After vz ≥ −10, TWR≈1 hover until coast ≤ Goo 12 — do
    not cut and do not slam 1. Live vz ~0 while the snap is still
    sinking means the stream is not bound — do not false-cut.
    """
    if _zero_stick_if_deaf(vessel, snap):
        return False
    dt = 1.0 / WATER_BRAKE_HZ
    t_end = now() + budget_s
    _steer_brake(vessel)
    vz_snap = _snap_v_vert(snap)
    stepped = False
    lit = bool(hover)
    while now() < t_end:
        if _zero_stick_if_deaf(vessel, snap):
            return False
        if abort is not None:
            try:
                if abort():
                    break
            except Exception:
                pass
        vz_live = _live_v_vert(vessel, telem)
        if (
            math.isfinite(vz_live)
            and abs(vz_live) < 1.0
            and math.isfinite(vz_snap)
            and vz_snap < WATER_BRAKE_VZ_CUT
            and not stepped
        ):
            try:
                vessel.control.throttle = _suicide_throttle(
                    vessel, snap, lit=lit, hover=hover
                )
            except Exception:
                pass
            return True
        fuel_live = _live_fuel(vessel)
        alt_live = _live_alt(vessel, telem)
        fuel = fuel_live if math.isfinite(fuel_live) else _snap_fuel(snap)
        alt = alt_live if math.isfinite(alt_live) else _snap_alt(snap)
        vz = vz_live if math.isfinite(vz_live) else vz_snap
        speed = abs(vz) if math.isfinite(vz) else _snap_speed(snap)
        live = type(
            "S",
            (),
            {
                "fuel": fuel,
                "alt": alt,
                "speed": speed,
                "v_vert": vz,
            },
        )()
        if not _suicide_need(live):
            try:
                vessel.control.throttle = 0.0
            except Exception:
                pass
            return False
        thr = _suicide_throttle(vessel, live, lit=lit, hover=hover)
        try:
            vessel.control.throttle = thr
        except Exception:
            pass
        if thr > 0.0:
            lit = True
        if not math.isfinite(vz_live):
            return True
        sleep(dt)
        stepped = True
    return True


def _steer_brake(vessel: object) -> None:
    """Surface zenith so leftover LF kills vertical speed. Gimbal only."""
    try:
        vessel.control.sas = False
    except Exception:
        pass
    ap = getattr(vessel, "auto_pilot", None)
    if ap is None:
        return
    try:
        frame = getattr(vessel, "surface_reference_frame", None)
        if frame is not None and hasattr(ap, "reference_frame"):
            ap.reference_frame = frame
        ap.target_pitch = WATER_PITCH_UP
        if hasattr(ap, "target_direction"):
            try:
                ap.target_direction = east_direction(WATER_PITCH_UP)
            except Exception:
                pass
        try:
            ap.target_roll = float("nan")
        except Exception:
            pass
        _ap_engage_once(ap)
    except Exception:
        pass


def _hold_or_cut(
    vessel: object,
    snap: object,
    hop_apo: float,
    *,
    cut: bool,
    hold: float = 1.0,
    brake: bool = False,
    braking: bool = False,
    prev_vz: float | None = None,
    dt: float | None = None,
    spent: bool = False,
    hover: bool = False,
) -> tuple[bool, bool]:
    """Throttle 0 at hop_apo and stay cut.

    An SRB ignores the cut — do not OffPlan the coast. ``hold`` is 1
    except hop-to-water slew (0.4). After latch, leftover LF is a
    suicide burn iff ``brake`` (wait water/splash). Once armed, watch
    until live TTI ≤ 3.5 then kill at 1; after vz ≥ −10 hover TWR≈1
    until coast ≤12. TTI rising is not a recut. Crumb relight
    (fuel ≤2) is not a second slam. ``spent`` holds that cut only
    when coast impact ≤ Goo 12. ``hover`` keeps leftover until coast
    ≤12 — not a TTI wait and not a vz −10 drop-out.
    """
    if _zero_stick_if_deaf(vessel, snap):
        return cut, False
    try:
        control = vessel.control
        apo = float(getattr(snap, "apo", float("nan")))
        fuel = _snap_fuel(snap)
        if not cut and math.isfinite(apo) and apo >= hop_apo:
            cut = True
        if not cut and math.isfinite(fuel) and fuel <= 0.0:
            cut = True
        if spent:
            if cut:
                control.throttle = 0.0
            else:
                control.throttle = hold
            return cut, False
        if brake and cut and (
            braking or _suicide_now(snap, spent=spent, hover=hover)
        ):
            del prev_vz, dt
            if _suicide_need(snap):
                control.throttle = _suicide_throttle(
                    vessel, snap, lit=hover, hover=hover
                )
                return cut, True
            control.throttle = 0.0
            return cut, False
        if cut:
            control.throttle = 0.0
        else:
            control.throttle = hold
    except Exception:
        pass
    return cut, False


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
    pulse: float | None = None,
    wait_water: bool = False,
    wait_splash: bool = False,
    splash_ids: tuple[str, ...] | None = None,
) -> str:
    """Light, flying card, recover when down or dead-with-HD. Caller Hangars.

    Factory inland pulse lives in hop_factory (no water/splash flags).
    This loop is parked hop-to-water / hop-splash only.

    Leftover (did not light) with drive files or no Experiment modules
    skips a fresh start. A hop this process lit starts the flying card
    when the bound sit can pay — FlyingLow once airborne, FlyingHigh
    only at alt ≥50 km. MET-still + q=0 flying is down now. Low flying
    (≤250 m) recover() only when recoverable after a real loft — not a
    full tank at pad alt. Frozen MET + flying + q=0 + low alt is crash
    UI. parts/mass 0 rec=no is total wreck — abort ksc leftover.
    Matching leftover: live sit/fuel/recoverable before light.

    ``wait_water``: slew 25° east after ``left_pad`` at
    ``WATER_SLEW_THROTTLE``; latch hop_apo; leftover LF suicide near
    Water (watch TTI ≤12, light at 3.5, kill until vz ≥ −10, hover
    until coast ≤12). Do not recover on first flying recoverable;
    abort landed only after ``left_pad``; splash dwell after
    ``sit=splashed``.

    ``wait_splash``: vertical, no east slew, no flying Toggle;
    ``hop_apo`` stays cut; same suicide; wait ``sit=splashed``.
    """
    if not wait_water and not wait_splash:
        from hop_factory import run_factory_vessel

        return run_factory_vessel(
            session,
            vessel,
            events=events,
            on_log=on_log,
            science_ids=science_ids,
            abort=abort,
            now=now,
            sleep=sleep,
            timeout=timeout,
            pulse=pulse,
        )
    from phases import OffPlan, check_expect

    wait_down = wait_water or wait_splash
    log_events = events if events is not None else EventLog()
    ids = (
        ()
        if wait_splash
        else (science_ids if science_ids is not None else hop_science_ids())
    )
    hop_apo = hop_target_apo(space=True) if wait_splash else hop_target_apo()
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
    said_lid = False
    waiting_hd = False
    prev_met: float | None = None
    still_t0: float | None = None
    unpaused = False
    unpause_at: float | None = None
    litho = False
    said_crash = False
    said_pitch = False
    said_hold = False
    said_slew = False
    said_brake = False
    apo_cut = False
    braking = False
    suicide_spent = False
    suicide_armed = False
    prev_brake_vz = float("nan")
    prev_brake_met = float("nan")
    water_splashed = False
    water_pitch = WATER_PITCH_UP
    inland_pitch = WATER_PITCH_UP
    inland_yawed = False
    inland_yaw_n = 0
    loft_hold = WATER_SLEW_THROTTLE if wait_water else 1.0
    splash_names = splash_ids if splash_ids is not None else ()
    chute_armed = False
    chute_open = False
    said_deploy = False
    said_coast = [""]
    lofted = False
    link_was: bool | None = None
    prev_stack_mass = float("nan")
    prev_stack_fuel = float("nan")
    prev_stack_parts: int | None = None
    _say(f"hop apo={hop_apo:.0f}", on_log)
    if wait_splash:
        _say(
            "hop-splash light vertical, no flying Toggle, wait splash",
            on_log,
        )
    elif wait_water:
        _say(
            f"hop-to-water slew pitch {WATER_PITCH_FROM_UP:g}° east after pad "
            f"(throttle {WATER_SLEW_THROTTLE:g}), hold through burnout, wait splash",
            on_log,
        )
    else:
        _say(
            f"hop slew yaw {INLAND_YAW_FROM_UP:g}° then pitch "
            f"{INLAND_PITCH_FROM_UP:g}° inland heading "
            f"{INLAND_HEADING_DEG:g} after pad, hold through burnout",
            on_log,
        )

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
            deaf = _zero_stick_if_deaf(vessel, snap)
            _link_edge(log_events, not deaf, link_was)
            link_was = not deaf
            sit_live = str(getattr(snap, "situation", "") or "").lower()
            leftover_splash = (
                wait_splash
                and sit_live in {"splashed"}
                and _experiment_count(vessel) > 0
            )
            if (
                not did_light
                and leftover_wreck_before_light(snap, vessel)
                and not leftover_splash
            ):
                sit = str(getattr(snap, "situation", "") or "") or _vessel_sit(
                    vessel
                )
                rec = "yes" if _recoverable(vessel) else "no"
                _say(
                    f"hop leftover sit={sit} fuel={_fmt(_snap_fuel(snap), 1)} "
                    f"recoverable={rec} met={_fmt(_vessel_met(vessel), 2)} "
                    "— do not light",
                    on_log,
                )
                if _recoverable(vessel):
                    got = _force_recover(vessel, on_log)
                    if got is not None:
                        return got
                if sit in _LIGHT_SIT:
                    raise MissionAbort("leftover dry — do not light")
                if not said_crash:
                    _crash_line(vessel, snap, on_log)
                    said_crash = True
                _leave_crash_ui(
                    session,
                    on_log,
                    total_wreck=_experiment_count(vessel) == 0,
                )
                raise MissionAbort("not recoverable")
            airborne = _airborne(snap)
            if airborne:
                if not left_pad:
                    _say("hop airborne", on_log)
                    log_events.emit("hop", result="airborne")
                    mission_event(
                        "airborne",
                        snap,
                        beauty=True,
                        pose="ascent",
                        session=session,
                    )
                left_pad = True
            if _lofted(snap):
                lofted = True
            down = _down(snap, flown=left_pad) or litho
            sit_now = str(getattr(snap, "situation", "") or "").lower()
            splashed = sit_now in {"splashed"}
            landed_dry = sit_now in {"landed"}
            if wait_down and splashed:
                water_splashed = True
                if not said_down:
                    _say(
                        "hop-splash splash" if wait_splash else "hop-to-water splash",
                        on_log,
                    )
                    said_down = True
                break
            if wait_down and left_pad and landed_dry and not splashed:
                _release_steer(vessel)
                if not _recoverable(vessel):
                    _leave_crash_ui(session, on_log)
                raise MissionAbort("not splashed")

            if left_pad and _vessel_gone(snap, vessel):
                if _recoverable(vessel):
                    if not said_down:
                        _say("hop down", on_log)
                        said_down = True
                    got = _force_recover(vessel, on_log)
                    if got is not None:
                        return got
                if not said_crash:
                    _crash_line(vessel, snap, on_log)
                    said_crash = True
                abort_ksc_leftover(vessel, on_log, why="total wreck")

            if left_pad and not down:
                n_parts = _parts_n(vessel)
                mass_now = _snap_mass(snap)
                fuel_now = _snap_fuel(snap)
                why = stack_sheared(
                    prev_stack_mass,
                    mass_now,
                    prev_stack_fuel,
                    fuel_now,
                    prev_stack_parts,
                    n_parts,
                )
                if why:
                    _say(f"hop shear {why}", on_log)
                    ctx.notes.append("shear")
                    call("hold", ctx)
                    if _recoverable(vessel):
                        got = _recover_hd(vessel, on_log)
                        if got is not None:
                            return got
                    call("abort_pad", ctx)
                    raise MissionAbort("shear")
                if math.isfinite(mass_now):
                    prev_stack_mass = mass_now
                if math.isfinite(fuel_now):
                    prev_stack_fuel = fuel_now
                if n_parts is not None:
                    prev_stack_parts = n_parts

            for reason in gates(snap):
                if reason == "empty tanks" or reason.startswith("atmosphere"):
                    continue
                # Telem flags parts/mass 0 at impact as shear. Hop
                # stack_sheared decides; empty vessel is crash UI / gone.
                if reason == "shear":
                    continue
                if reason == "ec=0" and _vessel_gone(snap, vessel):
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
                    has = _keep_hd(
                        vessel, ids, started, left_pad=left_pad, lit=did_light
                    )
                    if has:
                        if wait_down and not splashed:
                            if left_pad and not waiting_hd:
                                _say("hop ec=0 wait splash", on_log)
                                log_events.emit("science_dwell", result="ec")
                            waiting_hd = True
                        else:
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
                    elif wait_down:
                        if left_pad and not waiting_hd:
                            _say("hop ec=0 wait splash (no science yet)", on_log)
                        waiting_hd = True
                    elif not left_pad or down:
                        call("abort_pad", ctx)
                        raise MissionAbort(reason)

            apo = getattr(snap, "apo", float("nan"))
            try:
                apo_f = float(apo)
            except (TypeError, ValueError):
                apo_f = float("nan")
            lid = FLYING_HIGH_M if wait_splash else hop_offplan_apo()
            label = (
                "Space"
                if wait_splash or hop_wants_flying_high()
                else "FlyingLow"
            )
            if hop_wants_flying_high() and not wait_splash:
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
                    _light(vessel, on_log, snap)
                    lit = True
                    did_light = True
                    log_events.emit("hop", result="light")
                    mission_event(
                        "light",
                        snap,
                        beauty=True,
                        pose="pad-plume",
                        session=session,
                    )

            if left_pad and not down:
                vz_now = _snap_v_vert(snap)
                met_now = float("nan")
                try:
                    met_now = float(getattr(snap, "met", float("nan")))
                except (TypeError, ValueError):
                    met_now = float("nan")
                dt_vz = None
                prev_vz = None
                if (
                    math.isfinite(vz_now)
                    and math.isfinite(prev_brake_vz)
                    and math.isfinite(prev_brake_met)
                    and math.isfinite(met_now)
                ):
                    dt_vz = met_now - prev_brake_met
                    prev_vz = prev_brake_vz
                was_braking = braking
                apo_cut, braking = _hold_or_cut(
                    vessel,
                    snap,
                    hop_apo,
                    cut=apo_cut,
                    hold=loft_hold,
                    brake=wait_down,
                    braking=braking,
                    prev_vz=prev_vz,
                    dt=dt_vz,
                    spent=suicide_spent,
                    hover=suicide_armed,
                )
                if wait_down and apo_cut and not suicide_spent and (
                    braking or suicide_armed
                ):
                    braking = _suicide_gate(
                        vessel,
                        snap,
                        sleep=nap,
                        now=clock,
                        telem=telem,
                        abort=abort,
                        hover=suicide_armed,
                    )
                if braking or was_braking:
                    suicide_armed = True
                if was_braking and not braking:
                    fuel_now = _snap_fuel(snap)
                    crumbs = (
                        not math.isfinite(fuel_now)
                        or fuel_now <= WATER_BRAKE_FUEL_MIN
                    )
                    if crumbs or _coast_ok(snap):
                        suicide_spent = True
                if math.isfinite(vz_now):
                    prev_brake_vz = vz_now
                if math.isfinite(met_now):
                    prev_brake_met = met_now

            leftover_lf = _snap_fuel(snap)
            burning_now = _burning(vessel, snap, lofted=lofted)
            aim_up = (
                wait_down
                and apo_cut
                and math.isfinite(leftover_lf)
                and leftover_lf > 0.0
            )
            if deaf:
                pass
            elif (braking or aim_up) and lit and not down and left_pad:
                _steer_brake(vessel)
                if braking and not said_brake:
                    label = "hop-splash" if wait_splash else "hop-to-water"
                    _say(f"{label} suicide leftover LF", on_log)
                    said_brake = True
            elif wait_water and lit and not down and left_pad:
                water_pitch, slewing = _slew_east_pitch(
                    water_pitch, _nap_dt(pulse, snap)
                )
                _steer_east(
                    vessel,
                    pitch=water_pitch,
                    flown_pitch=_snap_pitch(snap),
                    flown_heading=_snap_heading(snap),
                )
                if slewing and not apo_cut:
                    try:
                        vessel.control.throttle = WATER_SLEW_THROTTLE
                    except Exception:
                        pass
                    if not said_slew:
                        _say(
                            "hop-to-water slew pitch east after pad "
                            f"throttle={WATER_SLEW_THROTTLE:g}",
                            on_log,
                        )
                        said_slew = True
                elif not said_pitch:
                    _say(
                        f"hop-to-water pitch {WATER_PITCH_FROM_UP:g}° east",
                        on_log,
                    )
                    said_pitch = True
                if not burning_now and not said_hold:
                    _say("hop-to-water hold east through burnout", on_log)
                    said_hold = True
            elif not wait_down and lit and not down and left_pad:
                flown_p = _snap_pitch(snap)
                flown_h = _snap_heading(snap)
                try:
                    met_slew = float(getattr(snap, "met", float("nan")))
                except (TypeError, ValueError):
                    met_slew = float("nan")
                if not inland_yawed:
                    inland_yaw_n += 1
                inland_pitch, inland_yawed = _inland_cmd_pitch(
                    inland_yawed,
                    inland_yaw_n,
                    flown_p,
                    flown_h,
                    met_slew,
                )
                _steer_inland(
                    vessel,
                    pitch=inland_pitch,
                    flown_pitch=flown_p,
                    flown_heading=flown_h,
                    burning=burning_now,
                )
                if not said_slew:
                    _say(
                        "hop slew yaw inland after pad "
                        f"heading={INLAND_HEADING_DEG:g}",
                        on_log,
                    )
                    said_slew = True
                if inland_yawed and not said_pitch:
                    _say(
                        f"hop pitch {INLAND_PITCH_FROM_UP:g}° inland "
                        f"heading={INLAND_HEADING_DEG:g}",
                        on_log,
                    )
                    said_pitch = True
                if not burning_now and not said_hold:
                    _say("hop hold inland through burnout", on_log)
                    said_hold = True

            if left_pad and not down and not chute_open:
                st_now = str(getattr(snap, "chute", "") or "")
                if st_now in _CHUTE_OPEN:
                    chute_open = True
                else:
                    if not chute_armed:
                        st = arm_chutes(vessel, on_log)
                        chute_armed = True
                        if st in {"", "none"}:
                            chute_open = True
                        else:
                            _say(f"hop chute {st}", on_log)
                    if not chute_open and not burning_now and chute_deploy_sit(snap):
                        st = deploy_chutes(vessel, on_log)
                        if st in _CHUTE_OPEN:
                            chute_open = True
                        if not said_deploy and st not in {"", "none"}:
                            _say(f"hop chute {st}", on_log)
                            said_deploy = True
                            mission_event(
                                "chute",
                                snap,
                                beauty=True,
                                pose="chute-silk",
                                session=session,
                            )

            _apply_hop_physics(
                session,
                coast=_want_coast_phys(
                    snap,
                    left_pad=left_pad,
                    down=down,
                    chute_open=chute_open,
                    burning=burning_now,
                ),
                on_log=on_log,
                last=said_coast,
            )

            if left_pad and not down and not science_attempted and not wait_splash:
                if (not did_light) and _keep_hd(
                    vessel, ids, started, left_pad=True
                ):
                    science_attempted = True
                    _say("science keep HD", on_log)
                    log_events.emit("science", result="keep")
                    mission_event(
                        "science",
                        snap,
                        beauty=True,
                        pose="science",
                        session=session,
                    )
                    waiting_hd = True
                elif _science_ready(snap):
                    need = bound_science_need(
                        live_sit=_live_sit(vessel, snap),
                        live_biome=_snap_biome(snap, vessel),
                        alt=_snap_alt(snap),
                    )
                    started = _start_paying(vessel, ids, snap, on_log, need)
                    if started:
                        science_attempted = True
                        _say("science " + ",".join(started), on_log)
                        log_events.emit("science", ids=list(started))
                        mission_event(
                            "science",
                            snap,
                            beauty=True,
                            pose="science",
                            session=session,
                        )
                        _say("science dwell", on_log)
                        log_events.emit("science_dwell", phase="start")
                    elif ids and not card_slots(vessel, ids):
                        science_attempted = True
                        call("abort_pad", ctx)
                        raise MissionAbort("no science (wanted " + ",".join(ids) + ")")
                    elif ids:
                        _say("science skip (situation cannot pay)", on_log)
                elif hop_wants_flying_high() and not said_lid:
                    _say("science wait FlyingHigh", on_log)
                    said_lid = True

            missed_lid = (
                hop_wants_flying_high()
                and not wait_splash
                and did_light
                and not started
                and left_pad
                and down
            )
            if missed_lid:
                if not _recoverable(vessel):
                    _leave_crash_ui(session, on_log, total_wreck=True)
                call("abort_pad", ctx)
                raise MissionAbort("no science (FlyingHigh lid)")

            waiting_lid = (
                hop_wants_flying_high()
                and not wait_splash
                and did_light
                and not started
                and left_pad
                and not down
            )

            if left_pad and down and not wait_splash and not waiting_hd:
                need = bound_science_need(
                    live_sit=_live_sit(vessel, snap),
                    live_biome=_snap_biome(snap, vessel),
                )
                landed_ids = hop_landed_science_ids()
                pending = tuple(eid for eid in landed_ids if eid not in started)
                more = (
                    _start_paying(vessel, pending, snap, on_log, need)
                    if pending
                    else []
                )
                if more:
                    started.extend(more)
                    science_attempted = True
                    _say("science " + ",".join(more), on_log)
                    log_events.emit("science", ids=list(more))
                    mission_event(
                        "science",
                        snap,
                        beauty=True,
                        pose="science",
                        session=session,
                    )
                    _say("science dwell", on_log)
                    log_events.emit("science_dwell", phase="start")

            hold_card = _hold_ground_card(
                vessel, started, ids, snap, wait_splash=wait_splash
            )

            # First recoverable after flight — situation may stay flying.
            # hop-to-water / hop-splash must not recover here (kills splash dwell).
            # Do not hop-down a full tank at pad alt (still burning, not lofted).
            pad_boost = _pad_boosting(
                lit=did_light,
                left_pad=left_pad,
                lofted=lofted,
                down=down,
                burning=burning_now,
            )
            if waiting_lid or wait_down or hold_card:
                pass
            elif pad_boost:
                pass
            elif left_pad and _recoverable(vessel):
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
                    _wait_vessel_gone(session, other, on_log)
                    try:
                        go_space_center(session, reload_save=False)
                        _say("hop dismissed flight results", on_log)
                    except Exception as exc:
                        log.warning("hop dismiss flight results: %s", exc)
                    return hit

            met = _vessel_met(vessel)
            frozen = False
            if left_pad and not _recoverable(vessel):
                still_t0, frozen = _met_still(met, prev_met, still_t0, clock())
            else:
                still_t0 = None
            sit_now = str(getattr(snap, "situation", "") or "")
            if frozen and sit_now in _AIR and _q_zero(snap):
                litho = True
                down = True

            if down and left_pad:
                if not said_down:
                    _say("hop down", on_log)
                    said_down = True

            if (
                hop_wants_flying_high()
                and not wait_splash
                and did_light
                and not started
                and left_pad
                and down
            ):
                if not _recoverable(vessel):
                    _leave_crash_ui(session, on_log, total_wreck=True)
                call("abort_pad", ctx)
                raise MissionAbort("no science (FlyingHigh lid)")

            pad_boost = _pad_boosting(
                lit=did_light,
                left_pad=left_pad,
                lofted=lofted,
                down=down,
                burning=burning_now,
            )
            if waiting_lid or wait_down or hold_card:
                pass
            elif pad_boost:
                pass
            elif left_pad and (down or _low_flying(snap)):
                got = _force_recover(vessel, on_log)
                if got is not None:
                    return got

            if down and not left_pad:
                call("abort_pad", ctx)
                raise MissionAbort("wreck")

            if (
                left_pad
                and not said_crash
                and (waiting_hd or down or still_t0 is not None)
                and not _recoverable(vessel)
            ):
                _recover_tick(vessel, on_log)

            if frozen:
                sit_v = _vessel_sit(vessel)
                if _crash_ui(snap, vessel, frozen=True):
                    if not said_crash:
                        _crash_line(vessel, snap, on_log)
                        said_crash = True
                    got = _force_recover(vessel, on_log)
                    if got is not None:
                        return got
                    if not unpaused:
                        _unpause(session, on_log)
                        unpaused = True
                        unpause_at = clock()
                        still_t0 = None
                        continue
                    if (
                        unpause_at is not None
                        and clock() - unpause_at < _UNPAUSE_SETTLE_S
                    ):
                        still_t0 = None
                        nap(_nap_dt(pulse, snap, braking=braking))
                        continue
                    # Already unpaused, still no Recover — total wreck.
                    # Do not go_space_center (overlay is not leftover-clean).
                    _leave_crash_ui(session, on_log, total_wreck=True)
                    abort_ksc_leftover(vessel, on_log, why="total wreck")
                elif sit_v in _AIR:
                    if not unpaused:
                        _unpause(session, on_log)
                        unpaused = True
                        unpause_at = clock()
                    still_t0 = None
                elif not unpaused:
                    _unpause(session, on_log)
                    unpaused = True
                    unpause_at = clock()
                    still_t0 = None
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
            hover_hz = (
                wait_down
                and suicide_armed
                and not suicide_spent
                and not down
            )
            fast_brake = braking or hover_hz
            if pulses > 1 and elapsed >= budget:
                if wait_down and not splashed:
                    raise MissionAbort("not splashed")
                if left_pad:
                    got = _recover_hd(vessel, on_log)
                    if got is not None:
                        return got
                has = _keep_hd(
                    vessel, ids, started, left_pad=left_pad, lit=did_light
                )
                if has and left_pad and not down:
                    # Airborne/dead with HD: do not timeout-dump.
                    if not waiting_hd:
                        _say("hop wait recoverable", on_log)
                        waiting_hd = True
                    nap(_nap_dt(pulse, snap, braking=fast_brake))
                    continue
                if down and left_pad:
                    raise MissionAbort("not recoverable")
                _say(f"hop timeout {elapsed:.0f}s", on_log)
                raise MissionAbort("timeout")
            nap(_nap_dt(pulse, snap, braking=fast_brake))

    if wait_down and water_splashed:
        _release_steer(vessel)
        from splash import run_on_vessel as run_splash_vessel

        return run_splash_vessel(
            session,
            vessel,
            events=log_events,
            on_log=on_log,
            science_ids=splash_names,
            abort=abort,
            now=now,
            sleep=sleep,
            timeout=timeout,
            pulse=_PULSE_S if pulse is None else pulse,
        )
    raise MissionAbort("not splashed" if wait_down else "timeout")


def run_hop(
    session: object,
    *,
    on_log: Callable[[str], None] | None = None,
    abort: Callable[[], bool] | None = None,
) -> str:
    """``python main.py hop``: Hangar seated craft when pad empty, then light.

    Unmatched leftover aborts ``ksc leftover``. Do not recover-then-Hangar.
    """
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
    a second hop on that pad. Unmatched leftover aborts ``ksc leftover``
    (PRELAUNCH Flea vs seated Valiant) — Hank recover-probe, not hop recover.
    Do not fly leftover pad/geiger as a hop.
    Live kRPC hop ship only — FLYING Debris is not leftover.
    """
    leftover = _find_unmatched_leftover(session)
    if leftover is not None:
        _recover_unmatched_leftover(session, leftover, on_log)
        return run_hop(session, on_log=on_log, abort=abort)
    vessel = _find_hop_vessel(session)
    if vessel is not None and leftover_should_hangar_new(vessel):
        _recover_wreck_then_clear(session, vessel, on_log)
    if vessel is None or _is_pad_motor(vessel):
        return run_hop(session, on_log=on_log, abort=abort)
    _ensure_flight(session, vessel, on_log)
    live = _active_vessel(session)
    if live is not None and _is_hop_craft(live):
        vessel = live
    return run_on_vessel(session, vessel, on_log=on_log, abort=abort)


HOP_TO_WATER_ABORT = (
    "hop-to-water refused: Start Flea cannot steer to Water "
    "(Stayputnik has no torque, Flea has no gimbal). "
    "Cape Shores vertical hop lithobrakes Shores (18-32: 74 m). "
    "need_builder for east pitch, or skip splash"
)


def run_hop_to_water(
    session: object,
    *,
    on_log: Callable[[str], None] | None = None,
    abort: Callable[[], bool] | None = None,
) -> str:
    """Valiant: Hangar seated craft, slew 25° east after pad, wait splash.

    After left_pad, point set_direction_and_up heading 90 north-up; do
    not set target_roll=0. Do not slam AP 65 at light. Flea still
    refuses (no Hangar). Unmatched leftover and matching wreck leftover
    abort ``ksc leftover``. Matching living leftover enters Flight.
    Gate live sit/fuel/recoverable before light — disk PRELAUNCH is a
    lie. Do not recover on first flying recoverable. Pad sit=landed
    after light is hop-off — abort landed only after left_pad. Empty
    pad Hangars seated craft.
    """
    from session import SessionError

    try:
        name = hop_craft_name()
    except SessionError as exc:
        raise MissionAbort(str(exc)) from exc
    if not water_can_steer(name):
        _say(HOP_TO_WATER_ABORT, on_log)
        raise MissionAbort(HOP_TO_WATER_ABORT)
    flying, splash = hop_to_water_science()
    leftover = _find_unmatched_leftover(session)
    if leftover is not None:
        _recover_unmatched_leftover(session, leftover, on_log)
    vessel = _find_hop_vessel(session)
    if vessel is not None and leftover_should_hangar_new(vessel):
        _recover_wreck_then_clear(session, vessel, on_log)
        vessel = None
    if vessel is None or _is_pad_motor(vessel):
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
    else:
        _ensure_flight(session, vessel, on_log)
        live = _active_vessel(session)
        if live is not None and _is_hop_craft(live):
            vessel = live
    return run_on_vessel(
        session,
        vessel,
        on_log=on_log,
        abort=abort,
        science_ids=flying,
        wait_water=True,
        splash_ids=splash,
    )


HOP_SPLASH_ABORT = (
    "hop-splash refused: Start Flea cannot loft Cape Shores to Water "
    "(vertical hang lithobrakes Shores; 16-57-24Z east slew is dead). "
    "need t7-splash Valiant"
)

SPLASH_CRAFT = "kspstuff-hop-valiant-t7-splash-pbc"


def run_hop_splash(
    session: object,
    *,
    on_log: Callable[[str], None] | None = None,
    abort: Callable[[], bool] | None = None,
) -> str:
    """Valiant t7: Hangar seated craft, light vertical, wait splash dwell.

    No east slew. No flying Toggle. hop_apo 80 km is a real cut
    (stays cut; leftover LF suicide near Water, watch TTI ≤12,
    light at 3.5, kill then TWR≈1 hover until coast ≤ Goo 12).
    Flea refuses (no Hangar). Unmatched leftover (east-fin PRELAUNCH
    ghost) and wreck leftover abort ``ksc leftover``. Matching living
    leftover enters Flight. Empty pad Hangars. Gate live sit/fuel/
    recoverable before light.
    """
    from session import SessionError

    try:
        name = hop_craft_name()
    except SessionError as exc:
        raise MissionAbort(str(exc)) from exc
    if not water_can_steer(name):
        _say(HOP_SPLASH_ABORT, on_log)
        raise MissionAbort(HOP_SPLASH_ABORT)
    splash = hop_splash_science()
    leftover = _find_unmatched_leftover(session)
    if leftover is None:
        leftover = _find_hop_vessel(session)
    if leftover is not None:
        sit = _vessel_sit(leftover)
        n_exp = _experiment_count(leftover)
        wreck = n_exp == 0 or sit in {"pre_launch", "prelaunch"}
        if wreck:
            _recover_wreck_then_clear(session, leftover, on_log)
            leftover = None
    vessel = leftover
    if vessel is None or _is_pad_motor(vessel):
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
    else:
        _ensure_flight(session, vessel, on_log)
        live = _active_vessel(session)
        if live is not None and _is_hop_craft(live):
            vessel = live
    return run_on_vessel(
        session,
        vessel,
        on_log=on_log,
        abort=abort,
        science_ids=(),
        wait_splash=True,
        splash_ids=splash,
    )
