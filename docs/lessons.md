# Lessons

**This is the feedback chain.** Chat is not. After anything unexpected
(failed API, wreck, bad gate, warp stuck):

1. Append a lesson (`L-NNN`) below. Do not edit old lessons except to mark
   `superseded by L-NNN`.
2. Put the fix in a **`.py` next to `main.py`**, not a heredoc
   script. If you need a new file, add it and list it in the lesson.
3. Patch `docs/agent-notes.md` if the API fact is still current.
4. Next agent reads this file **before** flying.

Agents do not drive the PyQt UI. CLI:

```bash
source .venv/bin/activate
python main.py status
python main.py mun
```

---

## L-001 — `AutoPilot.engage` missing (kRPC 0.6)

- **When:** 2026-08-19 first ascent
- **Symptom:** `AttributeError: 'AutoPilot' object has no attribute 'engage'`
- **Cause:** 0.6 uses `engaged` bool property.
- **Fix:** `orientation.set_autopilot` / `autopilot_error`

## L-002 — `get_services` is protobuf

- **Symptom:** `Session.status.services == ()`
- **Cause:** `conn.krpc.get_services()` returns `KRPC_pb2.Services`, not `{name}`.
- **Fix:** still open. Do not trust `status.services`. `getattr(conn, "remote_tech")` is a stub DLL, not the RT mod.

## L-003 — Stream form

- **Symptom:** `add_stream(flight.mean_altitude)` → float has no `__self__`
- **Cause:** property already ran as RPC.
- **Fix:** `add_stream(getattr, obj, "name")`. Hold `flight`/`orbit` until `remove()`. Setters cannot be streamed. `rate=20` yielded ~16 Hz batches.

## L-004 — Control getter lag

- **Symptom:** `throttle = 0.4` then immediate read is `0.0`
- **Cause:** kRPC 0.6: pitch/throttle getters refresh one physics tick after set.
- **Fix:** wait a tick before trusting a get. AP `error` raises if not engaged. Engaging AP clears SAS.

## L-005 — `warp_to` in atmosphere

- **When:** first Mun-lander circularize
- **Symptom:** on-screen “Cannot warp faster than 1x while in atmosphere”; ship reentered and burned.
- **Cause:** apo hit 80 km while still in atmo (peri deeply negative). `execute_node` called `warp_to` for a node 20 min away.
- **Fix:** `warp.in_atmosphere` — skip rails warp. Ascent only declares target apo when `altitude > atmosphere`. `_raise_periapsis` burns prograde with no warp first.

## L-006 — Rails rate is altitude-capped

- **Symptom:** 193 km Kerbin orbit, `maximum_rails_warp_factor=4` (100×). 31 h TLI wait felt frozen.
- **Cause:** stock warp bands. Observed: ~194 km → 4; ~800 km → 7.
- **Fix:** `warp.KERBIN_RAILS_ALTITUDE`. Do not raise to 800 km just for warp — it spent ~115 LF that the lander needed. Prefer 250 km (factor 5 / 1000×) or accept 100× in chunks with heartbeats (`warp_to_ut`).

## L-007 — High Mun flyby accepted as “encounter”

- **When:** Mun attempt 2
- **Symptom:** `Pe=1789758 m`, capture left 1750×1731 km Mun orbit, then “lower Pe to 8 km” Δv −102.
- **Cause:** planner took first SOI hit with `pe > 0`, not Pe in 12–50 km.
- **Fix:** `plan_mun_encounter` **refuses** Pe outside 12–50 km (`MissionAbort`). Do not deorbit from a 1700 km apo to 8 km Pe — that is an impact trajectory. Circularize low (~30 km) first.

## L-008 — Suicide burn started inside stopping distance

- **When:** Mun attempt 2 wreck
- **Telemetry:** `alt=5370 spd=748 vs=-33 burn_d=18561 thr=0` then throttle oscillation 1.0/0.4/0.0; LF 138→0; `alt=-11 spd=344` forever (wreck, loop did not stop).
- **Cause:** warped to Pe−30 s on a 1750×8 km ellipse → already at ~5 km with 750 m/s. Stopping distance 18 km. Then `else: throttle=0` when `alt > burn_d+80` while still 380 m/s at 4 km. No abort on `alt<0` or `thrust=0`.
- **Fix:** `suicide_burn` stays at throttle 1 while `burn_d > alt` or `spd>12` below 8 km. `check_alive` / `MissionAbort` on wreck, empty tanks, lithobrake. `freeze()` on abort. Start suicide from **>25 km**, not at Pe.

