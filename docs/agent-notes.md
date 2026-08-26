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

## Environment (live 2026-08-21, RSS)

| | |
|---|---|
| KSP | 1.12.5.3190 LinuxPlayer, portable `~/Games/KSP-rss` |
| Save | `letsgrok` (`SCIENCE_SANDBOX`). Env `KSPSTUFF_KSP`, `KSPSTUFF_SAVE` |
| Plugin | `GameData/kRPC` **0.6.0** (manual drop-in) |
| Aero | **FAR**, **RealChute** (+ ForStock), **RealHeat** — GameData 2026-08-21 |
| Kerbalism | Profile **default** (not RO) |
| Client | `.venv`, Python 3.14.7, `krpc==0.6.0` |
| Sockets | `127.0.0.1:50000` RPC, `127.0.0.1:50001` stream |
| Settings | `GameData/kRPC/PluginData/settings.cfg` — disk 2026-08-20: `autoStartServers = False`, `autoAcceptConnections = True`, `pauseServerWithGame = False` |

Steam `Kerbal Space Program` still has stock kRPC + Squad only. **Do not use it.**
`hangar.discover_ksp` prefers RSS when `GameData/RealSolarSystem` exists.
Do not load `Grok`, `test`, or old career folders.

The kRPC zip ships an empty `settings.cfg`. Disk now has a filled cfg with
**`autoStartServers = False`**. Without auto-start, the server does not bind
until someone clicks Start in the in-game window. **Do not write GameData**
to flip that flag.

Desk briefing (who may touch what): `docs/program/krpc.md`. Traps stay here.

Client and plugin **must match** (both 0.6.0 here). `KSP.log` must contain
`[kRPC]` after boot.

Launch `~/Games/KSP-rss/KSP.x86_64` (close CKAN GUI first — lock). First MM pass
after a CKAN change is slow; later boots ~70 s to MAINMENU. First
`Session.connect()` ~30 s (service schema over RPC). Later connects are cheaper.
System `python3` has no `krpc`; use `.venv`.

### Parts vs hosted experiments (disk)

`python main.py parts` lists **placeable** parts. `hosts=N` is Kerbalism
PAW slots on that part — not extra VAB parts. Stayputnik hosts
`geigerCounter`; the Geiger Counter part is `kerbalism-geigercounter`
at `engineering101`. Seated stack: `python main.py parts --stack`.
Do not sign an experiment id as hardware.

## Screenshot (no kRPC)

`grim -g "<x>,<y> <w>x<h>"` of the Hyprland layout box is **not** a window
shot. KSP stays `mapped` with an `at`/`size` while `visible` is false
(other workspace, or covered — e.g. a fullscreen Grok on the same
workspace). grim then copies the **output** pixels (TUI, Firefox, black).
Geometry also moves when the window is resized.

```bash
python main.py screenshot
python main.py screenshot --name <stem>   # screenshots/<stem>.png
python main.py screenshot --full          # monitor-size shot, then restore tile
```

`screenshot.py` finds `class=KSP.x86_64` only (no title match — a
Firefox tab named Kerbal is not KSP), prefers the RSS pid if two
copies run, then **window buffers only**:

1. `grim -T <hyprland stableId>` — foreign toplevel buffer. Works
   occluded / inactive workspace / XWayland. Does **not** focus or
   switch workspace.
2. `magick import -window` on the X11 id (`WM_CLASS` in
   `KSP.x86_64` / `KSP.x86` / `KSP`, pid match when known).

No `grim -g`. No focus-then-geometry. If both buffers miss, fail
closed — do not copy the output.

`grim -T` does **not** need focus, the active workspace, or the same
monitor as the TUI. `--full` only grows a *small* tile. If KSP is
already monitor-sized or already compositor/client FS (other
workspace, other monitor, unfocused), `--full` is grim -T with **no**
layout change — it must not `internal=0` a window that was already
fullscreen.

When it does grow: `internal=2, client=0` on KSP only, shot, restore
the **original** FS state + size (relative resize if dwindle ate the
tile) + that monitor's workspace if it changed + previous focus.
Does not dispatch FS on Firefox (pip_tile). Brief overlay flash is
possible while a small window is grown; Hyprland 0.56 did not steal
the monitor's active workspace in a live probe.

