# kRPC 0.6 — desk briefing

RSS + Kerbalism Default, save `letsgrok` on `~/Games/KSP-rss`. Plugin
and client **0.6.0**. FAR / RealChute / RealHeat are **physics mods**,
not kRPC services. Traps stay in [`docs/agent-notes.md`](../agent-notes.md).
**Do not write GameData.**

One **writer** per process: `Session.connect` on `127.0.0.1:50000` (RPC)
and `:50001` (stream). The Commander owns throttle, AP, stage. Disk
queries (`python main.py world|tech|parts`) never open a client. `status`
and `python main.py science` (career line) **do** — they are a second
Session. While `flight.lock` is live, do not run them.

There is **no Kerbalism kRPC service**. There is **no FAR kRPC** in
this client. Science is `MODULE Experiment` via `part.modules`. Bundled
`KRPC.RemoteTech.dll` is a stub. MechJeb is absent.

---

## Gene Grokman, Flight Director

**Scenes** (`conn.krpc.game_scene`, enum `.name` lowercase):
`space_center`, `flight`, `tracking_station`, `editor_vab` /
`editor_sph`, plus facility pseudo-scenes. Setter is **async** — poll
until it reports the requested scene. `GameScene.flight` resumes the
save’s active vessel and **fails if there is none**.
`LoadSpaceCenter` is deprecated; Hangar uses `KRPC.GameScene`.

**Leftover vs Flight.** Tracking can list a vessel while the scene is
still SpaceCenter. `active_vessel` is `None` at KSC with nothing
spawned. `vessel.flight()` / control in SpaceCenter raise
`Procedure not available in game scene 'SpaceCenter'`. Enter Flight
(`active_vessel` + `GameScene.flight`); do **not** Hangar a second stack
on that pad.

**Load / ready.** Helm must not sleep 30–60 s for Hangar. `hangar.wait_vessel_ready`
polls kRPC (~0.1 s): scene Flight, `active_vessel`, `parts.all` non-empty,
`flight()` callable. Then it prints `hangar ready <name> sit=… parts=N`.
PRELAUNCH is ready (MET may still be 0 until dry-launch). Screenshot is grim, not kRPC.

**What the Commander can see.** In Flight: streams (alt, q, orbit, MET, EC),
situation, parts/modules, recoverability. Screenshot is grim, not kRPC.
Helm cannot see the VAB, the tech tree, or “parts that unlock later.”
That is `python main.py world|tech|parts`.

**Save load (Mortimer only).** After an honest RD edit, copy to
`rd-<node>.sfs` then `python main.py load rd-<node>` (`SpaceCenter.load`).
`load persistent` autosaves RAM onto persistent.sfs first and **wipes
the spend**. Not quickload. Not revert-to-launch. Os is not asked. Helm
never loads a save. After a named RD load, if Flight is an RSS asteroid,
`python main.py ksc` — do not recover the rock (F-015).

**Honest play.** Never revert, quickload, return to VAB, or rewind UT.
`can_revert_to_launch` exists and is **forbidden** — it restores this
flight’s pad, not a new craft. Os will not click Recover / Cancel /
Launch anyway / crash UI. Recover the leftover (`vessel.recover()` when
`recoverable`) or Hangar the next stack. Catastrophic Flight Results
freezes MET and never sets `recoverable`; `go_space_center` dismisses
that modal. `launch_vessel(recover=True)` does **not** clear a live
occupant (`Launch site not clear`) — recover first, then launch with
`recover=True`. Empty crew on a command pod is the No Control dialog;
PBC probes launch **uncrewed**.

19-26-57Z: geiger Toggle, **MET 0.0**, empty HD, 575 s wall. That was
physics stopped, not a client trap. Lars `run_physics` after Hangar.

---

## Lars Grokman, Vehicle Engineering

**Streams.** Form is **`add_stream(getattr, obj, "prop")` only**.
`add_stream(flight.mean_altitude)` already ran the RPC (`AttributeError`
on float). Setters cannot be streamed (`StreamError`). Hold `flight` /
`orbit` for the life of the stream. `Session.add_stream` is a
pass-through. Pad/hop use `telem.Telem` — **`watch.py` is not in this
tree.** Writes stay RPC. `rate` is a cap, not exact Hz; one condition
wait is a batch. First `s()` blocks until the first push.

**Toggle.** Kerbalism `PartEvent.name` `Toggle` / `ToggleEvent` is
start **and** stop. Fire once. `modules_with_name` returns **new
proxies**; Python `id()` does not dedupe — key on (part, experiment_id).
Prefer Start over Toggle. Do not call stock `Experiment.run()`.

**MET vs wall-clock.** Os 2026-08-21: we do **not** need vessel MET
for Kerbalism file science. Pad dwell watches `run=` / `rem=` / UT.
MET 0 on PRELAUNCH is not an abort if the sit is recording. UT can
move while MET stays 0. Do not stage a Flea just to tick MET.
`hangar.run_physics` after Hangar (unpause, rails **0**, physics 1×).
Pad dwell may set `physics_warp_factor` 1–3 (2–4×) on
landed/prelaunch only; **never** `rails_warp_factor` other than 0;
**never** `WarpTo`; back to physics 0 (1×) after dwell.