## L-009 — One-off scripts are not spec

- **Symptom:** mission logic lived in `python - <<'PY'` and died with the session.
- **Fix:** fly via `python -m kspstuff mun`. New behaviour goes in `kspstuff.*`. UI is parked.
- **Superseded:** there is no `kspstuff` package. Fly `python main.py mun`. New behaviour is a `.py` next to `main.py`.

## L-011 — Silent ascent rode a 27 km peri through atmosphere

- **When:** 2026-08-19 `python -m kspstuff mun`
- **Telemetry:** after fairing/solar, **no 1 Hz line**. Live snapshot: `flying` Kerbin alt=38 km, apo=395 km, peri=27 km, throttle 1, rails 0. Later: `escaping` ecc=1.07, peri=41 km, transfer Terrier `flameout`/`has_fuel=False`, lander still staged, LF=360.
- **Cause:** Ascent only logged on stage/fairing. Break condition was `apo>target and alt>atm`, so with peri still in the air it kept the pitch program and burned until hyperbolic. No atmosphere/peri gate. `warp_to` in atmo is physics-warp. Recover died on flameout instead of lighting the next engine.
- **Fix:** 1 Hz `heartbeat` in the ascent loop. If `peri < atm+5 km` and `alt < atm`: orbital prograde, throttle 1. Break also requires `peri >= atm+5 km`. `atmosphere_danger` / `recover_periapsis` (`python -m kspstuff recover`) relights on flameout, recaptures if `ecc>=1`, then raises peri. `warp_to_ut` skips when `atmosphere_danger`.
- **Superseded by L-012:** the “break only when peri is already above atmosphere” rule is what overburned into a hyperbola. Heartbeat-as-print was not a controller.

## L-012 — Telemetry must drive intervention, not just print

- **When:** 2026-08-19 after L-011. User: entering atmosphere again, no checks.
- **Telemetry:** recover staged the lander (3 parts), burned retrograde then prograde while still `escaping`, declared **lift-done** at `peri=80090` with `apo=-4.4e6` / still hyperbolic. Ascent had kept burning after apo≫target because peri was still in the air (L-011 break rule). Transfer Terrier flameout, lander unstaged. Warp skipped on “peri below atmosphere” even when currently at 400 km — which blocked warping to the circularize-at-apo burn.
- **Cause:** `heartbeat` was a log line. Loops did not share a `FlightState`. Recover treated `ecc<1` for one tick as bound, then burned prograde (raises energy on a hyperbola). Success was peri≥floor only. Ascent dipping override only applied *inside* atmosphere. `execute_node` was silent.
- **Fix:** `watch.FlightWatch` — streams for alt/apo/peri/ecc/sma/q, 1 Hz resources, `pulse()` every iteration. Flags `ATMO DIP ESC FLAME WRECK`. Ascent: cut when apo≥target (do not wait for peri); prograde only if in atmo or already falling toward a dipping peri; energy cap on apo>1.4×target once that would overshoot. Recover: wait for AP alignment; recapture while `ecc≥0.98` or `sma<0` (situation name lags); success = bound **and** peri≥floor. `warp_to_ut` refuses only when *currently* in atmosphere. Node burns pulse and stop on overburn/escape. Parking 250 km (1000× rails). `require_parking` before TLI.
- **Superseded by L-019:** rails in atmo stay illegal; aborting the node is wrong — wait out the air, then warp.

## L-013 — Pad orbit looks like DIP/ESC

