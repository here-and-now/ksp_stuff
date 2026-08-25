"""kRPC 0.6 science experiments. Run and keep; never transmit.

Stock leftover: ``vessel.parts.experiments`` → ``Experiment.run``.
Kerbalism pad/hop: ``part.modules`` named ``Experiment``, started via
events — not ``Experiment.run``. Splash wreck may drop those modules;
Stayputnik TELEMETRY PAW and GooExperiment still start. ``Module.fields`` is PAW gui names;
``experiment_id`` is a hidden field (``field_list`` / ``get_field_by_id``
/ ``config``). Pad dwells until HD has the card (status / Has Data /
remaining, else cfg ``data_rate`` × ScienceDefs size, capped by remaining
EC / ``ec_rate``). Hop FlyingLow starts the **bound** flying card once airborne; FlyingHigh
Toggles only at alt ≥50 km (not T+1 FlyingLow; not a second Toggle
at the lid). Unbound leftover FlyingHigh tickets are not a lid.
Do not start an experiment whose situation cannot pay (sample remaining=0,
or bound sit/biome ≠ live sit/biome — 17-23-34Z SrfLanded bound Toggled
FlyingLow rem=0). Splash goo is not a hop start. Stop running slots
before ``vessel.recover()`` so leftover rem Kerbalism already recorded
lands in R&D (17-23-34Z Forest leftover 0.742→0.690, bank +0). Recovers when
landed/splashed/wreck-recoverable, or when EC=0 and the HD already
has data — it does not wait the pad catalog wall. One Toggle per experiment_id; 2HOT owns ``temperatureScan``,
not Stayputnik (a second Toggle stops Kerbalism). A leftover with files
on ``HardDrive`` (or no Experiment modules left) recovers without a
second Toggle. A new Hangar still
starts the flying card: idle remaining=0 is not leftover data. A paused
Flight Results wreck (MET frozen, recoverable never true) recovers hop
debris or leaves flight so the HD banks. EVA hatch is not wired
— skip evaReport / surfaceSample.
"""

from __future__ import annotations

import logging
import math
from typing import Any, Callable, Iterable

from card import HOP_EXPERIMENTS, PAD_EXPERIMENTS, SPLASH_EXPERIMENTS

log = logging.getLogger("kspstuff")

# Need a kerbal on EVA. Do not invent hatch APIs.
EVA_EXPERIMENTS = frozenset({"evaReport", "surfaceSample", "evaScience"})

_SKIP_EVENTS = (
    "reset",
    "discard",
    "transmit",
    "review",
    "collect",
    "store",
    "stop",
    "pause",
)
_START_EVENTS = (
    "Start Experiment",
    "Start experiment",
    "Start",
    "Run Experiment",
    "Run",
    "Deploy",
    "Toggle",
    "ToggleEvent",
    "RunEvent",
    "StartAction",
)
_KERBALISM_MODULES = frozenset({"Experiment", "ModuleScienceExperiment"})
_KERBALISM_MODULE_ALIASES = frozenset({"moduleksmexperiment", "kerbalismexperiment"})
# Duration experiments sit at remaining=0 before a fresh start. Sample rem=0
# (goo) cannot pay this sit. File duration rem=0 (TELEMETRY, 2HOT, PresMat,
# geiger) still needs a sit/biome match. FlyingHigh is alt ≥50 km, not any
# flying sit (1 km loft is FlyingLow). TELEMETRY-family often has no rem PAW
# while the file is still open; 2HOT / PresMat expose remaining.
_FLYING_HIGH_ALT_M = 50_000.0
_KERBALISM_FILE_EIDS = frozenset(
    {
        "kerbalism_TELEMETRY",
        "kerbalism_LITE",
        "kerbalism_MITE",
        "kerbalism_SITE",
    }
)
_DURATION_EIDS = _KERBALISM_FILE_EIDS | {
    "temperatureScan",
    "geigerCounter",
    "barometerScan",
}
# Sample rem=0 is spent. File rem=0 still pays even when the eid is new.
_SAMPLE_EIDS = frozenset({"mysteryGoo", "surfaceSample", "evaScience"})
_DRIVE_MODULES = frozenset({"HardDrive", "harddrive"})
_EMPTY_DRIVE = frozenset(
    {
        "",
        "empty",
        "none",
        "0",
        "0.0",
        "n/a",
        "-",
        "no data",
        "nodata",
        "no files",
        "nofiles",
        "0 files",
        "0 file",
        "false",
        "no",
    }
)
_DRIVE_DATA_KEYS = (
    "Data",
    "data",
    "Files",
    "files",
    "stored",
    "FilesSize",
    "fileSize",
    "used",
)
# kRPC part.name (uid stripped). Used when experiment_id is not a PAW field.
_PART_EXPERIMENTS = {
    "GooExperiment": "mysteryGoo",
    "sensorThermometer": "temperatureScan",
    "sensorBarometer": "barometerScan",
    "kerbalism-geigercounter": "geigerCounter",
    "probeCoreSphere_v2": "kerbalism_TELEMETRY",
    "probeCoreSphere": "kerbalism_TELEMETRY",
}
_EID_KEYS = ("experiment_id", "experimentID", "experiment")
_DONE_STATUS = (
    "done",
    "complete",
    "completed",
    "depleted",
    "finished",
    "recorded",
    "has data",
    "reset required",
)
_RUNNING_STATUS = (
    "running",
    "recording",
    "measuring",
    "in progress",
    "started",
    "waiting",
    "forced",
)
_HAS_DATA_KEYS = ("Has Data", "has_data", "HasData", "hasData")
_REMAIN_KEYS = (
    "remainingSampleMass",
    "remaining",
    "sample remaining",
    "data remaining",
    "Science Remaining",
    "remaining_mass",
)
DEFAULT_PAD_DWELL_S = 900.0
# Recover before the last fifth of the battery so the probe stays commandable.
PAD_EC_MARGIN = 0.8


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