**SpaceCenter RPCs.** Scene-gated. `WarpTo` **blocks** and cycles the
rails ladder — do not call it (pad: never). Setter lag: throttle/pitch
getters refresh one physics tick after a set. AP: `engaged` bool (no
`engage()`); `error` raises if disengaged; engage clears SAS. Stage 0
restage is a no-op.

**Tech unlock.** `KRPC.GameScene.research_and_development` opens the
facility. `SpaceCenter.science` is get-only
(`ResearchAndDevelopment.Instance.Science`). No UnlockTech /
ResearchTech RPC in 0.6. `python main.py tech-unlock <id>` is the
catalog buy. Do not write GameData or the save.

---

## Gus Grokman, VP Build

kRPC has **no VAB placer**. The writable object is a `.craft` in
`saves/<save>/Ships/VAB/`, then `SpaceCenter.launch_vessel(facility,
name, site, crew, recover)`. Crew list is **required** in 0.6 (empty
list = default assignments). Sign hardware from **disk catalog**, not
the live vessel.

`python main.py parts --unlocked` lists **placeable** parts. `hosts=N`
is Kerbalism PAW slots on that part — not extra VAB parts. Stayputnik
(`probeCoreSphere_v2`) hosts eight Experiment modules including
`geigerCounter`; the Geiger **part** `kerbalism-geigercounter` is
`engineering101` (locked). Seated stack: `python main.py parts --stack`.
Do not sign an experiment id as a part.

File tokens use dots (`mk1pod.v2_<uid>`); in-game names drop the uid
(underscore → dot). Goo canister has its own `HardDrive` (sample);
Stayputnik HD is 0.5 MB (`dataCapacity`). Tape must fit the card
(geiger 0.5 MB fills Stayputnik; do not co-run TELEMETRY 0.75 on pad-pbc).

---

## Mortimer Grokman, CEO

Program facts, not knobs:

| | |
|---|---|
| Tree | `~/Games/KSP-rss` (not Steam). Save `letsgrok`, `SCIENCE_SANDBOX`. |
| Body | RSS Earth (`space_center.bodies` has Earth → profile `rss`). |
| Life | Kerbalism **Default** (`GameData/KerbalismConfig/Settings.cfg` `Profile = default`). Reliability, Deploy, Science on. |
| Crew | PBC unmanned first. Mk1 locked. |
| Client | kRPC **0.6.0**, sockets 50000/50001, `autoAcceptConnections = True`. |
| Auto-start | Disk `PluginData/settings.cfg`: **`autoStartServers = False`**. Zip ships empty cfg. Without Start, nothing binds. **Do not edit GameData to “fix” this.** |
| Pause | `pauseServerWithGame = False`. Server can live while MET is frozen. |
| Comms | RealAntennas on CommNet. **No RA kRPC service.** Early probes stay omni. Do not transmit. |
| Writer | One `phase`/`pad` process. `flight.lock` is the wall. |
| Honesty | No revert / quickload / rewind. Crash UI is not a time machine. |

CKAN lock: close the GUI before launching `KSP.x86_64`. First MM pass
is slow; later boots ~70 s. First `Session.connect` ~30 s (schema).

---

## Linus Grokman, Director of Research

**Two APIs.** Stock leftover: `vessel.parts.experiments` →
`Experiment.run` / `has_data` (cfg `experimentID`). **This save is
Kerbalism.** MM cache: Goo / 2HOT / Stayputnik carry `MODULE { name =
Experiment; experiment_id = … }` plus `HardDrive`. kRPC
`Parts.Experiment` is **not** that module.

**Ids vs parts.** `experiment_id` is a hidden KSPField — not in
`Module.fields` (PAW gui names). Read `field_list` / `get_field_by_id` /
`module.config`. Duplicate gui names throw. Dedup by (part,
experiment_id). Native part wins: 2HOT owns `temperatureScan`, not
Stayputnik. Hosted geiger is still `geigerCounter` on Stayputnik.

**Credit.** File experiments (`kerbalism_TELEMETRY`, `temperatureScan`,
`geigerCounter`) credit R&D **while recording** — MET must move, EC
must last. Goo is a **sample**; that slot still wants recover. Do not
transmit. Do not `dump`/`reset`. Duration is ScienceDefs size /
`data_rate`, not `sample_amount`. Card lines: `experiment_id`, **part**,
`duration_s`, `ec_rate`, `recover_banks`.

Disk 2026-08-20: `sci = 3.70130873`, tree `start`. Cape landed goo
capped; Shores thermo capped. Query `world` / `parts --module Experiment`
/ seated `science.md` — not a live vessel while lock is live.