- **When:** 2026-08-19 first `FlightWatch` mun attempt
- **Telemetry:** `pre_launch alt=82 peri=-598435 apo=82 ecc=0.995 [ATMO DIP ESC]`. Ascent immediately burned orbital prograde, alt 82→122→92 m, then `relight staged 2 → 0` / flameout abort.
- **Cause:** peri is always underground on the pad, ecc≈1 for any suborbital hop. `dipping` and `escaping` used those raw numbers, so the climb-out override replaced the gravity turn at 80 m. `flameout` also fired on thrust-0-with-fuel (tip-over) and dumped the booster.
- **Fix:** DIP only when peri < atmosphere **and apo is already above it**. ESC only when energy says so **and** we are out of atmosphere (or apo is). Relight stages only on dry active engines / `should_stage`, not a tipped booster.

## L-018 — Recover flight/dialogs without a human click

- **When:** 2026-08-19. User: can you recover from those situations yourself? Screenshot still showed No Control while a 67 Mm ellipse (Bob aboard) was the active vessel. Jeb `RosterStatus.missing`; Val/Bill/Bob `assigned`. `launch_vessel("Jebediah Kerman")` therefore launched **empty** and blocked on the dialog. kRPC has `KRPC.game_scene = space_center` and `create_kerbal`.
- **Fix:** `hangar.go_space_center` (set `game_scene`, fallback `load_space_center`). `default_crew` only uses `available` kerbals; otherwise `create_kerbal("Grok Kerman", "Pilot")`. `launch_vessel` runs with a 25 s watchdog; a second kRPC client aborts a hung pre-flight by switching to space center, then we retry. Do not ask the user to click Recover / Cancel / Launch anyway.

## L-017 — Empty Mk1 is “No Control”

- **When:** 2026-08-19 mun retry. On-screen: “Warning: No Control! This vessel has no remote-controlled or manned command modules.” Launch anyway / Cancel. kRPC `WaitForVesselPreFlightChecks` hangs / fails.
- **Cause:** `hangar.launch` passed `crew=[]`. An empty Mk1 is not a probe — stock will not let you control it. “Launch anyway” would still be uncontrollable (AP/throttle writes do nothing useful).
- **Fix:** `hangar.default_crew` ships Jeb (then Val/Bill/Bob) unless the caller passes names. Do not click Launch anyway; Cancel and relaunch with crew.

## L-016 — Recover burned prograde *at peri*

- **When:** 2026-08-19 after L-015 energy cap (`apo=351098 ecc=0.176`)
- **Telemetry:** `Post-ascent recover` then `tpe=105 peri=66714 apo=352332` → prograde → `apo=1.58e6 … 65e6` while peri stuck ~70 km. AP then flipped prograde/retrograde (err 50–84°) as ecc flickered around 0.98.
- **Cause:** vis-viva: prograde at peri raises **apo**. Recover treated `dipping and heading_to_peri` as “burn prograde”. Peri cannot move until you burn at apo (or circularize there).
- **Fix:** Recover climbs only while *in* atmosphere and apo is still modest; near peri it coasts (warp to apo once above the air) and burns prograde on the way to apo. Apo runaway aborts. Post-ascent does **not** call recover just because peri is low — circularize-at-apo does that.

## L-015 — Climb-out after apo-done overburns to 8 Mm

- **When:** 2026-08-19 ksp-pilot mun. Spotter: `sub_orbital alt=74159 peri=69605 apo=8457959 ecc=0.863 thr=1`. Freeze: `orbiting peri=70729 apo=67e6 ecc=0.980 LF=446 [DIP ESC]`.
- **Cause:** `need_climb = in_atmo and apo_done` kept throttle 1 until leaving the air. `_raise_periapsis` did the same after the energy cap. Prograde in atmosphere with apo already at 250 km sends apo to the Mun. Energy cap (`apo > 1.4×target`) did not save us because the climb-out path lives *after* a break, or kept matching `in_atmo` while apo ran away.
- **Fix:** Once apo ≥ target, **coast** (throttle 0) unless already falling toward a dipping peri. `_raise_periapsis` returns immediately if apo is at target and we are going up. Parent froze the runaway; this stack is not Mun-capable (LF 446, 67 Mm apo).
- **Superseded by L-019:** `_raise_periapsis` still burned while heading to peri.

## L-014 — `launch_vessel` pre-flight after a wreck