def _attr(obj: Any, name: str, default: Any = None) -> Any:
    try:
        return getattr(obj, name)
    except Exception:
        return default


def _is_science_module(name: str) -> bool:
    n = (name or "").strip()
    if not n:
        return False
    if n in _KERBALISM_MODULES:
        return True
    low = n.lower()
    return low in {m.lower() for m in _KERBALISM_MODULES} or low in _KERBALISM_MODULE_ALIASES


def _module_has_start(module: Any) -> bool:
    try:
        names = list(_attr(module, "events") or [])
    except Exception:
        names = []
    try:
        event_list = list(_attr(module, "event_list") or [])
    except Exception:
        event_list = []
    for ev in event_list:
        gui = str(_attr(ev, "gui_name", "") or "")
        ident = str(_attr(ev, "name", "") or "")
        if _matches_start(gui) or _matches_start(ident):
            return True
    return any(_matches_start(str(n)) for n in names)


def _is_drive_module(name: str) -> bool:
    n = (name or "").strip()
    if not n:
        return False
    low = n.lower()
    if low in _DRIVE_MODULES:
        return True
    return "harddrive" in low


def _part_experiment_id(part: Any) -> str:
    raw = str(_attr(part, "name", "") or "")
    if not raw:
        return ""
    token = raw.replace(".", "_")
    stem = token.split("_")[0]
    return (
        _PART_EXPERIMENTS.get(raw)
        or _PART_EXPERIMENTS.get(token)
        or _PART_EXPERIMENTS.get(stem)
        or ""
    )


def module_field(module: Any, *keys: str) -> Any:
    """Module field by stable id, then cfg, then PAW gui name.

    kRPC 0.6 ``Module.fields`` / ``get_field`` are visible gui names and
    throw on duplicate names. Kerbalism ``experiment_id`` is not guiActive.
    """
    if not keys:
        return None
    want = {k.lower() for k in keys}

    try:
        flist = list(_attr(module, "field_list") or [])
    except Exception:
        flist = []
    for field in flist:
        fname = str(_attr(field, "name", "") or "")
        if fname.lower() not in want:
            continue
        val = _attr(field, "value")
        if val is not None and str(val) != "":
            return val

    getter_id = _attr(module, "get_field_by_id")
    if callable(getter_id):
        for key in keys:
            try:
                val = getter_id(key)
            except Exception:
                continue
            if val is not None and str(val) != "":
                return val

    try:
        by_id = _attr(module, "fields_by_id")
    except Exception:
        by_id = None
    if isinstance(by_id, dict):
        for key in keys:
            if key in by_id and by_id[key] not in (None, ""):
                return by_id[key]
            for dk, dv in by_id.items():
                if str(dk).lower() == key.lower() and dv not in (None, ""):
                    return dv

    cfg = _attr(module, "config")
    if cfg is not None:
        try:
            values = _attr(cfg, "values")
        except Exception:
            values = None
        if isinstance(values, dict):
            for key in keys:
                if key in values and values[key] not in (None, ""):
                    return values[key]
        getter = _attr(cfg, "get_value")
        if callable(getter):
            for key in keys:
                try:
                    val = getter(key)
                except Exception:
                    continue
                if val not in (None, ""):
                    return val

    try:
        fields = _attr(module, "fields")
    except Exception:
        fields = None
    if isinstance(fields, dict):
        for key in keys:
            if key in fields and fields[key] not in (None, ""):
                return fields[key]
            for dk, dv in fields.items():
                if str(dk).lower() == key.lower() and dv not in (None, ""):
                    return dv

    getter = _attr(module, "get_field")
    if callable(getter):
        for key in keys:
            try:
                val = getter(key)
            except Exception:
                continue
            if val not in (None, ""):
                return val

    for key in keys:
        val = _attr(module, key)
        if val is not None and not callable(val) and str(val) != "":
            return val
    return None


def _skip_event(text: str) -> bool:
    low = text.lower()
    return any(word in low for word in _SKIP_EVENTS)


def _matches_start(text: str) -> bool:
    low = text.lower()
    if _skip_event(low):
        return False
    return any(want.lower() == low or want.lower() in low for want in _START_EVENTS)


