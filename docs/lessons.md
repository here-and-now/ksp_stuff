# Lessons

**letsgrok only.** Kerbin/Mun campaign notes are in
`docs/archive/kerbin-lessons.md`. kRPC 0.6 API facts that are still
true live in `docs/agent-notes.md`.

After anything unexpected on this save (failed API, wreck, empty HD,
EC=0):

1. Append a heading **run — title** (example: `## 2026-08-20T11-01-00Z —
   Pad recover is not science`). No letter-codes. Old Cape files keep
   their compact names.
2. Put the fix in a `.py` next to `main.py`.
3. Patch `docs/agent-notes.md` if the API fact is still current.

```bash
source .venv/bin/activate
python main.py world
python main.py pad
```

---

## 1101Z — Pad recover is not science

- **When:** 2026-08-20 letsgrok `python main.py pad` (1101Z). Uncrewed
  `kspstuff-pad-pbc` (Stayputnik + Goo + thermometer + procedural SRB).
- **Symptom:** exit 0, duration 0 s, `science (none)` then `recovered`.
  Linus card was Kerbalism `mysteryGoo` + `temperatureScan`. Craft on
  disk had those parts. No skip lines in the handoff.
- **Cause:** `start_experiments` read `experiment_id` from kRPC 0.6
  `Module.fields` / `get_field` (visible PAW gui names). Kerbalism
  `experiment_id` is not guiActive, so eid was `""` and
  `eid not in PAD_EXPERIMENTS` skipped every `Experiment` module with
  no log. `pad.run_on_vessel` recovered anyway.
- **Fix:** `science.module_field` uses `field_list` / `get_field_by_id` /
  `module.config` / part-name map (`GooExperiment` → `mysteryGoo`).
  Log card misses. `pad` `MissionAbort("no science")` + `abort_pad`
  when a briefed card starts nothing; `science_ids=()` still recovers.
  Modules: `science.py`, `pad.py`.

## 1119Z — Second Toggle stops pad science

- **When:** 2026-08-20 letsgrok `python main.py pad` (1119Z) after 1101Z.
- **Symptom:** exit 0. Card started (`mysteryGoo`, `temperatureScan`) then
  recovered. Handoff listed each start twice (and Stayputnik skips twice).
  Kerbalism `Toggle` / `ToggleEvent` is start *and* stop.
- **Cause:** `iter_science_modules` walked `part.modules` then
  `modules_with_name`. kRPC 0.6 returns new Module proxies, so `id()` did
  not dedupe. A second trigger stopped the sample before recover.
  Stayputnik also carries `temperatureScan` (in-card by id; different part).
- **Fix:** One slot per (part, experiment_id). Kerbalism `Experiment` wins
  over leftover `ModuleScienceExperiment`. Prefer Start over Toggle. Keep
  a running module; do not Toggle it again. Modules: `science.py`.

## 1136Z — Pad recover on Start is empty HD

- **When:** 2026-08-20 letsgrok `python main.py pad` (1136Z) after 1119Z.
- **Symptom:** exit 0, duration 0 s. Card started (`mysteryGoo` once,
  `temperatureScan` on 2HOT + Stayputnik). Recovered. Save still sci 0.
- **Cause:** Kerbalism Default `MODULE Experiment` is time + EC
  (`data_rate` / `sample_amount`). Helm recovered on the Start tick;
  the HardDrive had nothing yet. Not a second Toggle.
- **Fix:** `pad` still named `pad`. After `start_experiments`, dwell with
  FlightWatch-free `Telem` until in-card slots are done (Has Data /
  remaining 0 / status complete / stopped after running) or the catalog
  wall-clock (`ScienceDefs` size / `data_rate` — not `sample_amount` /
  rate). Abort on EC=0, reliability, wreck, uplink `abort_pad` / `recover`
  / `hold`. Do not Toggle again. Empty start still `MissionAbort("no science")`.
  Modules: `pad.py`, `science.py`, `catalog.py`.
  (EC=0 abort superseded by 1204Z.)

## 1204Z — Pad EC=0 is not a wreck if the HD has data

- **When:** 2026-08-20 letsgrok `python main.py pad` (1204Z) after 1136Z.
- **Symptom:** exit 2 `ABORT ec=0` at T+483 s. Card started (`mysteryGoo`,
  `temperatureScan` on 2HOT + Stayputnik). Probe dead before recover.
- **Cause:** 1136Z dwell waited ScienceDefs size/`data_rate` (~641 s goo) and
  treated pad `pre_launch` EC=0 as wreck. `GooExperiment` `ec_rate` 0.18;
  Z-100 is 100 EC + Stayputnik 10. No solar. Catalog last-wins `ec_rate`
  was the lab (0.9), not the canister. abort_pad recovered then raised.