- **When:** 2026-08-19 mun retry after the pad tip-over
- **Symptom:** `SESSION Could not launch … Did not pass pre-flight checks` after `Installed kspstuff-mun-lander (12 parts)`. Hung until kRPC raised.
- **Cause:** previous wreck still in the flight scene / recover UI. `launch_vessel(recover=True)` does not always clear it.
- **Fix:** `hangar.launch` retries once, then `recover=False`. Error tells the human to click Recover / Space Center. CLI writes `docs/last-flight.md` so a fixer/pilot does not need the raw terminal dump.
- **Superseded by L-022:** do not ask the human to click Recover. A dirty leftover flight NREs `SaveGame`; reload KSC and retry `recover=False`.

## L-010 — Heartbeat required during warp

- **Symptom:** `warp_to(29021 s)` blocked with no log; could not intervene.
- **Fix:** `warp_to_ut` chunks (default 1200 s) + `watch.heartbeat` every phase. Status command: `python -m kspstuff status`.
- **Superseded by L-020:** chunked `warp_to` is what cycled 1×→max→1× every 20 min. Heartbeat stays; do not call `warp_to` in a loop.

## L-019 — Raise burned through peri; node warp aborted in atmo

- **When:** 2026-08-19 `python -m kspstuff mun` circularize
- **Symptom:** `_raise_periapsis` held throttle 1 from tpe=53 through peri in the air (apo 587 km → 1.58 Mm, peri 68630 → 69138). Then `ABORT node warp blocked — currently in atmosphere`.
- **Telemetry:**
  ```
  raise Kerbin sub_orbital alt=71769 peri=68630 apo=586957 ecc=0.279 LF=611 tpe=53 [DIP]
  raise Kerbin flying alt=69139 peri=69139 apo=1551359 ecc=0.526 LF=548 stg=1 thr=1.00 F=60000N parts=7 warp=1x tpe=0 [ATMO DIP]
  Periapsis now 69138 m  apo 1580026 m
  Planning circularization
  ABORT node warp blocked — currently in atmosphere
  ```
- **Cause:** vis-viva: prograde at peri raises **apo**, not peri (same as L-016). `_raise_periapsis` treated `heading_to_peri` as a reason to keep burning even after apo ≥ target. `_execute_fallback` / `warp_to_ut` raised `MissionAbort` because rails are illegal in atmosphere, instead of coasting at 1× until out of the air and then warping to the circularize-at-apo node (~20 min away).
- **Fix:** `launch._raise_periapsis` coasts (throttle 0) when heading to peri or apo ≥ target. `nodes._execute_fallback` and `warp.warp_to_ut` wait out atmosphere at 1×, then rails-warp to the node. Do not abort a future node just because the ship is currently in the air.

## L-020 — Chunked `warp_to` cycles the warp ladder

- **When:** 2026-08-19 TLI wait after parking ~350 km
- **Symptom:** on-rails warp walked 1×→5×→10×→50×→… then dropped to 1× and repeated. Live `warp=43x` (ramp between 10× and 50×) on a 349×354 km orbit that should hold 1000×.
- **Cause:** `warp_to_ut` called blocking `SpaceCenter.warp_to(chunk, 100000, 4)` every 1200 s of UT so a long wait could still heartbeat (L-010). Each `warp_to` ramps the ladder and returns to 1×. Plugin 0.6 order is `(ut, maxRailsRate, maxPhysicsRate)` — the 4.0 was physics 4×, not a rails cap.
- **Fix:** `warp.warp_to_ut` sets `rails_warp_factor` to the altitude cap (`maximum_rails_warp_factor` / `can_rails_warp_at`), heartbeats on wall-clock 1 Hz, and steps the factor down so remaining UT > 2 s × rate. `drop_warp` on abort/exit. Do not loop `warp_to`.

## L-021 — One `FlightWatch` is the process bus

- **When:** 2026-08-19 stack pass after flattening the checkout
- **Symptom:** every loop `sleep(0.05)` plus RPC `vessel.flight()` each pulse; suicide and `heartbeat()` during warp each opened their own streams. `check_alive` in the descent loop subscribed six streams per iteration.
- **Cause:** `FlightWatch` was a helper, not the clock. Streams are last-push; without `wait_for_stream_update` we polled stale values and paid RPC for new Flight objects.
- **Fix:** `pulse()` waits on the stream socket. Core subscribe list is alt/q/surface + apo/peri/ecc/sma/t_pe/t_ap. Slow RPC at 1 Hz. `enable_landing()` adds speed/vs on the same watch. Ascent, raise, circularize, recover, nodes, warp, SOI, suicide all take that instance. `heartbeat`/`status` remain one-shots.

