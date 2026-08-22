"""One-shot recover/crash sit. Never revert. Never Hangar."""

from __future__ import annotations

from hangar import _can_revert, dismiss_flight_results, game_scene, ksc_ready
from session import Session


def _sit(v: object) -> str:
    raw = getattr(v, "situation", None)
    name = getattr(raw, "name", None)
    if isinstance(name, str):
        return name.lower()
    return str(raw or "?")


def _enum(v: object, attr: str) -> str:
    raw = getattr(v, attr, None)
    name = getattr(raw, "name", None)
    if isinstance(name, str):
        return name.lower()
    return str(raw or "?")


def cmd_recover_probe(
    session: Session, *, recover: bool = False, space_center: bool = False
) -> int:
    sc = session.space_center
    scene = game_scene(session)
    ok, why = ksc_ready(session)
    revert = _can_revert(session)
    print(f"scene: {scene}", flush=True)
    print(f"ksc_ready: {ok} ({why})", flush=True)
    print(f"can_revert: {revert}", flush=True)
    for name in ("can_revert_to_launch", "can_revert_to_editor", "can_revert"):
        fn = getattr(sc, name, None)
        try:
            if callable(fn):
                print(f"{name}: {fn()}", flush=True)
            elif fn is not None:
                print(f"{name}: {fn}", flush=True)
        except Exception as exc:
            print(f"{name}: err {exc}", flush=True)
    vessels = []
    try:
        vessels = list(getattr(sc, "vessels", []) or [])
    except Exception as exc:
        print(f"vessels: err {exc}", flush=True)
    print(f"vessels n={len(vessels)}", flush=True)
    active = None
    try:
        active = sc.active_vessel
    except Exception:
        active = None
    try:
        print(f"active: {getattr(active, 'name', None)}", flush=True)
    except Exception as exc:
        print(f"active: dead ({exc})", flush=True)
    for v in vessels[:12]:
        name = getattr(v, "name", "?")
        sit = _sit(v)
        rec = bool(getattr(v, "recoverable", False))
        met = getattr(v, "met", None)
        fuel = None
        try:
            fuel = float(v.resources.amount("Kerosene"))
        except Exception:
            try:
                fuel = float(v.resources.amount("SolidFuel"))
            except Exception:
                fuel = None
        alt = None
        try:
            alt = float(v.flight().mean_altitude)
        except Exception:
            pass
        mark = " *" if v is active else ""
        print(
            f"  {name}{mark} sit={sit} recoverable={int(rec)} "
            f"met={met} fuel={fuel} alt={alt}",
            flush=True,
        )
    if space_center:
        print("dismiss flight results — not revert, no click", flush=True)
        msg = dismiss_flight_results(session)
        print(msg, flush=True)
        print(f"scene now {game_scene(session)}", flush=True)
        return 0
    if not recover:
        print("never revert_to_launch; pass --recover or --space-center", flush=True)
        return 0
    pad = None
    for v in vessels:
        try:
            rec = bool(getattr(v, "recoverable", False))
        except Exception:
            continue
        if not rec:
            continue
        sit = _sit(v)
        if sit in {"pre_launch", "prelaunch", "landed", "splashed"}:
            pad = v
            break
    if pad is None:
        print("recover: no recoverable leftover", flush=True)
        return 2
    name = getattr(pad, "name", "?")
    scene = game_scene(session)
    if scene != "flight":
        from hangar import go_flight

        print(f"enter flight from {scene} then recover() — not revert", flush=True)
        go_flight(session, pad)
        print(f"scene now {game_scene(session)} sit={_sit(pad)} met={getattr(pad, 'met', None)}", flush=True)
    print(f"recover() {name} sit={_sit(pad)} recoverable={int(bool(getattr(pad, 'recoverable', False)))}", flush=True)
    try:
        session.conn.krpc.paused = False
    except Exception:
        pass
    pad.recover()
    print("recover() returned", flush=True)
    return 0