- **Fix:** Cap pad dwell to remaining EC / sum(in-card `ec_rate`) × 0.8.
  Pad EC=0 recovers the HD if any slot has data or we already saw it
  running; abort only if the HD is empty. Catalog merge keeps the
  smallest positive `ec_rate`. Do not edit `.craft` — a full goo sample
  still needs more battery (Gene / VAB). Modules: `pad.py`, `science.py`,
  `catalog.py`.

## stack-review — uplink science is a second Toggle

- **When:** 2026-08-20 stack review after 1235Z (letsgrok pad, exit 0).
- **Symptom:** Live path was sound (card start, 740 s catalog wall, recover,
  sci 2.22). `run_on_vessel` still `take()`s hop radio before start and
  every dwell pulse: `call(science)` is a second Kerbalism Toggle; `stage`
  lights the unused pad SRB; `abort_pad` recovered then the compose
  continued (exit 0).
- **Cause:** Hop-era uplink table on the pad path. `start()` clears a
  leftover; a science/stage/abort written during Hangar still fires.
- **Fix:** Pad consumes uplink: abort-class raises; science and stage are
  not called. Empty card still aborts. Uncrewed Hangar unchanged.
  Modules: `pad.py`.

## hop — light, flying card, recover HD

- **When:** 2026-08-20 after 1235Z pad. Gene `need_stack` hop. Os: more
  science, off the ground.
- **Symptom:** Catalog was `pad` only. Pad does not light. Helm could not
  leave the Cape.
- **Cause:** `phases.NAMES` stopped at pad compose. FlyingLow is a
  different Kerbalism subject; ballistic peri is underground.
- **Fix:** `hop` in `phases.NAMES` / `blocks.md`. `python main.py hop` /
  `phase hop` on an already-launched uncrewed vessel — does **not**
  Hangar `kspstuff-pad-pbc`. Light, start the Kerbalism card once
  airborne, dwell through the ballistic, recover HD when
  landed/splashed/wreck-recoverable. `hop_apo` 15 km, cut at target,
  OffPlan above ~18 km. `check_expect(skip_peri=True)`. Empty tanks after
  the motor are expected. No chute, no FlightWatch, no stock
  `Experiment.run`. Modules: `hop.py`, `phases.py`, `science.py`,
  `main.py`.

## hop — Hangar the Flea, not the pad motor

- **When:** 2026-08-20 after 1235Z pad. Gene `need_stack` hop. Conference
  in: Gus `capable: yes` `kspstuff-hop-flea-pbc`, Linus flying card bound.
  `go: wait`.
- **Symptom:** `python main.py hop` / `run_phase` abort `no active vessel
  — Hangar a hop craft first (not kspstuff-pad-pbc)`. Catalog hop did not
  Hangar. `python main.py pad` Hangars the pad motor.
- **Cause:** `hop.run_hop` was an alias of `run_phase` on whatever was
  already active. Empty KSC after Cape recover has no vessel. Lighting a
  leftover `kspstuff-pad-pbc` would be the wrong motor. Splash
  `mysteryGoo` on the Linus card is not a hop start (FlyingLow goo will
  not finish on this hang).
- **Fix:** `python main.py hop` copies `crafts/kspstuff-hop-flea-pbc.craft`
  into the save VAB (byte-copy; do not `Craft.load` round-trip) and
  `hangar.launch(..., uncrewed=True)` — `go_space_center`, recover
  leftover, 25 s pre-flight watchdog. Refuses `kspstuff-pad-pbc`.
  `phase hop` Hangars when empty or leftover pad motor; already-launched
  hop skips Hangar. Airborne start is the flying card
  (`kerbalism_TELEMETRY` + `temperatureScan`); splash goo stays off.
  `hop_apo` 15 km, OffPlan ~18 km, `skip_peri`, recover when
  landed/splashed/wreck-recoverable. Modules: `hop.py`, `science.py`.

## 2026-08-20T15-58-12Z-hop — Dead probe EC=0 must recover the HD

- **When:** 2026-08-20 letsgrok `python main.py hop` (`2026-08-20T15-58-12Z-hop`).
  Uncrewed `kspstuff-hop-flea-pbc`. Jeb Hangared, lit, started the FlyingLow
  card (TELEMETRY + thermo). No chute.
- **Symptom:** exit 2 `ABORT timeout` at T+609 s. Last-flight is `gate ec=0`
  then `hop timeout 601s`. Never `hop down`. samples=1. HD not recovered.
- **Cause:** Hop treated airborne `ec=0` as a dwell gate. With science
  already started it `continue`d until `DEFAULT_HOP_S` (600 s) and dumped
  the timeout even if the HD had data. Recover required `_down` (landed /
  splashed / wreck) **and** `vessel.recoverable`. Pad 1204Z recovers on
  EC=0 if any slot has data; hop did not. Ballistic peri negative is not
  the abort.