def _part_name(part: Any) -> str:
    return str(_attr(part, "name", "") or "")


def _part_stem(part: Any) -> str:
    raw = _part_name(part)
    token = raw.replace(".", "_")
    return token.split("_")[0] if token else ""


def _slot_rank(part: Any, eid: str) -> int:
    """Lower wins. Native Science part; Stayputnik PAW is a duplicate host."""
    stem = _part_stem(part)
    pname = _part_name(part).lower().replace("_", "-")
    mapped = _PART_EXPERIMENTS.get(stem) or _PART_EXPERIMENTS.get(
        stem.replace("_", "-")
    )
    if mapped == eid:
        return 0
    if eid == "temperatureScan" and "thermometer" in pname:
        return 0
    if eid == "barometerScan" and "barometer" in pname:
        return 0
    if eid == "mysteryGoo" and "goo" in stem.lower():
        return 0
    if eid == "geigerCounter" and "geiger" in pname:
        return 0
    if eid.startswith("kerbalism_") and "probe" in pname:
        return 0
    if eid in {"temperatureScan", "geigerCounter"} and "probe" in pname:
        return 2
    return 1


def _mod_name(module: Any) -> str:
    return str(_attr(module, "name", "") or "")


def _slot_key(part: Any, module: Any, eid: str) -> tuple:
    """Stable identity: kRPC Module proxies from parts.all vs modules_with_name
    are different Python objects (id() does not dedupe)."""
    token = str(eid or "").strip()
    if token:
        return (_part_name(part), token)
    return (_part_name(part), _mod_name(module), "")


def _is_kerbalism_experiment(module: Any) -> bool:
    n = _mod_name(module)
    if n == "Experiment":
        return True
    return n.lower() in _KERBALISM_MODULE_ALIASES


def _already_running(module: Any) -> bool:
    """Kerbalism Toggle starts *and* stops. Do not fire if already running."""
    try:
        event_list = list(_attr(module, "event_list") or [])
    except Exception:
        event_list = []
    for ev in event_list:
        gui = str(_attr(ev, "gui_name", "") or "")
        ident = str(_attr(ev, "name", "") or "")
        blob = f"{gui} {ident}".lower()
        if not any(w in blob for w in ("stop", "pause")):
            continue
        if _attr(ev, "active") is True:
            return True
    status = module_field(module, "status", "Status", "state", "State")
    if status is None:
        return False
    low = str(status).lower()
    return any(w in low for w in ("running", "recording", "measuring", "in progress"))


def _start_rank(text: str) -> int:
    """Prefer Start/Run/Deploy over Toggle (Toggle is start *and* stop)."""
    if not text or _skip_event(text):
        return 99
    if not _matches_start(text):
        return 99
    return 1 if "toggle" in text.lower() else 0


def _trigger_module(module: Any) -> bool:
    try:
        event_list = list(_attr(module, "event_list") or [])
    except Exception:
        event_list = []
    names: list[str] = []
    for ev in event_list:
        gui = str(_attr(ev, "gui_name", "") or "")
        ident = str(_attr(ev, "name", "") or "")
        if gui:
            names.append(gui)
        if ident and ident not in names:
            names.append(ident)
    try:
        events = list(_attr(module, "events") or [])
    except Exception:
        events = []
    names.extend(str(x) for x in events)
    event_list = sorted(
        event_list,
        key=lambda ev: min(
            _start_rank(str(_attr(ev, "gui_name", "") or "")),
            _start_rank(str(_attr(ev, "name", "") or "")),
        ),
    )
    names = sorted(names, key=_start_rank)

    for ev in event_list:
        gui = str(_attr(ev, "gui_name", "") or "")
        ident = str(_attr(ev, "name", "") or "")
        if _matches_start(gui) or _matches_start(ident):
            trig = _attr(ev, "trigger")
            if callable(trig):
                try:
                    trig()
                    return True
                except Exception:
                    pass

    for ev_name in names:
        if not _matches_start(ev_name):
            continue
        trigger = _attr(module, "trigger_event")
        if callable(trigger):
            try:
                trigger(ev_name)
                return True
            except Exception:
                pass
        by_id = _attr(module, "trigger_event_by_id")
        if callable(by_id):
            try:
                by_id(ev_name)
                return True
            except Exception:
                pass
        has_ev = _attr(module, "has_event")
        if callable(has_ev):
            try:
                if has_ev(ev_name):
                    module.trigger_event(ev_name)
                    return True
            except Exception:
                pass

    # Bare Experiment: first non-skip event (often Toggle / ToggleEvent).
    for ev in event_list:
        gui = str(_attr(ev, "gui_name", "") or "")
        ident = str(_attr(ev, "name", "") or "")
        if _skip_event(gui) or _skip_event(ident):
            continue
        trig = _attr(ev, "trigger")
        if callable(trig):
            try:
                trig()
                return True
            except Exception:
                continue
    for ev_name in names:
        if _skip_event(ev_name):
            continue
        trigger = _attr(module, "trigger_event")
        if callable(trigger):
            try:
                trigger(ev_name)
                return True
            except Exception:
                continue
        by_id = _attr(module, "trigger_event_by_id")
        if callable(by_id):
            try:
                by_id(ev_name)
                return True
            except Exception:
                continue
    return False


