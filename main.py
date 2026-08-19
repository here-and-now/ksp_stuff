"""Agent CLI. No UI.

    python main.py status
    python main.py mun
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from collections import deque
from pathlib import Path

from hangar import game_scene
from mun import run_mission
from session import ConnectionSettings, Session, SessionError
from watch import FlightWatch, MissionAbort, freeze, heartbeat, recover_periapsis

log = logging.getLogger("kspstuff")

HANDOFF = Path("docs/last-flight.md")
_LINES: deque[str] = deque(maxlen=40)


def _log(msg: str) -> None:
    print(msg, flush=True)
    _LINES.append(msg)


def write_handoff(*, command: str, exit_code: int, abort: str | None = None) -> None:
    """Live handoff, jsonl close, and after-flight review under docs/flights/."""
    from datetime import datetime, timezone

    from crew import append_log, current_pilot
    from flightlog import close as log_close, path as log_path, stamp as log_stamp
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
    scene = game_scene(session)
    if session.active_vessel is None:
        _log(f"status scene={scene} no vessel")
        return 0
    with FlightWatch(session, on_log=_log) as watch:
        state = watch.pulse("status ", force_log=True)
        danger = state.danger()
        if danger:
            _log(f"GATE {danger}")
            return 3
        return 0


def cmd_recover(session: Session) -> int:
    from crew import current_pilot
    from flightlog import WriterLockError, release_lock, start

    crew = ""
    try:
        crew = current_pilot().name
    except Exception:
        pass
    try:
        from missions import assert_seated

        assert_seated(session)
        start("recover", crew=crew)
        try:
            recover_periapsis(session, extra=10_000.0, on_log=_log)
        except MissionAbort as exc:
            freeze(session)
            _log(f"ABORT {exc}")
            write_handoff(command="recover", exit_code=2, abort=str(exc))
            return 2
        write_handoff(command="recover", exit_code=0)
        return 0
    except WriterLockError as exc:
        _log(f"SESSION {exc}")
        return 1
    except SessionError as exc:
        _log(f"SESSION {exc}")
        return 1
    finally:
        release_lock()


def cmd_mun(session: Session, args: argparse.Namespace) -> int:
    from crew import current_pilot
    from flightlog import WriterLockError, release_lock, start

    t0 = time.monotonic()
    crew = ""
    try:
        crew = current_pilot().name
    except Exception:
        pass
    try:
        from missions import assert_seated, pad_kerbal_available

        if args.from_orbit:
            assert_seated(session)
        else:
            pad_kerbal_available(session)
            from missions import pad_craft_name

            pad_craft_name()
        start("mun", crew=crew)

        def abort() -> bool:
            return time.monotonic() - t0 > args.timeout

        try:
            run_mission(
                session,
                recover=not args.keep_debris,
                on_log=_log,
                abort=abort,
                from_orbit=bool(getattr(args, "from_orbit", False)),
            )
        except MissionAbort as exc:
            freeze(session)
            _log(f"ABORT {exc}")
            _log("Append a lesson to docs/lessons.md before the next attempt.")
            write_handoff(command="mun", exit_code=2, abort=str(exc))
            return 2
        except SessionError as exc:
            _log(f"SESSION {exc}")
            write_handoff(command="mun", exit_code=1, abort=f"SESSION {exc}")
            return 1
        heartbeat(session, _log, tag="done ")
        write_handoff(command="mun", exit_code=0)
        return 0
    except WriterLockError as exc:
        _log(f"SESSION {exc}")
        return 1
    except SessionError as exc:
        _log(f"SESSION {exc}")
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

        assert_seated(session)
        start(args.name, crew=crew)

        def abort() -> bool:
            if args.timeout <= 0:
                return False
            return time.monotonic() - t0 > args.timeout

        try:
            run(args.name, session, on_log=_log, abort=abort)
        except OffPlan as exc:
            freeze(session)
            _log(f"OFFPLAN {exc}")
            write_handoff(command=args.name, exit_code=4, abort=f"OFFPLAN {exc}")
            return 4
        except MissionAbort as exc:
            freeze(session)
            _log(f"ABORT {exc}")
            write_handoff(command=args.name, exit_code=2, abort=str(exc))
            return 2
        except SessionError as exc:
            _log(f"SESSION {exc}")
            write_handoff(command=args.name, exit_code=1, abort=f"SESSION {exc}")
            return 1
        heartbeat(session, _log, tag="done ")
        write_handoff(command=args.name, exit_code=0)
        return 0
    except WriterLockError as exc:
        _log(f"SESSION {exc}")
        return 1
    except SessionError as exc:
        _log(f"SESSION {exc}")
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
    sub.add_parser(
        "recover",
        help="Burn prograde until periapsis is above the atmosphere",
    )
    mun_p = sub.add_parser("mun", help="Pad compose (Hangar + ascent + Mun). Leftover crew: phase")
    mun_p.add_argument(
        "--timeout",
        type=float,
        default=2400.0,
        help="Wall-clock abort (seconds). Default 40 min.",
    )
    mun_p.add_argument(
        "--keep-debris",
        action="store_true",
        help="launch_vessel recover=False",
    )
    mun_p.add_argument(
        "--from-orbit",
        action="store_true",
        help="Do not Hangar a new stack. Fly the active vessel (don't abandon crew).",
    )
    ph = sub.add_parser("phase", help="Run one Gene-planned segment, then exit")
    ph.add_argument(
        "name",
        choices=("recover", "circularize", "tli", "soi", "capture", "land"),
    )
    ph.add_argument(
        "--timeout",
        type=float,
        default=0.0,
        help="Wall-clock abort (seconds). 0 = none (default).",
    )
    up = sub.add_parser("uplink", help="Gene → flying mun (no kRPC)")
    up.add_argument("verb", help="abort|freeze|hold|resume|capture|skip-warp|no-warp-pe|set")
    up.add_argument("rest", nargs="*", help="reason or `mun_pe 25000`")
    note_p = sub.add_parser("note", help="Append a line to docs/program/loop.md")
    note_p.add_argument("who")
    note_p.add_argument("text", nargs="+")
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
    args = parser.parse_args(argv)

    if args.cmd == "uplink":
        from uplink import write

        write(args.verb, " ".join(args.rest), who="Gene")
        print(f"uplink {args.verb} {' '.join(args.rest)}".rstrip(), flush=True)
        return 0
    if args.cmd == "note":
        from uplink import note

        note(args.who, " ".join(args.text))
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

    try:
        session = _connect(args)
    except SessionError as exc:
        print(exc, file=sys.stderr)
        return 1
    try:
        if args.cmd == "status":
            return cmd_status(session)
        if args.cmd == "recover":
            return cmd_recover(session)
        if args.cmd == "mun":
            return cmd_mun(session, args)
        if args.cmd == "phase":
            return cmd_phase(session, args)
        parser.error(f"unknown command {args.cmd}")
        return 2
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
