"""Agent CLI. No UI.

    python main.py world
    python main.py tech
    python main.py parts --unlocked
    python main.py status
    python main.py pad
    python main.py hop
    python main.py tech-unlock engineering101
    python main.py screenshot
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from collections import deque
from pathlib import Path

from hangar import game_scene
from session import ConnectionSettings, Session, SessionError
from telem import MissionAbort

log = logging.getLogger("kspstuff")

HANDOFF = Path("docs/last-flight.md")
_LINES: deque[str] = deque(maxlen=40)


def _log(msg: str) -> None:
    print(msg, flush=True)
    _LINES.append(msg)


def write_handoff(*, command: str, exit_code: int, abort: str | None = None) -> None:
    """Live last-flight, jsonl close, and after-flight review under logs/."""
    from datetime import datetime, timezone

    from crew import append_log, current_pilot
    from flightlog import (
        close as log_close,
        live_records,
        path as log_path,
        stamp as log_stamp,
    )

    if not live_records():
        return
    from review import write_review

    try:
        HANDOFF.parent.mkdir(parents=True, exist_ok=True)
        body = [
            f"command: {command}",
            f"exit: {exit_code}",
            f"abort: {abort or ''}",
            "last:",
        ]
        body.extend(f"  {line}" for line in _LINES)
        body.append("")
        text = "\n".join(body)
        HANDOFF.write_text(text, encoding="utf-8")
        stamp = log_stamp() or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%MZ")
        jsonl = log_path()
        if jsonl is not None:
            archive = jsonl.with_suffix(".md")
        else:
            archive = Path("docs/flights") / f"{stamp}-{command}.md"
        archive.parent.mkdir(parents=True, exist_ok=True)
        archive.write_text(text, encoding="utf-8")
        log_close()
        review_path = None
        if jsonl is not None:
            try:
                review_path = write_review(
                    jsonl,
                    command=command,
                    exit_code=exit_code,
                    abort=abort,
                    handoff=archive,
                )
            except Exception:
                log.debug("review failed", exc_info=True)
        try:
            person = current_pilot()
            note = f"{stamp} {command} exit={exit_code}"
            if abort:
                note += f" abort={abort}"
            note += f" → {archive.as_posix()}"
            if review_path is not None:
                note += f" review={review_path.as_posix()}"
            append_log(person, note)
        except Exception:
            log.debug("could not append crew log", exc_info=True)
    except Exception:
        log.debug("could not write %s", HANDOFF, exc_info=True)


def _connect(args: argparse.Namespace) -> Session:
    session = Session(
        ConnectionSettings(
            address=args.host,
            rpc_port=args.rpc_port,
            stream_port=args.stream_port,
        )
    )
    session.connect(profile=args.profile)
    return session


def cmd_status(session: Session) -> int:
    from telem import Telem, format_snapshot, gates

    scene = game_scene(session)
    with Telem(session, scene=scene) as telem:
        snap = telem.read()
    _log(format_snapshot(snap))
    danger = gates(snap)
    if danger:
        _log("gate " + "; ".join(danger))
        return 3
    return 0


def cmd_pad(session: Session, args: argparse.Namespace) -> int:
    from emergencies import Ctx, call as emergency_call
    from flightlog import WriterLockError, release_lock, start
    from pad import run_pad

    t0 = time.monotonic()
    try:
        from missions import pad_craft_name

        pad_craft_name()
        start("pad", crew="", session=session)

        def abort() -> bool:
            if args.timeout <= 0:
                return False
            return time.monotonic() - t0 > args.timeout

        try:
            result = run_pad(
                session,
                recover=not args.keep_debris,
                on_log=_log,
                abort=abort,
            )
        except MissionAbort as exc:
            emergency_call("hold", Ctx(session=session))
            _log(f"ABORT {exc}")
            write_handoff(command="pad", exit_code=2, abort=str(exc))
            return 2
        except SessionError as exc:
            _log(f"SESSION {exc}")
            write_handoff(command="pad", exit_code=1, abort=f"SESSION {exc}")
            return 1
        _log(result)
        write_handoff(command="pad", exit_code=0)
        return 0
    except WriterLockError as exc:
        _log(f"SESSION {exc}")
        return 1
    except SessionError as exc:
        _log(f"SESSION {exc}")
        write_handoff(command="pad", exit_code=1, abort=f"SESSION {exc}")
        return 1
    finally:
        release_lock()


def cmd_hop(session: Session, args: argparse.Namespace) -> int:
    from emergencies import Ctx, call as emergency_call
    from flightlog import WriterLockError, release_lock, start
    from hop import run_hop
    from phases import OffPlan

    t0 = time.monotonic()
    try:
        start("hop", crew="", session=session)

        def abort() -> bool:
            if args.timeout <= 0:
                return False
            return time.monotonic() - t0 > args.timeout

        try:
            result = run_hop(session, on_log=_log, abort=abort)
        except OffPlan as exc:
            emergency_call("hold", Ctx(session=session))
            _log(f"OFFPLAN {exc}")
            write_handoff(command="hop", exit_code=4, abort=f"OFFPLAN {exc}")
            return 4
        except MissionAbort as exc:
            emergency_call("hold", Ctx(session=session))
            _log(f"ABORT {exc}")
            write_handoff(command="hop", exit_code=2, abort=str(exc))
            return 2
        except SessionError as exc:
            _log(f"SESSION {exc}")
            write_handoff(command="hop", exit_code=1, abort=f"SESSION {exc}")
            return 1
        _log(result)
        write_handoff(command="hop", exit_code=0)
        return 0
    except WriterLockError as exc:
        _log(f"SESSION {exc}")
        return 1
    except SessionError as exc:
        _log(f"SESSION {exc}")
        write_handoff(command="hop", exit_code=1, abort=f"SESSION {exc}")
        return 1
    finally:
        release_lock()


def cmd_splash(session: Session, args: argparse.Namespace) -> int:
    from emergencies import Ctx, call as emergency_call
    from flightlog import WriterLockError, release_lock, start
    from splash import run_splash
    from phases import OffPlan

    t0 = time.monotonic()
    try:
        start("splash", crew="", session=session)

        def abort() -> bool:
            if args.timeout <= 0:
                return False
            return time.monotonic() - t0 > args.timeout

        try:
            result = run_splash(session, on_log=_log, abort=abort)
        except OffPlan as exc:
            emergency_call("hold", Ctx(session=session))
            _log(f"OFFPLAN {exc}")
            write_handoff(command="splash", exit_code=4, abort=f"OFFPLAN {exc}")
            return 4
        except MissionAbort as exc:
            emergency_call("hold", Ctx(session=session))
            _log(f"ABORT {exc}")
            write_handoff(command="splash", exit_code=2, abort=str(exc))
            return 2
        except SessionError as exc:
            _log(f"SESSION {exc}")
            write_handoff(command="splash", exit_code=1, abort=f"SESSION {exc}")
            return 1
        _log(result)
        write_handoff(command="splash", exit_code=0)
        return 0
    except WriterLockError as exc:
        _log(f"SESSION {exc}")
        return 1
    except SessionError as exc:
        _log(f"SESSION {exc}")
        write_handoff(command="splash", exit_code=1, abort=f"SESSION {exc}")
        return 1
    finally:
        release_lock()


def cmd_hop_to_water(session: Session, args: argparse.Namespace) -> int:
    from emergencies import Ctx, call as emergency_call
    from flightlog import WriterLockError, release_lock, start
    from hop import run_hop_to_water

    t0 = time.monotonic()
    try:
        start("hop-to-water", crew="", session=session)

        def abort() -> bool:
            if args.timeout <= 0:
                return False
            return time.monotonic() - t0 > args.timeout

        try:
            result = run_hop_to_water(session, on_log=_log, abort=abort)
        except MissionAbort as exc:
            emergency_call("hold", Ctx(session=session))
            _log(f"ABORT {exc}")
            write_handoff(command="hop-to-water", exit_code=2, abort=str(exc))
            return 2
        except SessionError as exc:
            _log(f"SESSION {exc}")
            write_handoff(command="hop-to-water", exit_code=1, abort=f"SESSION {exc}")
            return 1
        _log(result)
        write_handoff(command="hop-to-water", exit_code=0)
        return 0
    except WriterLockError as exc:
        _log(f"SESSION {exc}")
        return 1
    except SessionError as exc:
        _log(f"SESSION {exc}")
        write_handoff(command="hop-to-water", exit_code=1, abort=f"SESSION {exc}")
        return 1
    finally:
        release_lock()


def cmd_hop_splash(session: Session, args: argparse.Namespace) -> int:
    from emergencies import Ctx, call as emergency_call
    from flightlog import WriterLockError, release_lock, start
    from hop import run_hop_splash
    from phases import OffPlan

    t0 = time.monotonic()
    try:
        start("hop-splash", crew="", session=session)

        def abort() -> bool:
            if args.timeout <= 0:
                return False
            return time.monotonic() - t0 > args.timeout

        try:
            result = run_hop_splash(session, on_log=_log, abort=abort)
        except OffPlan as exc:
            emergency_call("hold", Ctx(session=session))
            _log(f"OFFPLAN {exc}")
            write_handoff(command="hop-splash", exit_code=4, abort=f"OFFPLAN {exc}")
            return 4
        except MissionAbort as exc:
            emergency_call("hold", Ctx(session=session))
            _log(f"ABORT {exc}")
            write_handoff(command="hop-splash", exit_code=2, abort=str(exc))
            return 2
        except SessionError as exc:
            _log(f"SESSION {exc}")
            write_handoff(command="hop-splash", exit_code=1, abort=f"SESSION {exc}")
            return 1
        _log(result)
        write_handoff(command="hop-splash", exit_code=0)
        return 0
    except WriterLockError as exc:
        _log(f"SESSION {exc}")
        return 1
    except SessionError as exc:
        _log(f"SESSION {exc}")
        write_handoff(command="hop-splash", exit_code=1, abort=f"SESSION {exc}")
        return 1
    finally:
        release_lock()


def cmd_ksc(session: Session) -> int:
    from flightlog import WriterLockError, release_lock, start
    from hangar import go_ksc

    try:
        start("ksc", crew="", session=session)
        msg = go_ksc(session)
        _log(msg)
        write_handoff(command="ksc", exit_code=0)
        return 0
    except WriterLockError as exc:
        _log(f"SESSION {exc}")
        return 1
    except SessionError as exc:
        _log(f"SESSION {exc}")
        write_handoff(command="ksc", exit_code=1, abort=f"SESSION {exc}")
        return 1
    finally:
        release_lock()


def cmd_load(session: Session, args: argparse.Namespace) -> int:
    from flightlog import WriterLockError, release_lock, start
    from hangar import load_save

    try:
        start("load", crew="", session=session)
        msg = load_save(session, getattr(args, "name", None) or "")
        _log(msg)
        write_handoff(command="load", exit_code=0)
        return 0
    except WriterLockError as exc:
        _log(f"SESSION {exc}")
        return 1
    except SessionError as exc:
        _log(f"SESSION {exc}")
        write_handoff(command="load", exit_code=1, abort=f"SESSION {exc}")
        return 1
    except Exception as exc:
        _log(f"SESSION {exc}")
        write_handoff(command="load", exit_code=1, abort=str(exc))
        return 1
    finally:
        release_lock()


def cmd_tech_unlock(session: Session, args: argparse.Namespace) -> int:
    from emergencies import Ctx, call as emergency_call
    from flightlog import WriterLockError, release_lock, start
    from tech_unlock import run_unlock

    t0 = time.monotonic()
    try:
        start("tech-unlock", crew="", session=session)

        def abort() -> bool:
            if args.timeout <= 0:
                return False
            return time.monotonic() - t0 > args.timeout

        try:
            result = run_unlock(
                session,
                getattr(args, "node", None),
                on_log=_log,
                abort=abort,
            )
        except MissionAbort as exc:
            emergency_call("hold", Ctx(session=session))
            _log(f"ABORT {exc}")
            write_handoff(command="tech-unlock", exit_code=2, abort=str(exc))
            return 2
        except SessionError as exc:
            _log(f"SESSION {exc}")
            write_handoff(command="tech-unlock", exit_code=1, abort=f"SESSION {exc}")
            return 1
        _log(result)
        write_handoff(command="tech-unlock", exit_code=0)
        return 0
    except WriterLockError as exc:
        _log(f"SESSION {exc}")
        return 1
    except SessionError as exc:
        _log(f"SESSION {exc}")
        write_handoff(command="tech-unlock", exit_code=1, abort=f"SESSION {exc}")
        return 1
    finally:
        release_lock()


def cmd_phase(session: Session, args: argparse.Namespace) -> int:
    from crew import current_pilot
    from flightlog import WriterLockError, release_lock, start
    from phases import OffPlan, run

    t0 = time.monotonic()
    crew = ""
    try:
        crew = current_pilot().name
    except Exception:
        pass
    try:
        from missions import assert_seated

        # Uncrewed PBC probe: no seated kerbal on the vessel; recover
        # deletes it — do not FlightWatch a missing ship.
        from phases import UNCREWED

        if args.name not in UNCREWED:
            assert_seated(session)
        start(
            args.name,
            crew="" if args.name in UNCREWED else crew,
            session=session,
        )

        def abort() -> bool:
            if args.timeout <= 0:
                return False
            return time.monotonic() - t0 > args.timeout

        try:
            run(args.name, session, on_log=_log, abort=abort)
        except OffPlan as exc:
            from emergencies import Ctx, call as emergency_call

            emergency_call("hold", Ctx(session=session))
            _log(f"OFFPLAN {exc}")
            write_handoff(command=args.name, exit_code=4, abort=f"OFFPLAN {exc}")
            return 4
        except MissionAbort as exc:
            from emergencies import Ctx, call as emergency_call

            emergency_call("hold", Ctx(session=session))
            _log(f"ABORT {exc}")
            write_handoff(command=args.name, exit_code=2, abort=str(exc))
            return 2
        except SessionError as exc:
            _log(f"SESSION {exc}")
            write_handoff(command=args.name, exit_code=1, abort=f"SESSION {exc}")
            return 1
        write_handoff(command=args.name, exit_code=0)
        return 0
    except WriterLockError as exc:
        _log(f"SESSION {exc}")
        return 1
    except SessionError as exc:
        _log(f"SESSION {exc}")
        write_handoff(command=args.name, exit_code=1, abort=f"SESSION {exc}")
        return 1
    finally:
        release_lock()


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Agent CLI for kRPC. UI is parked.",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--rpc-port", type=int, default=50000)
    parser.add_argument("--stream-port", type=int, default=50001)
    parser.add_argument(
        "--profile",
        choices=("auto", "stock", "rss"),
        default="auto",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status", help="Heartbeat line for the active vessel")
    pad_p = sub.add_parser(
        "pad",
        help="Pad compose: PBC probe + Kerbalism experiments (not hop)",
    )
    pad_p.add_argument(
        "--timeout",
        type=float,
        default=0.0,
        help="Wall-clock abort (seconds). 0 = none (default).",
    )
    pad_p.add_argument(
        "--keep-debris",
        action="store_true",
        help="launch_vessel recover=False",
    )
    hop_p = sub.add_parser(
        "hop",
        help="Sounding: Hangar Flea uncrewed, light, FlyingLow card, recover HD",
    )
    hop_p.add_argument(
        "--timeout",
        type=float,
        default=0.0,
        help="Wall-clock abort (seconds). 0 = none (default).",
    )
    splash_p = sub.add_parser(
        "splash",
        help="Splash goo: leftover hop Flea, wait Water, dwell, recover HD",
    )
    splash_p.add_argument(
        "--timeout",
        type=float,
        default=0.0,
        help="Wall-clock abort (seconds). 0 = none (default).",
    )
    water_p = sub.add_parser(
        "hop-to-water",
        help="Valiant slew 25° east after pad, wait Water splash (Flea refused)",
    )
    water_p.add_argument(
        "--timeout",
        type=float,
        default=0.0,
        help="Wall-clock abort (seconds). 0 = none (default).",
    )
    splash_loft_p = sub.add_parser(
        "hop-splash",
        help="t7 vertical loft, wait Water splash dwell (no east slew, no flying Toggle)",
    )
    splash_loft_p.add_argument(
        "--timeout",
        type=float,
        default=0.0,
        help="Wall-clock abort (seconds). 0 = none (default).",
    )
    tu_p = sub.add_parser(
        "tech-unlock",
        help="Spend science on a CTT node via kRPC (not GameData, not a pad sit)",
    )
    tu_p.add_argument(
        "node",
        nargs="?",
        default=None,
        help="RDNode id (engineering101). Default: plan tech:",
    )
    tu_p.add_argument(
        "--timeout",
        type=float,
        default=0.0,
        help="Wall-clock abort (seconds). 0 = none (default).",
    )
    load_p = sub.add_parser(
        "load",
        help="kRPC SpaceCenter.load of name.sfs (Mortimer after RD spend; not quickload)",
    )
    load_p.add_argument(
        "name",
        help="Save name without .sfs (rd-<node>, not persistent — F-014)",
    )
    sub.add_parser(
        "ksc",
        help="Leave Flight for Space Center (Mortimer after a bad focus; not a load)",
    )
    from phases import NAMES as PHASE_NAMES

    ph = sub.add_parser("phase", help="Run one Gene-planned segment, then exit")
    ph.add_argument("name", choices=PHASE_NAMES)
    ph.add_argument(
        "--timeout",
        type=float,
        default=0.0,
        help="Wall-clock abort (seconds). 0 = none (default).",
    )
    proto = sub.add_parser(
        "protocol",
        help="Fly gate / return parse (no kRPC)",
    )
    proto.add_argument("rest", nargs="*", help="fly | parse --desk <slug>")
    up = sub.add_parser("uplink", help="Gene → Commander (no kRPC)")
    up.add_argument(
        "verb",
        help="hold|cut|no_warp|stage|recover|science|abort_pad|freeze|abort|set|…",
    )
    up.add_argument("rest", nargs="*", help="reason or `mun_pe 25000`")
    note_p = sub.add_parser("note", help="Append a line to docs/program/loop.md")
    note_p.add_argument("who")
    note_p.add_argument("text", nargs="+")
    nt = sub.add_parser(
        "note-tech",
        help="Commander → Lars/Gus/Wernher (docs/program/note-tech.md)",
    )
    nt.add_argument("desk", help="Lars|Gus|Wernher|Gene")
    nt.add_argument("text", nargs="+")
    rev = sub.add_parser("review", help="Roll up a flight jsonl (no kRPC)")
    rev.add_argument("log", nargs="?", default=None, help="docs/flights/<stamp>-mun.jsonl")
    sub.add_parser("plan", help="Print docs/program/plan.md (Gene's numbers)")
    sub.add_parser("radio", help="Gene inbox: ship.md + uplink + loop (no kRPC)")
    brief_p = sub.add_parser("brief", help="Gene → seated mission briefing + loop")
    brief_p.add_argument("text", nargs="+")
    seat_p = sub.add_parser("seat", help="Point current.md at a mission dossier")
    seat_p.add_argument("who", help="flight id or roster string")
    sub.add_parser("missions", help="Print docs/missions/INDEX.md (no kRPC)")
    sub.add_parser("vab", help="Print VAB board + seated craft.md (no kRPC)")
    sub.add_parser("science", help="Print Linus board; career snapshot if connected")
    sub.add_parser(
        "science-scan",
        help="Open science at this tree (GameData Situation + save leftovers, no kRPC)",
    )
    sub.add_parser("world", help="KSP root, save, tree, science (no kRPC)")
    sub.add_parser(
        "desk",
        help="One disk snapshot for Gene/Linus/Gus/Lars packets (no kRPC)",
    )
    sub.add_parser(
        "sit-card",
        help="Write docs/program/sit-card.json for the seated sit (no kRPC)",
    )
    tech_p = sub.add_parser("tech", help="Disk tech tree + save unlocks (no kRPC)")
    tech_p.add_argument("node", nargs="?", default=None, help="RDNode id (start, basicRocketry, …)")
    parts_p = sub.add_parser("parts", help="Disk parts catalog (no kRPC)")
    parts_p.add_argument("--unlocked", action="store_true", help="Only parts on unlocked nodes")
    parts_p.add_argument("--node", default=None, help="TechRequired node id")
    parts_p.add_argument("--search", default=None, help="Substring on name/title/tech/category")
    parts_p.add_argument("--module", default=None, help="Module name substring (Experiment, ProceduralPart)")
    parts_p.add_argument(
        "--stack",
        action="store_true",
        help="Seated craft.md parts + hosted PAW experiments (not extra parts)",
    )
    parts_p.add_argument(
        "--craft",
        default=None,
        help="Path to a .craft file; list parts on that vehicle",
    )
    recp = sub.add_parser(
        "recover-probe",
        help="Print scene/revert/vessels after a crash. Never revert.",
    )
    recp.add_argument(
        "--recover",
        action="store_true",
        help="vessel.recover() leftover. Not revert_to_launch.",
    )
    recp.add_argument(
        "--space-center",
        action="store_true",
        help="Total wreck: Close to KSC. Not revert.",
    )
    shot_p = sub.add_parser(
        "screenshot",
        help="Capture the KSP window (no kRPC; works off-focus / other workspace)",
    )
    shot_p.add_argument(
        "--out",
        default=None,
        help="PNG path. Default screenshots/ksp-<utc>.png",
    )
    shot_p.add_argument(
        "--name",
        default=None,
        help="Stem under screenshots/ (never first-mystery-goo without --force)",
    )
    shot_p.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing PNG",
    )
    shot_p.add_argument(
        "--full",
        action="store_true",
        help="Compositor-fullscreen for the shot, then restore the tile",
    )
    args = parser.parse_args(argv)

    if args.cmd == "screenshot":
        from screenshot import cmd_screenshot

        return cmd_screenshot(
            Path(args.out) if args.out else None,
            force=bool(args.force),
            name=args.name,
            full=bool(args.full),
        )
    if args.cmd == "uplink":
        from uplink import write

        write(args.verb, " ".join(args.rest), who="Gene")
        print(f"uplink {args.verb} {' '.join(args.rest)}".rstrip(), flush=True)
        return 0
    if args.cmd == "note":
        from uplink import note

        note(args.who, " ".join(args.text))
        return 0
    if args.cmd == "note-tech":
        from uplink import note_tech

        path = note_tech(args.desk, " ".join(args.text), who="Jebediah")
        print(f"note-tech {path}", flush=True)
        return 0
    if args.cmd == "review":
        from review import latest_jsonl, write_review

        jsonl = Path(args.log) if args.log else latest_jsonl()
        if jsonl is None or not jsonl.is_file():
            print("no flight jsonl", file=sys.stderr)
            return 1
        out = write_review(
            jsonl,
            command=jsonl.stem.split("-")[-1],
            exit_code=-1,
            abort=None,
            handoff=HANDOFF if HANDOFF.is_file() else None,
        )
        print(out.as_posix(), flush=True)
        return 0
    if args.cmd == "radio":
        from uplink import radio_text

        print(radio_text(), end="")
        return 0
    if args.cmd == "plan":
        from missions import seated_plan_path

        path = seated_plan_path()
        text = path.read_text(encoding="utf-8")
        print(text, end="" if text.endswith("\n") else "\n")
        return 0
    if args.cmd == "brief":
        from missions import seated_briefing_path, seated_id, sync_shim
        from uplink import note

        body = " ".join(args.text)
        path = seated_briefing_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"# Briefing — Gene → {seated_id()}\n\n" + body.strip() + "\n",
            encoding="utf-8",
        )
        note("Gene", body)
        try:
            sync_shim()
        except Exception:
            pass
        print("briefed", flush=True)
        return 0
    if args.cmd == "seat":
        from missions import seat

        try:
            fid = seat(args.who)
        except Exception as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(f"seated {fid}", flush=True)
        return 0
    if args.cmd == "missions":
        from missions import index_text, write_index

        write_index()
        print(index_text(), end="")
        return 0
    if args.cmd == "vab":
        from missions import VAB_PATH, seated_craft_path, seated_id

        bits = []
        if VAB_PATH.is_file():
            bits.append(VAB_PATH.read_text(encoding="utf-8").rstrip())
        craft = seated_craft_path()
        bits.append(f"\n# seated {seated_id()} craft.md")
        if craft.is_file():
            bits.append(craft.read_text(encoding="utf-8").rstrip())
        print("\n".join(bits) + "\n", end="")
        try:
            from world import WorldError, craft_part_names, format_stack, load_world

            world = load_world()
            names = craft_part_names(craft.read_text(encoding="utf-8") if craft.is_file() else "")
            print(format_stack(world, names, label=f"seated {seated_id()}"), end="")
        except WorldError as exc:
            print(f"# catalog: {exc}", flush=True)
        return 0
    if args.cmd == "protocol":
        from protocol import cmd_protocol

        return cmd_protocol(list(args.rest))
    if args.cmd == "desk":
        from desk import format_desk
        from world import WorldError

        try:
            print(format_desk(), end="")
        except WorldError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        return 0
    if args.cmd == "sit-card":
        from desk import sit_card
        from world import WorldError

        try:
            card = sit_card()
        except WorldError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(json.dumps(card, indent=2))
        return 0
    if args.cmd in {"world", "tech", "parts"}:
        from world import (
            WorldError,
            craft_part_names,
            filter_parts,
            format_parts,
            format_stack,
            format_tech,
            format_world,
            load_world,
        )

        try:
            world = load_world()
        except WorldError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        if args.cmd == "world":
            print(format_world(world), end="")
            return 0
        if args.cmd == "tech":
            print(format_tech(world, args.node), end="")
            return 0
        if args.cmd == "parts" and (args.stack or args.craft):
            if args.craft:
                path = Path(args.craft)
                label = path.as_posix()
                text = path.read_text(encoding="utf-8") if path.is_file() else ""
            else:
                from missions import seated_craft_path, seated_id

                path = seated_craft_path()
                label = f"seated {seated_id()} craft.md"
                text = path.read_text(encoding="utf-8") if path.is_file() else ""
            names = craft_part_names(text)
            print(format_stack(world, names, label=label), end="")
            return 0
        parts = filter_parts(
            world,
            unlocked=bool(args.unlocked),
            node=args.node,
            search=args.search,
            module=args.module,
        )
        print(
            format_parts(
                world,
                parts,
                search=args.search,
                unlocked=bool(args.unlocked),
            ),
            end="",
        )
        return 0
    if args.cmd == "science-scan":
        from science_scan import format_science_scan
        from world import WorldError, load_world

        try:
            print(format_science_scan(load_world()), end="")
        except WorldError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        return 0
    if args.cmd == "science":
        from missions import SCIENCE_PATH, seated_id, seated_science_path

        bits = []
        if SCIENCE_PATH.is_file():
            bits.append(SCIENCE_PATH.read_text(encoding="utf-8").rstrip())
        card = seated_science_path()
        bits.append(f"\n# seated {seated_id()} science.md")
        if card.is_file():
            bits.append(card.read_text(encoding="utf-8").rstrip())
        print("\n".join(bits) + "\n", end="")
        try:
            from world import WorldError, format_world, load_world

            print(format_world(load_world()), end="")
        except WorldError as exc:
            print(f"WORLD (no disk) {exc}", flush=True)
        from flightlog import writer_lock_live

        if writer_lock_live():
            print("SESSION flight.lock live — no career probe", flush=True)
            return 1
        try:
            session = _connect(args)
        except SessionError as exc:
            print(f"CAREER (no probe) {exc}", flush=True)
            return 0
        try:
            from career import snapshot_career

            snap = snapshot_career(session)
            print(
                f"CAREER mode={snap.game_mode} science={snap.science} "
                f"funds={snap.funds} rep={snap.reputation}",
                flush=True,
            )
        except Exception as exc:
            print(f"CAREER (no probe) {exc}", flush=True)
        finally:
            session.close()
        return 0

    if args.cmd == "status":
        from flightlog import writer_lock_live

        if writer_lock_live():
            print("SESSION flight.lock live — no second Session", file=sys.stderr)
            return 1
    try:
        session = _connect(args)
    except SessionError as exc:
        print(exc, file=sys.stderr)
        return 1
    try:
        if args.cmd == "status":
            return cmd_status(session)
        if args.cmd == "recover-probe":
            from recover_probe import cmd_recover_probe

            return cmd_recover_probe(
                session,
                recover=bool(getattr(args, "recover", False)),
                space_center=bool(getattr(args, "space_center", False)),
            )
        if args.cmd == "pad":
            return cmd_pad(session, args)
        if args.cmd == "hop":
            return cmd_hop(session, args)
        if args.cmd == "splash":
            return cmd_splash(session, args)
        if args.cmd == "hop-to-water":
            return cmd_hop_to_water(session, args)
        if args.cmd == "hop-splash":
            return cmd_hop_splash(session, args)
        if args.cmd == "tech-unlock":
            return cmd_tech_unlock(session, args)
        if args.cmd == "load":
            return cmd_load(session, args)
        if args.cmd == "ksc":
            return cmd_ksc(session)
        if args.cmd == "phase":
            return cmd_phase(session, args)
        parser.error(f"unknown command {args.cmd}")
        return 2
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