def _trigger_stop(module: Any) -> bool:
    """Fire Stop/Pause. Never Toggle (Toggle starts a stopped slot)."""
    try:
        event_list = list(_attr(module, "event_list") or [])
    except Exception:
        event_list = []
    ranked: list[tuple[int, Any]] = []
    for ev in event_list:
        gui = str(_attr(ev, "gui_name", "") or "")
        ident = str(_attr(ev, "name", "") or "")
        blob = f"{gui} {ident}".lower()
        if "toggle" in blob:
            continue
        rank = 0 if "stop" in blob else 1 if "pause" in blob else 99
        if rank >= 99:
            continue
        ranked.append((rank, ev))
    ranked.sort(key=lambda item: item[0])
    for _rank, ev in ranked:
        if _attr(ev, "active") is False:
            continue
        trig = _attr(ev, "trigger")
        if callable(trig):
            try:
                trig()
                return True
            except Exception:
                pass
    try:
        names = list(_attr(module, "events") or [])
    except Exception:
        names = []
    for ev_name in names:
        low = str(ev_name).lower()
        if "toggle" in low:
            continue
        if "stop" not in low and "pause" not in low:
            continue
        trigger = _attr(module, "trigger_event")
        if callable(trigger):
            try:
                trigger(ev_name)
                return True
            except Exception:
                continue
        by_id = _attr(module, "trigger_event_by_id")
        if callable(by_id):
            try:
                by_id(ev_name)
                return True
            except Exception:
                continue
    return False


def _infer_eid(part: Any, module: Any) -> str:
    eid = module_field(module, *_EID_KEYS)
    if eid is not None and str(eid).strip():
        return str(eid).strip()
    return _part_experiment_id(part)


def iter_science_modules(vessel: Any) -> list[tuple[Any, Any, str]]:
    """(part, module, experiment_id) from part.modules — not parts.experiments.

    One slot per (part, experiment_id). Kerbalism ``Experiment`` wins over a
    leftover ``ModuleScienceExperiment``. ``modules_with_name`` proxies are
    merged by that key, not Python ``id()``.
    """
    slots: dict[tuple, tuple[Any, Any, str]] = {}
    order: list[tuple] = []

    def add(part: Any, module: Any, eid: str) -> None:
        key = _slot_key(part, module, eid)
        prev = slots.get(key)
        if prev is None:
            slots[key] = (part, module, eid)
            order.append(key)
            return
        _, old_mod, _ = prev
        if _is_kerbalism_experiment(module) and not _is_kerbalism_experiment(old_mod):
            slots[key] = (part, module, eid)

    try:
        parts = list(vessel.parts.all)
    except Exception:
        parts = []
    for part in parts:
        try:
            modules = list(part.modules)
        except Exception:
            continue
        for module in modules:
            try:
                named = _is_science_module(_mod_name(module))
                eid = _infer_eid(part, module)
                if not named:
                    # Splash wreck: Kerbalism Experiment gone; Stayputnik
                    # TELEMETRY and GooExperiment still have a start PAW.
                    if not eid or not _module_has_start(module):
                        continue
                add(part, module, eid)
            except Exception:
                continue
    finder = _attr(_attr(vessel, "parts"), "modules_with_name")
    if callable(finder):
        for mname in ("Experiment", "ModuleScienceExperiment"):
            try:
                extras = list(finder(mname) or [])
            except Exception:
                continue
            for module in extras:
                try:
                    part = _attr(module, "part")
                    if not _is_science_module(_mod_name(module) or mname):
                        continue
                    add(part, module, _infer_eid(part, module))
                except Exception:
                    continue
    return [slots[k] for k in order]


def _norm_sit(text: str) -> str:
    return (text or "").strip().lower().replace(" ", "").replace("_", "")


def sit_matches(
    live_sit: str,
    live_biome: str,
    need_sit: str,
    need_biome: str,
    *,
    alt: float = float("nan"),
) -> bool:
    """Bound sit/biome vs live vessel. Empty need is not a gate.

    FlyingHigh pays only at alt ≥50 km. sit=flying at 1 km is not High.
    biome global / none / any is not a biome. sub_orbital at High alt
    is still High — Forest / Grasslands / Shores: same.
    """
    need = _norm_sit(need_sit)
    live = _norm_sit(live_sit)
    bio_need = (need_biome or "").strip().lower()
    if not bio_need and "@" in (need_sit or ""):
        bio_need = need_sit.split("@", 1)[1].strip().lower()
    if bio_need in {"global", "none", "any"}:
        bio_need = ""
    bio_live = (live_biome or "").strip().lower()
    if (
        bio_need
        and bio_live
        and bio_need not in bio_live
        and bio_live not in bio_need
    ):
        return False
    if not need:
        return True
    if "flyinghigh" in need:
        if "landed" in live or "splash" in live:
            return False
        try:
            alt_f = float(alt)
        except (TypeError, ValueError):
            return False
        return math.isfinite(alt_f) and alt_f >= _FLYING_HIGH_ALT_M
    if need.startswith("flying"):
        return "flying" in live
    if "splash" in need:
        return "splash" in live
    if "landed" in need or "srfland" in need:
        return "landed" in live
    return True


