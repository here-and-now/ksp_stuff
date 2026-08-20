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