## L-022 — `launch_vessel(recover=True)` SaveGame NRE

- **When:** 2026-08-19 mun after a ~350 km parking ellipse whose process was killed mid-warp (`freeze`)
- **Symptom:** craft installed, crew resolved, then `SESSION Could not launch 'kspstuff-mun-lander' from VAB onto LaunchPad: Object reference not set to an instance of an object`
- **Telemetry:**
  ```
  Crew Jebediah Kerman  apo=250000 cap=1.25
  Installed kspstuff-mun-lander (12 parts)
  SESSION Could not launch 'kspstuff-mun-lander' from VAB onto LaunchPad: Object reference not set to an instance of an object
  ```
  KSP: `FlightState..ctor` → `Game.Updated` → `GamePersistence.SaveGame` → `FlightDriver.StartWithNewLaunch` → kRPC `LaunchConfiguredVessel` / `WaitForVesselPreFlightChecks`.
- **Cause:** leftover dirty vessel/scene. `launch_vessel(..., recover=True)` saves the current game before putting the new craft on the pad; that `SaveGame` NREs. `go_space_center` no-ops when `game_scene` already says `space_center`. Not the No Control dialog (L-017 / L-018).
- **Fix:** `hangar.go_space_center` always leaves flight (even if the scene name already looks like KSC). On SaveGame NRE, `load_space_center`, wait, retry `launch_vessel(..., recover=False)`. 25 s watchdog stays. Do not ask the user to click Recover.

## L-023 — Rails-warp to Mun peri lithobraked a 23 km encounter

- **When:** 2026-08-19 `python main.py mun` (Jeb). Parking 312×317 km. TLI Δv 714 m/s, planned Mun Pe 23 km. Post-circ LF=647 stg=1 F=60 kN (transfer Terrier).
- **Symptom:** Reached Mun SOI, planned capture at peri, then lithobrake. Empty tanks, hyperbolic, peri underground. `status` GATE escaping. mun still in `warp_to_ut` on frozen UT.
- **Telemetry:**
  ```
  Mun encounter  UT+1004s  Δv=713.8 m/s  Pe=22962 m
  TLI done, warping to Mun SOI
  SOI Mun
  Circularize@Pe node Δv=-386.52 m/s
  warp Mun escaping alt=2840 peri=-109172 apo=-1790316 ecc=1.121 LF=0 stg=-1 thr=0.00 F=0N parts=-1 warp=1x tpe=221 [ESC]
  status Mun escaping alt=2840 peri=-109172 apo=-1790316 ecc=1.121 LF=0 stg=-1 thr=0.00 F=0N parts=-1 warp=1x tpe=221 [ESC]
  GATE escaping ecc=1.121 apo=-1790316
  ```
- **Cause:** Capture never burned (`warp` tag, thr=0). `execute_node` rails-warped toward the capture peri at 1000× inside Mun SOI; patched-conic Pe went from +23 km to −109 km and the ship hit the surface. `time_to_soi_change` NaN near 9.5 Mm sat `warp_to_soi` at 1×, but they still entered SOI (not the 400 s timeout). TLI did not dry the lander (LF=647 after circularize; LF=0 is the wreck). `FlightWatch` has no airless DIP, so no gate until ESC after the freeze.
- **Fix:** `mun.py` — after TLI require next Pe still 12–50 km; `warp_to_soi` uses apo if `time_to_soi_change` is NaN, stops on SOI / Pe < 12 km; capture burns retrograde now if Pe is already low, does not warp to a subsurface peri. `warp.py` — 50× rails cap when airless Pe < 80 km; drop warp / abort on Pe < 0; abort if UT freezes. `nodes.py` `stop_if` on the capture warp. `watch.py` lithobrake danger + `check_alive`.

## L-024 — Gene talks to the script through uplink.md