def _is_sample(module: Any, eid: str) -> bool:
    """Goo / EVA sample. File sensors expose remaining, not remainingSampleMass."""
    token = str(eid or "").strip()
    if token in _SAMPLE_EIDS or token in EVA_EXPERIMENTS:
        return True
    return module_field(module, "remainingSampleMass") is not None


def remaining_pays(module: Any, eid: str) -> bool:
    """Sample remaining=0 cannot pay. File duration idle rem=0 still might."""
    rem = _remaining_value(module)
    if rem is None or rem > 0.0:
        return True
    token = str(eid or "").strip()
    if token in _DURATION_EIDS:
        return True
    return not _is_sample(module, eid)


def _union_card_eids(
    names: Iterable[str] | None,
    need: dict[str, tuple[str, str]] | None,
) -> list[str] | None:
    """Names plus bound need eids. Fly extras cannot hide splash leftover."""
    if names is None:
        return None
    out: list[str] = []
    seen: set[str] = set()

    def add(raw: object) -> None:
        token = str(raw or "").strip()
        if token and token not in seen:
            seen.add(token)
            out.append(token)

    for n in names:
        add(n)
    for eid in need or ():
        add(eid)
    return out


def experiment_can_pay(
    module: Any,
    eid: str,
    *,
    sit: str = "",
    biome: str = "",
    need_sit: str = "",
    need_biome: str = "",
    alt: float = float("nan"),
) -> bool:
    """True if starting this slot can credit leftover / remaining."""
    if not remaining_pays(module, eid):
        return False
    return sit_matches(sit, biome, need_sit, need_biome, alt=alt)


def start_experiments(
    vessel: Any,
    *,
    names: Iterable[str] | None = None,
    on_log: Callable[[str], None] | None = None,
    sit: str | None = None,
    biome: str | None = None,
    need: dict[str, tuple[str, str]] | None = None,
    alt: float = float("nan"),
) -> list[str]:
    """Start Kerbalism ``Experiment`` modules via events.

    Does **not** call ``vessel.parts.experiments`` / ``Experiment.run()``.
    One trigger per experiment_id (card order). Native part wins — Stayputnik
    ``temperatureScan`` is a duplicate of 2HOT; a second Toggle stops Kerbalism.
    Bound ``need`` eids stay in the card: wrong sit logs cannot-pay, not
    not-in-card. Fly extras cannot hide splash leftover.
    """
    need_map = need or {}
    want_list = _union_card_eids(names, need_map) if names is not None else None
    want = set(want_list) if want_list is not None else None
    done: list[str] = []
    live_sit = (
        sit if sit is not None else str(_attr(vessel, "situation", "") or "")
    ).strip()
    live_biome = (
        biome if biome is not None else str(_attr(vessel, "biome", "") or "")
    ).strip()

    def _say(msg: str) -> None:
        log.info(msg)
        if on_log:
            on_log(msg)

    found = iter_science_modules(vessel)
    if not found:
        stock = run_ready(vessel, names=want_list, on_log=on_log)
        if stock:
            return stock
        _say("science skip (no Experiment modules)")
        return done

    best: dict[str, tuple[int, Any, Any, str]] = {}
    found_order: list[str] = []
    for part, module, eid in found:
        pname = _part_name(part) or "?"
        if want is not None and eid not in want:
            _say(f"science skip {eid or '?'} on {pname} (not in card)")
            continue
        if eid in EVA_EXPERIMENTS:
            _say(f"science skip {eid} (EVA)")
            continue
        broken = module_field(module, "broken", "isBroken", "malfunction")
        if broken in (True, 1, "True", "true", "1"):
            _say(f"science skip {eid or _attr(module, 'name', 'Experiment')} broken")
            continue
        if not eid:
            _say(f"science skip ? on {pname} (no experiment_id)")
            continue
        rank = _slot_rank(part, eid)
        prev = best.get(eid)
        if prev is None:
            best[eid] = (rank, part, module, eid)
            found_order.append(eid)
            continue
        old_rank, old_part, _, _ = prev
        if rank < old_rank:
            _say(
                f"science skip {eid} on {_part_name(old_part) or '?'} "
                f"(prefer {pname})"
            )
            best[eid] = (rank, part, module, eid)
        else:
            _say(f"science skip {eid} on {pname} (already {_part_name(old_part)})")

    sequence = [e for e in (want_list or found_order) if e in best]
    for eid in sequence:
        _rank, part, module, _eid = best[eid]
        pname = _part_name(part) or "?"
        label = eid or str(_attr(module, "name", "Experiment") or "Experiment")
        if _already_running(module):
            _say(f"science keep {label} running")
            done.append(str(label))
            continue
        need_sit, need_biome = need_map.get(eid, ("", ""))
        if not experiment_can_pay(
            module,
            eid,
            sit=live_sit,
            biome=live_biome,
            need_sit=need_sit,
            need_biome=need_biome,
            alt=alt,
        ):
            _say(f"science skip {label} (situation cannot pay)")
            continue
        if _trigger_module(module):
            _say(f"science start {label}")
            done.append(str(label))
        else:
            _say(f"science skip {eid or '?'} on {pname} no event")
    return done