Default dest is `screenshots/ksp-<utc>.png`. Refuses to overwrite
`screenshots/first-mystery-goo.png` unless `--force`.

Press stills: Verena `shot:` → parent `--name <slug>`. Ops: Gene
(between exits) or the seated Commander may take **one**
`--name stuck-<stem>` when last-flight / jsonl cannot explain the
scene, then read the PNG. grim is not kRPC.

Flight cadence (grim; beauty may F2 + pose on the hop Session — do
**not** read unless stuck): pad/hop writes
`screenshots/runs/<stamp>-<command>/T+MMMMMM-<event>.png`. Tape ~10 s
ticks (keep last 3) plus sit/stage/wreck/EC=0, HUD on. Press beats
(`light`, `airborne`, `science`, `chute`, `splash`, `recover`) hide
HUD then restore. Failures are debug-only — never abort the fly. Never
overwrite press heroes (`first-mystery-goo`, `first-hop`,
`rocket-flea`). Verena picks from that folder after the hop; she does
not grim while `phase` is live.

### World desk (disk, no kRPC)

kRPC 0.6 has no RD-node list and no UnlockTech. `GameScene.research_and_development`
opens the facility; `SpaceCenter.science` is get-only **RAM** R&D.
`vessel.recover()` credits that bank immediately. `persistent.sfs`
`SCENARIO ResearchAndDevelopment` `sci =` lags until Hangar/scene
autosave — after-flight desk must not treat the save file as the
bank. `python main.py desk` prefers live `SpaceCenter.science` (skip
while `flight.lock` is live) then last-flight `sci:` if it is ahead
of disk. Buy CLI:
`python main.py tech-unlock <id>` (aborts if no purchase RPC — do not
edit GameData or the save). Read GameData + save for the tree:

```bash
python main.py world
python main.py tech [node]
python main.py parts --unlocked|--node ID|--search TXT|--module Experiment
```

Sources: `GameData/ModuleManager.ConfigCache` (post-MM PART), save
`CAREER.TechTreeUrl` (letsgrok → HETTN.TechTree), `SCENARIO ResearchAndDevelopment`.
Kerbalism science is `MODULE Experiment` + `HardDrive`. RealFuels is resource
**names**. RealAntennas kRPC is live (`conn.real_antennas`). Early
probes stay omni until a hop goes deaf. Do not cheat a link
(MaxTL / fake target / TxPower). Encode *how to look*, not the
solar system.

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
in the scene that has a vessel. A leftover still listed in tracking while
`game_scene` is `space_center` is not Flight: `vessel.flight()` / control
raise `Procedure not available in game scene 'SpaceCenter'`. Set
`active_vessel` (and `GameScene.flight` if the scene did not move) and wait
for `flight` — do not Hangar a second stack on that pad.
`space_center.vessels` is the live Tracking pool. `persistent.sfs`
FLIGHTSTATE can still list `type=Debris` `sit=FLYING` that Tracking is
empty of. Desk leftover is disk *ships* only; hop leftover is the kRPC
pool. Debris is not leftover.

`KRPC.GameScene` setter is **async** (plugin 0.6 XML): setting returns
immediately; poll until it reports the requested scene. `GameScene.flight`
resumes the save’s active vessel and fails if there is none.
`LoadSpaceCenter` is deprecated.

`python main.py world|tech|parts|screenshot` are disk / grim — no Session.
`status` and `python main.py science` (career snapshot) **open** a Session.
While `flight.lock` is live they are a second writer — do not run them.

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

kRPC 0.6 `PilotAddon.HasControlConnection` is RemoteTech-only (no RT →
always true). House hop keys off `vessel.comms.can_communicate`. Live
reads: `can_communicate`, `signal_strength`, `control_path` (slow pulse),
`CommLink.Start` / `End`, `CommNode.Name` / `IsHome`. RA targeting
exists on `conn.real_antennas` (`Antenna.SetTarget*`); do not use it
to cheat a link. Discover when a hop goes deaf.

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

MechJeb `conn.stream(...)` still untested live. Autopilot wait is not
in this tree — Lars writes it when Gene `need_stack`.

**Pipeline**