- **When:** 2026-08-19 after Jeb's Mun lithobrake: Flight could see ESC and could not stop the warp.
- **Symptom:** Gene and Jeb only existed as TUI voices. No way for Flight to abort or retarget the running `main.py mun`.
- **Cause:** One kRPC writer (correct) was also the only brain. Children cannot write `control.*`.
- **Fix:** `uplink.py`. Gene writes `docs/program/uplink.md` (`python main.py uplink …`). The mun `FlightWatch(uplink=True)` takes it every pulse: `abort`/`freeze`/`hold` freeze the stick; `capture` / `no-warp-pe` / `set mun_pe` change the plan. `status` does not take. `loop.md` is notes. Gene uplinks on gates and bad plans only. Pilot cannot override abort. Wreck gates still fire if Gene is silent.

## L-025 — After-flight review from a 1 Hz jsonl

- **When:** 2026-08-19 after Gene could not reconstruct Jeb's lithobrake from 40 handoff lines
- **Symptom:** last-flight.md truncates; no envelope (min peri, time in ESC, LF curve, warp vs alt)
- **Cause:** 1 Hz went to stdout only. Agents must not ingest the stream, but disk can.
- **Fix:** `flightlog.py` records ~1 Hz + flag-change + uplink events to `docs/flights/<utc>-mun.jsonl`. On every mun/recover exit `review.py` writes `*-review.md`. Gene fills **Learn**. Wernher reads the review, not the jsonl. `python main.py review` rebuilds. Status does not record.

## L-026 — Leftover uplink abort kills the next pad start

- **When:** 2026-08-19 `python main.py mun` (Val). Fresh 12-part lander on the pad after Jeb's Mun lithobrake (L-023).
- **Symptom:** Ignition, then abort whose text is the previous wreck. She never left the pad.
- **Telemetry:**
  ```
  pad Kerbin pre_launch alt=82 peri=-598435 apo=82 ecc=0.995 LF=3600 stg=3 thr=0.00 F=0N parts=12 warp=1x tpe=276 [ATMO]
  Ignition
  asc Kerbin flying alt=82 peri=-598436 apo=83 ecc=0.995 LF=3588 stg=2 thr=1.00 F=569813N parts=12 warp=1x tpe=276 [ATMO]
  ABORT uplink abort ESC lithobrake leftover wreck peri=-109172 parts=-1
  ```
- **Cause:** `FlightWatch(uplink=True)` takes `docs/program/uplink.md` on every pulse. Gene's `abort` of Jeb's leftover ESC wreck stayed in the file. Pad `heartbeat` does not take; first ascent pulse did. Pad peri/ESC is already ignored (L-013); the radio was not.
- **Fix:** `uplink.clear` at `flightlog.start` (mun/recover). `watch._apply_uplink` consumes but does not abort/freeze/hold while `pre_launch` or on the Kerbin pad (alt < 200 m). Wreck/flame gates still fire. Gene can still abort after the climb-out.

## L-027 — Occupied pad is not a SaveGame NRE

- **When:** 2026-08-19 Val `python main.py mun` after L-026 pad abort (1823Z)
- **Symptom:** craft installed, crew resolved, then `SESSION Could not launch … Launch site not clear`
- **Telemetry:**
  ```
  Crew Valentina Kerman  apo=250000 cap=1.2
  Installed kspstuff-mun-lander (12 parts)
  SESSION Could not launch 'kspstuff-mun-lander' from VAB onto LaunchPad: Launch site not clear
  ```
  1823Z leftover: Kerbin landed alt=82, 12 parts, LF=3568, stg=2. Status at KSC: `scene=space_center` no vessel.
- **Cause:** L-026 freeze left the lander on the pad. `go_space_center` packed it; `launch_vessel(recover=True)` still failed pre-flight (`WaitForVesselPreFlightChecks`). Hangar then retried `recover=False` (L-014/L-022), which cannot clear an occupied site. Val stayed `assigned` on that stack. Not L-022 (no SaveGame NRE).
- **Fix:** `hangar.clear_launch_site` before `launch_vessel` and on this error: `vessel.recover()` (wait/switch if still flying at 82 m), then `go_space_center`. Keep `recover=True` on “Launch site not clear”. 25 s watchdog stays. Do not ask for a Recover click.