- **Fix:** Recover on first recoverable after leaving the pad (situation
  may stay flying). EC=0 with HD data (in-card or already started) recovers
  immediately when KSP will take the vessel; otherwise wait wreck-
  recoverable. Do not OffPlan a dead probe. Do not timeout-dump while
  airborne with an HD — abort timeout only if the HD is empty; down and
  not recoverable is still `not recoverable`. Empty pad EC=0 still aborts.
  Modules: `hop.py`, `science.py`.

## 2026-08-20T16-24-37Z-hop — Leftover dead probe recovers HD without a fresh start

- **When:** 2026-08-20 letsgrok `python main.py phase hop`
  (`2026-08-20T16-24-37Z-hop`). Leftover uncrewed `kspstuff-hop-flea-pbc`
  already flying ~73 m, EC=0, fuel=0. Gene: skip Hangar, recover HD, do
  not light. FlyingLow card ran on 15-58-12Z (disk TELEMETRY 0.110 +
  thermo 0.401). `recover_banks: yes`.
- **Symptom:** exit 2 `ABORT no science (wanted kerbalism_TELEMETRY,temperatureScan)`.
  Last-flight: hop airborne, `gate ec=0`, `science skip (no Experiment
  modules)`, abort. HD not recovered. Leftover still flying.
- **Cause:** Hop required `start_experiments` after airborne. Empty
  Experiment list (dead / disabled Kerbalism modules) aborted **before**
  recover. `_hd_ready` only saw Experiment `Has Data` or a start in this
  process — not HardDrive files, not “modules gone”. 15-58-12Z recover-
  on-EC=0 never ran because the science abort is earlier in the same pulse.
- **Fix:** Skip a fresh Experiment start when the HardDrive already has
  data or Experiment modules are gone after leaving the pad; recover on
  first recoverable. Do not Toggle a leftover card. Empty card on a clean
  pad still aborts (modules present but none start; pad EC=0 with empty
  HD). Modules: `hop.py`, `science.py`.

## 2026-08-20T16-36-39Z-hop — Paused wreck must bank the HD

- **When:** 2026-08-20 letsgrok `python main.py phase hop`
  (`2026-08-20T16-36-39Z-hop`). Leftover uncrewed `kspstuff-hop-flea-pbc`.
  Gene: skip Hangar, recover HD, do not light. MET already 0d 00:01:15
  (same as 16-24-37Z).
- **Symptom:** exit 2 `ABORT abort` at T+526 s. Last-flight is `gate ec=0`
  then uplink `abort`. HD not recovered. Stuck still: empty Cape grass,
  alt 72 m, situation flying, toolbar "no vessels", navball 127 m/s.
- **Cause:** 16-24-37Z leftover recover-on-first-recoverable waited for
  `vessel.recoverable`. Catastrophic Flight Results paused physics; MET
  stuck; recoverable never true. `ec=0` with HD `continue`d the wait and
  skipped the rest of the pulse. Gene uplink-aborted. Do not ask Os to
  click Recover.
- **Fix:** Keep waiting a *live* fall (MET moving) until recoverable —
  do not timeout-dump. Frozen MET (~5 s stuck) or a gone vessel after
  leaving the pad recovers hop debris, then `hangar.go_space_center`
  to dismiss Flight Results so the HD banks. Empty pad EC=0 still
  aborts. Modules: `hop.py`.

## 2026-08-20T15-58-12Z-hop — 1 Hz snapshots must hit the run jsonl

- **When:** 2026-08-20 letsgrok `python main.py hop`
  (`2026-08-20T15-58-12Z-hop`). Uncrewed Flea. Os still
  `screenshots/rocket-flea.png` is T+7 s, alt 2.1 km, apo 11.6 km,
  motor lit. Pad 1235Z same hole.
- **Symptom:** jsonl is two lines (start + end `samples=1`). Review
  envelope `samples 0`, alt min None, apo max None, duration 0.0 s.
  Last-flight is `gate ec=0` then timeout — airborne aged out of the
  40-line tail. The room read 72 m from a leftover wreck still because
  the log could not answer where or when.
- **Cause:** `hop.py` / `pad.py` call `Telem.read` each pulse and
  `EventLog.emit("snapshot")` in memory. `EventLog()` has no path.
  `flightlog.record` has no hop or pad caller. Review envelopes
  `kind=state` rows only, so start/end never fill alt/apo.
- **Fix:** Each `Telem.read` writes a `kind=state` row to the seated
  run jsonl (alt, apo, peri, situation, MET, EC, fuel) via
  `flightlog.record(..., force=True)`. Pad dwell uses the same Telem
  pulse. Learn can envelope a hop. Modules: `telem.py`, `flightlog.py`,
  `review.py`.