Pad/hop use `telem.Telem` (getattr streams). **`watch.py` / `FlightWatch` are
not in this tree.** Hold `flight` / `orbit`; never `vessel.flight()`
per pulse. `vessel.flight()` with **no** frame is the vessel origin —
`speed` is always ~0 (Jeb hop-to-water jsonl). Surface `speed` /
`horizontal_speed` / `heading` stream from
`vessel.flight(body.reference_frame)`. Geographic `latitude` /
`longitude` (degrees) live on that same `Flight` object — hangar
`_on_launch_site` already reads `vessel.flight().latitude` /
`.longitude`. Stream them on the no-frame hold; do not RPC per pulse.
`vessel.biome` is the RSS biome name (`Shores`, `Forest`, …). Downrange
km is haversine from `sites` default pad (Cape under RSS) using
`body.equatorial_radius`. Writes stay RPC. `status` is the
one-shot Session probe.

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
`engaged` bool. No `orientation.py` in this tree.

**AP hold (live):** `engaged=True`, `target_pitch=0`, `target_heading=90`,
`target_roll=0`. `error` streamed at 10 Hz: 73° → 2.6° in 2.25 s.
`ap.wait()` then returned in 0.35 s at `error≈1°`. Disengage → `error`
raises again. Setting `engaged=True` while already engaged **restarts**
the controller (0.5 s `soft_start_time`) — 09-28-59Z inland never held.
Near vertical, heading/roll vs zenith up are ill-defined. Hop inland and
hop-to-water: `set_direction_and_up(direction, north, 0)` in surface
frame; engage once **off vertical** (65/270). 09-44-59Z engaged at ~90
and yawed 340 at burnout. Do not write `target_pitch`/`target_heading`
(09-16-24Z logged 270, flew pad 297/87). `target_roll=0` vs default
zenith up tumbled Stayputnik 16-57-24Z; north up is off the 270/090
path. `target_direction` still maps to those Eulers.

**Launch × physics warp (live 2026-08-23 warp-batch):** Hangar/revert/light
are 1×. `run_physics` after each. Revert returns a ghost (~13 t) before
the hop (mass/parts/stage snapshot). Lighting that ghost, or a second
`activate_next_stage` after whoosh stage 2→1, is the chute. `pre_launch`
MET does not tick — 3× on clamps is not a race. After loft, 3× races
wall-clock (2 s → ~5 s MET). Grim during 3× desyncs the loop. Os allowed
`revert_to_launch` for that batch only.

**Pause (plugin 0.6):** `conn.krpc.paused` is the KRPC service flag.
`space_center.paused` may also exist. Flight Results / `launch_vessel`
can freeze physics **without** that flag reading True — always *set*
`paused=False`, then `rails_warp_factor=0` and `physics_warp_factor=0`
(0 is 1× physics, not stopped). `hangar.run_physics` after Hangar and
before pad dwell.

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

- `discover_ksp()` prefers `~/Games/KSP-rss`; default save `letsgrok`.
  Steam stock is last. Do not install crafts into the Steam tree.
- `install(craft, overwrite=True)` wrote a parseable `.craft` into save `Grok`.
- `launchable_vessels("VAB")` listed those names.
- `launch_vessel(..., crew=[])` on an Mk1 pod raises the in-game **No
  Control** pre-flight dialog; kRPC waits there. Empty command pods are
  not probes. Crew names must be `RosterStatus.available` — assigned or
  missing kerbals still launch empty. `create_kerbal(name, "Pilot", True)`
  if the roster is busy. Close from Flight is `SpaceCenter.save("persistent")`
  then `conn.krpc.game_scene = GameScene.space_center`. The setter loads
  the last SaveGame (`launch_vessel` → `FlightDriver.StartWithNewLaunch`)
  unless RAM was saved first — otherwise UT rewinds 3–4 min (21-21-27Z).
  Save fail: do not set scene. Rewind after setter is Close failure; do
  not Hangar. **Not** `load_space_center` (pad MET 0). **Not**
  `load("persistent")` (F-014 autosaves then reads stale disk). Never
  leftover-ksc. Os disabled Allow reverting flights. Never
  `revert_to_launch`. Walk leftover **ships** home: recover() in Flight
  if rec=yes, wait until gone from `vessels`. Asteroids
  (Ast. XRL-564, `VesselType.spaceobject`) are not ships — do not
  recover them. Crash / not recoverable: Close with
  `reload_save=False`. kRPC 0.6 `UI.clear` removes *client* widgets
  only; `stock_canvas` has no Flight Results buttons (live KSC
  probe). Overlay bit `can_revert` may stay true after walk-home with
  reverting off — that is leftover, not Flight Results (07-50 KSC
  overview, Tracking "no vessels"). `ksc_ready` is scene
  `space_center`, leftover ships n=0; do not treat leftover
  `can_revert` as overlay on that sit. `tracking_station` is not KSC.
  Hangar does not `launch_vessel` until KSC is clean. Os will not click Recover / Cancel / Launch
  anyway. `vessel.recover()` returns before the ship leaves the list
  — wait until gone.