def _number(val: Any) -> float | None:
    if val is None or isinstance(val, bool):
        return None
    if isinstance(val, (int, float)):
        out = float(val)
        return out if out == out else None
    text = str(val).strip().replace(",", "")
    if not text:
        return None
    token = text.split()[0].rstrip("%")
    try:
        return float(token)
    except ValueError:
        return None


def _truthy(val: Any) -> bool:
    if val in (True, 1, "1", "True", "true", "yes", "Yes"):
        return True
    if isinstance(val, str) and val.strip().lower() in ("has data", "stored"):
        return True
    return False


def _status_text(module: Any) -> str:
    val = module_field(module, "status", "Status", "state", "State", "Experiment_status")
    return str(val).strip().lower() if val is not None and str(val).strip() else ""


def status_running(module: Any) -> bool:
    if _already_running(module):
        return True
    low = _status_text(module)
    return bool(low) and any(w in low for w in _RUNNING_STATUS)


def _has_data_field(module: Any) -> bool:
    for key in _HAS_DATA_KEYS:
        if _truthy(module_field(module, key)):
            return True
    return False


def _remaining_zero(module: Any) -> bool:
    num = _remaining_value(module)
    return num is not None and num <= 0.0


def _remaining_value(module: Any) -> float | None:
    for key in _REMAIN_KEYS:
        num = _number(module_field(module, key))
        if num is not None:
            return num
    return None


def _best_slots(
    vessel: Any, names: Iterable[str] | None = None
) -> list[tuple[Any, Any, str]]:
    """One module per experiment_id. Native Science part beats Stayputnik PAW."""
    want = {str(n).strip() for n in names if n} if names is not None else None
    best: dict[str, tuple[int, Any, Any, str]] = {}
    order: list[str] = []
    for part, module, eid in iter_science_modules(vessel):
        if not eid:
            continue
        if want is not None and eid not in want:
            continue
        rank = _slot_rank(part, eid)
        prev = best.get(eid)
        if prev is None:
            best[eid] = (rank, part, module, eid)
            order.append(eid)
            continue
        if rank < prev[0]:
            best[eid] = (rank, part, module, eid)
    return [(best[e][1], best[e][2], e) for e in order]


def paying_eids(
    vessel: Any,
    names: Iterable[str] | None,
    *,
    sit: str = "",
    biome: str = "",
    need: dict[str, tuple[str, str]] | None = None,
    alt: float = float("nan"),
) -> list[str]:
    """In-card ids that can start and pay in this sit/biome."""
    want = [str(n).strip() for n in (names or ()) if n]
    if not want:
        return []
    live_sit = sit or str(_attr(vessel, "situation", "") or "")
    live_biome = biome or str(_attr(vessel, "biome", "") or "")
    need_map = need or {}
    ok: set[str] = set()
    for _part, module, eid in _best_slots(vessel, want):
        need_sit, need_biome = need_map.get(eid, ("", ""))
        if experiment_can_pay(
            module,
            eid,
            sit=live_sit,
            biome=live_biome,
            need_sit=need_sit,
            need_biome=need_biome,
            alt=alt,
        ):
            ok.add(eid)
    return [eid for eid in want if eid in ok]


def card_slots(vessel: Any, names: Iterable[str] | None) -> bool:
    """True if any named Experiment slot exists (paying or not)."""
    return bool(_best_slots(vessel, names))


def ground_card_done(vessel: Any, names: Iterable[str]) -> bool:
    """Landed/splashed dwell finished: rem=0 spent or file transmitted.

    Kerbalism file remaining=0 is done even if still running. Sample rem=0
    running is spent — stop and recover. Duration with no rem field still
    recording is not done. Idle file rem=0 that never Toggled is not dwell-done
    — airborne rem=0 does not skip splash leftover.
    """
    slots = _best_slots(vessel, names)
    if not slots:
        return True
    for _part, module, eid in slots:
        if status_running(module):
            rem = _remaining_value(module)
            if rem is None:
                if str(eid).strip() in _KERBALISM_FILE_EIDS:
                    return False
                continue
            if rem > 0.0:
                return False
            continue
        if not experiment_done(module, eid=eid):
            return False
    return True


