"""kRPC 0.6 science experiments. Run and keep; never transmit.

``vessel.parts.experiments`` → ``Experiment`` (name, available, has_data,
run, reset, dump, transmit). EVA hatch is not wired — skip evaReport /
surfaceSample. Goo is one-shot; crew reports are rerunnable.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Iterable

log = logging.getLogger("kspstuff")

# Need a kerbal on EVA. Do not invent hatch APIs.
EVA_EXPERIMENTS = frozenset({"evaReport", "surfaceSample", "evaScience"})

# First pad hop card. Other parts run only if the caller names them.
HOP_EXPERIMENTS = ("crewReport", "mysteryGoo")

_SKIP_EVENTS = ("reset", "discard", "transmit", "review", "collect", "store")


def experiment_name(exp: Any) -> str:
    try:
        return str(exp.name or "")
    except Exception:
        return ""


def list_experiments(vessel: Any) -> list[Any]:
    try:
        return list(vessel.parts.experiments)
    except Exception:
        log.debug("vessel.parts.experiments failed", exc_info=True)
        return []


def describe(exp: Any) -> str:
    name = experiment_name(exp) or "?"
    bits = [name]
    for key in ("title", "biome", "available", "has_data", "inoperable", "rerunnable"):
        try:
            bits.append(f"{key}={getattr(exp, key)}")
        except Exception:
            continue
    try:
        bits.append(f"part={exp.part.name}")
    except Exception:
        pass
    return " ".join(bits)


def _flag(exp: Any, name: str) -> bool:
    try:
        return bool(getattr(exp, name))
    except Exception:
        return False


def _trigger_rerun(exp: Any) -> bool:
    """Second crew report after Keep: Run() refuses has_data. No dump."""
    try:
        modules = list(exp.part.modules)
    except Exception:
        return False
    for module in modules:
        if getattr(module, "name", "") != "ModuleScienceExperiment":
            continue
        try:
            for ev in module.event_list:
                gui = (getattr(ev, "gui_name", None) or "").lower()
                if any(word in gui for word in _SKIP_EVENTS):
                    continue
                if not getattr(ev, "active", False):
                    continue
                ev.trigger()
                return True
        except Exception:
            pass
        try:
            for ev_name in module.events:
                low = str(ev_name).lower()
                if any(word in low for word in _SKIP_EVENTS):
                    continue
                module.trigger_event(ev_name)
                return True
        except Exception:
            continue
    return False


def run_ready(
    vessel: Any,
    *,
    names: Iterable[str] | None = None,
    on_log: Callable[[str], None] | None = None,
) -> list[str]:
    """Run available experiments. Keep data. Never transmit. Skip EVA."""
    want = {n.strip() for n in names} if names is not None else None
    done: list[str] = []

    def _say(msg: str) -> None:
        log.info(msg)
        if on_log:
            on_log(msg)

    for exp in list_experiments(vessel):
        name = experiment_name(exp)
        if not name:
            continue
        if name in EVA_EXPERIMENTS:
            _say(f"science skip {name} (EVA)")
            continue
        if want is not None and name not in want:
            continue
        if _flag(exp, "inoperable"):
            _say(f"science skip {describe(exp)} inoperable")
            continue
        has_data = _flag(exp, "has_data")
        available = _flag(exp, "available")
        if has_data and not _flag(exp, "rerunnable"):
            _say(f"science keep {describe(exp)}")
            continue
        if not available and not has_data:
            _say(f"science skip {describe(exp)} unavailable")
            continue
        try:
            if has_data and _flag(exp, "rerunnable"):
                if not _trigger_rerun(exp):
                    _say(f"science skip {describe(exp)} has_data")
                    continue
            else:
                exp.run()
        except Exception as exc:
            _say(f"science fail {name}: {exc}")
            continue
        line = f"science ran {describe(exp)}"
        _say(line)
        done.append(name)
    return done