- `launch_vessel(..., recover=True)` from **space_center** and from **flight**
  entered `flight` / `pre_launch` with `active_vessel` set. Internally KSP
  **saves** via `FlightDriver.StartWithNewLaunch` → `GamePersistence.SaveGame`.
  A dirty leftover (killed mid-warp, `freeze`) NREs `FlightState..ctor`
  ("Object reference not set"). `game_scene` already `space_center` is not
  a clean Game — always re-set the scene. On that NRE Close
  (`game_scene=space_center`, no `load_space_center`) and retry
  `recover=False`. Do not wait for a Recover click (L-022). The NRE can happen **after** in-game pre-flight PASS
  (`Go for Launch!`) and **not raise** on the Python client: kRPC
  `launch_vessel` stays in-flight, the hop Session lock is held, and
  `go_space_center` on that Session deadlocks. Watchdog abort is a
  **second** client (connect itself must timeout). After hang, raise —
  do not retry RPCs on the poisoned Session. `python main.py ship`
  must not keep the previous hop as live radio (`stale: yes` when
  `as_of` predates `flight.lock`). After leftover-clean Hangar,
  `Go for Launch!` + kRPC scene `flight` is a **live pad load**, not a
  dialog: RSS Kopernicus/Parallax can sit past 25 s. Abort-to-KSC then
  dumps the vessel and leaves `launch_vessel` in-flight. Run that RPC
  on a side client; poll `game_scene` on the hop Session; abort only
  while still `space_center`. `Session.close` must not wait forever
  for the abandoned RPC.
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

## Science (kRPC 0.6)

**Stock hop** uses `vessel.parts.experiments` (`ModuleScienceExperiment`).
`Part.experiment` raises if the part has more than one — use
`Part.experiments`. Python `Experiment`: `name` / `title` (cfg
`experimentID`: `crewReport`, `mysteryGoo`, `temperatureScan`, …),
`available`, `has_data`, `inoperable`, `rerunnable`, `deployed`,
`biome`, `run()` / `reset()` / `dump()` / `transmit()`.

`science.run_ready` calls `run()` only. Never stock `Experiment.transmit()` /
`dump()` / `reset()`. Skip EVA. Kerbalism TX is an Experiment **event**
(`Transmit` / `TransmitEvent`), uplink verb `transmit` (T-445). Cape
`RateToHome` is 64 bps. Mk1 `ModuleScienceContainer` is
`evaOnlyStorage = True`. `Run()` refuses `has_data`.

**Kerbalism pad** is not that API. Live MM cache: Goo / thermometer /
Stayputnik carry `MODULE { name = Experiment; experiment_id = … }`.
kRPC `Module.fields` and `get_field` are **visible PAW gui names** and
throw if two fields share a gui name. `experiment_id` is a hidden
KSPField. Use `Module.field_list` (`PartField.name` / `.value`),
`get_field_by_id`, or `Module.config.values`. Events: `event_list`
(`PartEvent.name` is stable, e.g. `Toggle` / `ToggleEvent`;
`gui_name` is localized Start/Stop). `parts.modules_with_name("Experiment")`
lists them. Those Module objects are **new proxies** — Python `id()` is
not a stable key vs `part.modules`. Dedup by (part name, experiment_id).
`Toggle` / `ToggleEvent` starts *and* stops; fire once. Do not Toggle to TX.
`science.start_experiments` does **not** call `Experiment.run()`. Recover
the HardDrive **after dwell**, or Gene `uplink transmit` for Kerbalism TX
events (never stock dump/reset/transmit()). Cape 64 bps. Kerbalism Default is time + EC: goo ~641 s (`size` 429 MB
/ `data_rate` ~0.669, `ec_rate` 0.18 on `GooExperiment`), thermometer
~138 s (`ec_rate` 0.002). `sample_amount` is sample count, not duration.
Z-100 is 100 EC; Stayputnik 10; no solar on `kspstuff-pad-pbc`. Pad dwell
caps at remaining EC / sum(in-card `ec_rate`) × 0.8 and recovers on pad
EC=0 if the HD has data (L-045). Done: PAW `status` (recording/running vs
done/depleted/reset required), `Has Data`, remaining sample/data 0,
Stop inactive after we saw it running. No clean flag → wall-clock cap.

