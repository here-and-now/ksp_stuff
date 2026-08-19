# kRPC technical notes

Source of truth for **how this process talks to the game**. Not a mission log.
Mission scripts (ascent profiles, specific stacks) come later, after the layers
below are pinned.

If chat and this file disagree, this file wins. After a live probe: patch the
section, then append a dated line under [Log](#log). When a helper was wrong,
fix the helper in the same turn.

---

## Process

Work **bottom-up**. Do not skip to gravity turns or constellation dumps while
the layer underneath is still guessed.

| Order | Layer | Question |
|---|---|---|
| 1 | Connection | One `Session`, both sockets, scene, profile |
| 2 | Reads | RPC get vs `add_stream`; what we subscribe to |
| 3 | Writes | `control.*`, autopilot, staging as RPCs |
| 4 | Craft I/O | `.craft` on disk → `launch_vessel` (kRPC has no VAB placer) |
| 5 | Loops | Ascent / nodes / comms, built on 1–4 |

For each slice: smallest live probe → if the client API differs, change our
wrapper → update the table here → next slice. Encode knowledge in helpers
(`Session`, `set_autopilot`, `Hangar`, `StackBuilder`), not in one-off scripts.

---

## Environment (live 2026-08-19)

| | |
|---|---|
| KSP | 1.12.5.3190 LinuxPlayer, Steam `220200` |
| Root | `~/.steam/steam/steamapps/common/Kerbal Space Program` |
| Plugin | `GameData/kRPC` **0.6.0** (Squad + SquadExpansion only besides that) |
| Client | `.venv`, Python 3.14.7, `krpc==0.6.0` |
| Sockets | `127.0.0.1:50000` RPC, `127.0.0.1:50001` stream |
| Settings | `GameData/kRPC/PluginData/settings.cfg` — `AutoStartServers=True`, `AutoAcceptConnections=True` |

The kRPC zip ships an empty `settings.cfg`. Without auto-start, the server does
not bind until someone clicks Start in the in-game window.

Client and plugin **must match** (both 0.6.0 here). `KSP.log` must contain
`[kRPC]` after boot; a stock-only GameData listing means the plugin did not load.

`steam -applaunch 220200`. First kRPC boot ~2 min to main menu / space center.
First `Session.connect()` ~30 s (service schema over RPC). Later connects are
cheaper. System `python3` has no `krpc`; use `.venv`.

---

## Connection

`krpc.connect(name, address, rpc_port, stream_port)` opens **two** TCP
connections. The stream socket is required even if you never call `add_stream`;
connect fails if 50001 is closed.

`Session` owns that client. Managers must not call `krpc.connect()` themselves.
`connect()` is explicit (importing `kspstuff` is a no-op). `close()` drops
`conn` / `space_center` / addon handles.

`conn.krpc.get_status().version` → `"0.6.0"` (live).
`conn.krpc.game_scene` → enum; `.name` is `space_center` / `flight` / …
`space_center.bodies` is a name→body map. `profile auto` uses that map
(Earth present → RSS, else stock).

`space_center.active_vessel` is **`None`** at the space center with nothing
spawned. Touching `.name` / `.comms` there raises. Scene-dependent probes belong
in the scene that has a vessel.

---

## Service detection (L-040)

`Session._probe_services` reads **`get_services().services`** (protobuf
``Services`` message). ``status.services`` is the name tuple. Iterating
`get_services()` itself as if it were a list used to fail silently → `()`.

**`getattr(conn, "remote_tech")` is not “RemoteTech is installed”.**
`KRPC.RemoteTech.dll` ships *inside* GameData/kRPC. The stub exists on a
stock-only install. ``status.remotetech`` means the client object exists.
Same idea for other bundled addon DLLs. MechJeb is *not* in the stock zip;
``conn.mech_jeb`` is None here.

**CommNet / RealAntennas** are inferred from `active_vessel.comms` and
`parts.with_module("ModuleRealAntenna")`. At KSC with no vessel that probe
excepts → `commnet=False`. Re-probe after spawn.

`conn.space_center` exists. `conn.mech_jeb` does not on this install.

---

## Reads: RPC vs stream

kRPC has two read styles on the same connection:

| | RPC get | Stream |
|---|---|---|
| Call | `flight.mean_altitude` | `s = conn.add_stream(getattr, flight, "mean_altitude")`; `s()` |
| Wire | one request/response per read | server pushes on the **stream** socket |
| Setters | yes | **no** (`add_stream(setattr, …)` raises `StreamError`) |
| Cleanup | none | `s.remove()` (or `with conn.stream(...)`) |
| Rate | whatever you poll | `s.rate = Hz` (0 = every physics update) |
| Wait | `time.sleep` | lock `conn.stream_update_condition`, then `conn.wait_for_stream_update(timeout=)` |

`Stream.__call__` returns the last pushed value; it does not fetch. First
`s()` starts the stream and **blocks until the first update**.

**Live (2026-08-19, vessel in `flight` / `orbiting`)**

- Form: **`add_stream(getattr, obj, "prop")` only.**
  `add_stream(flight.mean_altitude)` raises `AttributeError: 'float' object
  has no attribute '__self__'` — the property already ran as an RPC.
- `add_stream(setattr, control, "throttle", 0)` → `StreamError: Cannot stream
  a property setter`.
- `Session.add_stream` is a thin pass-through; same rules.
- Hold `flight` / `orbit` objects for the life of the stream. `remove()` then
  `s()` → `StreamError: Stream does not exist`.
- `rate = 20` on six streams: first `s()` after create **0.45 s**. Over 10.02 s
  wall (MET +10.0 s, so 1× physics): **160** `wait_for_stream_update` wakes
  (**~16 Hz**), 159 MET changes. Do not treat `rate` as exact Hz; it is a cap.
  One condition wait delivers a **batch** — read every `s()` after the wake.
- Stream vs RPC get on the same tick: apo/peri/mass identical; MET/altitude
  lagged one physics step (ΔMET 0.02 s, Δalt ~8 cm). Streams are last-push,
  not a second fetch.

`orientation.py` stream-wait and MechJeb `conn.stream(...)` still untested live.

**Pipeline**

`watch.FlightWatch` is the **only** hot reader in the writer process.
Subscribe once (`getattr` on held `flight`/`orbit`): alt, q, surface
altitude, apo, peri, ecc, sma, t_pe, t_ap. Suicide calls
`enable_landing()` for body-frame speed / vertical speed on the same
watch — do not open a second stream set. `pulse()` waits on
`stream_update_condition` then reads every `s()` (one wake is a batch).
Log one line per second with flags `ATMO DIP ESC FLAME WRECK`.
Resources, warp, throttle, thrust, situation, engines are RPC at 1 Hz.
Hold `flight` / `orbit` / body-frame `flight`; never `vessel.flight()`
per pulse. Writes stay RPC. Ascent, nodes, warp, recover, suicide all
`pulse()` the same instance. `heartbeat()` / `status` are one-shots.
Do not treat the 1 Hz line as intervention — the loop branches on
`FlightState`.

UI `TelemetrySample` / pyqtSignal is parked with the rest of the UI.

---

## Writes: control and autopilot

All of these are RPC **setters**. Not streamable.

**Setter lag (live):** `control.throttle` and `control.pitch` getters refresh
**one physics tick after a set**. Immediate read returns the previous value
(`set 0.4` → immediate `0.0`, ~0.08–0.15 s later `0.4`). Same as the 0.6
client docstring on `Control.pitch`.

**Throttle (live, engine already `active`):** `throttle=0.4` produced
0.4 × `max_thrust` (24 kN of 60 kN). `throttle=0` zeros thrust. On the
pad in `pre_launch`, `throttle=1` with `engine.active=False` produces
**no thrust** until `activate_next_stage`.

**Raw axes (live):** `control.pitch` in `[-1, 1]` writes; same one-tick lag.
Not tested against AP at the same time.

**SAS vs AP (live):** `control.sas` and `ap.sas` stay in sync. Engaging the
autopilot **clears SAS** (`control.sas` and `ap.sas` both False, `engaged`
True). Set `control.sas=False` yourself anyway. `error` / `pitch_error` /
`heading_error` / `current_*_error` all raise
`RuntimeError: The auto-pilot is not engaged` while `engaged` is false.
`current_target_pitch` is readable when disengaged. Use
`set_autopilot` / `autopilot_error` in `orientation.py`.

**AP hold (live):** `engaged=True`, `target_pitch=0`, `target_heading=90`,
`target_roll=0`. `error` streamed at 10 Hz: 73° → 2.6° in 2.25 s.
`ap.wait()` then returned in 0.35 s at `error≈1°`. Disengage → `error`
raises again.

**Warp (plugin 0.6, from `KRPC.SpaceCenter.json`):**

`WarpTo(ut, maxRailsRate, maxPhysicsRate)` **blocks** and ramps the
ladder, then returns to 1×. Do not call it in a 20 min loop — that is
the on-screen 1×→max→1× cycle (L-020). Drive `rails_warp_factor` (0–7);
`maximum_rails_warp_factor` is the altitude cap; `can_rails_warp_at(n)`
before a set. `warp_rate` is the multiplier (10 = 10×). Physics factor
is 0–3 (1×/2×/3×/4×). `warp.warp_to_ut` holds the cap and heartbeats
on wall-clock 1 Hz.

`orbit.time_to_soi_change` is NaN when no SOI change is predicted, and
was NaN near the Mun patch (~9.5 Mm) even after a planned encounter
(`next_orbit` still Mun). Fall back to `time_to_apoapsis` on a transfer.
Vessel `orbit.next_orbit` is None until the *live* orbit intersects Mun
SOI; a maneuver `node.orbit.next_orbit` can be Mun while the burn is
still short (apo below Mun SMA ~12 Mm). Do not treat Pe=None as a lost
encounter until apo is in that band (L-028).
High rails (1000×+) toward an airless close peri punches the patched
conic through the surface (L-023: planned Pe 23 km → −109 km). Cap
rails at 50× when airless Pe < 80 km; do not warp to a subsurface peri.

**Staging (live):**

- `pre_launch`, `current_stage=1`: `activate_next_stage()` → stage `0`,
  situation `flying`, engine `active=True`, thrust appears. This is ignition.
- Already at stage `0`: another `activate_next_stage()` is a **no-op**
  (stage stays 0).

Staging *policy* (`should_stage`) is still not pinned. Resource helpers:
`vessel.decouple_stage_at(n).resources()` (0.6) then
`resources_in_decouple_stage(n, cumulative=False)`.

---

## Craft I/O (no VAB API)

kRPC can change scene and call `SpaceCenter.launch_vessel`. It **cannot**
click parts onto a ship. The writable object is a `.craft` file:

```text
<KSP>/saves/<save>/Ships/VAB/<name>.craft
```

then:

```text
space_center.launch_vessel(facility, name, site, crew, recover)
```

`Hangar` is that folder + those two RPCs. Live this session:

- `discover_ksp()` found the Steam install.
- `install(craft, overwrite=True)` wrote a parseable `.craft` into save `Grok`.
- `launchable_vessels("VAB")` listed those names.
- `launch_vessel(..., crew=[])` on an Mk1 pod raises the in-game **No
  Control** pre-flight dialog; kRPC waits there. Empty command pods are
  not probes. Crew names must be `RosterStatus.available` — assigned or
  missing kerbals still launch empty. `create_kerbal(name, "Pilot", True)`
  if the roster is busy. `conn.krpc.game_scene = GameScene.space_center`
  (or deprecated `space_center.load_space_center`) leaves a junk flight /
  modal without a click. `can_revert_to_launch` exists but restores the
  *current* flight’s pad, not a new craft.
- `launch_vessel(..., recover=True)` from **space_center** and from **flight**
  entered `flight` / `pre_launch` with `active_vessel` set. Internally KSP
  **saves** via `FlightDriver.StartWithNewLaunch` → `GamePersistence.SaveGame`.
  A dirty leftover (killed mid-warp, `freeze`) NREs `FlightState..ctor`
  ("Object reference not set"). `game_scene` already `space_center` is not
  a clean Game — always re-set the scene. On that NRE call
  `load_space_center` and retry `recover=False`. Do not wait for a Recover
  click (L-022).
- `launch_vessel(..., recover=True)` does **not** clear a leftover
  landed/flying on the pad. Pre-flight raises `Launch site not clear`
  (`WaitForVesselPreFlightChecks`). Recover the occupant with
  `vessel.recover()` when `vessel.recoverable` (biome `LaunchPad` /
  landed+recoverable on the home body). A freeze-after-ignition leftover
  can still be `flying` at ~82 m — switch, wait until recoverable, then
  recover. Then `go_space_center` and retry **with** `recover=True`.
  `recover=False` is the wrong fallback on that error (L-027). Assigned
  crew on the leftover become `available` after recover.
- `launch_vessel(..., recover=False)` from **flight** also works: switches
  `active_vessel` to the new pad craft; the previous vessel stayed in the
  `space_center.vessels` list (`orbiting`, `loaded=False`).

`StackBuilder` / `Craft` write ConfigNodes. Part **tokens** in the file use
dots: internal `mk1pod_v2` → `mk1pod.v2_<uid>`. KSP fills `MODULE` blocks from
`part.cfg` on load if we omit them (stock). `istg` / `dstg` / `sidx` are KSP
stage fields on the part; they must match how `activate_next_stage` fires, but
the mapping is still being pinned — do not treat current templates as spec.

**Partial parts round-trip (live):** `kspstuff-hecs-sounding` file parts
`probeCoreHex_v2`, `fuelTankSmallFlat`, `liquidEngine3_v2` → in-game
`vessel.parts.all` names `probeCoreHex.v2`, `fuelTankSmallFlat`,
`liquidEngine3.v2` (underscore→dot, uid stripped). Count matched (3). Not
yet asserted in code.

`Catalog.stock()` is a **handful of hardcoded stack-node offsets**, not a full
GameData scan. `scan_gamedata(ksp_root)` walks `PART` cfgs. Next craft-layer
test: encode the name mapping and assert file vs `vessel.parts` after launch.

---

## Science (kRPC 0.6 schema, not yet live-run)

`vessel.parts.experiments` is every `ModuleScienceExperiment`.
`Part.experiment` raises if the part has more than one — use
`Part.experiments`. Python `Experiment`:

- `name` / `title` — cfg `experimentID` (`crewReport`, `mysteryGoo`,
  `evaReport`, `temperatureScan`, …)
- `available`, `has_data`, `inoperable`, `rerunnable`, `deployed`, `biome`
- `run()`, `reset()`, `dump()`, `transmit()`, `data`, `science_subject`

`science.py` calls `run()` only. Do **not** transmit goo (`xmitDataScalar`
0.3). Do **not** `dump`/`reset` to free a second sample. EVA report /
surface sample live on the kerbal EVA part — no hatch API here; skip.
Mk1 pod `ModuleScienceContainer` is `evaOnlyStorage = True` (IVA cannot
stash). `Run()` refuses `has_data`; a rerunnable second crew report tries
the experiment module event, not dump. Goo is one-shot.

Kerbin FlyingLow / FlyingHigh split is 18 km (stock). Hop `hop_apo`
defaults 15 km so the coast stays FlyingLow.

---

## Capability matrix

Status: **live** = exercised against this KSP; **code** = written, not live;
**broken** = live and wrong.

| Item | Status |
|---|---|
| `Session.connect` / `close`, kRPC 0.6.0 | live |
| `game_scene`, `bodies`, profile `auto` → stock | live |
| `active_vessel` at KSC, nothing spawned | live (`None`) |
| `launch_vessel` + recover, `launchable_vessels` | live |
| `control.throttle`, `activate_next_stage`, `sas`, `pitch` | live |
| throttle/pitch getter lag (1 physics tick) | live |
| pad ignition = throttle then `activate_next_stage` | live |
| `auto_pilot.engaged`, `target_pitch/heading/roll`, `wait`, `error` | live |
| AP `error` while disengaged | live (raises) |
| AP engage clears SAS | live |
| `launch_vessel(..., recover=False)` from flight | live |
| `.craft` part names vs `vessel.parts` (underscore→dot) | live (one 3-part craft) |
| `orbit.*`, `flight.mean_altitude`, `dynamic_pressure` as **RPC get** | live |
| `add_stream(getattr, obj, name)` + `rate` + `wait_for_stream_update` | live |
| `add_stream(bound_property)` / streaming setters | live (both fail as specified) |
| `orientation` stream wait (direction vs target) | code only |
| MechJeb `node_executor` | absent |
| `status.services` list | broken (protobuf) |
| `status.remotetech` meaning | broken (stub DLL) |
| `status.commnet` at KSC | broken (needs vessel) |
| PyQt connect + plot | code only |
| `.craft` round-trip vs `vessel.parts` | not done |
| RSS / RO / RP-1 | code only |
| `Experiment.run` / hop sounding | code only |

---

## Open (technical)

- Encode craft part-name round-trip (`mk1pod_v2` ↔ `mk1pod.v2`) and assert
  after `launch_vessel`. Extend catalog only as names are needed.
- Ascent hot-path reads are on `FlightWatch` streams; writes stay RPC. Respect
  the one-tick getter lag (do not treat immediate `control.throttle` as the
  value just set). Do not gate ascent on `ecc` while still in atmosphere
  (suborbital hops report `ecc≈1`).
- Fix `_probe_services` (protobuf services; stub vs mod). CommNet reads on a
  loaded vessel (`CN 1.00` in `list_vessels`); still false at KSC with no vessel.
- `vessels.py` `inclination_deg` looks like radians labelled as degrees
  (orbiting craft ~1.48 rad reported as 84.7). Not re-measured.
- Do not grow new mission loops until the craft assert is in code.

---

## Log

- **2026-08-19** — kRPC 0.6.0 client+plugin. `Session.connect` on 50000/50001.
  Schema ~30 s first time. `get_services()` is protobuf → `status.services==()`.
  `remote_tech` attr true with no RT mod. `active_vessel` None at KSC.
- **2026-08-19** — Empty plugin `settings.cfg` does not auto-bind; wrote
  AutoStartServers / AutoAcceptConnections / 127.0.0.1 ports.
- **2026-08-19** — `AutoPilot.engage` missing; `engaged` bool property works.
  Wrapper: `orientation.set_autopilot`.
- **2026-08-19** — `Hangar.install` + `launch_vessel(recover=True)` from KSC
  and from flight. Scene `flight`, situation `pre_launch`.
- **2026-08-19** — Telemetry in the first flight loop was RPC polling at ~20 Hz
  control / 4 Hz samples. Stream port up; no `add_stream` on that path.
- **2026-08-19** — Stream probe, `orbiting` vessel. `getattr` form works;
  bound property does not; setattr → `StreamError`. First value 0.45 s.
  `rate=20` → ~16 Hz batch wakes over 10 s at 1×. Stream snapshot is ≤1
  physics tick behind RPC get. `Session.add_stream` + `remove()` ok.
- **2026-08-19** — `FlightWatch.pulse` waits on `stream_update_condition`.
  Core streams: alt, q, surface, apo, peri, ecc, sma, t_pe, t_ap.
  Landing adds speed/vs on the same watch. Slow RPC 1 Hz. One watch
  per writer process; `heartbeat` is the one-shot.
- **2026-08-19** — `FlightWatch` is the mission telemetry layer. Recover
  that stopped at peri≥80 km while still hyperbolic is a failed recover.
  Warp is illegal only *in* atmosphere, not because peri will reenter later.
- **2026-08-19** — `WarpTo` is `(ut, maxRailsRate, maxPhysicsRate)` and
  blocks. Chunked calls cycle the rails ladder. `warp_to_ut` now sets
  `rails_warp_factor` and only steps down near the target UT.
- **2026-08-19** — Write probe. Throttle/pitch get lags one tick. Throttle
  fraction maps to thrust when `engine.active`. AP `error` raises if
  disengaged; engage clears SAS; hold 90/0 reached ~1° via `wait()`.
  Pad `activate_next_stage` is ignition (`pre_launch`→`flying`). Stage 0
  restage is a no-op. `launch_vessel(recover=False)` from flight keeps the
  previous vessel in the list. 3-part sounding: file names → in-game
  underscore-to-dot. Added `autopilot_error`.
- **2026-08-19** — `launch_vessel(recover=True)` SaveGame NREs on a dirty
  leftover (`FlightState..ctor`). Scene already `space_center` is not
  clean. `load_space_center` then `recover=False` (L-022).
- **2026-08-19** — `time_to_soi_change` NaN near a Mun patch. 1000× rails
  to a close airless peri drove Pe underground (L-023).
- **2026-08-19** — Pad leftover after abort: `Launch site not clear`.
  `vessel.recoverable` / `vessel.recover()` clear it; keep
  `launch_vessel(recover=True)` (L-027).
- **2026-08-19** — Vessel `orbit.next_orbit` is None after a short TLI
  even when the node had a Mun patch (apo 11.17 Mm < Mun SMA). L-028.
- **2026-08-20** — Experiment API from `KRPC.SpaceCenter.xml` 0.6:
  `parts.experiments`, `run`/`has_data`/`available`. No live run (KSC,
  no vessel). Hop block L-041.
