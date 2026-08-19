# kspstuff

kRPC helpers for Kerbal Space Program. Agent CLI, not the PyQt UI (parked).

This is a rewrite of an older RemoteTech + MechJeb automation pile (gravity
turn, resonant-orbit relay dump, antenna targeting). The old scripts are in
git history; they worked, they were also a mess.

Nothing talks to the game until you open a `Session` or run `python main.py`.
No venv is created by this repo, and nothing is installed for you.

## What it was

Around 2022–2024 this repo drove:

- FAR-aware gravity turn with a max-Q PID
- MechJeb circularize / resonant orbit / node executor
- Dumping a 3-sat relay constellation and RCS-tuning periods to ~1 ms
- RemoteTech dish targeting (home body + two nearest neighbours)

Each class opened its own `krpc.connect()`. The UI was a Bokeh app. Kerbin
and stock `LiquidFuel` were hardcoded. `fine_tune_orbital_period` was
accidentally nested inside another method. There were two overlapping comms
classes.

## What it is now

One shared `Session`, stock vs RSS/RO/RP-1 profiles. Agent CLI:

```bash
source .venv/bin/activate
python main.py status
python main.py phase circularize
```

Lessons (failure → library fix) live in [`docs/lessons.md`](docs/lessons.md).
kRPC client-layer notes: [`docs/agent-notes.md`](docs/agent-notes.md).
Agents start from `AGENTS.md` (parent spawns Gene, the named kerbal,
`ksp-stack`; **do not spawn spotter**; do not sit on the 1 Hz stream).
PyQt under `ui/` is unused.

```
main.py              CLI: status / phase / mun / recover
session.py           one kRPC connection, optional MechJeb / CommNet / RA detect
profile.py           Kerbin vs Earth, fuels, default ascent numbers, pads
launch.py            gravity turn, max-Q PID, staging, fairings, circularize
watch.py             FlightWatch 1 Hz heartbeat + ATMO/DIP/ESC/FLAME gates
warp.py              hold rails_warp_factor; refuse only while currently in atmosphere
mun.py               pad → LKO → Mun landing
nodes.py             MechJeb executor, vis-viva fallback, 1 Hz node burns
constellation.py     layers (MEO/GEO/polar), resonant dump, period tune, slots
comms.py             CommNet coverage; RemoteTech targeting kept as leftover
realantennas.py      ModuleRealAntenna fields, deploy, dish-aim checklist
vessels.py           snapshots (no pandas)
career.py            funds / science / reputation / contracts
cfg.py               ConfigNode parse/dump (.craft, part.cfg)
craft.py             stack builder + stock templates
catalog.py           stack-node offsets from GameData
hangar.py            saves/<save>/Ships/VAB|SPH + kRPC launch_vessel
ui/                  PyQt6 parked: Vessels, Launch, Hangar, Constellation, Comms, Career
```

Launch and constellation work run on a worker thread so the window stays
alive. Abort is a flag, not `kill -9`.

## Run later (not now)

Needs KSP with [kRPC](https://github.com/krpc/krpc) and, for the old
workflow, MechJeb2 + [KRPC.MechJeb](https://github.com/Genhis/KRPC.MechJeb).
RemoteTech is optional; RP-1 normally uses RealAntennas on CommNet instead.

The repo is a working tree, not a pip package. `.venv` holds third-party
deps only (`krpc`, `numpy`, `PyQt6`, `pyqtgraph`). Do not `pip install` this
project.

```bash
source .venv/bin/activate
python main.py status
```

From a REPL in this directory, `import session` works because `python` puts `.` on `sys.path`. Do not `pip install` this project and do not `python -m kspstuff`.

`--profile auto` (default) picks RSS if the save has Earth, otherwise stock
Kerbin.

## RSS / RO / RP-1

The UI is meant to survive a future RP-1 run. Today that means:

- Home body is `Earth`, not `Kerbin`
- Launch heading uses site latitude (Cape ≈ 28.6°) instead of `90 − i`
- Staging looks at RO fuel names (Kerosene, LOx, UDMH, NTO, LH2, …)
- Optional TWR cap
- CommNet status works without RemoteTech
- Career tab reads stock funds/science/contracts

There is no kRPC RP-1 service. Avionics, KCT, and program points are not
exposed; `career.py` says so. Ullage is `parts.ullage` as a hook.

Typical RP-1 comms stack is RealAntennas + CommNet.

## RealAntennas (no kRPC service)

RA extends CommNet. There is no `conn.real_antennas`. What kRPC can do:

| Can do | Cannot do |
|---|---|
| `vessel.comms` — link, strength, delay, control path | Set dish targets (stored as a nested ConfigNode) |
| Read `ModuleRealAntenna` PAW: band, gain, Tx dBm, TL, aim string, condition | Extra gain from duplicate dishes on the same band |
| Deploy stock/RA antennas | Control delay like RemoteTech |

So the automation is **geometry + inventory + coverage**, not “aim dish 2 at sat B”:

1. Pick a layer (early: 4× MEO VHF omnis ~3400 km; later: 3× GEO S/X).
2. Dump/phasing still uses resonant orbits if you launch a stack (`n-1 : n`).
3. **Commission comms** deploys antennas and reads CommNet.
4. Dishes default to Earth centre — good enough for GEO→DSN. Point at Goldstone/Madrid/Canberra or a specific craft in-game (part menu → Antenna Targeting).
5. **Slot report** shows ΔRAAN / Δmean-anomaly vs Walker slots, including empty slots for later launches.

VHF/UHF omnis need no pointing. S/X/K to the DSN only exist at Goldstone, Madrid, and Canberra.

## Craft files (no VAB API)

kRPC can switch to the VAB scene and can **launch** a ship. It cannot click parts onto a stack. The way in is a `.craft` file in the current save:

```
<KSP>/saves/<save>/Ships/VAB/<name>.craft
```

then `space_center.launch_vessel("VAB", name, "LaunchPad", [])`.

Hangar tab: find this Steam KSP install, pick a save, list crafts, write a stock template, launch. Templates live in `crafts/stock/` as well.

What this is **not** yet: an agent playing the VAB, RP-1 procedural tanks, RealFuels mixtures, or avionics mass limits. Those belong in MODULE blocks we do not invent until a run exists. The stack builder only needs node offsets (`node_stack_top/bottom` from `part.cfg`).

```python
from craft import simple_orbiter
from hangar import discover_hangar

craft = simple_orbiter()
hangar = discover_hangar(save="your-save")
hangar.install(craft, overwrite=True)
# hangar.launch(session, craft.name)   # when kRPC is up
```

`KSPSTUFF_KSP` / `KSPSTUFF_SAVE` override discovery.

## Library bits

```python
from session import Session
from profile import RSS_RP1
from launch import Ascent, AscentConfig
from constellation import Constellation, ConstellationConfig, LAYERS
from comms import commission_network

with Session(profile=RSS_RP1) as session:
    Ascent(session, AscentConfig(inclination=28.6, target_altitude=200_000)).run()
```

RemoteTech-only leftover (ignored on RP-1/RA):

```json
{
  "HighGainAntenna": "setup_network",
  "RTShortDish2": ["active_vessel"]
}
```