RSS Earth FlyingLow / FlyingHigh split is 50 km (stock Kerbin 18 km).
Hop `hop_apo` FlyingLow clamp 8–18 km; FlyingHigh card unclamps to
Space (atmosphere_depth 140 km). OffPlan is that lid, not the cut.

---

## Capability matrix

Status: **live** = exercised against this KSP; **code** = written, not live;
**broken** = live and wrong.

| Item | Status |
|---|---|
| `Session.connect` / `close`, kRPC 0.6.0 | live |
| `game_scene`, `bodies`, profile `auto` → Earth/RSS | live (stock Kerbin retired) |
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
| Autopilot stream wait | not in tree (Gene need_stack) |
| MechJeb `node_executor` | absent |
| `status.services` list | broken (protobuf) |
| `status.remotetech` meaning | broken (stub DLL) |
| `status.commnet` at KSC | broken (needs vessel) |
| PyQt connect + plot | code only |
| `.craft` round-trip vs `vessel.parts` | not done |
| RSS / Kerbalism disk `world`/`tech`/`parts` | code (fixtures + live cache) |
| Kerbalism `Experiment` run / pad | live (Cape 2026-08-20) |
| Pad dwell + recover | live (1235Z) |

---

## Open (technical)

- Encode craft part-name round-trip (`mk1pod_v2` ↔ `mk1pod.v2`) and assert
  after `launch_vessel`. Extend catalog only as names are needed.
- Ascent hot-path reads are on `telem.Telem` streams; writes stay RPC. Respect
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

- **2026-08-25** — T-454: `Session(readonly=True)` connects
  `name=kspstuff-read`. GET only: Control / `game_scene` /
  `active_vessel` / `recover()` raise `ReadOnlyError`.
  `add_stream` is tracked; `close()` `stream.remove()` then
  `conn.close()` (5 s). Writer `Telem.read()` still writes jsonl /
  `ship.md`. Reader Telem does not. `status` and lock-live desk
  leftover_ships use the reader. `kind=recover` sit/rec is a jsonl
  row at `recover()` — last snap is not recover sit (T-453 `hz` is
  actual wall dt, not requested 5–20).
- **2026-08-25** — T-427 prove passed. GSTL/PAW/diff_max=2 (Align real).
  Harmony prefix `RACommLink` Fwd/Rev + postfix `MaxDataRateToHome`
  caps to `TechLevelInfo.MaxDataRate`. Cape `RateToHome` **64 bps**
  (table and path). Kerbalism 0.008 kB/s. Burst `RateBoundariesJob`
  not patched. Pre-clamp Cape was 31500 bps / 3.94 kB/s (channel width)
  — not current. Dump `rate_bps` is still the table; at Cape it matches
  the path. Tape: Snapshot `rate_bps` = `Comms.RateToHome`. Packet:
  `docs/program/ra-rate.md`.
- **2026-08-25** — Os: `KRPC.RealAntennas.dll` in GameData/kRPC.
  `conn.real_antennas` live (Flight / Tracking / KSC). `ra_align`
  stamps owned comms TL (anti-cheat vs sandbox MaxTL). Targeting:
  discover when a hop goes deaf. Do not cheat a link.
- **2026-08-24** — T-325: stream `comms.can_communicate` / `signal_strength`;
  `control_path` home `CommNode.Name` on the slow pulse. RT-only
  `PilotAddon.HasControlConnection`. RA targeting is the 2026-08-25
  service, not this hop gate.