## 2026-08-20T18-02-57Z-hop — Fresh Hangar must start the flying card

- **When:** 2026-08-20 letsgrok `python main.py hop`
  (`2026-08-20T18-02-57Z-hop`). Uncrewed `kspstuff-hop-flea-pbc`. Jeb
  Hangared, lit, recovered. Linus flying card TELEMETRY 28 s / 0.052 +
  thermo 112 s / 0.002. World sci still 3.20062709.
- **Symptom:** exit 0, recovered. Last-flight is `hop light`, `hop
  airborne`, `science keep HD`, then `gate ec=0`, paused wreck,
  dismissed Flight Results. Never `science kerbalism_TELEMETRY,…`.
  samples 63, apo max 12 km, MET 75.6, EC 310 → 0 at impact. HD empty.
- **Cause:** `_keep_hd` skipped `start_experiments` on a **new** Flea.
  Leftover-HD skip (16-24-37Z) is for already-dead probes. Idle
  TELEMETRY remaining=0 made `card_has_data` true, so hop treated a
  fresh Hangar as leftover and recovered nothing. Thermo never ran.
- **Fix:** Leftover-HD skip only if this process did **not** light.
  `card_has_data(..., remaining=False)` for hop keep-HD — remaining=0
  is not leftover data. A Hangar that lights always starts the flying
  card. Empty pad card still aborts. Modules: `hop.py`, `science.py`.

## 2026-08-20 leftover-flea-spacecenter — Enter leftover Flight from tracking

- **When:** 2026-08-20 letsgrok `python main.py phase hop` after Gene skip
  Hangar. Disk leftover PRELAUNCH `kspstuff-hop-flea-pbc`, activeVessel 12.
  Last-flight still 18-02-57Z recovered. Stuck still: KSC overview,
  tracking `kspstuff-hop-flea-pbc EARTH`.
- **Symptom:** exit 1 SESSION. `RPCError Procedure not available in game
  scene 'SpaceCenter'`. Helm never entered Flight. `status` died the
  same way. Tracking still lists the Flea. No Hangar.
- **Cause:** `phase hop` skipped Hangar (leftover already launched) then
  called Telem/control in SpaceCenter. `vessel.flight()` is not a
  SpaceCenter procedure. Leftover lived in tracking, not on the pad
  scene. A second Hangar would occupy the same site.
- **Fix:** Find the hop Flea in active or `space_center.vessels`. If the
  scene is not Flight, `switch_to` / `GameScene.flight` and wait.
  Then light / recover that stack. Empty KSC still Hangars. Modules:
  `hop.py`, `hangar.py`.

## 2026-08-20T18-22-47Z-hop — One Toggle per flying-card id

- **When:** 2026-08-20 letsgrok `python main.py phase hop`
  (`2026-08-20T18-22-47Z-hop`). Scene-enter worked. Uncrewed leftover
  Flea. Jeb lit, airborne, started the card.
- **Symptom:** exit 0. Handoff `science start temperatureScan`,
  `kerbalism_TELEMETRY`, **again** `temperatureScan`, then dwell, EC=0,
  paused wreck, dismissed Flight Results. **No `recovered` line.**
  World sci still 3.20062709. TELEMETRY 28 s should have credited
  FlyingLow while recording if it actually ran.
- **Cause:** Stayputnik also carries `temperatureScan` (in-card by id).
  `start_experiments` Toggled 2HOT **and** the core. Kerbalism Toggle
  is start *and* stop (1119Z). File experiments credit while recording
  — a stopped TELEMETRY writes nothing. `_finish_hd` dismissed the
  crash UI and returned recovered without logging or `vessel.recover()`.
- **Fix:** One trigger per experiment_id, card order, native part
  (thermo on `sensorThermometer`, TELEMETRY on Stayputnik). Skip the
  core's duplicate thermo. Paused-wreck dismiss logs `recovered` and
  retries recover after `go_space_center`. Modules: `science.py`,
  `hop.py`.

## splash — wait for Water, then goo dwell

- **When:** 2026-08-20 Gene `need_stack: splash`. Os max Start harvest.
  Catalog was pad + hop. Linus splash goo (`mysteryGoo` Water, 641 s /
  0.18, recover_banks) is not a hop start.
- **Symptom:** Hop lights, starts FlyingLow, recovers on first
  recoverable / EC=0 wreck. Splash dwell never runs.
- **Cause:** `phases.NAMES` stopped at hop. Hop's recover-on-down is
  correct for the flying card and fatal for a 641 s Water sample.
- **Fix:** `splash` in `phases.NAMES` / `blocks.md`. `python main.py
  splash` / `phase splash` on leftover `kspstuff-hop-flea-pbc` — no
  Hangar, no light, no pad motor. Wait until splashed, one Toggle
  GooExperiment, dwell, recover HD. Landed is not splashed. Flying
  recoverable does not recover. Frozen wreck still `go_space_center`.
  Modules: `splash.py`, `science.py`, `phases.py`, `main.py`.