def stop_experiments(
    vessel: Any,
    *,
    names: Iterable[str] | None = None,
    on_log: Callable[[str], None] | None = None,
) -> list[str]:
    """Stop running slots so HD files flush before ``vessel.recover()``."""
    done: list[str] = []

    def _say(msg: str) -> None:
        log.info(msg)
        if on_log:
            on_log(msg)

    for _part, module, eid in _best_slots(vessel, names):
        if not _already_running(module):
            continue
        if _trigger_stop(module):
            _say(f"science stop {eid}")
            done.append(str(eid))
    return done


def card_run_rem(
    vessel: Any, names: Iterable[str]
) -> tuple[bool, float | None]:
    """Preferred in-card slot: running, remaining (None if no field)."""
    running = False
    rem_min: float | None = None
    for _part, module, _eid in _best_slots(vessel, names):
        if status_running(module):
            running = True
        rem = _remaining_value(module)
        if rem is None:
            continue
        rem_min = rem if rem_min is None else min(rem_min, rem)
    return running, rem_min


def card_wait_line(
    vessel: Any,
    names: Iterable[str],
    *,
    met: float | None = None,
    ut: float | None = None,
    sit: str | None = None,
    ec: float | None = None,
) -> str:
    """Why the Commander is sitting: experiment remaining / running, plus clock.

    Not a timer. Commander reads this. Empty card → ``wait science none``.
    """
    bits: list[str] = []
    for part, module, eid in _best_slots(vessel, names):
        rem = _remaining_value(module)
        rem_s = f"{rem:g}" if rem is not None else "?"
        run = "1" if status_running(module) else "0"
        st = _status_text(module) or "?"
        part_s = _part_stem(part) or _part_name(part) or "?"
        if rem is not None and rem <= 0 and run == "1":
            file_s = "recording"
        elif rem is not None and rem <= 0:
            file_s = "spent"
        else:
            file_s = "open"
        bits.append(
            f"{eid} part={part_s} run={run} rem={rem_s} file={file_s} {st}"
        )
    body = ",".join(bits) if bits else "none"
    extra: list[str] = []
    if met is not None and met == met:
        extra.append(f"met={met:.1f}")
    if ut is not None and ut == ut:
        extra.append(f"ut={ut:.1f}")
    if sit:
        extra.append(f"sit={sit}")
    if ec is not None and ec == ec:
        extra.append(f"ec={ec:.0f}")
    tail = (" " + " ".join(extra)) if extra else ""
    return f"wait science {body}{tail}"


def _reset_ready(module: Any) -> bool:
    try:
        event_list = list(_attr(module, "event_list") or [])
    except Exception:
        event_list = []
    for ev in event_list:
        blob = (
            f"{_attr(ev, 'gui_name', '') or ''} {_attr(ev, 'name', '') or ''}"
        ).lower()
        if "reset" not in blob:
            continue
        if _attr(ev, "active") is True:
            return True
    return False


def experiment_done(
    module: Any, *, saw_running: bool = False, eid: str = ""
) -> bool:
    """Kerbalism Experiment finished this subject. Does not Toggle.

    Sample rem=0 is spent. File duration rem=0 idle (never Toggled, no Has
    Data) still pays this sit — airborne rem=0 is not splash leftover done.
    """
    if status_running(module):
        return False
    if _has_data_field(module):
        return True
    if _remaining_zero(module):
        if _is_sample(module, eid):
            return True
        if saw_running:
            return True
        low = _status_text(module)
        if low and any(w in low for w in _DONE_STATUS):
            return True
        return False
    low = _status_text(module)
    if low and any(w in low for w in _DONE_STATUS):
        return True
    if _reset_ready(module):
        return True
    return bool(saw_running)


def card_complete(
    vessel: Any,
    names: Iterable[str],
    saw_running: dict[tuple, bool] | None = None,
) -> bool:
    """True when every in-card science slot is done (or none exist)."""
    want = {str(n).strip() for n in names if n}
    if not want:
        return True
    seen = saw_running if saw_running is not None else {}
    slots = [
        (part, module, eid)
        for part, module, eid in iter_science_modules(vessel)
        if eid in want
    ]
    if not slots:
        return False
    done = True
    for part, module, eid in slots:
        key = _slot_key(part, module, eid)
        if status_running(module):
            seen[key] = True
            done = False
            continue
        if experiment_done(module, saw_running=seen.get(key, False), eid=eid):
            continue
        done = False
    return done


def card_has_data(
    vessel: Any,
    names: Iterable[str],
    *,
    remaining: bool = True,
) -> bool:
    """True if any in-card slot already has HD data (not merely started).

    ``remaining=False`` skips remaining-sample 0. Duration experiments
    (TELEMETRY) sit at 0 before a fresh start — that is not leftover HD.
    Pad EC=0 still uses remaining=0 after a sample is consumed.
    """
    want = {str(n).strip() for n in names if n}
    if not want:
        return False
    for _part, module, eid in iter_science_modules(vessel):
        if eid not in want:
            continue
        if _has_data_field(module):
            return True
        if remaining and _remaining_zero(module):
            return True
        low = _status_text(module)
        if low and any(w in low for w in _DONE_STATUS):
            return True
    return False