- **2026-08-23** — `Flight.latitude` / `Flight.longitude` are degrees on
  `vessel.flight()` (no-frame hold). `vessel.biome` is the RSS name.
  Downrange km is haversine from Cape (`sites.default_pad_ll`) with
  `body.equatorial_radius`. ship.md + tape `where:` — T-166.
- **2026-08-23** — AP `set_direction_and_up` while already engaged
  disturbs the hold (09-59-28Z MET20 297/66, burnout 336/39). Point
  the same 65/270 vector once. 10-17-18Z skip-if-`engaged` flew
  38/−10 (east, past horizon): re-point that vector if flipped; do
  not re-engage. 10-33-44Z 353/26 missed the 90° gate; returning
  after `set_direction_and_up` skipped `target_direction` — write
  the vector, then north-up.
- **2026-08-23** — AP engage at ~90 has no heading (09-44-59Z burnout
  340/43). Command 25° off vertical, then `engaged=True` once.
- **2026-08-23** — AP `engaged=True` while already engaged restarts 0.6
  PID / 0.5 s soft-start. Near vertical use `set_direction_and_up`
  (north up), not `target_direction` Eulers vs zenith (09-28-59Z).
- **2026-08-23** — `SpaceCenter.science` is RAM. `recover()` credits it;
  `persistent.sfs` sci lags until Hangar autosave (08-04-05Z desk +0.0001
  vs +4.2). Desk `sci:` is bank, not sfs, when kRPC or last-flight has it.
- **2026-08-20** — kRPC 0.6: `GameScene.research_and_development` opens
  R&D; `get_Science` only. No UnlockTech. `python main.py tech-unlock`.
- **2026-08-20** — Disk `PluginData/settings.cfg`: `autoStartServers = False`
  (not True). GameScene setter async. `python main.py science` opens a
  Session. Telemetry is `telem.Telem`; no `watch.py`. Desk briefing
  `docs/program/krpc.md`. No Kerbalism kRPC service.
- **2026-08-20** — `--full` must skip the FS dance when the buffer is
  already monitor-sized / already FS (inactive workspace still
  `grim -T`). Always restore original `fullscreen`/`fullscreenClient`,
  not `internal=0`.
- **2026-08-20** — Hyprland screenshot: `grim -g` of KSP `at`/`size`
  captured the covering Grok TUI while `visible=false`. Live capture is
  `grim -T <stableId>` (`python main.py screenshot`). X11
  `magick import -window` also works on this XWayland client. No
  geometry / focus fallback — fail closed (2026-08-23).
- **2026-08-20** — kRPC `Module` from `parts.modules_with_name` is a new
  proxy vs `part.modules`; `id()` does not dedupe. Kerbalism `Toggle` starts
  and stops. `start_experiments` keys on (part name, experiment_id) (L-043).
- **2026-08-20** — Canonical root `~/Games/KSP-rss`, save `letsgrok`. Disk
  readers `world.py` / ConfigCache / HETTN. Steam path is last. Do not fly hop/mun.
- **2026-08-19** — kRPC 0.6.0 client+plugin. `Session.connect` on 50000/50001.
  Schema ~30 s first time. `get_services()` is protobuf → `status.services==()`.
  `remote_tech` attr true with no RT mod. `active_vessel` None at KSC.
- **2026-08-19** — Empty plugin `settings.cfg` does not auto-bind; wrote
  AutoStartServers / AutoAcceptConnections / 127.0.0.1 ports.
- **2026-08-19** — `AutoPilot.engage` missing; `engaged` bool property works.
  No orientation helper in-tree.
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
- **2026-08-20** — Kerbalism pad 1101Z: `Module.fields` is PAW gui
  names, not `experiment_id`. Use `field_list` / `get_field_by_id` /
  `config`. L-042.
- **2026-08-20** — Pad 1136Z started the card then recovered empty
  (sci 0). Kerbalism experiments need dwell; `pad` waits for done or
  size/`data_rate` (L-044). Do not `sample_amount`/`data_rate` (goo
  count=1 → ~1.5 s).
- **2026-08-20** — Pad 1204Z died EC=0 at T+483 s during goo dwell
  (L-045). Goo canister `ec_rate` 0.18; MM cache last-wins was lab 0.9.
  Pad recovers partial HD; Z-100 cannot feed a full 641 s sample.