## hop-to-water — Start Flea cannot steer to Water

- **When:** 2026-08-20 Gene `need_stack: hop-to-water`. Splash is in
  catalog; hop still dies on Shores (18-32 lithobrake 74 m) and
  recovers — that leftover is not Water.
- **Symptom:** Splash waits for `splashed`. Hop recover-on-down leaves
  a Shores wreck or an empty KSC. Gene wanted an east leftover.
- **Cause:** `kspstuff-hop-flea-pbc` is Stayputnik + RT-5 Flea + basic
  fins. No reaction wheel, no gimbal, no chute. SAS holds vertical.
  Cape pad biome is Shores; Atlantic is east. A 15 km vertical hang
  falls on the pad. TWR 12 does not buy range without pitch. An east
  AP heading would be a fake.
- **Fix:** `hop-to-water` in `phases.NAMES` / `blocks.md`.
  `python main.py hop-to-water` / `phase hop-to-water` aborts before
  Hangar: Start Flea cannot steer to Water. Do not skip hop recover
  to dump a Shores wreck on splash. need_builder for east pitch, or
  skip splash. Modules: `hop.py`, `phases.py`, `main.py`.

## pad-card — seated science.md, not PAD_EXPERIMENTS

- **When:** 2026-08-20 Gene `need_stack: pad-card`. Linus bound
  `geigerCounter` 497 s / 0.005 on `kspstuff-pad-pbc`. go: wait.
- **Symptom:** `pad.py` `run_on_vessel` defaulted
  `science_ids=PAD_EXPERIMENTS` (mysteryGoo + temperatureScan). A geiger
  card would re-fly F-005 Cape goo+thermo.
- **Cause:** Hop and splash already read seated `science.md`. Pad still
  used the hardcoded pair.
- **Fix:** `pad_science_ids()` / `card_pad_ids` — Pad/landed rows only.
  FlyingLow and splash stay off. Empty card still falls back to
  `PAD_EXPERIMENTS`. Bound geiger starts geiger. Modules: `pad.py`,
  `science.py`.

## 2026-08-20T19-06-59Z-pad — Frozen MET dwell must not recover empty HD

- **When:** 2026-08-20 letsgrok `python main.py pad`
  (`2026-08-20T19-06-59Z-pad`). Card `geigerCounter` 497 s / 0.005.
  pad-card patch skipped goo/thermo and started geiger.
- **Symptom:** exit 0, recovered twice. World sci still 3.70130873.
  samples 442, wall 583 s, **met max 0.0**, situation **pre_launch**
  first and last. EC 310→280 (command drain). Catalog wall 575 s.
  Stuck still: KSC, no vessels, sci 3.7.
- **Cause:** `dwell_for_card` uses wall-clock `pad_dwell_s`. UT moved;
  vessel MET stayed 0 (pre_launch). Kerbalism file science credits
  while recording — the geiger clock never ran. Timeout still
  `recover_or_abort` on an empty HD.
- **Fix:** Dwell watches MET. Frozen MET → unpause / enter Flight.
  Catalog timeout with no stored data (Has Data / HardDrive, not idle
  remaining=0) aborts `MET frozen, empty HD` or `dwell timeout empty
  HD`. Timeout with data still recovers. Modules: `pad.py`.

## 2026-08-20T19-26-57Z-pad — Unpause physics so pad MET actually moves

- **When:** 2026-08-20 letsgrok `python main.py pad`
  (`2026-08-20T19-26-57Z-pad`). Geiger Toggle, then ABORT MET frozen,
  empty HD. Sci still 3.70.
- **Symptom:** exit 2. `science start geigerCounter`, dwell, `pad MET
  frozen`, timeout 575 s, abort. Never `pad unpause`. MET max 0.0,
  pre_launch. Jeb: unpause/Flight did not move MET.
- **Cause:** `_unpause_clock` only cleared `krpc.paused` when the flag
  already read True, and skipped Flight when scene was already flight.
  Hop Flight Results freeze is not that flag. Hangar `launch_vessel`
  leaves the clock stopped. Kerbalism file science is MET. The honest
  abort fired; time never ran.
- **Fix:** `hangar.run_physics` always sets `paused=False` on krpc and
  space_center, rails/physics warp 1×. Call after Hangar launch and
  **before** pad dwell. Freeze still retries. Empty HD after frozen
  MET still aborts. Modules: `hangar.py`, `pad.py`.

## 2026-08-20T20-08-26Z-pad — MET does not tick in pre_launch

