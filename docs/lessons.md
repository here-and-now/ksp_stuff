# Lessons

**letsgrok only.** Kerbin/Mun campaign notes are in
`docs/archive/kerbin-lessons.md`. kRPC 0.6 API facts that are still
true live in `docs/agent-notes.md`.

After anything unexpected on this save (failed API, wreck, empty HD,
EC=0):

1. Append `L-NNN` below. Do not edit old lessons except to mark
   superseded.
2. Put the fix in a `.py` next to `main.py`.
3. Patch `docs/agent-notes.md` if the API fact is still current.

```bash
source .venv/bin/activate
python main.py world
python main.py pad
```

---

## L-042 — Pad recover is not science

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

## L-043 — Second Toggle stops pad science

- **When:** 2026-08-20 letsgrok `python main.py pad` (1119Z) after L-042.
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

## L-044 — Pad recover on Start is empty HD

- **When:** 2026-08-20 letsgrok `python main.py pad` (1136Z) after L-043.
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
  (EC=0 abort superseded by L-045.)

## L-045 — Pad EC=0 is not a wreck if the HD has data

- **When:** 2026-08-20 letsgrok `python main.py pad` (1204Z) after L-044.
- **Symptom:** exit 2 `ABORT ec=0` at T+483 s. Card started (`mysteryGoo`,
  `temperatureScan` on 2HOT + Stayputnik). Probe dead before recover.
- **Cause:** L-044 waited ScienceDefs size/`data_rate` (~641 s goo) and
  treated pad `pre_launch` EC=0 as wreck. `GooExperiment` `ec_rate` 0.18;
  Z-100 is 100 EC + Stayputnik 10. No solar. Catalog last-wins `ec_rate`
  was the lab (0.9), not the canister. abort_pad recovered then raised.
- **Fix:** Cap pad dwell to remaining EC / sum(in-card `ec_rate`) × 0.8.
  Pad EC=0 recovers the HD if any slot has data or we already saw it
  running; abort only if the HD is empty. Catalog merge keeps the
  smallest positive `ec_rate`. Do not edit `.craft` — a full goo sample
  still needs more battery (Gene / VAB). Modules: `pad.py`, `science.py`,
  `catalog.py`.