- **2026-08-20** — Hop leftover Flight Results: `vessel.met` frozen,
  `recoverable` never true. `go_space_center` dismisses that modal.
- **2026-08-21** — Catastrophic Failure Flight Results stay
  `situation=flying` q=0 low alt with MET frozen; sit never becomes
  `landed` and `recoverable` stays false. Space Center / Close
  (`go_space_center`) leaves the modal. Do not Revert. Telem
  `wreck=false` until MET-still + q=0 + alt≤250 m.
- **2026-08-22** — Flight Results overlay follows `GameScene` (R&D and
  tracking still show it). No OCR, no UI click. leftover-ksc save/load
  **retired** (T-142). Walk home `recover()` + Close.
- **2026-08-22** — OKTO `ModuleReactionWheel` duplicate PAW gui
  `Reaction Wheels`: kRPC 0.6 `Module.fields` / `get_field` raise
  `ValueError Key: Reaction Wheels`. `telem._module_flag` uses
  `field_list` / `get_field_by_id`; do not getattr `.fields` unguarded.
- **2026-08-23** — T-142: leftover-ksc RIP. Walk home `recover()` +
  Close (`reload_save=False`). `load leftover-ksc` refused. Never
  revert. Never recover Ast. XRL-564. kRPC 0.6 UI still cannot click
  Flight Results (`stock_canvas` empty; `UI.clear` client-only).
- **2026-08-23** — T-145: after walk-home, scene `space_center`,
  leftover ships n=0, Tracking "no vessels", screenshot KSC overview
  with no Flight Results. `can_revert` / `can_revert_to_launch` stayed
  true (active vessel UUID dead). That leftover bit is not overlay.
  `ksc_ready` / `overlay_painted` must not fail that sit.
- **2026-08-24** — T-388: splash `recover()` then Close too soon leaves
  a SUB_ORBITAL tracking ghost (same name, `recoverable=0`, MET still
  ticks). `vessel.recoverable` at `space_center` is often false — enter
  Flight first. recover() returns before the ship leaves `vessels`;
  wait gone *before* Close. A later Session may 404 the GUID (`No such
  vessel`) — `name` raising is not leftover. Desk hangar leftover is
  live `leftover_ships`, not stale `persistent.sfs` SUB_ORBITAL after
  recover. A *living* SUB_ORBITAL leftover (go_flight parts loaded)
  will land — wait the MET clock, then `recover()`. Close while flying
  does not drop it. Crash-UI MET freeze never sets `recoverable`. After
  Close, Tracking may list the same GUID as SUB_ORBITAL rec=0 —
  remember kRPC `_object_id` (Vessel has no `.id` in this 0.6 client)
  on disk (`unrecoverable.last`) so the next process skips it. Os will
  not click Recover. Never revert. Never leftover-ksc.
- **2026-08-26** — T-479: Kerbalism `VesselData` ctor
  `parts.Add(part.flightID)` throws on duplicate uint keys (OnSave /
  Close persist). Harmony skip-dup (`kspstuff_kerbalism/`, Os copy,
  `build.sh` does **not** install). Not a vessel-name dict. Persist
  after the blob is gone is still the safe kRPC Close. Never
  leftover-ksc. Never `load("persistent")`. Never revert.
- **2026-08-24** — T-396: `GameScene.space_center` from Flight loads the
  last SaveGame (launch snapshot) unless `SpaceCenter.save("persistent")`
  wrote current RAM first. Detect-and-log after UT drops cannot un-rewind.
  Save fail stays Flight. Named `hop-exit-<stamp>` is legal; never
  leftover-ksc; never `load("persistent")` (F-014). Air leftover is not
  a Hangar veto; rewind is.