- **When:** 2026-08-20 letsgrok `python main.py pad`
  (`2026-08-20T20-08-26Z-pad`). Hangar fresh, `run_physics` ran
  (`pad unpause`). exit 2 ABORT MET frozen, empty HD. Sci 3.70.
- **Symptom:** UT moved (~1 s/pulse), EC drained, **met max 0.0**,
  situation **pre_launch** first and last, stage 1, warp Nonex.
  Screenshot still T+0. Unpause is not enough.
- **Cause:** KSP does not increment `vessel.met` in PRELAUNCH. Kerbalism
  file science (geiger) is that clock. Goo/thermo 1235Z could bank as
  samples without MET. First stage with SRB `istg=1` would light the
  motor (hop). Pad never staged.
- **Fix:** pad-pbc SRB `istg=0`. Pad does one throttle-0
  `activate_next_stage` on pre_launch (`pad launch clock`) so MET
  starts on the pad. Uplink `stage` still skipped. Frozen MET + empty
  HD still aborts. Modules: `pad.py`, `craft.py`.

## hangar ready — wait on kRPC, not a timer

- **When:** Os: Jeb must not wait 30–60 s for load or geiger. Wait only
  with a named clock and data.
- **Cause:** Pilot card said 30–60 s chunks. Pad/hop slept 1 s after
  Hangar. Dwell did not print experiment remaining.
- **Fix:** `hangar.wait_vessel_ready` polls Flight + `parts.all` +
  `flight()`. Prints `hangar ready`. Dwell prints `wait science <id>
  run= rem= met=`. Commander asks what the sit is for; a timer is not
  a reason. Modules: `hangar.py`, `pad.py`, `hop.py`, `science.py`,
  `.grok/agents/pilot.md`.

## 2026-08-20T20-55-22Z-hop — tech-unlock catalog (kRPC R&D, not GameData)

- **When:** 2026-08-20 letsgrok hop recovered, sci 8.90, tree still
  `start`. Gene `need_stack: tech-unlock`. Linus: buy
  **engineering101** (5) then Gus can sign `kerbalism-geigercounter`.
  F-013: this is the unlock, not a pad geiger sit.
- **Symptom:** `python main.py tech` queries. No buy CLI. Gene does not
  click R&D. Os: never write GameData.
- **Cause:** kRPC 0.6 SpaceCenter exposes `get_Science` and
  `GameScene.research_and_development`. Live `get_services` has no
  UnlockTech / ResearchTech / PurchaseTech. `RDTech.ResearchTech` is
  the honest in-game spend; it is not an RPC.
- **Fix:** `tech_unlock.py` + `python main.py tech-unlock [node]` /
  `phase tech-unlock`. Disk checks node/parents/owned. Opens R&D,
  invokes a purchase RPC if the server grows one, game-`save` persist.
  Aborts if 0.6 still has no RPC. Does not patch the save. Modules:
  `tech_unlock.py`, `phases.py`, `main.py`.

## pad-geiger-hangar — Hangar Gus-signed geiger craft, not pad_pbc()

- **When:** Gene `need_stack: pad-geiger-hangar`. Gus `capable: yes`
  `kspstuff-geiger-pbc` with `kerbalism-geigercounter`. Linus bound
  Cape Surface geiger 497/0.005 on that part (F-013). go: wait.
- **Symptom:** `python main.py pad` used `pad_craft_name()` as the
  **filename** but still called `pad_pbc(wanted)` — Stayputnik + Goo +
  2HOT + SRB, **no Geiger Counter**. A geiger-named template is still
  the wrong stack.
- **Cause:** Pad Hangar generated the Start template. Hop already
  byte-copies `crafts/*.craft`. Seated `craft.md` / VAB already named
  `kspstuff-geiger-pbc`.
- **Fix:** Copy `crafts/<name>.craft` when the file exists. `pad_pbc()`
  only for `kspstuff-pad-pbc`. Missing named file aborts (do not
  generate). Dry-launch skips `current_stage != 0` so a Flea at
  `istg=1` does not light. Modules: `pad.py`, `missions.py`.

## pad-clock — rem/running/UT, not MET; pad physics-warp only

- **When:** Os 2026-08-21: we do not need MET to do science. Safe
  physics-warp testing. Never rails us into the future.
- **Symptom:** Pad aborted `MET frozen, empty HD` on PRELAUNCH while
  a Kerbalism file could still be recording (`wait science run= rem=`).
  Dry-launch existed to tick MET; lighting a Flea would hop.
- **Cause:** 19-06Z treated vessel MET as the science clock. Catalog
  timeout with MET 0 aborted even when the sit was running. kRPC
  `physics_warp_factor` 0 is 1×; rails `WarpTo` jumps UT.