def iter_drive_modules(vessel: Any) -> list[tuple[Any, Any]]:
    """(part, module) Kerbalism ``HardDrive`` slots — not Experiment PAW."""
    found: list[tuple[Any, Any]] = []
    seen: set[tuple[str, int]] = set()

    def add(part: Any, module: Any) -> None:
        key = (_part_name(part), id(module))
        if key in seen:
            return
        seen.add(key)
        found.append((part, module))

    try:
        parts = list(vessel.parts.all)
    except Exception:
        parts = []
    for part in parts:
        try:
            modules = list(part.modules)
        except Exception:
            continue
        for module in modules:
            try:
                if _is_drive_module(_mod_name(module)):
                    add(part, module)
            except Exception:
                continue
    finder = _attr(_attr(vessel, "parts"), "modules_with_name")
    if callable(finder):
        try:
            extras = list(finder("HardDrive") or [])
        except Exception:
            extras = []
        for module in extras:
            try:
                part = _attr(module, "part")
                if _is_drive_module(_mod_name(module) or "HardDrive"):
                    add(part, module)
            except Exception:
                continue
    return found


def _drive_holds_data(module: Any) -> bool:
    """True if this HardDrive PAW/config shows files or samples."""
    if _has_data_field(module):
        return True
    for key in _DRIVE_DATA_KEYS:
        val = module_field(module, key)
        if val is None:
            continue
        if _truthy(val):
            return True
        num = _number(val)
        if num is not None:
            if num > 0.0:
                return True
            continue
        text = str(val).strip().lower()
        if not text or text in _EMPTY_DRIVE or text.startswith("empty"):
            continue
        return True
    return False


def hd_has_data(vessel: Any) -> bool:
    """True if any Kerbalism HardDrive holds files — even with Experiment gone."""
    for _part, module in iter_drive_modules(vessel):
        if _drive_holds_data(module):
            return True
    return False


def pad_ec_rate(
    names: Iterable[str],
    *,
    vessel: Any = None,
    catalog: Any = None,
) -> float:
    """Sum in-card Experiment ``ec_rate``. Live modules win; catalog fallback."""
    want = [str(n).strip() for n in names if n]
    want_set = set(want)
    if not want_set:
        return 0.0
    cat_rates: dict[str, float] = {}
    cat_exps = _attr(catalog, "experiments") if catalog is not None else None
    if isinstance(cat_exps, dict):
        for eid, spec in cat_exps.items():
            rate = _number(_attr(spec, "ec_rate"))
            if rate is not None and rate > 0.0:
                cat_rates[str(eid)] = rate
    total = 0.0
    if vessel is not None:
        for _part, module, eid in iter_science_modules(vessel):
            if eid not in want_set:
                continue
            rate = _number(module_field(module, "ec_rate", "ecRate"))
            if rate is None or rate <= 0.0:
                rate = cat_rates.get(eid)
            if rate is not None and rate > 0.0:
                total += rate
        return total
    seen: set[str] = set()
    for eid in want:
        if eid in seen:
            continue
        seen.add(eid)
        rate = cat_rates.get(eid)
        if rate is not None and rate > 0.0:
            total += rate
    return total


def pad_dwell_s(
    names: Iterable[str],
    *,
    vessel: Any = None,
    catalog: Any = None,
    ec: float | None = None,
) -> float:
    """Wall-clock cap: size/data_rate, min remaining EC/ec_rate.

    Not sample_amount/rate. EC cap is None-safe: unknown rate → data wall only.
    """
    want = [str(n).strip() for n in names if n]
    if not want:
        return 0.0
    rates: dict[str, float] = {}
    sizes: dict[str, float] = {}
    cat_exps = _attr(catalog, "experiments") if catalog is not None else None
    if isinstance(cat_exps, dict):
        for eid, spec in cat_exps.items():
            rate = _number(_attr(spec, "data_rate"))
            size = _number(_attr(spec, "size_mb"))
            if rate is not None:
                rates[str(eid)] = rate
            if size is not None:
                sizes[str(eid)] = size
    if vessel is not None:
        for _part, module, eid in iter_science_modules(vessel):
            if eid not in want:
                continue
            rate = _number(module_field(module, "data_rate", "dataRate"))
            if rate is not None:
                rates[eid] = rate
    times: list[float] = []
    for eid in want:
        rate_f = rates.get(eid) or 0.0
        size_f = sizes.get(eid) or 0.0
        if rate_f > 0.0 and size_f > 0.0:
            times.append(size_f / rate_f)
    data_s = max(times) * 1.15 + 2.0 if times else DEFAULT_PAD_DWELL_S
    drain = pad_ec_rate(names, vessel=vessel, catalog=catalog)
    if ec is not None and drain > 0.0:
        try:
            ec_f = float(ec)
        except (TypeError, ValueError):
            ec_f = float("nan")
        if ec_f == ec_f and ec_f >= 0.0:
            return min(data_s, (ec_f / drain) * PAD_EC_MARGIN)
    return data_s