- **2026-08-23** — Tape eyes: state rows carry `recoverable`, `chute`,
  `sci_run`/`sci_rem`, `mass`, `available_thrust`, streamed
  `flight.g_force`. `kind=landing` also on wreck; `kind=recoverable` on
  edge; `flightlog.close` synthesizes landing if the hop stayed flying
  (23-54-24Z start/end only). Packet skim `tape:` / `events:` — not 9
  columns. `reliability_broken` is Kerbalism module flags, not exploded
  parts. Shear is `len(parts.all)`, `parts.root`, `vessel.mass`, debris
  `VesselType`. Skim `stack: mass=pad→last parts=n shear=` and
  `descent: peak→last n= gap=`. Tape apex is peak **alt**, not max apo.
  Bind streams by `Vessel.id`, not Python `is`. `reliability_broken` /
  sci/debris/`parts.all` are the slow walk — once, then again at
  landed/splashed. Do not re-arm every cheap pulse (16-47-21Z 0.07 Hz
  / 26 samples / 380 s). Do not getattr `Module.fields` when
  `field_list` already listed (OKTO duplicate gui; ~13 s/pulse).
  grim 10 s ticks skip after a grab ≥0.8 s; `Telem.read` does not grim
  inside the timed pulse. Silk recover with last `sit=flying` still
  envelopes `sit=landed rec=yes`.
- **2026-08-23** — Warp-batch (Os revert-ok that sit): Hangar 1×
  stage=2 eng=0/1. Light 8 s → 545 m. Revert ghost mass ~13 t then
  hop 4077 kg stage=2. 3× after loft: 2 s wall → 5.34 s MET, rails 0.
  1× tracks wall. Whoosh on revert-load is the ghost / a premature
  stage — wait for the Hangar snapshot before `activate_next_stage`.
  kRPC 0.6 still unused: `Flight.mach` / `static_pressure` /
  `terminal_velocity` / `atmosphere_density`, `Vessel.delta_v` /
  `burn_time` / torque tensors, `CrewCount`. RealChute is
  `parts.parachutes` State else `RealChuteModule` field_list. No FAR
  service. Do not getattr `Module.fields` unguarded.
- **2026-08-21** — FAR + RealChute + RealHeat on `KSP-rss`. No FAR
  kRPC service in 0.6 client. `dynamic_pressure` is still stock
  `flight`. RealChuteModule replaced ModuleParachute on stock chutes
  (MM cache). Unlocked chute search is empty (survivability 15).
  RealHeat retunes shock/convection; not a heatshield part. hop.py
  still forbids parachute in the craft. First FAR hop is unflown.
- **2026-08-21** — Save `FLYING` Debris is not Tracking leftover.
  `space_center.vessels` empty while `persistent.sfs` still lists
  Debris: desk hangar `none`. Hangar `refuse` is exact craft basename,
  not a `geiger-pbc` substring.
- **2026-08-23** — `launch_vessel` SaveGame NRE after pre-flight PASS
  hung the hop Session (T-116 `2026-08-23T06-32-23Z-hop`). Abort
  client `game_scene=space_center` does not unblock the first RPC.
  Do not `go_space_center` on that connection. Hangar raises
  `session poisoned`. `ship.md` hangar sit + `stale: yes`.
- **2026-08-23** — T-137: after leftover-clean Hangar, pre-flight PASS
  and kRPC scene **Flight**, the 25 s abort-to-KSC killed the pad load
  (Kopernicus/Parallax). `launch_vessel` runs on a side client
  (`kspstuff-launch`); hop Session polls `game_scene`. Abort only
  while still KSC. `Session.close` times out 5 s.
- **2026-08-23** — T-139: aero shear is `parts.all` length + `mass`,
  not `Module` broken. `parts.root`, debris vessel type. Tape
  synthesizes `shear` from mass jumps on old jsonl.

## FAR / RealChute / RealHeat (disk 2026-08-21)

Physics, not a new hangar catalog.

- **FAR:** `FerramAerospaceResearch` + FARAeroPartModule on parts.
  Stock gravity-turn / Q numbers from the Flea hop are **not** a FAR
  envelope. Telem still streams stock `dynamic_pressure`.
- **RealChute:** `RealChuteModule` + `ProceduralChute` on Mk16 / Mk25
  / RC_* . Tech **survivability** (15 sci) or later. We have 2.43 sci.
  Do not tell Gus we have a chute.
- **RealHeat:** `REALHEAT` cfg (shock multipliers). Ballistic hops and
  recoveries can cook parts stock heat would spare. No kRPC.
- **Not RO:** RealFuels-Stockalike may already be on this tree. That is
  not RealismOverhaul. Parked copy is `~/Games/KSP-RO`.