- **Fix:** Dwell watches rem / running / UT. Recording does not abort
  because MET is 0. Empty HD with nothing recording still aborts.
  Pad physics 2–4× on landed/prelaunch (`physics_warp_factor` 1–3),
  rails always 0, never WarpTo, 1× after dwell. Keep dry-launch skip
  when stage would light. Hangar still `kspstuff-geiger-pbc` (F-013).
  Modules: `pad.py`, `science.py`.

## 2026-08-20T22-11-44Z-pad — Geiger part ranks above Stayputnik PAW

- **When:** 2026-08-20 letsgrok `python main.py pad`
  (`2026-08-20T22-11-44Z-pad`). Card `geigerCounter` on
  `kerbalism-geigercounter`. Craft has the part. Uplink abort.
- **Symptom:** Helm Toggled Stayputnik PAW `geigerCounter` and skipped
  the Geiger Counter. `wait science geigerCounter run=1 rem=0 waiting`
  plus `run=0 rem=0 stopped`. UT moved. Flea unlit. Science not filing.
- **Cause:** `_PART_EXPERIMENTS` had Goo and 2HOT only. `_slot_rank`
  returned 1 for `geigerCounter` on both Stayputnik and
  `kerbalism-geigercounter`. First found (PAW) won. Idle PAW rem=0 is
  not a file (F-013).
- **Fix:** Map `kerbalism-geigercounter` → `geigerCounter` rank 0
  (probe PAW rank 2). Start / wait / rem use that preferred slot.
  PAW-only stack still starts. Modules: `science.py`.

## hop-hammer-hangar — Hangar seated Hammer, not the Flea

- **When:** Gene `need_stack: hop-hammer-hangar`. Gus `capable: yes`
  `kspstuff-hop-hammer-pbc` (RT-10, 2HOT, no Geiger). Leftover
  FlyingLow thermo. `hop_apo` 18 km. go: wait.
- **Symptom:** `python main.py hop` still byte-copied
  `kspstuff-hop-flea-pbc`. Pad already Hangars seated/VAB; hop did not.
- **Cause:** `install_and_launch` hardcoded `CRAFT` Flea. `_is_hop_craft`
  only matched the Flea, so a leftover Flea would skip Hangar.
- **Fix:** Hangar `hangar_craft_name()` (seated craft.md / VAB). Refuse
  pad-pbc and geiger-pbc. Leftover skip only the named hop. `hop_apo`
  18 km stays inside the 8–18 km clamp. Modules: `hop.py`, `missions.py`.

## 2026-08-20T22-56-44Z-hop — Hammer 18.8 km is still FlyingLow

- **When:** 2026-08-20 letsgrok `python main.py hop`
  (`2026-08-20T22-56-44Z-hop`). Hangar Hammer. skip Stayputnik thermo,
  start temperatureScan on 2HOT. exit 4 OFFPLAN apo 18858 > 18000.
  Solid ~540 left. Flea not Hangared.
- **Symptom:** `hop_apo` 18 km / OffPlan > 18. Hold set throttle 0.
  RT-10 cannot unlight. Thermo started; never got rem=. MET 15.5 s.
- **Cause:** OffPlan used the hop_apo **clamp** as the science lid.
  FlyingLow is < 50 km. 18.8 km is still the sit. check_expect
  `expect_apo_max` 18000 would have killed it too.
- **Fix:** OffPlan apo > 50 km FlyingLow. hop_apo stays a cut wish
  (solids ignore throttle). check_expect skip_apo on hop. Modules:
  `hop.py`, `phases.py`. Gus if Gene needs a motor that *stops* at 18.

## 2026-08-21T10-30-35Z-hop — Dismiss is not a living recover

- **When:** 2026-08-21 letsgrok `python main.py hop`
  (`2026-08-21T10-30-35Z-hop`). Hangar `kspstuff-hop-flea-pbc`. Card
  FlyingLow geiger (whatever files; 497 s not the hang). Payoff
  recovery@EarthFlew leftover 1.00. FAR+RealHeat+RealChute; chute
  locked. F-013 geiger on craft, engineering101.
- **Symptom:** exit 0, abort none. `science start geigerCounter`, dwell,
  `gate ec=0`, wait recoverable, paused wreck, dismissed Flight
  Results, `recovered` twice. World sci still 2.9559. recovery@EarthFlew
  leftover still 1.00. samples 49, wall 81.4 s, apo max 7571 m, MET
  max 65.8, last flying alt=74 m, EC 310→0.
- **Cause:** Lithobrake froze MET with `recoverable` never true.
  `_finish_hd` treated `go_space_center` as banking the HD and logged
  recovered even when `vessel.recover()` never ran (18-22-47Z test
  asserted that). recovery@EarthFlew and Kerbalism files need a living
  recover, not a crash-UI dismiss. Catalog 497 s was not the miss.
- **Fix:** Frozen MET unpauses physics (`hangar.run_physics`) and waits
  `vessel.recoverable`, then `recover()`. Still stuck: recover hop
  debris if KSP will take it, then dismiss. Dismiss without `recover()`
  aborts — do not exit 0. Modules: `hop.py`.

## 2026-08-21T10-47-59Z-hop — MET-still q=0 flying is down now

- **When:** 2026-08-21 letsgrok `python main.py hop`
  (`2026-08-21T10-47-59Z-hop`). Hangar `kspstuff-hop-flea-pbc`. Card
  FlyingLow geiger on `kerbalism-geigercounter`. F-013 unlocked, on
  craft. FAR+RealHeat+RealChute; chute locked.
- **Symptom:** exit 2, `ABORT not recoverable`. Geiger started, dwell,
  then 600 s `hop wait recoverable`. Lithobrake MET 65 alt 75 EC 9.9
  q=0 still flying `wreck=false`. Unpause only after the wall. Flight
  Results Catastrophic, no Recover button. `recover()` never;
  `go_space_center` dismissed results. samples ~458, wall 619.6 s,
  apo max 7472 m. sci 4.0894 → 4.4896 leftover geiger 2.098,
  recovery@EarthFlew leftover 0.167. Last living hop recovered flying
  199 m.
- **Cause:** Frozen-MET unpause / finish-wreck ran only after
  `waiting_hd` (EC=0 leftover, or the 600 s timeout). A lit hop with
  science started and EC still 9.9 never set that flag, so MET-still
  q=0 flying was treated as a live fall. Crash UI then had no Recover.
- **Fix:** MET-still + q=0 while flying is down now, even without
  `waiting_hd`. Unpause, `recover()` before dismiss, 1 Hz recover line
  names sit + recoverable. Dismiss without `recover()` still aborts.
  Modules: `hop.py`.

## 2026-08-21T11-09-13Z-hop — recover() in Flight, not after dismiss

- **When:** 2026-08-21 letsgrok `python main.py hop`
  (`2026-08-21T11-09-13Z-hop`). Hangar `kspstuff-hop-flea-pbc`. Card
  FlyingLow geiger on `kerbalism-geigercounter`. F-013 unlocked, on
  craft. FAR+RealHeat+RealChute; chute locked.
- **Symptom:** exit 0, abort none, `sci_delta` 0. Geiger started, dwell,
  lithobrake MET 65.8 alt 75 EC 9.9 apo 7.5 km. `hop recover sit=flying
  recoverable=no` through down / unpause / paused wreck / finish wreck.
  `hop dismissed flight results` then `recovered sit=pre_launch
  recoverable=yes`. leftover recovery@EarthFlew 0.167, geiger FlyingLow
  2.098. samples 54, wall 86.3 s.
- **Cause:** `_force_recover` while flying recoverable=no threw; then
  `go_space_center` dismissed Flight Results. `_finish_hd` recovered
  whatever was recoverable **after** dismiss — KSP reported
  `pre_launch` recoverable. That is not a living Flight recover; the
  HD never banked. Recover at ~199 m flying worked on an earlier hop;
  this path waited for the crash UI.
- **Fix:** Call `vessel.recover()` while still Flight when flying
  ≤250 m or already down, **before** `go_space_center`. Do not treat
  post-dismiss `pre_launch` recoverable as hop HD. Dismiss without a
  Flight `recover()` still aborts. Modules: `hop.py`.

## 2026-08-21T11-28-40Z-hop — wait landed in Flight

- **When:** 2026-08-21 letsgrok `python main.py hop`
  (`2026-08-21T11-28-40Z-hop`). Hangar `kspstuff-hop-flea-pbc`. Card
  FlyingLow geiger on `kerbalism-geigercounter`. F-013 unlocked, on
  craft. FAR+RealHeat+RealChute; chute locked.
- **Symptom:** exit 2, `ABORT not recoverable`. Geiger started, dwell.
  `hop recover sit=flying recoverable=no` through airborne / down /
  unpause / paused wreck / finish wreck. `hop dismissed flight results`
  then abort. sci 4.7898 unchanged. leftover recovery@EarthFlew 0.167,
  geiger FlyingLow 1.747. samples 53, wall 84.8 s, last flying alt 78.6
  MET 64.3 EC 9.9. Contrast 11-23-25Z: `sit=landed recoverable=yes`
  before dismiss, sci +0.30.
- **Cause:** `_force_recover` / `_finish_hd` called `recover()` while
  still flying recoverable=no (throws), then `go_space_center` dismissed
  Flight Results. 11-23-25Z banked only after sit=landed in Flight.
  Dismiss is not a living recover.
- **Fix:** Wait `sit=landed` (or splashed) in Flight, then `recover()`.
  Low flying `recover()` only when recoverable. Do not
  `go_space_center` on flying recoverable=no. Frozen MET still unpauses.
  Modules: `hop.py`.
