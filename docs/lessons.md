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

## 2026-08-25 — hop-coast-phys-warp

- **When:** T-442. t7-wheel-pbc. Quiet loft after lid. No chute on hang.
  Do not Hangar. Never revert.
- **Symptom:** `hop coast physics 4x` then Hank `phys-warp 4`; `hop
  physics 1x` as soon as descent starts (~200 km). Not Hank uplink.
- **Cause:** `chute_arm_sit` was lofted `_descending` at any alt, so
  `want_coast` was false from apo to splash. Arm was silk shear ~15 km,
  not 200 km vacuum.
- **Fix:** `chute_arm_sit` is lofted descent in thick air (≤18 km). Quiet
  descent above thick air honors `uplink_rate`. 1× stays thick air /
  high q / silk / burn. This pid will not reload.
- **Modules:** `physics_warp.py`. Not `hop_factory.py` this hire (XOR).

## 2026-08-25T08-20-54Z-hop — hop-coast-phys-warp

- **When:** T-438. t7-wheel-pbc. T-081. Hank `uplink phys-warp 4` after
  50 km lid. f013 TELEMETRY Stayputnik on_craft=yes; 2HOT start
  on_craft=yes; PresMat stability on_craft=yes; geiger e101
  on_craft=yes; goo start on_craft=yes. Tree start,engineering101,
  basicRocketry,survivability,stability. Do not Hangar. Never revert.
- **Symptom:** phys-warp 4 taken at MET~109 / 79 km quiet loft; clock
  stayed 1× through ~178 km sub_orbital (wall≈MET). No `hop coast
  physics 4x`.
- **Cause:** After lid, `_high_dwell_sit` was passed as `burning=` into
  `apply_sit_warp`, so `want_coast` was always False until down. Hank's
  clock never applied.
- **Fix:** High dwell is not a burn. Pass `burning=burning_now` only.
  Wernher `want_coast` already 1× on thick air ≤18 km / high q / silk /
  burn. Quiet loft honors uplink `phys-warp`. Forest / Grasslands: same.
  Never revert. Do not Hangar.
- **Modules:** `hop_factory.py`. Not `physics_warp.py` this hire (XOR).

## 2026-08-25T07-51-42Z-hop — hold-ground-card

- **When:** T-436. t7-wheel-pbc. Bound splash Water T-028 TELEMETRY /
  T-422 2HOT / T-423 PresMat. f013 TELEMETRY Stayputnik host on_craft=yes;
  2HOT start on_craft=yes; PresMat stability on_craft=yes. Tree
  start,engineering101,basicRocketry,survivability,stability. Do not Hangar.
  Never revert.
- **Symptom:** High lid 50 km apo 225 km splash Water rec=yes exit 0.
  skip TELEMETRY / temperatureScan / barometerScan **not in card** while
  desk card lists them. Started goo+geiger (High leftover rem≈0). Bank
  2.29 +0. Splash bind unpaid.
- **Cause:** T-081 fly extras `barometerScan,geigerCounter,mysteryGoo`
  hid splash leftover. `paying_eids` dropped cannot-pay then
  `start_experiments` logged the rest not-in-card. PresMat idle rem=0
  was not duration (2HOT was). Airborne skip should be cannot-pay;
  Water splash still Toggles the leftover.
- **Fix:** Bound `need` eids stay in the card — fly extras cannot hide
  splash leftover. Wrong sit logs cannot-pay, not not-in-card. File rem=0
  (PresMat as well as 2HOT / TELEMETRY / geiger) still pays; sample rem=0
  (goo) still skips. Forest / Grasslands / Water: same. Never revert.
- **Modules:** `science.py`. Not `hop_factory.py` this hire (XOR).

## 2026-08-25T06-57-16Z-hop — flyinghigh-lid

- **When:** T-424. t7-wheel-pbc. Bound splash Water T-028/T-422/T-423.
  Plan hop_apo 50 km. Do not Hangar. Never revert.
- **Symptom:** hop apo=18000, pitch 25 from pad, `hop coast physics 4x`
  at ~3 km q=2670, crash UI sit=flying rec=no met=73.94 alt=3265.9.
- **Cause:** Splash bind is not FlyingHigh. `hop_wants_flying_high` false
  clamped Gene's 50 km lid to 18 km. No vertical hold. Slew in thick
  air. 4× is Wernher T-426.
- **Fix:** `_inland_high_sit`: splash / missing flying card still waits
  the High lid. Bound FlyingLow flying card is airborne Toggle. Unbound
  leftover High is not the latch. `hop_target_apo(space=True)` keeps
  Gene 50 km. Forest / Grasslands: same. Never revert. Do not Hangar.
- **Modules:** `hop_factory.py`. Not `physics_warp.py` this hire (XOR).

## 2026-08-25T06-57-16Z-hop — hop-coast-phys-warp

- **When:** T-426. t7-wheel-pbc. hop_apo=18000 pitch 25 from pad. Lars
  T-424 lid. Splash Water bind. Do not Hangar. Never revert.
- **Symptom:** `hop coast physics 4x` then crash UI sit=flying rec=no
  met=73.94 alt=3265.9 q=2670. Envelope apo 3.5 km. Tape thin.
- **Cause:** `want_coast` 4× after lofted 250 m + burnout + q≤1 kPa
  (NaN q fail-open). 18 km lid is still thick air. 3 km FAR at 4×
  sheared.
- **Fix:** `thick_air_sit` 1× at alt ≤18 km. Unknown q is high (fail
  closed). Vacuum `in_atmo` False is not thick. Same inland hop Forest
  / Grasslands. Never revert. Do not Hangar.
- **Modules:** `physics_warp.py`. Not `hop_factory.py` this hire (XOR).

## 2026-08-25 — RA 64 bps is the table and the Cape path

- **When:** T-427. Os radio prove **passed** after Harmony clamp.
- **Symptom (pre-clamp):** dump / desks owned TL2 **64 bps**. Live Cape
  `RateToHome` was **31500** bps, Kerbalism **3.94 kB/s**. That is not
  current.
- **Cause:** `MaxDataRateToHome` = min Fwd/Rev from `RateBoundariesJob`
  (L ChannelWidth 31.5 kHz × 1 bit/s/Hz). Never read
  `TechLevelInfo.MaxDataRate`. Align stamped GSTL, not RF.
- **Fix:** Harmony prefix `RACommLink` set_Fwd/RevDataRate (antenna
  setters reclamp) + postfix `MaxDataRateToHome`. Cap is
  `TechLevelInfo.MaxDataRate`. Burst job not patched. Prove: Cape
  RateToHome **64**, Kerbalism 0.008 kB/s, table still 64, GSTL=2.
  Dump: 64 is table **and** the path at Cape. Tape: `rate_bps`.
  Packet `docs/program/ra-rate.md`.
- **Modules:** `krpc_realantennas/src/RateClamp.cs`, `telem.py`,
  `comms_catalog.py`, `flightlog.py`. `build.sh` does not install.

## 2026-08-25 — ctt-stability

- **When:** T-399. After Mortimer paid `stability`. Desk tree lists it.
- **Symptom:** `house_dump` still priced next CTT as `stability` 18 LOCKED.
- **Cause:** `STABILITY_COST = 18` hardcoded. Dump did not read owned nodes.
- **Fix:** `next_ctt` cheapest locked RDNode whose parents are owned
  (GameData tree, not persistent.sfs). Fallback `generalRocketry` 20
  when `stability` is owned. Never load the save while a hop is flying.
- **Modules:** `house_dump.py`. Not hop.py.

## 2026-08-25 — Close is Tracking, then KSC

- **When:** After IL dump of `FlightResultsDialog` / `StartWithNewLaunch`.
- **Cause:** Space Center from Flight is the overlay Space Center button
  (launch `persistent`, pad MET 0). Tracking is `onLeavingFlight`.
  Persist RAM first; UT drop is Hangar veto. Sandbox RA GSTL is MaxTL
  unless house `align_tech_level`.
- **Fix:** `_close_to_ksc` persist → Tracking → KSC. `ra_align` stamps
  owned comms TL. Never leftover-ksc. Never revert.
- **Modules:** `hangar.py`, `ra_align.py`, `desk.py`. kRPC RealAntennas.

## 2026-08-24T21-21-27Z-hop — leftover-ksc

- **When:** 2026-08-24 letsgrok T-396. t7-wheel-pbc hop splash rec=yes
  recover() in Flight, then walk_home `_close_to_ksc`. Os: clean KSP,
  UT back 3–4 min, tracking showed the same flight again. Never revert.
  Do not Hangar on a rewound clock.
- **Symptom:** Close logged after the damage. `load_space_center` was
  already refused. Scene setter from Flight still loaded Hangar's
  launch SaveGame. Vessel reappeared. leftover-air was not this fire.
- **Cause:** `launch_vessel` internally `FlightDriver.StartWithNewLaunch`
  → `GamePersistence.SaveGame`. `GameScene.space_center` from Flight is
  the Space Center button: KSP loads that last SaveGame. RAM (recovered,
  UT current) was never written first. `_ut_rewound` only logged.
- **Fix:** From Flight: `SpaceCenter.save("persistent")` then scene.
  Save fail: do not set scene. After scene, UT drop is Close failure —
  do not Hangar. Never `load_space_center`. Never leftover-ksc. Never
  `load("persistent")` (F-014). Air leftover is not a Hangar veto.
- **Modules:** `hangar.py`. Not hop.py.

## 2026-08-24T19-57-33Z-hop — far-shear

- **When:** 2026-08-24 letsgrok. T-394. t7-pbc. Bound FlyingHigh
  T-069 Forest TELEMETRY leftover + T-368 goo + T-369 geiger.
  f013 TELEMETRY Stayputnik on_craft=yes; Goo start unlocked=yes
  on_craft=yes; geiger e101 unlocked=yes on_craft=yes. Tree
  start,engineering101,basicRocketry,survivability. Do not Hangar.
- **Symptom:** hop_apo=50000. goo+geiger Toggle at High, dwell, hold
  burnout, 4× then 1×, shear 20→9 rec=no. Envelope apo=275 km
  q_max=134 kPa g=13 sit=flying impact 132 m/s sci_run=1 bank
  12.38→16.19 (files; goo sample lost). Tape MET 90 lid q=1.8 kPa
  thr 1; MET 103 75 km sci_run=1 q=69 Pa; 4× climb through apo;
  1× from ~271 km. High descent MET 533 alt 53 km q=1.6 kPa.
- **Cause:** `want_coast` 4× after real burnout when q ≤1 kPa. High
  dwell is still lofted burnout on that clock. 4× through apo
  tumbled into High descent q; q gate never saw 4× there (already
  1× on `chute_arm_sit`). FAR sheared on 1× lithobrake.
- **Fix:** `_high_dwell_sit` 1× once FlyingHigh lid latches, until
  down. Skip FlyingLow may still 4×. Same inland hop Forest /
  Grasslands. Never revert. Do not Hangar.
- **Modules:** `hop_factory.py`. Not `physics_warp.py` this hire (XOR).

## 2026-08-24T19-57-33Z-hop — leftover-prelaunch-ghost

- **When:** 2026-08-24 letsgrok T-388. After rec=0 MET freeze Close,
  walk_home logged not pad occupancy but the next `python` still
  leftover=1 hangar recover sit=sub_orbital. protocol fly wait leftover.
  Never revert. Do not Hangar.
- **Symptom:** GUID skip was process-local. overlay.last
  `unrecoverable:` empty. kRPC 0.6 Vessel has no `.id`.
- **Cause:** `remember_unrecoverable` no-op without id. recover-probe
  overlay write started with an empty in-memory set.
- **Fix:** identity is kRPC `_object_id` (stable across clients this
  game). Persist immediately to `unrecoverable.last`. leftover_ships
  reads that file in a fresh process.
- **Modules:** `hangar.py`. Not hop.py.

## 2026-08-24T19-23-00Z-hop — science-skip-timeout

- **When:** 2026-08-24 letsgrok. T-392. t7-pbc. Bound FlyingHigh
  T-069 Forest TELEMETRY leftover + T-368 goo global + T-369 geiger.
  f013 TELEMETRY Stayputnik on_craft=yes; Goo start unlocked=yes
  on_craft=yes; geiger e101 unlocked=yes on_craft=yes. Tree
  start,engineering101,basicRocketry,survivability. Do not Hangar.
- **Symptom:** hop_apo=50000. Pitch 25, burnout, `science skip
  (situation cannot pay)`, coast 4×, splash rec=yes sci=run=0 bank
  12.38. Tape MET 92 alt 54 km sit=flying biome=Shores fuel 0.9
  thr 1; apex 274 km sit=sub_orbital. Trio never Toggled.
- **Cause:** T-331 skip-latch fired at the High lid when paying_eids
  was empty. `sit_matches` treated biome `global` as Shores, and
  required live sit to contain `flying` (sub_orbital at High alt
  is still High). geiger idle rem=0 was not a file duration.
- **Fix:** `sit_matches` High is alt ≥50 km (not landed/splash);
  global/none/any is not a biome. geigerCounter idle rem=0 still
  pays. Factory skip-latch is FlyingLow cannot-pay only — High
  waits the lid, then Toggle. Forest / Grasslands / Shores: same.
  Never revert. Do not Hangar.
- **Modules:** `science.py`, `hop_factory.py`. Not `physics_warp.py`
  this hire (XOR).

## 2026-08-24T19-23-00Z-hop — leftover-prelaunch-ghost

- **When:** 2026-08-24 letsgrok T-388. t7-pbc hop exit 0 splash recover,
  recover() still listed, SC ghost sub_orbital. `--space-center`
  wait-land → MET frozen sit=landed rec=0 (crash UI). Close. leftover
  n=1. Desk hangar recover sit=sub_orbital. protocol fly wait leftover.
  Os will not click Recover. Never revert.
- **Symptom:** crash-UI wreck cannot `recover()`. Close leaves the same
  GUID in Tracking as SUB_ORBITAL rec=0. leftover_ships counted it as
  pad occupancy.
- **Cause:** KSP Recover never arms on Flight Results freeze. Tracking
  sit after Close is SUB_ORBITAL even though Flight was landed rec=0.
- **Fix:** `remember_unrecoverable(vessel.id)` after crash-UI rec=0.
  leftover_ships / ksc_ready skip that GUID. Not pad occupancy. Close
  `reload_save=False`. Never leftover-ksc.
- **Modules:** `hangar.py`. Not hop.py.

## 2026-08-24T19-09-12Z-hop — leftover-prelaunch-ghost

- **When:** 2026-08-24 letsgrok T-388. t7-pbc litho sit=landed rec=no
  met=606 alt=380. `--space-center` then KSC leftover sit=sub_orbital
  rec=0. Second `--space-center`: go_flight parts=20, not recoverable,
  Close, leftover n=1. protocol fly wait leftover. Do not Hangar.
  Never revert.
- **Symptom:** Close on a living SUB_ORBITAL leftover does not drop it.
  go_flight loads the craft (20 parts, MET ticking). Dead-GUID filter
  does not apply.
- **Cause:** T-388 first patch Closed when rec=0 after Flight. That
  ship will land. KSP Recover only after landed/splashed.
- **Fix:** `walk_home` waits leftover land on the MET clock (4× high,
  1× below 5 km, rails 0). recover() when KSP will take it. MET freeze
  (crash UI) stops the wait. Still rec=0: Close `reload_save=False`.
  Never leftover-ksc.
- **Modules:** `hangar.py`. Not hop.py.

## 2026-08-24T18-59-08Z-hop — flyinghigh-lid

- **When:** 2026-08-24 letsgrok. T-391. t7-chute hang. Bound FlyingHigh
  Forest TELEMETRY leftover + goo + geiger. f013 TELEMETRY Stayputnik
  on_craft=yes; Goo start unlocked=yes on_craft=yes; geiger e101
  unlocked=yes on_craft=yes. Tree start,engineering101,basicRocketry,
  survivability.
- **Symptom:** hop_apo=50000, expect_apo_max=400000. OFFPLAN apo 163402
  > 140000 Space. Tape MET 85 alt 41.8 km thr 1 fuel 123, still
  climbing. 18-34-09Z apo 275 km paid after the cut.
- **Cause:** Factory OffPlan used Space atm_depth 140 km on predicted
  apo before live hop_apo. Gene's envelope was 400 km. A paying
  FlyingHigh loft at 41 km is not Space.
- **Fix:** `_offplan_apo_lid` raises the abort to expect_apo_max when
  that number is higher than the sit lid. hop_apo stays the cut.
  FlyingLow stays ≥50 km. Never revert.
- **Modules:** `hop_factory.py`. Not `physics_warp.py` this hire (XOR).

## 2026-08-24T18-34-09Z-hop — leftover-prelaunch-ghost

- **When:** 2026-08-24 letsgrok T-388. t7-pbc lofted apo 275 km, hop
  recovered sit=splashed rec=yes exit 0. Then `recover-probe --recover`:
  recover() splash, walk-home still listed. KSC leftover n=1
  sit=SUB_ORBITAL recoverable=0 met climbing. `--space-center` Close
  did not drop it. `ksc` SESSION leftover. Do not Hangar. Never revert.
- **Symptom:** splash recover left a tracking ghost. `walk_home` saw
  rec=0 at Space Center and Closed without entering Flight. protocol
  fly waited leftover. Next Session: dead GUID
  (`No such vessel`), vessels n=0, `ksc_ready` true.
- **Cause:** `vessel.recoverable` at `space_center` is often false.
  recover() returns before the ship leaves `vessels`. Close during that
  gap leaves a SUB_ORBITAL tracking remnant (same name, rec=0). Dead
  GUID is not leftover (`name` raises).
- **Fix:** `walk_home` enters Flight first. recover() if KSP will take
  it; wait gone before Close; after Close wait recovered names off the
  list. Already in Flight + rec=0: recover-in-progress, wait gone, do
  not Close first. Still not recoverable after Flight: Close
  `reload_save=False`. Desk hangar uses live `leftover_ships` (empty
  tracking beats stale sfs SUB_ORBITAL). Never `revert_to_launch`.
  Never leftover-ksc.
- **Modules:** `hangar.py`, `desk.py`. Not hop.py.

## 2026-08-24T18-15-43Z-hop — flyinghigh-lid

- **When:** 2026-08-24 letsgrok. T-386. t7-chute-pbc hang. Bound FlyingHigh
  Forest TELEMETRY leftover + goo + geiger. f013 TELEMETRY OKTO
  on_craft=yes; Goo start unlocked=yes on_craft=yes; geiger e101
  unlocked=yes on_craft=yes; 2HOT start unlocked=yes on_craft=yes. Tree
  start,engineering101,basicRocketry,survivability.
- **Symptom:** hop_apo=50000. hold vertical until lid 50000 m, hop light,
  airborne, crash UI sit=landed rec=no met=28.22 alt=388.7 q=3598. Envelope
  hard impact 81 m/s apo=739 pitch=-85 Shores rec=no sci_run=0 bank=9.47.
  Tape MET 0.84 alt 88 thr 1; MET 8.6 alt 422 thr 0 fuel 1431 pitch 89.5
  q=3700; apex MET 16.9 thr 0 pitch 84; last MET 25 pitch=-85.
- **Cause:** Throttle was not 1 the whole burn. Lid vertical called
  `_steer_inland` at pitch 90: SAS off, AP not engaged (zenith has no
  heading), roll-0 vs zenith. `_hold_or_cut` still ran. Leftover LF at
  400 m is still the burn sit. Flip is after the cut, falling.
- **Fix:** `_hold_lid` keeps throttle 1 and SAS vertical until lid alt or
  crumbs. Do not inland-slew or apo-cut that sit. After lid, slew. Forest /
  Grasslands: same. Never revert. Do not Hangar.
- **Modules:** `hop_factory.py`. Not `physics_warp.py` this hire (XOR).

## 2026-08-24T17-59-29Z-hop — flyinghigh-lid

- **When:** 2026-08-24 letsgrok. T-384. t7-chute-pbc hang. Bound FlyingHigh
  Forest TELEMETRY leftover + goo + geiger. f013 TELEMETRY OKTO
  on_craft=yes; Goo start unlocked=yes on_craft=yes; geiger e101
  unlocked=yes on_craft=yes; 2HOT start unlocked=yes on_craft=yes. Tree
  start,engineering101,basicRocketry,survivability.
- **Symptom:** hop_apo=50000. hold vertical until lid 50000 m, hop light,
  airborne, science wait FlyingHigh, shear 28→1. Envelope hard impact
  81 m/s apo=880 pitch=-89 Shores rec=no sci_run=0 bank=9.47. Tape MET
  0.84 alt 88 thr 1; MET 9.44 alt 492 thr 0 fuel 1417 q=4502.
- **Cause:** Factory science-waited FlyingHigh at light. Wait is loft, not
  a dwell at 1 km. sit_matches treated FlyingHigh as any flying sit.
  Throttle 0 with leftover LF before lid alt; FAR sheared the vertical
  stack.
- **Fix:** Bound FlyingHigh pays only after lid alt. Do not wait, skip-latch,
  or cut until live alt is High. `_lid_burn_sit` keeps hold=1. Forest /
  Grasslands: same. Never revert. Do not Hangar.
- **Modules:** `hop_factory.py`, `science.py`. Not `physics_warp.py` this
  hire (XOR).

## 2026-08-24T17-50-46Z-hop — flyinghigh-lid

- **When:** 2026-08-24 letsgrok. T-382. t7-chute-pbc hang. Bound FlyingHigh
  Forest TELEMETRY leftover + goo + geiger. f013 TELEMETRY OKTO
  on_craft=yes; Goo start unlocked=yes on_craft=yes; geiger e101
  unlocked=yes on_craft=yes; 2HOT start unlocked=yes on_craft=yes. Tree
  start,engineering101,basicRocketry,survivability.
- **Symptom:** hop_apo=50000. science wait FlyingHigh, pitch 25 inland,
  crash UI sit=landed rec=no met=29.20 alt=339.3 q=4574. Envelope hard
  impact 89 m/s apo=782 Shores sci_run=0 bank=9.47.
- **Cause:** Factory slewed 25° inland as soon as airborne. FlyingHigh at
  ~1 km with apo hundreds of metres is not the lid. Pitch-over dumped
  the loft; t7 lithobraked.
- **Fix:** `_lid_vertical_sit` holds vertical until lid alt. Predicted
  apo is not the lid. After lid, inland slew. Forest / Grasslands: same.
  Never revert. Do not Hangar.
- **Modules:** `hop_factory.py`. Not `physics_warp.py` this hire (XOR).

## 2026-08-24T17-42-28Z-hop — silk-while-burn

- **When:** 2026-08-24 letsgrok. T-381. t7-chute-pbc hang. Bound FlyingHigh
  Forest TELEMETRY leftover + goo + geiger. f013 TELEMETRY OKTO
  on_craft=yes; Goo start unlocked=yes on_craft=yes; geiger e101
  unlocked=yes on_craft=yes; 2HOT start unlocked=yes on_craft=yes. Tree
  start,engineering101,basicRocketry,survivability.
- **Symptom:** hop_apo=50000. science wait FlyingHigh, pitch 25 inland,
  chute deployed, shear 28→1. Envelope hard impact 91 m/s apo=802
  Shores rec=no chute=cut sci_run=0 bank=9.47. Tape apex MET 18 alt 797
  thr 0 fuel 1424 vz=-10 chute=stowed; T-380 4× did not run.
- **Cause:** `_chute_arm_now` skipped Arm. Factory Deploy still sat on
  raw `chute_deploy_sit` (vz<0 ≤2 km). `deploy_chutes` Arms inside.
  800 m FlyingHigh wait with leftover LF is not the lid.
- **Fix:** `_chute_deploy_now` Deploys after lid alt or crumb burnout,
  and only on `chute_deploy_sit`. Climbing / wait-burn is not silk.
  Same inland hop Forest / Grasslands. Never revert. Do not Hangar.
- **Modules:** `hop_factory.py`. Not `physics_warp.py` this hire (XOR).

## 2026-08-24T17-26-04Z-hop — sci-unchanged-recovered

- **When:** 2026-08-24 letsgrok. T-346 unbrick. t7-chute-pbc. Bound
  FlyingHigh T-069/T-368/T-369. Last envelope shear rec=no apo=917
  sci_run=0 bank=9.47. Hang still capable.
- **Symptom:** `protocol fly` wait, `fly_ready` none, desk `pay: no`.
  Pad idle — cannot loft 50 km because the last wreck was 917 m.
- **Cause:** `waste_blocks_refly` used `_sci_run_zero` (wreck or
  recover). T-337 law is living recover + sci_run=0 only.
- **Fix:** latch is `_sci_unchanged_waste` (recoverable=true +
  sci_run=0). Wreck rec=no re-flies last `cli:`. FlyingHigh still
  needs apo ≥50 km on a living +0. Never revert. Do not Hangar.
- **Modules:** `tickets.py`. Not hop.py.

## 2026-08-24T17-26-04Z-hop — far-shear

- **When:** 2026-08-24 letsgrok. T-380. t7-chute-pbc hang. Bound FlyingHigh
  Forest TELEMETRY leftover + goo + geiger. f013 TELEMETRY OKTO
  on_craft=yes; Goo start unlocked=yes on_craft=yes; geiger e101
  unlocked=yes on_craft=yes; 2HOT start unlocked=yes on_craft=yes. Tree
  start,engineering101,basicRocketry,survivability.
- **Symptom:** hop_apo=50000. science wait FlyingHigh, pitch 25 inland,
  hold burnout, 4× rails=0, shear 28→1. Envelope apo=917 q_max=4728
  fuel 1575→1413 rec=no chute=stowed sci_run=0 bank=9.47.
- **Cause:** `want_coast` treated lofted (250 m) + throttle 0 + q≤5 kPa
  as 4×. FlyingHigh wait at ~1 km with leftover LF is not lofted
  burnout. 4.7 kPa is not actually low. FAR sheared at 4×.
- **Fix:** `high_q_sit` 1× until q ≤1 kPa. Factory `_lid_burn_sit` keeps
  leftover LF before lid alt on the burn clock (unpause is not 4×).
  Same inland hop Forest / Grasslands. Never revert. Do not Hangar.
- **Modules:** `physics_warp.py`, `hop_factory.py`. Not `hop.py`.

## 2026-08-24T16-02-25Z-hop — sci-unchanged-recovered

- **When:** 2026-08-24 letsgrok. T-346. t7-chute-pbc. Bound FlyingHigh
  T-069 Forest TELEMETRY + T-368 goo + T-369 geiger. Last envelope
  catastrophic apo=2574 Shores rec=no sci_run=0 bank=9.47.
- **Symptom:** `protocol fly` said yes. Parent would light last `cli:`
  on a FlyingHigh bind this 2.5 km hop cannot pay.
- **Cause:** Waste gate required living recover, so wreck +0 skipped
  it. `_sit_biome_match` treated FlyingHigh as any `flying` sit
  (T-369 empty biome matched Shores at 2.5 km).
- **Fix:** FlyingHigh vs envelope uses apo ≥50 km (not any flying sit).
  Waste latch stayed living recover. Wreck rec=no over-latched next sit
  (T-346 unbrick). Never revert.
- **Modules:** `tickets.py`, `protocol.py`, `desk.py`. Not hop.py.

## 2026-08-24T15-44-16Z-hop — flyinghigh-lid

- **When:** 2026-08-24 letsgrok. T-374. t7-chute-pbc hang. Bound FlyingHigh
  Forest TELEMETRY leftover + goo + geiger. f013 TELEMETRY OKTO
  on_craft=yes; Goo start unlocked=yes on_craft=yes; geiger e101
  unlocked=yes on_craft=yes. Tree start,engineering101,basicRocketry,
  survivability.
- **Symptom:** hop_apo=50000. science wait FlyingHigh, hold burnout, chute
  armed, shear 28→10, recover Shores apo 2357 rec=yes sci_run=0. Tape
  MET 15 alt 1.2 km thr 0 fuel 1317 vz=+148 chute=stowed; apex 2.3 km
  vz<0 then silk deployed pad 0.41 km.
- **Cause:** Factory Armed on `chute_arm_sit` during FlyingHigh wait-burn.
  Descent at 2 km with a full tank is not the lid. Silk killed the loft.
  Throttle 0 with leftover LF is not burnout.
- **Fix:** `_chute_arm_now` Arms after lid alt or crumb burnout, and only
  on `chute_arm_sit`. Climbing / wait-burn is not silk. Same inland hop
  Forest / Grasslands. Never revert.
- **Modules:** `hop_factory.py`. Not `physics_warp.py` this hire (XOR).

## 2026-08-24T15-24-17Z-hop — flyinghigh-lid

- **When:** 2026-08-24 letsgrok. T-373. t7-chute-pbc hang. Bound FlyingHigh
  Forest TELEMETRY leftover + goo + geiger. f013 TELEMETRY OKTO
  on_craft=yes; Goo start unlocked=yes on_craft=yes; geiger e101
  unlocked=yes on_craft=yes. Tree start,engineering101,basicRocketry,
  survivability.
- **Symptom:** hop_apo=50000. 15-05-30Z predicted apo 163 km OffPlan. Next
  hop 15-24-17Z crash UI MET 59 alt 2279 q=4572 rec=no, fuel leftover,
  apo max 2.8 km. `hop hold inland through burnout` then 4× into dirt.
- **Cause:** FlyingHigh hop_apo latched on predicted apo and on first
  `chute_arm_sit` descent. Thick-air apo is not 50 km alt. Descent at
  2.3 km with fuel still needed the lid. Warp ran after Arm, so the
  first `chute_arm_sit` tick was still 4×.
- **Fix:** `_lid_alt_reached` cuts on live altitude. Predicted apo is
  not the latch. `chute_arm_sit` cuts only after the lid or crumbs.
  `apply_sit_warp` before Arm so that tick is already 1×. Toggle after
  50 km alt, then cut, silk, recover. Never revert.
- **Modules:** `hop_factory.py`. Not `physics_warp.py` this hire (XOR).

## 2026-08-24T15-05-30Z-hop — flyinghigh-lid

- **When:** 2026-08-24 letsgrok. T-371. t7-chute-pbc hang. Bound FlyingHigh
  Forest TELEMETRY leftover + goo + geiger. f013 TELEMETRY OKTO
  on_craft=yes; Goo start unlocked=yes on_craft=yes; geiger e101
  unlocked=yes on_craft=yes. Tree start,engineering101,basicRocketry,
  survivability.
- **Symptom:** hop_apo=50000, `science wait FlyingHigh`, then OFFPLAN
  apo 163170 > 140000 Space. Tape MET 97 apo 46 km thr 1 fuel 349;
  MET 126 alt 62 km apo 163 km fuel crumbs thr 0. No Toggle.
- **Cause:** Factory OffPlan Space ran before `_hold_or_cut`. hop_apo
  50 km never latched; leftover fuel kept throttle 1 through the lid.
  62 km alt is already FlyingHigh — Space abort stole the Toggle.
- **Fix:** Cut hop_apo first. FlyingHigh after that cut is the inland
  hop (Toggle, chute, land leftover), not Space OffPlan. Crumb fuel
  is not a reason to keep throttle 1. Never revert.
- **Modules:** `hop_factory.py`. Not `physics_warp.py` this hire (XOR).

## 2026-08-24T15-10-47Z-hop — flyinghigh-lid

- **When:** 2026-08-24 letsgrok. T-372. t7-chute-pbc hang. Bound FlyingHigh
  leftover. f013 TELEMETRY OKTO on_craft=yes. Tree
  start,engineering101,basicRocketry,survivability.
- **Symptom:** 15-10-47Z `hop coast physics 4x`, `chute armed`, `chute
  deployed`, then `hop physics 1x`, shear 28→18 ABORT. 13-31-03Z t7
  no-chute 88.8 km shear=no. Tape thin: last state 8.7 km chute=armed
  q=46 kPa vz=+371 parts=28.
- **Cause:** `want_coast` kept 4× on lofted descent (`chute_arm_sit`)
  and flipped 4× again on silk. RealChute inflated at 4×. 1× was after
  canopy, not before Arm.
- **Fix:** `apply_sit_warp` 1× when `chute_arm_sit` or
  `chute_deploy_sit` or silk. Climbing armed may still 4×. Factory
  should warp before Arm so the first descent tick is already 1×.
  Never revert.
- **Modules:** `physics_warp.py`. Not `hop_factory.py` this hire (XOR).

## 2026-08-24T13-49-58Z-hop — flyinghigh-lid

- **When:** 2026-08-24 letsgrok. T-357. proc-stiff-pbc hang. Bound FlyingHigh
  Forest TELEMETRY leftover. f013 TELEMETRY OKTO on_craft=yes. Tree
  start,engineering101,basicRocketry,survivability.
- **Symptom:** hop_apo=50000, `science wait FlyingHigh`, crash UI flying
  rec=no met=277 alt=3025 q=20 kPa chute=stowed. Forest apo 32040 rec=no
  impact 197 m/s. 18 km hops chute fine. Tape throttle 1 fuel 0.292
  warp=Nonex through descent.
- **Cause:** Waiting FlyingHigh is a sit flag, not a dwell. Factory Arm
  sat behind `not burning_now`. hop_apo 50 km never reached, crumb fuel
  kept throttle 1, `_burning` stayed true, `chute_arm_sit` never ran.
  waiting_lid pass skipped recover only — warp/chute already keyed off
  burning.
- **Fix:** Descent after loft (`chute_arm_sit`) cuts. Arm on
  `chute_arm_sit`, Deploy on `chute_deploy_sit`, independent of
  waiting_lid / burning crumbs. Same inland hop as cannot-pay: loft,
  coast, chute, land leftover. Never revert.
- **Modules:** `hop_factory.py`. Not `physics_warp.py` this hire (XOR).

## 2026-08-24T12-45-00Z-hop — hold-ground-card

- **When:** 2026-08-24 letsgrok. T-348. proc-stiff-pbc hang. Bound Forest
  land leftover T-077 2HOT seq0 (0.497) and splash T-313 seq1. f013
  2HOT start unlocked=yes on_craft=yes; TELEMETRY OKTO on_craft=yes. Tree
  start,engineering101,basicRocketry,survivability.
- **Symptom:** Forest land rec=yes chute=armed sci=run=1 rem=0 bank +0.
  leftover thermo 0.497 unstarted. Log: airborne TELEMETRY start/dwell,
  hop down, recover sit=landed. No science start temperatureScan after
  down.
- **Cause:** Factory recovered on airborne TELEMETRY rem=0 at first
  recoverable. `hop_landed_science_ids` union was not sit-matched to
  live landed Forest, so T-077 never Toggled. T-347 hold is the Toggle
  pulse; T-342 rem=0 after dwell still recovers.
- **Fix:** `hop_landed_science_ids` sit_matches live sit (SrfLanded@Forest
  on landed, splash on splash, empty while flying). Start that leftover
  before recover. Hold unpaid leftover while flying; rem=0 after dwell
  recovers. Forest / Grasslands same helper. Never revert.
- **Modules:** `hop.py`, `hop_factory.py`.

## 2026-08-24T12-16-38Z-hop — hold-ground-card

- **When:** 2026-08-24 letsgrok. T-347. proc-stiff-pbc hang. Bound Forest
  land T-077 2HOT (`temperatureScan` 83 s file) + T-287 TELEMETRY. f013
  2HOT start unlocked=yes on_craft=yes; TELEMETRY OKTO on_craft=yes. Tree
  start,engineering101,basicRocketry,survivability.
- **Symptom:** Forest land apo ~25 km rec=yes chute=cut sci=run=0 rem=0
  bank 8.87→8.87 (+0). leftover thermo 0.54→0.514. Log: science start
  temperatureScan + TELEMETRY, science dwell, hop down, recover same
  pulse. No wait-science line.
- **Cause:** Factory recovered the Toggle pulse. Leftover file rem=0
  while running is idle PAW, not transmitted. `ground_card_done` said
  done. T-342 rem=0 after dwell still recovers next pulse.
- **Fix:** Landed start holds that pulse (wreck still recovers). Then
  `_hold_ground_card`: rem>0 recording, rem=0 after dwell recover. Same
  inland Forest / Grasslands. Never revert.
- **Modules:** `hop_factory.py`. Not `science.py` this hire (XOR).

## 2026-08-24T11-25-56Z-hop — forest-splashed-thermo

- **When:** 2026-08-24 letsgrok. T-344. Same hop as hold-ground-card. Bound
  Forest splash T-313 2HOT (`temperatureScan` 138 s file). f013 2HOT start
  unlocked=yes on_craft=yes. Tree
  start,engineering101,basicRocketry,survivability.
- **Symptom:** Forest splash apo 29468 rec=yes chute=cut sci=run=1 rem=0
  bank +0.10 TELEMETRY only. Log: `science skip temperatureScan on
  sensorThermometer (not in card)`. T-313 never Toggled.
- **Cause:** `paying_eids` dropped idle rem=0 unless the eid was in
  `_DURATION_EIDS`. 2HOT is file duration, not a sample; unstarted rem=0
  never entered the paying card, so `_start_paying` passed TELEMETRY only.
- **Fix:** `temperatureScan` is duration. Sample rem=0 (goo) still skips.
  Sit/biome match still required. TELEMETRY with no rem PAW still
  recording is not done; 2HOT exposes remaining. Forest / Grasslands same
  helper. Never revert.
- **Modules:** `science.py`. Not `hop_factory.py`.

## 2026-08-24T08-44-03Z-hop — sci-unchanged-recovered

- **When:** 2026-08-24 letsgrok. T-341. Living recover sci_run=0 is not clean-0
  re-fly. 08-44 Shores land 7 m/s rec=yes +0 vs Forest leftover; 10-57 Forest
  splash rec=yes sci_run=0 then rebound T-313/T-288.
- **Symptom:** `protocol fly` said yes after leftover n=0. Parent lit last
  `cli:` on the same +0 bind. Pad grind.
- **Cause:** Gate treated recovered leftover-clean as clean 0. Envelope
  sit/biome was not checked against bound tickets. Hang/bind unchanged.
- **Fix:** `waste_blocks_refly` — living recover + sci_run=0 waits until a
  bound sit/biome matches the envelope, or hang/bind changed. attach_run
  latches `payload.waste`. Uncrewed `needs_learn` stays false. Never revert.
- **Modules:** `protocol.py`, `tickets.py`, `ops.py`. Not hop_factory.

## 2026-08-24T11-25-56Z-hop — hold-ground-card

- **When:** 2026-08-24 letsgrok. T-342. proc-stiff-pbc hang. Bound Forest
  splash T-288 TELEMETRY + T-313 thermo. f013 2HOT start unlocked=yes
  on_craft=yes; TELEMETRY OKTO on_craft=yes. Tree
  start,engineering101,basicRocketry,survivability.
- **Symptom:** Forest splash apo 29468 rec=yes chute=cut sci=run=1 rem=0
  bank 8.77→8.87 (+0.10). TELEMETRY start/dwell, hop down, then silence
  until Os uplink abort. hold_card true → factory `pass`, never recover.
- **Cause:** `ground_card_done` treated duration rem=0 while running as
  still recording. Kerbalism file rem=0 is transmitted. Timeout does not
  fire while down, so the pulse waited forever.
- **Fix:** rem=0 is done (sample spent or file transmitted), landed or
  splashed. Factory recovers when leftover rem is gone. Same inland hop
  Forest / Grasslands. Never revert.
- **Modules:** `science.py`. Not `hop_factory.py` this hire (XOR). Helper
  `_hold_ground_card` already follows `ground_card_done`.

## 2026-08-24T11-11-37Z-hop — chute-deploy-sit

- **When:** 2026-08-24 letsgrok. T-340. proc-stiff-pbc hang. Bound Forest
  leftover. f013 2HOT start unlocked=yes on_craft=yes; TELEMETRY OKTO
  on_craft=yes. Tree start,engineering101,basicRocketry,survivability.
- **Symptom:** crash UI sit=flying rec=no met=264 alt=2918 q=5748
  chute=stowed. Forest apo 34222. Impact 111 m/s. T-338 Arm waited for
  ≤2 km after burnout.
- **Cause:** Factory Arm+Deploy both sat on `chute_deploy_sit` (vz<0
  **and** ≤2 km). Lofted descent at 2.9 km never Armed. T-338 whoosh was
  first-airborne Arm, not this sit.
- **Fix:** Arm on Wernher `chute_arm_sit` (lofted descent). Deploy still
  `chute_deploy_sit` ≤2 km or semi. Do not Arm first airborne. 1× high
  q. Same inland Forest / Grasslands. Never revert.
- **Modules:** `hop_factory.py`. Not `physics_warp.py` this hire (XOR).

## 2026-08-24T11-11-37Z-hop — chute-deploy-sit

- **When:** 2026-08-24 letsgrok. T-339. proc-stiff-pbc hang. Bound Forest
  leftover. f013 2HOT start unlocked=yes on_craft=yes; TELEMETRY OKTO
  on_craft=yes. Tree start,engineering101,basicRocketry,survivability.
- **Symptom:** crash UI sit=flying rec=no met=264 alt=2918 q=5748
  chute=stowed. Forest apo 34222. No Arm after T-338. Impact 111 m/s.
- **Cause:** `chute_deploy_sit` was vz<0 **and** ≤2 km. Factory Arm+Deploy
  both sat on that gate, so silk never armed before FAR ate the stack
  at ~3 km. T-338 whoosh was first-airborne Arm, not this sit.
- **Fix:** `chute_arm_sit` = lofted descent (vz<0 / pitch down). Not
  light. Not only below 2 km. `chute_deploy_sit` still ≤2 km or semi.
  1× high q / canopy. 4× only lofted burnout AND q≤5 kPa. Lars must
  Arm on `chute_arm_sit`, Deploy on `chute_deploy_sit`. Never revert.
- **Modules:** `physics_warp.py`. Not `hop_factory.py` this hire (XOR).

## 2026-08-24T10-57-33Z-hop — chute-arm-ascent

- **When:** 2026-08-24 letsgrok. T-338. proc-stiff-pbc hang (do not Hangar
  proc-4t). Bound Forest leftover. f013 2HOT start unlocked=yes
  on_craft=yes; TELEMETRY OKTO on_craft=yes. Tree
  start,engineering101,basicRocketry,survivability.
- **Symptom:** Os heard RealChute zhiiiissh at light. Tape: hop light,
  hop airborne, immediately `chute armed` / `hop chute armed`, then
  slew/pitch. Recovered sit=splashed Forest apo=35841 impact=5 m/s
  rec=yes chute=cut sci=run=0. parts 36 shear=no.
- **Cause:** Factory pulse armed Mk16 on first `left_pad` tick. RealChute
  Arm is a PAW whoosh, not extra-stage. Ascent/loft/burn still packed.
- **Fix:** Arm and Deploy on Wernher `chute_deploy_sit` (vz<0 below 2 km)
  after real burnout. Do not Arm while burning or lofting. Same inland
  hop Forest / Grasslands. Never extra-stage. Never revert.
- **Modules:** `hop_factory.py`. Not `physics_warp.py` this hire (XOR).

## 2026-08-24T10-31-47Z-hop — control-blocks

- **When:** 2026-08-24 letsgrok. T-335. proc-stiff-pbc hang (do not Hangar
  proc-4t, T-332 FAR shear). Bound T-077 Forest SrfLanded thermo leftover
  + T-287 land TELEMETRY. f013 2HOT start unlocked=yes on_craft=yes.
  Tree start,engineering101,basicRocketry,survivability.
- **Symptom:** Factory pulse owned skip as a second flight:
  `_loft_after_skip` / `_coast_after_skip`, extra Hangar unpause, wall
  timeout while MET was 8 / 129. Paying loft and cannot-pay loft
  diverged. 10-31-47Z 4× at burnout q≈29.5 kPa sheared.
- **Cause:** Warp was a new hop after skip, not a clock on the sit.
  Timeout was wall seconds. Skip unpause was extra, not `apply_sit_warp`.
- **Fix:** Factory inland calls Wernher sits: `apply_sit_warp` (4× only
  lofted burnout AND q≤5 kPa; unpause is not 1×), `airborne_cannot_pay`
  (skip is a flag, not a dwell), `chute_deploy_sit` (vz<0 below 2 km),
  `timeout_hit` (MET / down; wall only if MET unknown), `leftover_call`
  (recover if recoverable else ksc leftover). Same inland hop whether
  airborne science pays or not. Never revert. Never WarpTo. Never rails.
  Forest / Grasslands same.
- **Modules:** `hop_factory.py`. Not `physics_warp.py` this hire (XOR).

## 2026-08-24T10-31-47Z-hop — control-blocks


- **When:** 2026-08-24 letsgrok. T-334. proc-4t-pbc. Bound T-077 Forest
  SrfLanded thermo leftover + T-287 land TELEMETRY. f013 2HOT start
  unlocked=yes on_craft=yes. Tree start,engineering101,basicRocketry,
  survivability. Do not Hangar 4t (T-332).
- **Symptom:** Warp treated as a new flight. Stamp helpers
  `_loft_after_skip` / `_coast_after_skip` in hop_factory. T-328 skip
  latch wall 612 s MET~8. T-329/T-330 unpause killed 4×; chute never
  vz<0 below 2 km; wall 785 s still flying. 10-31-47Z first 4× coast
  at burnout q≈29.5 kPa FAR-sheared 40→8.
- **Cause:** 1× profile already worked. 4× then overfit the skip stamp
  instead of sits. Timeout was wall seconds. Hangar `run_physics` is
  unpause+1×. High q was not a 1× sit.
- **Fix:** `physics_warp` sit blocks Lars calls: `want_coast` /
  `apply_sit_warp` (4× only lofted burnout AND q≤5 kPa; unpause is not
  1×), `airborne_cannot_pay` (skip is a flag, not a dwell),
  `chute_deploy_sit` (vz<0 below 2 km), `timeout_hit` (MET / down),
  `leftover_call` (recover if recoverable else ksc leftover). Never
  revert. Never WarpTo. Never rails. Forest / Grasslands same.
- **Modules:** `physics_warp.py`. Not `hop_factory.py` this hire (XOR).

## 2026-08-24T10-00-57Z-hop — science-skip-timeout

- **When:** 2026-08-24 letsgrok `python main.py hop`
  (`2026-08-24T10-00-57Z-hop`). proc-4t-pbc. Bound T-077 Forest
  SrfLanded thermo leftover + T-287 land TELEMETRY. hop_apo 18 km.
  f013 2HOT start unlocked=yes on_craft=yes; TELEMETRY OKTO host
  on_craft=yes. Tree start,engineering101,basicRocketry,survivability.
  Do not Hangar.
- **Symptom:** T-329 loft-after-skip. Skip, unpause, hold, coast 4×,
  then 1×, 4×. Wall timeout 785 s still sit=flying rec=no Forest
  apo 49 km alt 42 km vz +369 chute=armed never down. MET 129.
  Land leftover never started. Abort ksc leftover.
- **Cause:** Skip unpause was Hangar `run_physics` (clock + 1×).
  loft_after_skip also used wreck MET-still, so a living 47 km
  coast did not keep the clock or 4×. Mk16 deploy is still vz<0
  below 2 km — Forest/Grasslands never reached it.
- **Fix:** `_coast_after_skip`: airborne cannot-pay unpauses the
  clock without killing warp, then `apply_coast` after burnout.
  Not a wreck freeze. Cut, coast, chute ≤2 km, start landed ids,
  then recover.
- **Modules:** `hop_factory.py`, `physics_warp.py`.

## 2026-08-24T09-32-32Z-hop — science-skip-timeout

- **When:** 2026-08-24 letsgrok `python main.py hop`
  (`2026-08-24T09-32-32Z-hop`). proc-4t-pbc. Bound T-077 Forest
  SrfLanded thermo leftover + T-287 land TELEMETRY. hop_apo 18 km.
  f013 2HOT start unlocked=yes on_craft=yes; TELEMETRY OKTO host
  on_craft=yes. Tree start,engineering101,basicRocketry,survivability.
  Do not Hangar.
- **Symptom:** T-328 latched skip. Then wall timeout 612 s still
  sit=flying rec=no. Tape MET 0–8.3 apo=534 Shores. Never hop-down,
  never coast, never chute. Land leftover never started. Abort
  ksc leftover.
- **Cause:** Skip latch cleared FlyingHigh wait, so the pulse tried
  flying hop-down / `_pool` instead of keeping the inland loft.
  MET stayed ~8 s while the wall ran 612 s. Land leftover starts
  after lofted+down, which never came.
- **Fix:** `_loft_after_skip`: airborne cannot-pay still loft.
  Unpause on skip. Do not hop-down or `_pool` until land. Cut at
  hop_apo, coast, chute, start landed ids, then recover. Timeout
  still recovers if recoverable else ksc leftover.
- **Modules:** `hop_factory.py`.

## 2026-08-24T09-07-59Z-hop — science-skip-timeout

- **When:** 2026-08-24 letsgrok `python main.py hop`
  (`2026-08-24T09-07-59Z-hop`). proc-4t-pbc. Bound T-077 Forest
  SrfLanded thermo leftover + T-287 land TELEMETRY. hop_apo 18 km.
  f013 2HOT start unlocked=yes on_craft=yes; TELEMETRY OKTO host
  on_craft=yes. T-069 FlyingHigh unbound. Do not Hangar.
- **Symptom:** lofted, `science skip (situation cannot pay)`, wall
  timeout 695 s, ABORT timeout. Tape sit=flying apo=525 biome=Shores
  rec=no sci=run=0. Flying leftover. Landed ids never started.
- **Cause:** Factory logged airborne cannot-pay but left
  `science_attempted` false, so every pulse retried the flying card.
  Timeout raised without recover of a flying vessel. Bound sit is
  landed; skip is not a 50 km wait.
- **Fix:** Latch skip, keep lofting. After lofted+down start landed
  ids. FlyingHigh wait only before a Toggle sit, not after skip.
  Budget while still airborne recovers if recoverable, else
  `ksc leftover`.
- **Modules:** `hop_factory.py`.

## 2026-08-24 — link-lost

- **When:** Os 2026-08-24: hop honors `can_communicate`. T-326.
  PBC unmanned. f013 2HOT start unlocked=yes on_craft=yes. Do not
  Hangar. Disk only.
- **Symptom:** kRPC 0.6 `PilotAddon.HasControlConnection` is true
  without RemoteTech. `requireSignalForControl` does not stop
  `vessel.control` writes. Unmanned probe keeps throttle/SAS/stage
  with no radio. Throttle 1 after a fake LOS is a lithobrake.
- **Cause:** House hop never asked the radio. Control is not
  `can_communicate`.
- **Fix:** `_command_ok` / `_zero_stick_if_deaf`. Pad-light while
  deaf aborts `no signal (pad)`. After pad, zero stick; coast,
  science Toggle, and recover stay legal. Fail open unless we know
  deaf (`snap.link` False, or comms False). Crewed is always ok.
- **Modules:** `hop.py`, `hop_factory.py`.

## 2026-08-23T22-33-35Z-hop — FlyingHigh lid abort on a hop that never reached 50 km

- **When:** 2026-08-23 letsgrok `python main.py hop`
  (`2026-08-23T22-33-35Z-hop`). Long-pbc. Bound T-069 FlyingHigh
  Forest TELEMETRY. f013 TELEMETRY on_craft=yes; thermometer start
  unlocked on_craft=yes. Do not Hangar. Live hop pid already loaded —
  next hop takes this.
- **Symptom:** hop_apo 50000, apo_max 1611 m, alt_max 1549 m, Shores
  0.58 km. Apex throttle 1 fuel 1400 chute deployed. Last sit=landed
  throttle 1 fuel 0.3. Exit 2 ABORT no science (FlyingHigh lid). sci +0.
  Recoverable yes. T-077 Forest land still on the card.
- **Cause:** Factory treated pad loft (250 m) as a missed 50 km lid and
  aborted before land leftover. `_hold_or_cut` kept throttle 1 to
  hop_apo on the ground.
- **Fix:** `_reached_high_lid` / `_abort_high_lid` name the Toggle sit.
  A hop that never reached 50 km recovers leftover; cut throttle once
  lofted and down or under silk. Do not dump the tank on the pad.
- **Modules:** `hop_factory.py`, `hop.py` (`_abort_high_lid`).

## 2026-08-23T20-47-10Z-hop — pad boost dwelt Shores goo then hop-down

- **When:** 2026-08-23 letsgrok `python main.py hop`
  (`2026-08-23T20-47-10Z-hop`). Stiff-pbc. f013 2HOT start
  unlocked=yes on_craft=yes. Do not Hangar. Live hop pid already
  loaded — next hop takes this.
- **Symptom:** Light, airborne T+1, slew 270, chute armed. Flying card
  skip thermo/TELEMETRY (not in card), start mysteryGoo, dwell, hop-down.
  apo_max 119 m alt_max 104 m biome Shores only. Throttle 0 MET 1.88
  fuel 1053. Exit 2 ABORT. sci +0.
- **Cause:** `_science_ready` is sit=flying, not lofted. Factory started
  the flying card at pad alt, then `_pad_boosting` dropped on
  sit=landed so a bounce hopped down and dwelt capped Shores goo.
- **Fix:** Flying card after loft. `_pad_boosting` stays true while
  burning and not lofted (bounce landed with fuel is still pad boost).
  Relight. Do not hop-down or dwell Shores on a 104 m hop.
- **Modules:** `hop_factory.py`, `hop.py` (`_pad_boosting`).

## T-312 — hop helpers name sit, not a stamp

- **When:** Os 2026-08-23: hop.py hub reasonably good. T-312. f013 2HOT
  start unlocked=yes on_craft=yes. Do not Hangar. Disk only.
- **Symptom:** hop.py module docstring and helper docs were a scrapbook
  of stamps. Pad-boost recover skip was an inline boolean in both pulses.
- **Cause:** A stamp was the law. Forest today / Grasslands tomorrow
  needs sit-named helpers, not a ticket if.
- **Fix:** Helpers name lofted / burning / landed / splashed.
  `_pad_boosting` is lit, not lofted, still burning — not recover, not
  coast. Docstrings are the rule. Tests keep the stamps. Factory inland
  stays hop_factory; parked water/splash stay hop.py.
- **Modules:** `hop.py`.

## 2026-08-23T18-34-22Z-hop — false burnout coast 3× then hop-down

- **When:** 2026-08-23 letsgrok `python main.py hop`
  (`2026-08-23T18-34-22Z-hop`). First hop after T-308 coast 3×.
  Stiff-pbc. f013 2HOT start unlocked=yes on_craft=yes. Do not Hangar.
  Live hop pid already loaded — next hop takes this.
- **Symptom:** MET 1.8 throttle 0 fuel 1054 alt 101 apo 114. `hop hold
  inland through burnout` then hop-down on the pad (downrange 0.45 km).
  chute stowed. sci +0. Exit 0.
- **Cause:** `_burning` is throttle>0.05. A 0-tick after light looks like
  cutoff; `_want_coast_phys` then 3×; recoverable over the pad hops down.
- **Fix:** Real burnout is fuel gone, or throttle 0 after loft well above
  pad. 1× while burning / pad boost. Do not hop-down a full tank at 101 m.
  Rails 0. Uplink `phys-warp` still works.
- **Modules:** `hop.py`.

## 2026-08-23T18-10-57Z-hop — splash leftover skipped SrfLanded seq1

- **When:** 2026-08-23 letsgrok `python main.py hop`
  (`2026-08-23T18-10-57Z-hop`). Stiff-pbc living recover Forest
  17.7 km sit=splashed (tape sit=landed). f013 2HOT start
  unlocked=yes on_craft=yes. Do not Hangar. Live hop pid already
  loaded — next hop takes this.
- **Symptom:** Goo airborne, recover HD, sci 8.7721 +0. Bound T-288
  Forest SrfSplashed TELEMETRY leftover 0.16 never started. T-077
  SrfLanded thermo and T-287 SrfLanded TELEMETRY also unstarted.
- **Cause:** `hop_landed_science_ids()` only listed SrfLanded.
  `bound_science_need` first-seq pinned TELEMETRY to T-287
  SrfLanded so splash cannot-pay. Airborne goo set `started` and
  skipped the ground start.
- **Fix:** Union land+splash leftover ids. Match live sit to the
  bound ticket that can pay (splash → T-288, land → T-287), not
  first seq. Down still starts that leftover after airborne goo.
- **Modules:** `hop.py`.

## 2026-08-23T18-19-00Z-hop — hop coast physics 2–4× after burnout

- **When:** Os 2026-08-23: factory hops sit ~300 s at 1× after
  `hop hold inland through burnout` until chute. T-308. f013 2HOT
  start unlocked=yes on_craft=yes. Do not Hangar. Live hop pid
  already loaded — next hop takes this.
- **Symptom:** Pad physics-warps 2–4× on landed/prelaunch. Hop
  coast never set `physics_warp_factor`. `no_warp` dropped once
  and did not persist. No uplink to raise physics warp.
- **Cause:** Coast loop left rails/physics at hangar 1×. Desk had
  `skip_warp` but hop did not drive a coast factor from it.
- **Fix:** After burnout, while flying and waiting chute, factory
  3× physics (`physics_warp_factor` 2), rails 0, never WarpTo.
  1× while burning, on chute deploy, recover, shear/wreck/hold.
  Uplink `phys-warp 2|3|4` / `warp 2|3|4` persists on `uplink.desk`
  (like skip_warp). `no_warp` keeps 1× until a new phys-warp.
  Modules: `hop.py`, `uplink.py`, `emergencies.py`.

## 2026-08-23T17-23-34Z-hop — recover rem=0 did not bank leftover

- **When:** 2026-08-23 letsgrok `python main.py hop`
  (`2026-08-23T17-23-34Z-hop`; 17-32-20Z same). Stiff-pbc living
  recover 5 m/s Forest. f013 2HOT start unlocked=yes on_craft=yes.
  Do not Hangar.
- **Symptom:** `sci_run=1 rem=0` entire hop, `sci_bank` 8.0492 +0.
  leftover `temperatureScan@EarthSrfLandedForest` 0.742→0.690 not in
  R&D. Bound was SrfLanded (T-077); hop Toggled FlyingLow T+1.
- **Cause:** fly `science_ids` union started thermo/TELEMETRY/goo
  airborne. Forest FlyingLow remaining=0 cannot pay. Recover ran
  while the slot was still recording, so leftover rem never flushed
  to the HD.
- **Fix:** Do not start a slot whose sit/biome cannot pay (sample
  rem=0, or bound SrfLanded/FlyingLow@Grasslands vs live Forest).
  Start SrfLanded after touchdown. Stop running experiments before
  `vessel.recover()`.
- **Modules:** `science.py`, `hop.py`, `pad.py`.

## 2026-08-23T16-47-21Z-hop — T-305 envelope burn is cutoff dump

- **When:** 2026-08-23 letsgrok `python main.py hop`
  (`2026-08-23T16-47-21Z-hop`). Stiff-pbc living recover 5 m/s Forest.
  f013 2HOT start unlocked=yes on_craft=yes. Do not Hangar.
- **Symptom:** envelope `burn: heading=15 pitch=16` MET 74 n=5. Powered
  hold heading **297** pitch **65** (MET 25–58, hz 20).
- **Cause:** `_burnout_row` took min pitch through first cutoff
  inclusive. Cutoff dump is throttle=0 (no torque). 09-28-59Z 209/3 was
  still throttled.
- **Fix:** burn window ends at last powered sample; envelope min-pitch
  among throttled rows. No hop.py.
- **Modules:** `tape.py`.

## 2026-08-23T16-47-21Z-hop — T-284 thin tape 0.07 Hz

- **When:** 2026-08-23 letsgrok `python main.py hop`
  (`2026-08-23T16-47-21Z-hop`). Stiff-pbc living recover 5 m/s Forest.
  f013 2HOT start unlocked=yes on_craft=yes. Do not Hangar.
- **Symptom:** 26 state rows / 380 s MET, `hz_median` 0.07. Requested
  `hz` 5–20. Last state `sit=flying recoverable=no` while last-flight
  `recovered sit=landed recoverable=yes`. Descent gaps ~14 s wall.
- **Cause:** Slow `parts.all` + `field_list` sci/broken walk (~13 s)
  re-armed after every cheap pulse, and/or a 10 s grim tick inside
  `Telem.read` made every pulse miss the shot interval. Fast path still
  called `parts_count` (`parts.all`) every row. Close synthesized
  `kind=landing` with `sit=flying`.
- **Fix:** Cache parts/root on the fast path; skip sci/broken after an
  expensive walk except landed/splashed; grim ticks skip after a slow
  grab; envelope silk recover as `sit=landed rec=yes`. No hop.py.
- **Modules:** `telem.py`, `screenshot.py`, `tape.py`, `flightlog.py`.

## 2026-08-23T16-47-21Z-hop — T-164 slam 65 held pad 297

- **When:** 2026-08-23 letsgrok `python main.py hop`
  (`2026-08-23T16-47-21Z-hop`; T-164 fingerprint
  `2026-08-23T10-47-12Z-hop`). Stiff-pbc living recover 5 m/s Forest
  16.8 km. f013 2HOT start unlocked=yes on_craft=yes. Do not Hangar.
- **Symptom:** exit 0. Powered hold heading **297** pitch **65** (MET
  25–58). Envelope burn heading 15 pitch 16 horiz 167 MET 74 is the
  first fuel=0 sample, not the hold. 10-47-12Z same 297/65 then
  Shores +0. Ground track west; nose never 270.
- **Cause:** command 65/270 at left_pad engages from zenith; pitch
  over is pad 299, then FAR fins lock 297 (27° — 45° gate skips
  rewrite). Re-point at cutoff pitch dump rewrites and yaws (T-161).
- **Fix:** yaw 10° off zenith heading 270 at low q, then the 25°
  path. Re-point only while burning (or pitch < 0). Do not rewrite
  fuel=0. Modules: `hop.py`.

## 2026-08-23T10-47-12Z-hop — T-166 ship radio had no where

- **When:** 2026-08-23 letsgrok hops (`2026-08-23T10-47-12Z-hop` and
  prior Cape hangs). Stiff-pbc. f013 2HOT start unlocked=yes
  on_craft=yes. Do not Hangar.
- **Symptom:** tape `biomes=[Shores]` after the fact. `ship.md` was
  heading/wreck/ec/alt only. Walt/Hank could not tell Forest vs
  Shores live. Envelope one biome token, no lat/lon/downrange.
- **Cause:** Telem streamed heading/pitch/horiz, not
  `flight.latitude` / `longitude`. Radio omitted biome even though
  jsonl already had it.
- **Fix:** stream lat/lon on the no-frame Flight hold; jsonl
  lat/lon/downrange km (haversine from Cape pad); `ship.md` extra
  keys; tape `where:` line. No hop.py.
- **Modules:** `telem.py`, `flightlog.py`, `tape.py`, `sites.py`.

## 2026-08-23T10-33-44Z-hop — T-163 re-point skipped target_direction

- **When:** 2026-08-23 letsgrok `python main.py hop`
  (`2026-08-23T10-33-44Z-hop`). Stiff-pbc living recover 5 m/s. f013
  2HOT start unlocked=yes on_craft=yes. Do not Hangar.
- **Symptom:** exit 0. burn heading 353 pitch 26 horiz 83 MET 51.
  Apex 301/60 horiz 68. MET139 heading 56 pitch −19. Last 299/89
  horiz 0 biome Shores. sci 5.6718 +0. Jeb 122 under horizon; no
  65/270 re-point.
- **Cause:** T-162 re-point waited for pitch < 0 or heading error
  > 90°. 353 is 83° from 270 (still west of north). `_point_surface`
  returned after `set_direction_and_up` and never wrote
  `target_direction`. Forest is 270, not 090.
- **Fix:** re-point if pitch drops >20° below 65 or heading error
  > 45° (297/66 still skipped). Write `target_direction` then
  `set_direction_and_up`. Do not re-engage. Modules: `hop.py`.

## 2026-08-23T10-17-18Z-hop — T-162 inland latch flipped east 38/−10

- **When:** 2026-08-23 letsgrok `python main.py hop`
  (`2026-08-23T10-17-18Z-hop`). Stiff-pbc living recover 5 m/s. f013
  2HOT start unlocked=yes on_craft=yes. Do not Hangar.
- **Symptom:** exit 0. burn heading 38 pitch −10 horiz 102 MET 47.
  Apex 298/63 horiz 73. MET104 84/−45 horiz 13 at 7 km. Last 298/89
  horiz 0 biome Shores. sci 5.6718 +0.
- **Cause:** T-161 skipped `set_direction_and_up` whenever AP
  `engaged`. The 65/270 command latched; the stack flew through the
  horizon to the east. Forest is 270, not 090.
- **Fix:** latch the commanded vector, not `engaged`. Re-point 65/270
  if flown pitch < 0 or heading is the eastern half. Do not re-engage.
  Modules: `hop.py`.

## 2026-08-23T09-59-28Z-hop — T-161 burnout yaw 336 / 5 km chute dumps horiz

- **When:** 2026-08-23 letsgrok `python main.py hop`
  (`2026-08-23T09-59-28Z-hop`). Stiff-pbc living recover 5 m/s. f013
  2HOT start unlocked=yes on_craft=yes. Do not Hangar.
- **Symptom:** exit 0. MET 20 heading 297 pitch 66 horiz 99. burn
  heading 336 pitch 39 horiz 83 MET 52. Apex 303/57 horiz 69. Last
  299/89 horiz 0 biome Shores. sci 5.6718 +0. 7 km stayed Cape Shores.
- **Cause:** 65/270 engaged after pad (pitch held). Rewriting
  `set_direction_and_up` every pulse (20 Hz while throttled) yawed
  336 by burnout. Deploy at 5 km still killed remaining horiz.
- **Fix:** after engage, do not rewrite the 65/270 hold. Deploy ≤2 km
  down. Modules: `hop.py`.

## 2026-08-23T09-44-59Z-hop — T-160 engage-once at zenith

- **When:** 2026-08-23 letsgrok `python main.py hop`
  (`2026-08-23T09-44-59Z-hop`). Stiff-pbc living recover 5 m/s. f013
  2HOT start unlocked=yes on_craft=yes. Do not Hangar.
- **Symptom:** exit 0. MET 19 heading 300 pitch 89. burn heading 340
  pitch 43 horiz 20 MET 51. Apex 300/88 horiz 20. Last 299/89 biome
  Shores. sci 5.6718 +0.
- **Cause:** inland 10 °/s slew used `telem.pulse_s` (0.05 s while
  throttled) so `_steer_inland` engaged at ~90. Heading 270 is
  undefined at zenith; AP yawed 340 at burnout then weathercocked
  pad 299. Not a new craft.
- **Fix:** after `left_pad`, command 65/270 then engage once. Do not
  engage near zenith. Hold through burnout. Modules: `hop.py`.

## 2026-08-23T09-28-59Z-hop — envelope hid burnout attitude

- **When:** 2026-08-23 letsgrok `python main.py hop`
  (`2026-08-23T09-28-59Z-hop`, same hang 09-16-24Z). Living recover
  5 m/s. f013 2HOT start unlocked=yes on_craft=yes. Do not Hangar.
- **Symptom:** packet `hz_median 0.08` (25 samples / 288 s). Skim
  apex heading 298 pitch 86 — Jeb `ship.md` MET 49 heading **209**
  pitch **3** horiz 22 (slew flash). Envelope had no burn row.
- **Cause:** T-147 apex is peak **alt**; that sample is after cutoff
  (MET 63 pitch 86). The 209/3 row was on disk. Slow `Telem.read`
  (>1 s) re-armed the 1 s sci/broken/debris walk every pulse, so
  requested 5/20 Hz stayed ~0.08 Hz and slew is one point.
- **Fix:** envelope `burn:` + `--window burnout` (min pitch while
  throttled through first cutoff). Skip slow part-walks after an
  expensive read; 20 Hz while throttled. Modules: `telem.py`,
  `tape.py`. Not hop.py (Lars T-158 gates).

## 2026-08-23T09-28-59Z-hop — T-157 target_direction still unheld

- **When:** 2026-08-23 letsgrok `python main.py hop`
  (`2026-08-23T09-28-59Z-hop`). Stiff-pbc living recover 5 m/s. f013
  2HOT start unlocked=yes on_craft=yes. Do not Hangar.
- **Symptom:** exit 0. Events slew heading=270. Apex heading 298
  pitch 86 horiz 22. Last heading 299 pitch 89 horiz 0 biome Shores.
  sci 5.6718 +0. Jeb 209/3 through burnout; 0.08 Hz tape missed it.
- **Cause:** `_steer_heading` wrote `engaged=True` every pulse. kRPC
  0.6 Engage restarts PID and 0.5 s soft-start, so AP never holds.
  `target_direction` is still pitch/heading vs default zenith up —
  ill-defined at pad 90° (same 09-16-24Z Euler trap).
- **Fix:** `set_direction_and_up` (surface dir, north up). Engage once.
  Modules: `hop.py`.

## 2026-08-23T09-16-24Z-hop — T-151 slew logged, not held

- **When:** 2026-08-23 letsgrok `python main.py hop`
  (`2026-08-23T09-16-24Z-hop`). Stiff-pbc living recover 5 m/s. f013
  2HOT start unlocked=yes on_craft=yes. T-152 deploy gate already in.
  Do not Hangar.
- **Symptom:** exit 0. Events slew heading=270. Apex heading 297
  pitch 87 horiz 22. Last heading 299 pitch 89 horiz 0 biome Shores.
  sci 5.6718 +0. Chute held past apex (deploy ~2.8 km).
- **Cause:** `_steer_heading` set `target_pitch`/`target_heading` (and
  swallowed `target_direction`). Near vertical those Eulers stay pad
  299 (16-57-24Z). The 270 line was stdout, not a hold.
- **Fix:** After `left_pad`, command surface `target_direction` only
  (roll NaN). Do not write pitch/heading. Hold through burnout.
  Modules: `hop.py`.

## 2026-08-23T08-54-41Z-hop — chute at apo dumps inland slew

- **When:** 2026-08-23 letsgrok `python main.py hop`
  (`2026-08-23T08-54-41Z-hop`). Stiff-pbc living recover 5 m/s. f013
  2HOT start unlocked=yes on_craft=yes. Do not Hangar.
- **Symptom:** exit 0. Events slew heading=270. Apex alt 13609
  chute=deployed heading 329 pitch 60 horiz 15.8. Last heading 299
  pitch 89 horiz 0 biome Shores. sci 5.6718 +0.
- **Cause:** hop.py `deploy_chutes` on `apo_cut` or any vz<0. Canopy
  at 13 km killed the inland horiz. Craft `deployAlt` is Gus T-153.
- **Fix:** Arm airborne. Deploy only vz<0 and alt≤5 km. Modules:
  `hop.py`.

## 2026-08-23T08-29-36Z-hop — vertical hop stays Shores

- **When:** 2026-08-23 letsgrok `python main.py hop`
  (`2026-08-23T08-29-36Z-hop`). Stiff-pbc living recover 5 m/s.
  f013 2HOT start unlocked=yes on_craft=yes. Do not Hangar.
- **Symptom:** exit 0. Pad heading 299 horiz 0.01 pitch 90. Last
  heading 300 horiz 0.01 pitch 89. Tape biomes=[Shores] apo 16.8 km.
  sci_bank 5.6718 (+0). T-068 Forest FlyingLow unpaid. T-070/T-071
  Grasslands still bound. Shores FlyingLow thermo+TELEMETRY capped.
- **Cause:** hop.py lights SAS vertical. Pad 299 is cape heading, not
  downrange. 7.5° from vertical stayed Shores (14-33-29Z). 090 is
  Water (hop-to-water). Straight-up cannot pay Forest.
- **Fix:** after `left_pad`, slew 25° from vertical heading 270 inland
  (`target_direction`, roll NaN). Do not slam 65 at light. Hold AP
  through burnout. Throttle 1 (stiff q~37 kPa). hop-to-water 090 and
  hop-splash vertical stay. Modules: `hop.py`.

## 2026-08-23T08-04-05Z-hop — desk sci was stale sfs after recover

- **When:** 2026-08-23 letsgrok `python main.py hop`
  (`2026-08-23T08-04-05Z-hop`). Living recover, mysteryGoo FlyingLow
  finished MET 674 > 641 s (T-112 est 4.20). Do not Hangar. Do not
  leftover-ksc.
- **Symptom:** Os saw ~4.2 banked in the game. Hank desk immediately
  after: `sci 1.4718 (+0.0001)`. Tape `sci_run=1 rem=0` (rem=0 is
  canister empty/file, not bank). Next hop Hangar flushed
  `persistent.sfs`; mid-flight desk `5.6718 (+4.2000)`.
- **Cause:** `world.research.science` is save-file `sci =`. `recover()`
  credits RAM `SpaceCenter.science`. Autosave waits for Hangar/scene.
  After-flight sit object was disk-lag.
- **Fix:** last-flight writes live RD `sci:`; jsonl `kind=sci_bank`.
  Desk prefers kRPC (lock free) then last-flight when it is ahead of
  sfs; `sci_src` / `sci_disk (lag)`. Envelope `bank=`. Modules:
  `desk.py`, `career.py`, `main.py`, `flightlog.py`, `telem.py`,
  `tape.py`, `recover_probe.py`. Not hop.py.

## 2026-08-23T07-21-05Z-hop — envelope hid descent; Telem.read was 13 s

- **When:** 2026-08-23 letsgrok `python main.py hop`
  (`2026-08-23T07-21-05Z-hop`). Same hang as 07-50-48Z (hz 2.86 is
  crash-UI 20 Hz, not a denser loft).
- **Symptom:** packet `hz_median 0.07` (14 samples / 183 s). Skim apex
  10.8 km then last 412 m — “no descent tape”. Gus T-147.
- **Cause:** tape apex was **max apo** (still climbing at MET 39). The
  jsonl *had* 14 km → 12.9 → … → 1.9 km → 412 m, one row ~14 s.
  `Telem.read` walked every module `field_list` + unguarded
  `Module.fields` (OKTO duplicate gui) + science/debris every pulse.
  Requested 5 Hz was a lie. Hop nap cannot sample what read does not
  return.
- **Fix:** apex = peak alt; `descent:` on skim; `--window descent`;
  impact uses last airborne if 2 s MET is empty. Skip `.fields` after
  `field_list`; cache sci/broken/debris 1 s; bind streams by
  `Vessel.id`; 20 Hz below 8 km. Modules: `telem.py`, `tape.py`.
  Not hop.py (Lars chute/recover).

## 2026-08-23T07-50-48Z-hop — total wreck is ksc leftover, not recover spin

- **When:** 2026-08-23 letsgrok `python main.py hop`
  (`2026-08-23T07-50-48Z-hop`). Hangar
  `kspstuff-hop-valiant-chute-stiff-pbc` parts=36 through apex mass
  1602. Bound TELEMETRY + mysteryGoo + 2HOT. F-013 2HOT start
  unlocked=yes on_craft=yes. Do not Hangar. Mk16 vs 1.6 t is Gus T-144.
- **Symptom:** exit 2 `ABORT not recoverable`. Last: sit=flying
  rec=no chute=none parts=0 mass=0 impact **89 m/s** Shores. Tape:
  `gate ec=0` + `hop recover sit=flying recoverable=no` many times,
  then `hop crash ui` alt=73 q=0, `hop crash ui space_center (total
  wreck)`. Hank leftover-ksc then failed on Flight Results overlay.
- **Cause:** kRPC death (T-141 not-shear) still waited recoverable.
  Recover tick + ec=0 spun. `go_space_center` on the overlay lied
  leftover-clean.
- **Fix:** `parts_n`/mass 0 rec=no after loft is total wreck: abort
  `ksc leftover` (`recover-probe --space-center`). Do not recover-tick,
  do not unpause-spam, do not Space Center. Recover if KSP still
  offers Recover. Modules: `hop.py`.

## 2026-08-23T00-10-20Z-hop — fly science_ids must not hide bound tickets

- **When:** 2026-08-23 letsgrok `python main.py hop`
  (`2026-08-23T00-10-20Z-hop`). Hangar chute-pbc. F-013 TELEMETRY hosted
  OKTO on_craft=yes; mysteryGoo start unlocked=yes on_craft=yes. Do not
  Hangar.
- **Symptom:** skip `kerbalism_TELEMETRY` / `mysteryGoo` (not in card);
  start `temperatureScan` over capped Shores; sci 1.4717 unchanged.
  T-081 `payload.science_ids=[temperatureScan]` while T-071 TELEMETRY
  and T-112 goo were the flying card.
- **Cause:** `protocol._bound_ids` returned fly `science_ids` if set,
  else `science_ids_for`. A stale fly list hid bound tickets. Hop skip
  is that card.
- **Fix:** `card_science_ids` unions bound tickets then fly extras.
  Fly cannot drop binds. T-081 card stays
  temperatureScan,kerbalism_TELEMETRY,mysteryGoo. Modules: `tickets.py`,
  `protocol.py`, `desk.py`, `hop.py` (science card only).

## 2026-08-23T07-21-05Z-hop — impact death is not boost shear

- **When:** 2026-08-23 letsgrok `python main.py hop`
  (`2026-08-23T07-21-05Z-hop`). Hangar
  `kspstuff-hop-valiant-chute-stiff-pbc` parts=36. Bound TELEMETRY +
  mysteryGoo. F-013 2HOT start unlocked=yes on_craft=yes. Do not Hangar
  (T-142 leftover-ksc is Wernher).
- **Symptom:** exit 2 `ABORT shear`. Stiff **36 parts through apex**
  mass 1602 kg. Next sample MET **182.6** alt **412 m** mass **0**
  parts_n **0** root empty chute=armed vz **−91** landing hard **91 m/s**
  Shores. hz_median **0.07** (14 samples / 183 s). No descent tape
  between 10.8 km up and 412 m.
- **Cause:** `stack_sheared` / telem `parts_n` drop treated kRPC
  vessel-death at impact as FAR tank shear (07-06-08Z was 1283→270
  **with remaining parts** at 13 km). Hop aborted before recover.
  Deploy waited for alt≤5 km + vz<0 — that sample never came. 91 m/s
  with Mk16 on a 1.6 t stiff hang is late/small canopy (Gus).
- **Fix:** `parts_n<=0` or `mass<=0` is not shear. Ignore telem gate
  `shear` (hop decides). `deploy_chutes` on **coast** (cutoff / descent),
  not only a 5 km sample. Modules: `hop.py`.

## 2026-08-23T07-06-08Z-hop — FAR shear is a gate, not a crash-UI dwell

- **When:** 2026-08-23 letsgrok `python main.py hop`
  (`2026-08-23T07-06-08Z-hop`). Hangar
  `kspstuff-hop-valiant-proc-tank-pbc` (OKTO + Mk16 + 2HOT). Bound
  T-068/T-070 temperatureScan FlyingLow. F-013 2HOT start unlocked=yes
  on_craft=yes. Do not Hangar. Do not patch telem (T-139).
- **Symptom:** exit 2 `ABORT not recoverable`. Science started. chute
  armed. apo 20.2 km Shores. landing catastrophic **154 m/s**. Apex
  MET **45** mass **270.6** pitch **−58** q 16 kPa fuel 0 (was 1283 kg
  / 178 fuel). Last mass **0** alt 45 flying recoverable=no. `broken`
  null, wreck false until crash UI. Same 154 m/s as 06-53-50Z
  (1677→270 while fuel still 124).
- **Cause:** Post-burnout FAR q + attitude ripped tank/engine off the
  OKTO. Hop has no mass/parts gate; `reliability_broken` stays null.
  Dwell continued until crash UI.
- **Fix:** `stack_sheared`: parts_n drop, or mass drop ≥40% and beyond
  fuel burned. `hold` then abort `shear`. Do not wait crash UI.
  Modules: `hop.py`.

## 2026-08-23T06-53-50Z-hop — kRPC armed is not a deployed canopy

- **When:** 2026-08-23 letsgrok `python main.py hop`
  (`2026-08-23T06-53-50Z-hop`). Hangar
  `kspstuff-hop-valiant-proc-tank-pbc` (OKTO + Mk16 + 2HOT + Goo). Bound
  T-068/T-070 temperatureScan, T-071 TELEMETRY, T-112 mysteryGoo.
  F-013 2HOT start unlocked=yes on_craft=yes. Do not Hangar.
- **Symptom:** exit 2 `ABORT not recoverable`. Logs `chute armed`,
  science start thermo+TELEMETRY+goo, dwell. landing catastrophic
  **154 m/s** Shores. Pad/airborne tape chute **cut**, MET 21–169
  **armed**, 206 m still armed vz **−154** q 14 kPa, last **none**
  sit=flying recoverable=no stage 0. apo 18.8 km. sci 1.4717 → 1.4717.
- **Cause:** T-115 `arm_chutes` set kRPC `Parachute.armed` and fired
  RealChute `Arm parachute` at first airborne. RealChute **auto-deploy
  did not fire**. Hop latched `chute_armed` and never `Deploy chute`.
  Packed Mk16 to lithobrake. Cut on the pad is kRPC State, not a
  canopy that opened then ripped.
- **Fix:** `deploy_chutes` (RealChute `Deploy chute` / kRPC `deploy()`)
  when coasting, vz < 0, alt ≤ 5 km. Retry until deployed. Repack if
  cut. Do not extra-stage. Modules: `pad.py`, `hop.py`.

## 2026-08-23T00-10-20Z-hop — Mk16 never armed, 154 m/s Shores

- **When:** 2026-08-23 letsgrok `python main.py hop`
  (`2026-08-23T00-10-20Z-hop`). Hangar
  `kspstuff-hop-valiant-proc-tank-pbc` (OKTO + Mk16 + 2HOT). Bound
  T-068/T-070 temperatureScan FlyingLow 138/0.002. F-013 2HOT start
  unlocked=yes on_craft=yes. Geiger unlocked, **not** on craft — do not
  patch a Geiger dwell. Do not Hangar. KSC leftover is Hank.
- **Symptom:** exit 0 recovered sit=landed recoverable=yes. sci
  1.4717 → 1.4717. landing catastrophic **154 m/s** Shores heading
  **134** pitch **−59**. Pad stage **2**, airborne→last stage **1**.
  vz **−176** at 5 km, **−154** at 192 m, q **10k→14k** (no bleed).
  Tape chute/recoverable/sci_run **absent** (thin eyes; Wernher). EC
  343→0 on impact. MET freeze 168.66 alt 51.
- **Cause:** hop.py still **No chute** from the Flea sit. Light is the
  only `activate_next_stage`. Mk16 `preferredStage=PARACHUTESTAGE` never
  armed. RealChute auto-deploy needs **Arm parachute** (minPressure
  0.04 / deploymentAlt 1000). 154 m/s is ballistic, not a failed
  canopy. T-005 leftover-Flea overlay is **not** this hop (fuel 720,
  apo 25 km Valiant) — that fingerprint is hangar kernel (T-052).
- **Fix:** `pad.arm_chutes` after airborne (kRPC `Parachute.armed` /
  RealChuteModule `Arm parachute`). Do **not** extra-stage at light.
  Do not immediate Deploy (high-q shred). Modules: `pad.py`, `hop.py`,
  `blocks.md`.

## 2026-08-22T23-35-40Z-hop — 20 Hz freeze is not a 0.25 s Close

- **When:** 2026-08-22 letsgrok `python main.py hop`
  (`2026-08-22T23-35-40Z-hop`). Hangar
  `kspstuff-hop-valiant-chute-stiff-pbc` parts=36. Bound T-068/T-070
  temperatureScan FlyingLow 138/0.002. F-013 2HOT start unlocked=yes
  on_craft=yes. Do not Hangar. KSC leftover is Hank.
- **Symptom:** exit 2 `ABORT not recoverable`. Science started 2HOT
  dwell. apo 20.4 km Shores. landing hard **89 m/s** heading **299**
  pitch 90. Last sit=**flying** alt **72.6** MET **186.48** q=0
  horiz 8.64. `hop recover sit=flying recoverable=no` then crash UI
  unpause then `space_center (total wreck)`. 23-14-23Z same hang
  **landed** recovered at 90 m/s. hz_median 0.28; impact tape 20 Hz.
  No landing event.
- **Cause:** MET-still was **5 pulses**. Near-ground telem is 20 Hz, so
  freeze→Close in **0.25 s** before KSP flipped sit=landed. Chute still
  not a 138 s hang (Gus T-089) — recover is this desk.
- **Fix:** Frozen MET is **5 wall seconds**. After unpause, settle 2 s
  for sit=landed/`recoverable` before Close. Modules: `hop.py`.

## 2026-08-22T22-33-17Z-hop — bound FlyingLow is not leftover FlyingHigh

- **When:** 2026-08-22 letsgrok `python main.py hop`
  (`2026-08-22T22-33-17Z-hop`). Hangar
  `kspstuff-hop-valiant-chute-pbc`. Bound T-068/T-070 temperatureScan
  FlyingLow 138/0.002. F-013 2HOT start unlocked=yes on_craft=yes.
  hop_apo 18 km. Do not Hangar. KSC leftover is Hank.
- **Symptom:** exit 2 `ABORT no science (FlyingHigh lid)`. Light
  vertical. First flying MET **1.1** alt **96**. apo max **25.5 km**,
  alt max **15.8 km** — never 50 km. Biome **Shores** the whole way.
  `science wait FlyingHigh`; 2HOT never Toggle. EC 2049→0. Frozen last
  MET **162.8** alt **55** flying q=0 vz **−146** heading **299**
  horiz **33**. `gate ec=0` / `hop ec=0 wait recoverable` /
  `hop recover sit=flying recoverable=no` then `hop down`.
- **Cause:** `hop_wants_flying_high` scanned **every** open science
  ticket. Unbound leftover T-069 `FlyingHigh@Forest` TELEMETRY (no
  `experiment_id`) set the 50 km lid. Bound flying ids were
  `temperatureScan` FlyingLow. Lit hop with empty modules then waited
  recoverable as leftover HD. Crash UI never Close (FlyingHigh abort
  first) — leftover freeze.
- **Fix:** Lid is the **bound** flying card only. Unbound leftover
  High is not 50 km. FlyingLow Toggles airborne. Lit empty wreck is
  not leftover HD. Missed-lid unrecoverable leaves crash UI (Space
  Center). Chute 138 s is the dwell. Modules: `hop.py`.

## 2026-08-22T22-24-26Z-hop — OKTO RW duplicate PAW is not a hop abort

- **When:** 2026-08-22 letsgrok `python main.py hop`
  (`2026-08-22T22-24-26Z-hop`). Hangar
  `kspstuff-hop-valiant-chute-pbc` sit=pre_launch parts=33 hop_apo=18000.
  F-013 temperatureScan sensorThermometer start unlocked=yes on_craft=yes.
  Matching leftover PRELAUNCH (fuel 675, MET 0) stays on pad. Do not
  Hangar. Do not recover.
- **Symptom:** Hangar ready, then first `telem.read()` `ValueError Key:
  Reaction Wheels` in `reliability_broken` → `_module_flag` (`telem.py`
  `getattr(module, "fields")`). Never staged. MET 0 throttle 0. jsonl
  one `kind=start` — heading none / horiz none. last-flight still prior
  `ksc` exit 0. Stuck still: pad, HDG 000, no crash UI.
- **Cause:** OKTO (`probeCoreOcto_v2`) carries `ModuleReactionWheel`.
  kRPC 0.6 `Module.fields` is a dict of **visible PAW gui names** and
  throws on duplicate keys. Stayputnik hangs never hit this (no wheel).
  Hop did not fly; the abort is schema, not a burn.
- **Fix:** none in `hop.py`. `telem._module_flag` walks `field_list` /
  `get_field_by_id` first; `Module.fields` is try/except (OKTO
  `ModuleReactionWheel` duplicate gui `Reaction Wheels`). First
  `telem.read()` must not abort. Matching PRELAUNCH leftover stays —
  Commander hop may enter Flight. Do not Hangar. Do not recover.
  Modules: `telem.py`.

## 2026-08-22T10-11-27Z-hop-to-water — 20 Hz dump 108 LF then 9 m/s rebuilt to 62

- **When:** 2026-08-22 letsgrok `python main.py hop-to-water`
  (`2026-08-22T10-11-27Z-hop-to-water`). East-t3. F-013 mysteryGoo
  GooExperiment start unlocked=yes on_craft=yes. Do not Hangar. KSC
  leftover is Hank (`ksc leftover`).
- **Symptom:** exit 2 `ABORT no science (wanted mysteryGoo)`. Latch
  hop_apo **held**: MET **79.4** thr **0** fuel **108.7**. Suicide 1 Hz
  **never thr=1**. MET **176.1** thr 0 leftover **108.7** heading **292**
  horiz **21.6** speed **224** vz **−223** alt **2415**. Gap MET
  **176→209** dumped **108.7→crumbs 1.98**. MET **208.9** thr 0 fuel
  **1.98** heading **295** horiz **1.93** speed **9.2** vz **−9.4** alt
  **195**, then rebuild. Splash MET **214.3** sit=splashed heading
  **304.6** horiz **2.00** speed **62.3** landing hard **62 m/s** Shores.
  kind=state pad heading **298.9** never 090 (T-016).
- **Cause:** 20 Hz `_suicide_gate` between Telem.read (same 09-48
  off-tape burn). vz-cut at ≥ −10 while coast from 195 m is ~62
  returned/spent (crumbs). Throttle 1 after the kill at leftover TWR
  dumps to crumbs; cutting lets gravity rebuild 9→62. Goo
  crashTolerance 12. Modules gone.
- **Fix:** After vz ≥ −10, TWR≈1 hover until vacuum coast ≤12 — do
  not slam 1, do not drop out at the cut, do not spent unless coast
  ok or crumbs. Watch TTI ≤12; light at 3.5 or TWR burn-distance.
  Crumbs still not a relight. Do not loft. Keep Hank ksc leftover.
  Modules: `hop.py`, `blocks.md`.

## 2026-08-22T09-48-51Z-hop-to-water — suicide never throttle 1 at 1 Hz

- **When:** 2026-08-22 letsgrok `python main.py hop-to-water`
  (`2026-08-22T09-48-51Z-hop-to-water`). East-t3. F-013 mysteryGoo
  GooExperiment start unlocked=yes on_craft=yes. Do not Hangar. KSC
  leftover is Hank (`ksc leftover`).
- **Symptom:** exit 2 `ABORT no science (wanted mysteryGoo)`. Latch
  hop_apo **held**: MET **79.2** thr **0** fuel **110.1**. Suicide 1 Hz
  **never thr=1** (one pad-light sample only). Recut MET **180.4**
  leftover **50.4** vz **−7.7** alt 1675 (unlogged 20 Hz dump 110→50).
  Hover did not light: MET **181.6** vz **−20.1** leftover 50.4 thr
  **0** until TTI≤12 MET **190.6** vz **−107**. Pulses to crumbs.
  Splash MET **212.7** sit=splashed biome Shores heading **296** horiz
  **7.66** speed **92.5** landing hard **92 m/s**. kind=state heading
  pad **299** never 090 (T-016).
- **Cause:** `_suicide_gate` returned False at vz ≥ −10 **before**
  `suicide_armed` latched, so T-040 hover waited TTI≤12 again. TTI≤12
  first light at 2.4 km dumped ~60 LF. Gate sits between Telem.read so
  jsonl never shows thr=1. Leftover 50 at 1.7 km cannot hover to Goo
  12 after gravity rebuilds.
- **Fix:** Watch TTI ≤12; **throttle 1** at live TTI ≤ **3.5**. Latch
  armed on first braking even if the gate cuts. After vz-cut, hover
  when vz < −10 without TTI wait; spent only if coast ≤12. Crumbs not
  a relight. Do not loft. Modules: `hop.py`, `blocks.md`.

## 2026-08-22T09-11-59Z-hop-to-water — splash must be ≤ Goo crashTolerance 12

- **When:** 2026-08-22 letsgrok `python main.py hop-to-water`
  (`2026-08-22T09-11-59Z-hop-to-water`). East-t3. F-013 mysteryGoo
  GooExperiment start unlocked=yes on_craft=yes. T-035 capable: no
  (crashTolerance 12; survivability 15 LOCKED). Do not Hangar. KSC
  leftover is Hank.
- **Symptom:** 09-11 splash MET 211.8 sit=splashed biome Shores heading
  **299** horiz **2.2** speed **82** landing hard **82 m/s** (jsonl
  impact ~67). 08-44-32Z splash **119 m/s** Shores (recut vz −30 leftover
  60 loft). `science skip (no Experiment modules)` both hops. kind=state
  heading pad **299** never 090.
- **Cause:** Suicide cut at vz ≥ −20 at **1766 m** leftover **57**. Vacuum
  coast from that gate is ~186 m/s; drag still ~82. T-033 spent-latch
  stops TTI≤12 pulse-relight (the slam) but leftover 57 is the Δv that
  must hover-slam until coast impact ≤12. Chutes locked. Hardware cannot
  buy the can.
- **Fix:** Cut at vz ≥ **−10** (margin under Goo 12). Leftover after that
  cut is spent **only if** vacuum coast ≤12. Else hover-relight when vz
  drops below the cut — do not wait TTI≤12. Crumbs still not a relight.
  Do not loft past the cut. Modules: `hop.py`, `blocks.md`.

## 2026-08-22T09-11-59Z-hop-to-water — leftover after vz-cut is spent

- **When:** 2026-08-22 letsgrok `python main.py hop-to-water`
  (`2026-08-22T09-11-59Z-hop-to-water`). Hangar east-t3. F-013 mysteryGoo
  GooExperiment start unlocked on_craft; TELEMETRY Stayputnik host.
  Bank 13.26 Δ0. Do not Hangar. KSC clean (Hank dismiss_flight_results).
- **Symptom:** exit 2 `ABORT no science (wanted mysteryGoo)`. Latch
  hop_apo **held**: MET **78.6** thr **0** fuel **114.1**. Suicide recut
  MET **179.2** thr **0** vz **−19.3 leftover 57** (seen-vz ≥ −20). Then
  TTI≤12 pulse-relight: MET **188.7** fuel 57 vz **−110**; MET **191.7**
  leftover 28.8 vz **−13.7**; MET **199** leftover 13.8; MET **205**
  crumbs **1.16**. Splash MET **211.8** sit=splashed biome Shores heading
  **299** horiz **2.2** speed **82** landing hard **82 m/s** EC=0.
  `science skip (no Experiment modules)`. kind=state heading pad **299**
  burn **300** splash **299** — never 090 (T-016).
- **Cause:** 20 Hz gate cut at vz ≥ −20 (08-44 was predict-cut at −30).
  `_suicide_now` then re-armed leftover 57 when TTI fell ≤12 (MET 188.7
  alt 1158 / vz 110). Each pulse cut at −20 again, gravity rebuilt, slam
  to crumbs, dry fall from 333 m → 82 m/s killed GooExperiment.
- **Fix:** Latch suicide **spent** when the vz-cut fires. Hold throttle
  0 after vz ≥ −20. Crumbs (fuel ≤2) are not a relight; leftover 57
  after cut is not a second slam. Do not fake 090. Modules: `hop.py`,
  `blocks.md`.

## 2026-08-22T08-44-32Z-hop-to-water — suicide recut at vz −30 leftover loft

- **When:** 2026-08-22 letsgrok `python main.py hop-to-water`
  (`2026-08-22T08-44-32Z-hop-to-water`). Hangar east-t3. F-013 mysteryGoo
  GooExperiment start unlocked on_craft; TELEMETRY Stayputnik host.
  Bank 13.26 unchanged. Do not Hangar.
- **Symptom:** exit 2 `ABORT no science (wanted mysteryGoo)`. Latch
  hop_apo **held**: MET **78.6** thr **0** fuel **114.2**. Suicide MET
  **174.9** thr **1** vz **−209** alt 2.07 km. MET **176.5** vz **−113**
  still thr 1. Recut MET **178.0** thr **0** vz **−29.9 leftover 60.6**.
  Relight MET **187.2** vz **−103**; overburn MET **188.9** vz **+2.7**
  leftover 30 then loft vz **+85**. Splash MET **218** sit=splashed
  biome Shores heading **298** horiz **17.9** speed **120** landing
  catastrophic **119 m/s** EC=0. `science skip (no Experiment modules)`.
  kind=state heading pad **299** burn **301** splash **298** — never 090.
- **Cause:** next-pulse predictor cut at vz −30 (jsonl ~1.5 s, accel
  ~53 m/s²) before vz ≥ −20. `_suicide_now` then re-armed leftover 60
  and lofted. Heading 090 is Stayputnik no wheel (T-016).
- **Fix:** Hold throttle 1 until vz ≥ −20 is **seen**. 20 Hz
  `_suicide_gate` while armed (Telem.read is ~1.5 s). Do not predict-cut.
  Crumbs (fuel ≤2) are not a relight. Do not fake 090. Modules: `hop.py`,
  `blocks.md`.

## 2026-08-21T23-15-52Z-hop-to-water — leftover KSC is Hank recover-probe

- **When:** 2026-08-21 letsgrok `python main.py hop-to-water`
  (`2026-08-21T23-15-52Z-hop-to-water`). T-029. Pad now empty. Do not
  Hangar. Do not fly.
- **Symptom:** hop leftover wreck recovered then Hangared new inside
  the mission script. Hank never saw a recover-probe call. Last-flight
  abort was science, leftover already gone.
- **Telemetry:**
  ```
  abort: no science (wanted mysteryGoo)
  hop leftover wreck sit=splashed recoverable=yes experiments=0 — recover, Hangar new
  recovered leftover wreck
  hop recover still listed after recover()
  ```
- **Cause:** unmatched leftover and matching wreck leftover called
  `recover()` + `go_space_center`, then Hangar. `ops next` hired
  Jebediah on hangar `recover`/`phase` and S1 recover.
- **Fix:** those hop gates print `ksc leftover` and abort with
  `python main.py recover-probe --recover` (or `--space-center` if
  not recoverable). Empty pad still Hangars. Living leftover still
  enters Flight. Splash/HD recover of **this** hop stays. `ops next`
  hires hank with that CLI. `protocol.fly_gate` waits leftover n>0.
  Unittest skips live FlyingHigh tickets in `hop_wants_flying_high`
  (wait_water would never timeout). Modules: `hop.py`, `ops.py`,
  `protocol.py`, `desk.py`.

## 2026-08-21T23-15-52Z-hop-to-water — suicide cuts before vz lofts

- **When:** 2026-08-21 letsgrok `python main.py hop-to-water`
  (`2026-08-21T23-15-52Z-hop-to-water`). Hangar east-t3. F-013 mysteryGoo
  GooExperiment start unlocked on_craft; TELEMETRY Stayputnik host.
  Chutes LOCKED. Bank 13.26 unchanged. Do not Hangar.
- **Symptom:** exit 2 `ABORT no science (wanted mysteryGoo)`. Latch
  hop_apo **held**: MET **79.1** thr **0** apo 18.7 km fuel **111.1**.
  Suicide MET **171** thr **1** vz **−194** alt 3.75 km (tti 18). MET
  **173.1** thr 1 vz **−65** (no TTI recut). MET **174.5** thr **1**
  vz **+24.5** fuel **47**; recut MET **176.5** vz **+140** leftover
  **16.6**. Relight MET **208.9** vz **−126** fuel 11.5 then crumbs
  thr 1. Splash MET **225** sit=splashed biome Shores heading **303.7**
  horiz **24.3** speed **221** landing catastrophic **220 m/s** EC=0.
  `science skip (no Experiment modules)`. kind=state heading pad
  **299** burn **300** splash **304** — never 090 (3× 080–100
  fly-throughs). Landing T-013 / T-024 catastrophic.
- **Cause:** vz latch stayed on through −65 because the next jsonl
  sample was 1.4 s later (hz_median **0.57**) and already +24 — TWR
  lofted leftover. Arm TTI **20** lit at 3.75 km. After recut,
  `_suicide_now` re-armed at tti 19 with crumbs. Heading 090 is
  Stayputnik no wheel (T-016), not this setter.
- **Fix:** Arm TTI ≤12. Cut at vz ≥ −20 **or** when the next pulse
  would cross it. Burst 20 Hz while braking (TTI rises as speed dies).
  Fuel ≤2 LF is not a relight; a later TTI≤12 slam may use leftover.
  Do not fake 090. Modules: `hop.py`, `blocks.md`.

## 2026-08-21T22-57-36Z-hop-to-water — suicide latches until vz cut

- **When:** 2026-08-21 letsgrok `python main.py hop-to-water`
  (`2026-08-21T22-57-36Z-hop-to-water`). Hangar east-t3 after leftover
  recover. F-013 mysteryGoo GooExperiment start unlocked on_craft;
  TELEMETRY Stayputnik host. Chutes LOCKED. Bank 13.26 unchanged.
- **Symptom:** exit 2 `ABORT no science (wanted mysteryGoo)`. Latch
  hop_apo **held**: MET **79.2** thr **0** apo 18.97 km fuel **109.5**.
  Suicide MET **179.7** thr **1** alt 1.95 km speed 201 tti 9.7 pitch
  **61**. MET **181.6** thr 1 pitch **89** speed 88 tti **19** vz **−72**
  fuel 73; MET **183** thr **0** fuel 46 vz **+19**. Relight MET **198.7**
  then loft vz **+40**; crumbs MET 219 thr 1 fuel 0.68. Splash MET
  **226.3** sit=splashed biome Shores impact **119 m/s** heading **314**
  horiz **8.1** fuel=0 EC=0. `science skip (no Experiment modules)`.
  Landing T-013 / T-023 catastrophic. Heading **300** is T-016.
- **Cause:** `_suicide_now` used TTI to **cut** as well as arm. First
  burn killed ~110 m/s; TTI rose above 12 and the loop cut while still
  descending, then relit after TTI fell — leftover LF lofted (vz +19 /
  +40) instead of staying on until vz was dead. Experiment modules gone
  is the same 119 m/s wreck (T-022 = T-017 class).
- **Fix:** Arm on TTI (≤20 s, alt ≤8 km). Latch throttle 1 until vz
  ≥ −20 or fuel=0. TTI rising is not a recut. After hop_apo, point
  zenith while leftover LF remains. Do not patch start_experiments.
  Modules: `hop.py`, `blocks.md`.

## 2026-08-21T22-45-26Z-hop-to-water — recover leftover then Hangar

- **When:** 2026-08-21 letsgrok `python main.py hop-to-water`
  (`2026-08-21T22-45-26Z-hop-to-water`). Seated east-t3. F-013 mysteryGoo
  GooExperiment start unlocked on_craft; TELEMETRY Stayputnik host.
  Desk leftover n=0 was disk; live kRPC leftover sit=splashed MET 212.2
  fuel=0 recoverable=yes (the 22-03-59Z wreck). Bank 13.26 unchanged.
  Do not Hangar this hire.
- **Symptom:** exit 0 `recovered`. CLI `hop leftover sit=splashed
  fuel=0.0 recoverable=yes met=212.20 — do not light` then
  `recovered`. kind=state heading **300** horiz **41.6** pitch **77.6**
  biome Shores landing catastrophic impact **230 m/s**. Never lit.
  Latch + leftover-LF suicide untested. No new loft.
- **Cause:** matching leftover entered Flight (correct). Dry splashed
  wreck recovered in `run_on_vessel` and **returned** recovered. hop.py
  did not Hangar the seated craft after that recover. hop-splash 18-03
  starts splash on living Water leftover; this wreck had no loft left.
- **Fix:** hop-to-water matching leftover already down (splashed/landed
  dry, recoverable) recovers, then Hangar seated craft. Unrecoverable
  flying wreck still abort (14-52-25Z). hop-splash splash-on-leftover
  unchanged. Modules: `hop.py`, `blocks.md`.

## 2026-08-21T22-03-59Z-hop-to-water — hop_apo cut latches; leftover LF is suicide

- **When:** 2026-08-21 letsgrok `python main.py hop-to-water`
  (`2026-08-21T22-03-59Z-hop-to-water`; hop-splash twin 18-15-08Z /
  19-43-18Z / 21-14-09Z). Hangar east-t3. F-013 mysteryGoo
  GooExperiment start unlocked on_craft; TELEMETRY Stayputnik host.
  Bank 13.26 unchanged. Do not Hangar.
- **Symptom:** exit 2 `ABORT no science (wanted mysteryGoo)`.
  kind=state: pad heading **299** pitch 90; burn hold heading **~301**
  pitch **~65** throttle **0.4**; apo max **19.06 km** MET 77.5 thr
  0.4; MET **79.7** thr **0** apo 18.37 km fuel 104.5; MET **81.8**
  thr 0 apo 17.62 km heading **75.3** (090 fly-through); MET **84**
  thr **0.4** relight; MET **136.7** apo 17.16 km thr **0.4** dumped
  leftover **43.9** LF; last flying MET 211.4 alt **226 m** speed
  **233** horiz **41** heading **301**; splash MET **212.2** sit=splashed
  biome Shores impact **230 m/s** fuel=0 EC=0. `science skip (no
  Experiment modules)`. Landing T-013 catastrophic.
- **Cause:** wait_water set throttle 0.4 whenever apo < hop_apo
  (hop-splash `_hold_or_cut` throttle 1 — same class T-011). First
  cutoff was real; apo fell on the coast and the loop relit into
  descent. Empty-tank 18 km ballistic is still ~230 m/s; the recut
  spent the leftover that could have braked.
- **Fix:** Latch hop_apo (and fuel=0): stay cut. Do not recut 0.4/1.0
  because apo fell. wait_water / wait_splash leftover LF is a suicide
  burn (TTI ≤12 s, alt ≤8 km, speed >40, throttle 1 zenith). Heading
  **301** after T-007 target_direction is Stayputnik no wheel (T-016),
  not this setter. Modules: `hop.py`, `blocks.md`.

## 2026-08-21T16-57-24Z-hop-to-water — heading 090 is target_direction not roll 0

- **When:** 2026-08-21 letsgrok `python main.py hop-to-water`
  (`2026-08-21T16-57-24Z-hop-to-water`; 16-33-22Z same class). Hangar
  east-fin. F-013 mysteryGoo GooExperiment start unlocked on_craft;
  TELEMETRY Stayputnik host. Bank 13.26 unchanged. Do not Hangar.
- **Symptom:** exit 2 `ABORT not recoverable`. Light vertical, slew
  0.4 after left_pad, pitch 25° east and hold through burnout all
  logged. kind=state heading **never holds 090**: pad **299**, MET 4
  throttle 0.4 heading **299** horiz 4.6, then tumble 144/273/301…,
  five ±15° fly-throughs, burnout MET~62.8 fuel=0 heading **99** then
  **322**, lithobrake MET **89.64** alt 70.5 heading **299** horiz
  **14.5** flying recoverable=no q=0. apo max **3.66 km**, horiz max
  **85.6**. Never splashed. sci **+0**.
- **Cause:** `_steer_east` set `target_pitch` + `target_heading=90` +
  `target_roll=0` while still near vertical. kRPC: heading/roll are
  ill-defined at pitch 90; `target_roll=0` with default up (zenith)
  commands a roll Stayputnik cannot provide (no wheel, stability
  LOCKED). Gimbal is pitch/yaw. The 090 command was issued; the
  vehicle tumbled instead of tilting east.
- **Fix:** After left_pad, point east with surface
  `target_direction` (x=up y=north z=east) while slewing pitch 90→65.
  Leave `target_roll` unset (NaN) so AP damps roll rate. Still do not
  slam 65 at light. Still hold through burnout. Modules: `hop.py`,
  `blocks.md`.

## 2026-08-21T19-43-18Z-hop-splash — splash dwell at EC=0 is not abort

- **When:** hop-splash Hangar t7-splash vertical. jsonl heading 18.6 horiz 62.4 pitch 13.0 aoa 0 biome **Shores**. apo max 98.3 km. MET 487 sit=splashed. EC 2401 at 68 m flying, then 0 on first splashed sample. TELEMETRY started airborne T+1. sci +0.
- **Symptom:** `science keep kerbalism_TELEMETRY` then `wait science none` `gate ec=0` `ABORT ec=0`. Goo never Toggle. Briefing said dwell may start EC=0.
- **Cause:** dwell_for_card aborted EC=0 when nothing was recording. Splash wait already skipped that gate (17-46-04Z); dwell did not. 24×Z-100 were not empty — the splashed resource snapshot is 0. Airborne TELEMETRY Toggle spent the FlyingLow sample and the Start PAW before Water.
- **Fix:** splash dwell returns on EC=0 instead of abort (so TELEMETRY/goo can start). hop-splash does not Toggle while flying. Modules: `pad.py`, `hop.py`.

## 2026-08-21T18-15-08Z-hop-splash — splash TELEMETRY/goo without Experiment modules

- **When:** hop-splash Hangar t7-splash worked. Vertical loft, splash MET 475 sit=splashed biome **Forest** (not Water). jsonl heading 228 horiz 62 pitch 13 aoa 0. EC=0 fuel=0. leftover wreck recover+Hangar first. sci +0.
- **Symptom:** `science skip (no Experiment modules)` then ABORT `no science (wanted kerbalism_TELEMETRY)`. Stayputnik still hosts TELEMETRY PAW; GooExperiment still on craft. experiments=0 on leftover wreck.
- **Cause:** `start_experiments` only walked Kerbalism `Experiment` / `ModuleScienceExperiment` **by module name**. After splash those modules are gone; hosted TELEMETRY and goo PAW remain.
- **Fix:** treat a start-PAW module with a mapped part (Stayputnik → `kerbalism_TELEMETRY`, GooExperiment → `mysteryGoo`) as science. Stock `run()` fallback if still empty. Do not Toggle antenna. Modules: `science.py`.

## 2026-08-21T18-03-12Z-hop-splash — splashed leftover is splash card, not dark recover

- **When:** leftover from 17-46-04Z already `sit=splashed` MET 532 fuel=0 EC=0 recoverable=yes. hop-splash 18-03-12Z recovered without lighting. jsonl heading 29 horiz 78 pitch 0.77 aoa 0 biome **Shores**. TELEMETRY/goo never Toggle. sci +0. 24×Z-100 unused.
- **Symptom:** `leftover_wreck_before_light` true on dry splashed + recoverable → `do not light` then `recover()`. Exit 0. Card unstarted.
- **Cause:** leftover wreck treated **splashed** like flying/landed dry wreck. hop-splash exists to start splash TELEMETRY then goo **after Water**, including EC=0 leftover (17-46 already skipped abort; 18-03 skipped the start).
- **Fix:** when `wait_splash`/`wait_water` and `sit=splashed`, skip leftover-wreck recover; enter splash dwell. Modules: `hop.py`.

## 2026-08-21T17-46-04Z-hop-splash — EC=0 before splash science is not abort

- **When:** hop-splash t7-splash, apo 80 km vertical loft, splashed MET ~532, then ABORT `ec=0`. sci +0. TELEMETRY/goo never Toggle. jsonl had heading/horiz; no pitch/AoA/biome. FAR belly-flop look was the 80 km coast, not a re-entry burn.
- **Symptom:** `splash wait water` then `gate ec=0` while already Water. Card unstarted.
- **Cause:** splash wait treated EC=0 as abort before start. Dwell first pulse with no HD data same. Telem streamed heading/horiz only.
- **Fix:** skip EC=0 abort until the splash card has started (or HD has data). jsonl `pitch` / `aoa` / `biome`. Modules: `splash.py`, `hop.py`, `pad.py`, `telem.py`.

## 2026-08-21T16-57-24Z-hop-to-water — hop-splash is vertical wait splash

- **When:** 2026-08-21 Gene `need_stack: hop-splash` after
  `2026-08-21T16-57-24Z-hop-to-water` abort `not recoverable`. Linus
  splash TELEMETRY then mysteryGoo 641 s; flying ids empty. leftover
  east-fin PRELAUNCH ghost. Os 15 sci. Do not Hangar. Do not re-fly.
- **Symptom:** `hop` aborts empty flying. hop recovers on first splash
  and kills dwell. `hop-to-water` waits splash but slews 090 (heading
  never holds, apo 3.66 km, lithobrake Shores). `splash` does not
  Hangar or light.
- **Cause:** `phases.NAMES` had no `hop-splash`. FlyingLow 18 km clamp
  is the wrong cut for t7 (Gene `hop_apo` 80 km, OffPlan 140 km). East
  slew is dead (no reaction wheel).
- **Fix:** `hop-splash` in `phases.NAMES` / `blocks.md`. Hangar seated
  t7-splash, recover unmatched leftover without lighting, light
  vertical, no flying Toggle, `hop_apo` 80 km, wait splashed, splash
  dwell (TELEMETRY then goo). Crash UI Tracking, not Space Center.
  Flea refused. Modules: `hop.py`, `splash.py`, `phases.py`, `main.py`.

## 2026-08-21T recover-pad-again — Space Center from crash is pad reload

- **When:** east-fin hop-to-water lithobrake MET 89. Os: crash then
  "recover" went to Space Center, ship on the pad again. Probe:
  `pre_launch` MET 0 `can_revert_to_launch=True`. Screenshot pad pin.
- **Cause:** `GameScene.space_center` from Catastrophic Flight Results
  is the Space Center button. KSP restores the launch save. Unpause
  then Close made it worse. Not `revert_to_launch` (never called).
- **Fix:** crash UI → Tracking Station, never Space Center, never
  unpause. Modules: `hop.py`.

## 2026-08-21T recover-sit — recover() then pad leftover is a save reload

- **When:** After hop-to-water crash. KSC pin `east-one-pbc` on the
  pad. Probe: `sit=pre_launch` MET 0 `recoverable=yes`
  `can_revert_to_launch=True`. `recover()` returned; kRPC still listed
  the ship. Seconds later the pad was empty (Os: vessel is gone).
- **Cause:** `recover()` is async. `load_space_center` after Close
  reloads the **launch save**, so the same stack is on the pad again.
  That is not `revert_to_launch` (never called).
- **Fix:** Wait until the vessel list is empty after `recover()`.
  Crash Close: scene setter only (`reload_save=False`). Modules:
  `hop.py`, `hangar.py`, `recover_probe.py`.

## 2026-08-21T16-14Z — jsonl speed=0 is the vessel frame

- **When:** hop-to-water 15-26 through 16-25. Jeb HUD horiz ~20–90 m/s,
  heading 090 then 290. jsonl `speed` was 0 on every sample.
- **Cause:** `vessel.flight()` with no reference frame is the vessel
  origin. Speed in that frame is always ~0.
- **Fix:** stream `speed` / `horizontal_speed` / `heading` from
  `vessel.flight(body.reference_frame)`. hop-to-water holds throttle
  0.4 through slew (do not slam 1.0 after 25°). Modules: `telem.py`,
  `hop.py`.

## 2026-08-21T16-11-58Z-hop-to-water — do not slam pitch 65 at TWR 5

- **When:** 2026-08-21 letsgrok `python main.py hop-to-water`
  (`2026-08-21T16-11-58Z-hop-to-water`). Hangar
  `kspstuff-hop-valiant-east-bare-pbc`. F-013 2HOT start unlocked on
  craft. Bank 10.96 unchanged. Os: stack breaks apart, no decoupler.
  Do not Hangar. Do not re-fly.
- **Symptom:** exit 2 `ABORT not splashed`. Pitch 25° heading 90 at
  light, throttle 1. Fuel=0 MET 11.7 apo max **5.3 km** (prior 2×T100
  hops 10–12 km). T+54 `sit=landed` Shores alt=71 EC=0. Never
  `sit=splashed`.
- **Cause:** `_steer_east` set `target_pitch=65` `engaged=True` on the
  same pulse as `_light` at TWR ~5. Stayputnik has no wheel. Valiant
  100 kN. Bare stack has no decoupler — joints shear. East Δv never
  built; apo halved.
- **Fix:** Light vertical. After `left_pad`, slew AP 10 °/s toward
  65 heading 90 at throttle **0.4**, then hold through burnout. Do
  not command 65 on the pad. Modules: `hop.py`, `blocks.md`.

## 2026-08-21T15-26-18Z-hop-to-water — AP must hold east through burnout

- **When:** 2026-08-21 letsgrok `python main.py hop-to-water`
  (`2026-08-21T15-26-18Z-hop-to-water`). Hangar
  `kspstuff-hop-valiant-east-pbc`. F-013 2HOT start unlocked on craft.
  Bank 10.96 unchanged. leftover PRELAUNCH east-pbc. Do not Hangar.
- **Symptom:** exit 2 `ABORT not recoverable`. Pitch 25° heading 90
  logged. T+2 HDG 090 horiz ~21–27 m/s (still Shores, water on the
  horizon). Burnout MET~27 fuel=0 apo max **10.0 km**. T+63 HDG 304
  horiz still ~25 m/s. Lithobrake MET 100 alt 28.5 flying
  recoverable=no q=0. Never `sit=splashed`. jsonl `speed=0` all
  samples (HUD was ~90 m/s).
- **Cause:** `_steer_east` ran only while `_burning`; `_release_steer`
  at fuel=0. Stayputnik has no torque after cutoff, so the stack
  weathervaned. Separately, 25° was **commanded** not flown: T+2 FPA
  ~13° / ~20 m/s east — 7.5° gimbal + fins + FAR did not rotate onto
  the 25° program. Holding AP after cutoff cannot mint the missing
  east Δv.
- **Fix:** Keep AP `target_pitch=65` heading 90 **through burnout**
  (surface frame, `engaged=True`). Release when down/splashed, not at
  fuel=0. If the next hop still Shores at ~25 m/s east, that is Gus
  (gimbal / fins / a wheel), not another pitch number. Modules:
  `hop.py`, `blocks.md`.

## 2026-08-21T15-26-18Z-hop-to-water — Close is not a reload loop

- **When:** 2026-08-21 letsgrok `python main.py hop-to-water`
  (`2026-08-21T15-26-18Z-hop-to-water`). East Valiant, pitch 25° east,
  lithobrake flying recoverable=no. Os: after crash recover, KSP
  reload-looped (scene switch).
- **Symptom:** crash UI then `go_space_center` / `load_space_center`
  every 0.3 s for the Close poll. Looks like recover → reload → reload.
- **Cause:** `go_space_center` called `_close_to_ksc` (scene setter +
  `load_space_center`) **inside** the wait loop. `_leave_crash_ui` then
  called `load_space_center` again.
- **Fix:** Close **once**, then poll `ksc_ready`. No second
  `load_space_center` after dismiss. Modules: `hangar.py`, `hop.py`.

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

## 2026-08-21T11-52-45Z-hop — Dead GUID is not leftover

- **When:** 2026-08-21 letsgrok `python main.py phase hop`
  (`2026-08-21T11-52-45Z-hop` then leftover). Card FlyingLow geiger on
  `kerbalism-geigercounter`. F-013 unlocked, on craft. Tracking night,
  search no vessels, KSC empty, sci 6.1.
- **Symptom:** exit 1, `ValueError: No such vessel fbacb1ed-…`.
  `_find_hop_vessel`. Disk desk still `hangar recover
  kspstuff-hop-flea-pbc Debris sit=FLYING`.
- **Cause:** `_active_vessel` returned a kRPC proxy for a GUID Tracking
  no longer has. `_is_hop_craft` did `getattr` `.name` outside the
  except. Disk leftover is not live.
- **Fix:** Dead GUID is no leftover — scan `space_center.vessels`.
  Empty Tracking Hangars. `.name` on a dead proxy returns empty, not
  a raise. Modules: `hop.py`.

## 2026-08-21T12-04-13Z-hop — Catastrophic never lands

- **When:** 2026-08-21 letsgrok `python main.py hop`
  (`2026-08-21T12-04-13Z-hop`). Hangar `kspstuff-hop-flea-pbc`. Card
  FlyingLow geiger on `kerbalism-geigercounter`. F-013 unlocked, on
  craft. FAR+RealHeat+RealChute; chute locked. Os Flight Results PNG:
  Outcome Catastrophic Failure, no Recover (Revert / Tracking / Space
  Center / Close). Liftoff 00:00:00, collisions 00:01:07, highest alt
  3149 m, MET 1m 7s. Never revert.
- **Symptom:** Parent uplinked abort. Jeb waited ~250 s on `hop wait
  landed recoverable=yes` while 1 Hz jsonl was already the wreck: MET
  stuck 67.62, alt 74.03, q=0, speed=0, fuel=0, situation=flying,
  wreck=false, UT ticking. `recover()` spam `sit=flying recoverable=no`.
  exit 2, sci unchanged 6.0524.
- **Cause:** Frozen + flying + q=0 set litho/down, then `if frozen and
  sit in _AIR: wait landed` + `run_physics`. Catastrophic Failure never
  becomes landed. Telem `wreck=false` on that sit is a lie.
- **Fix:** That fingerprint is crash UI now. Log one line (sit +
  recoverable + met + alt + q). `recover()` if recoverable; else
  `go_space_center` (Close / Space Center, not revert) and abort `not
  recoverable`. Do not wait the 600 s wall. Telem marks wreck on
  MET-still + q=0 + low flying. Modules: `hop.py`, `telem.py`.

## 2026-08-21T12-30-03Z-hop — unmatched Flea; FlyingHigh lid

- **When:** 2026-08-21 letsgrok `python main.py hop`
  (`2026-08-21T12-30-03Z-hop`). Gene `need_stack: hop-flyinghigh`.
  Seated `kspstuff-hop-valiant-pbc`. Bound FlyingHigh thermo 138 s +
  TELEMETRY 30 s. F-013 2HOT start unlocked on craft. leftover
  PRELAUNCH `kspstuff-hop-flea-pbc`.
- **Symptom:** exit 2 `ABORT not recoverable`. hop entered leftover
  Flea, lit it, FAR apo 7.7 km, lithobrake MET 65.7 alt 74.6 q=0
  recoverable=no. sci 6.35 (+0). `hop_apo` 18 km clamp + OffPlan 50 km
  would cut a Valiant FlyingHigh loft to FlyingLow crumbs.
- **Cause:** leftover match used seated name only after Valiant; CLI
  hop still Hangared/entered the Flea. OffPlan lid was FlyingLow 50 km.
  `hop_apo` clamped 8–18 km so Gene 80 km could not cut.
- **Fix:** Unmatched leftover recovers without lighting, then Hangars
  the seated craft. FlyingHigh card: `hop_apo` unclamps to Space
  (140 km); OffPlan apo > atmosphere_depth, not 50 km. FlyingLow
  clamp 8–18 km stays. Modules: `hop.py`.

## 2026-08-21T13-08-57Z-hop — Valiant 2×T100 is not FlyingHigh

- **When:** 2026-08-21 letsgrok `python main.py hop`
  (`2026-08-21T13-08-57Z-hop`). Seated `kspstuff-hop-valiant-pbc`. Bound
  FlyingHigh thermo 138 s + TELEMETRY 30 s. F-013 2HOT start unlocked
  on craft; TELEMETRY Stayputnik PAW. leftover unmatched Flea recovered
  without lighting, then Hangar Valiant. `hop_apo` 80 km.
- **Symptom:** exit 2 `ABORT not recoverable`. T100 burnout MET~27
  alt~7 km, apo max 12335 m then ~7.6 km; never ≥50 km. Throttle 1
  until dry (Kerosene 450 → 0). Card started T+1 FlyingLow. EC 310→0,
  crash UI sit=flying recoverable=no met=158.86 alt=39.6 q=0. sci 6.35
  unchanged. leftover now PRELAUNCH Valiant.
- **Cause:** tanks/Δv, not sequencing. Gus 2×FL-T100 + Valiant ~1.55
  km/s SL cannot loft RSS FlyingHigh. hop already unclamped the 80 km
  cut and 140 km Space OffPlan; the motor emptied below the lid.
- **Fix:** none in `hop.py` — do not fake FlyingHigh. Gene: `need_builder`
  more tank/motor before another FlyingHigh hop. Modules: none.

## 2026-08-21T13-31-03Z-hop — FlyingHigh Toggle only ≥50 km

- **When:** 2026-08-21 letsgrok `python main.py hop`
  (`2026-08-21T13-31-03Z-hop`). Seated `kspstuff-hop-valiant-t7-pbc`.
  Bound FlyingHigh thermo 138 s + TELEMETRY 30 s. F-013 2HOT start
  unlocked on craft; TELEMETRY Stayputnik PAW. leftover unmatched
  2×T100 recovered without lighting, Hangar t7. `hop_apo` 80 km.
- **Symptom:** exit 0 splash recover. apo max 88.8 km. FlyingHigh lid
  MET~98 alt 50.4 km. Card `science start temperatureScan,kerbalism_TELEMETRY`
  at T+1 alt ~100 m FlyingLow. sit=splashed recoverable=yes MET 440
  EC 0. sci 6.35 (+0). leftover PRELAUNCH t7.
- **Cause:** hop started the bound card on first airborne, not at the
  50 km FlyingHigh lid. Kerbalism filed FlyingLow crumbs. A second
  Toggle at the lid would stop Kerbalism (one Toggle per id).
- **Fix:** FlyingHigh waits alt ≥50 km before Toggle. Log
  `science wait FlyingHigh`. Down below the lid after lighting aborts
  `no science (FlyingHigh lid)` — do not bank FlyingLow. Modules:
  `hop.py`.

## 2026-08-21T13-58-18Z-hop — Frozen landed recoverable=no is crash UI

- **When:** 2026-08-21 letsgrok `python main.py hop`
  (`2026-08-21T13-58-18Z-hop`). Seated `kspstuff-hop-valiant-t7-pbc`.
  Bound FlyingHigh thermo + TELEMETRY. F-013 2HOT start unlocked on
  craft. `hop_apo` 80 km. hangar none after wreck; KSC empty. Do not
  Hangar this leftover.
- **Symptom:** exit 2 `ABORT not recoverable`. Lid Toggle ok ~T+98 alt
  ≥50 km, apo max 90.1 km, sci +1.30 (9.66 → 10.96). Down: last flying
  alt 161 m q=32.7k then `sit=landed` alt=33 m MET frozen 407.5 q=0
  EC=0 `recoverable=no`. Stuck PNG: Vessel is destroyed, Shores Landed
  32 m, no Recover. `hop recover sit=landed recoverable=no` then
  unpause-spam, paused wreck, finish wreck, abort. Isolation none.
- **Cause:** Crash UI only matched frozen flying q=0 low (12-04-13Z
  never lands). This wreck reported `landed`. `_force_recover` called
  `recover()` on ground even when `recoverable=no`; frozen-MET then
  `run_physics` instead of Close. Unpause does not grow a Recover
  button on a destroyed vessel.
- **Fix:** Frozen MET + `sit=landed` + `recoverable=no` is crash UI
  now: log sit/recoverable/met/alt/q, `go_space_center` (Close / Space
  Center, not revert), abort `not recoverable`. Do not unpause-spam.
  `recover()` only when `recoverable`. Living land stays
  `recoverable=yes`. Modules: `hop.py`.

## hop-to-water — Valiant pitches 7.5° east, waits splash

- **When:** 2026-08-21 Gene `need_stack` after Gus signed
  `kspstuff-hop-valiant-east-pbc` (Valiant gimbal 7.5°, 2×FL-T100).
  Linus Water shorts. Flea hop-to-water was refused (18-32 Shores).
- **Symptom:** `python main.py hop-to-water` aborted before Hangar.
  Vertical hop recover-on-down banks Shores or an empty KSC. Splash
  never sees `splashed`.
- **Cause:** Stayputnik + Flea cannot steer. Gus now has gimbal during
  the burn; Stayputnik still has no torque after cutoff. Hop recovers
  on first flying recoverable — that kills a Water dwell.
- **Fix:** Valiant `hop-to-water` Hangars the seated craft, AP
  `target_pitch=82.5` heading 90 while burning, flying card airborne,
  no recover until `sit=splashed`, then splash dwell + HD. Landed
  aborts `not splashed`. Flea still refused, no Hangar. Modules:
  `hop.py`, `splash.py`, `blocks.md`.

## 2026-08-21T14-33-29Z-hop-to-water — 7.5° east is still Shores

- **When:** 2026-08-21 letsgrok `python main.py hop-to-water`
  (`2026-08-21T14-33-29Z-hop-to-water`). Hangar
  `kspstuff-hop-valiant-east-pbc`. F-013 2HOT start unlocked on craft.
  Card thermo + TELEMETRY. Do not Hangar this leftover PRELAUNCH
  east-pbc.
- **Symptom:** exit 2 `ABORT not recoverable`. Pitch 7.5° east logged.
  Burnout MET~26 fuel=0 apo max **12.1 km** (vertical 13-08-57Z was
  12.3 km). Never `sit=splashed`. Crash UI flying recoverable=no
  met=154.50 alt=74.5 q=0. Sci +0. Stills: biome **Shores** T+1 through
  T+124, horiz ~7 m/s then ~34–44 m/s, water on the horizon.
- **Cause:** AP `target_pitch=82.5` held gimbal **range** as the hop
  angle. 7.5° from vertical does not clear Cape Shores to Water on this
  2×T100 hang (FAR eats the east). Gimbal 7.5° is authority, not the
  flight path.
- **Fix:** Pitch **25°** from vertical (`target_pitch=65`, heading 90)
  during the one burn. Still release AP at cutoff. Flea still refused.
  Modules: `hop.py`, `blocks.md`.

## 2026-08-21T14-45-33Z-hop-to-water — pad landed is not Shores

- **When:** 2026-08-21 letsgrok `python main.py hop-to-water`
  (`2026-08-21T14-45-33Z-hop-to-water`). Matching leftover
  `kspstuff-hop-valiant-east-pbc` entered Flight. F-013 2HOT start
  unlocked on craft. Sci 10.96 unchanged. Do not Hangar.
- **Symptom:** exit 2 `ABORT not splashed` at MET 0.6. Light logged;
  pitch 25° never ran. Two jsonl samples: pre_launch then `sit=landed`
  alt=97 throttle=1 thrust=89k q=461. Still: 37.5 m terrain, vs=49.2
  m/s, HDG 357, engine on, Shores. KSP still Landed on pad hop-off.
- **Cause:** `wait_water` aborted `landed_dry` before `left_pad`.
  `_down(flown)` already ignores pad landed; the Shores gate did not.
  Abort sat above `_light` / `_steer_east` on the next pulse.
- **Fix:** Abort landed only after `left_pad` (airborne), same as
  `_down`. Pad sit=landed after light keeps burning and pitches east.
  Shores lithobrake after flight still aborts `not splashed`. Modules:
  `hop.py`, `blocks.md`.

## 2026-08-21T14-52-25Z-hop-to-water — leftover wreck is not a light

- **When:** 2026-08-21 letsgrok `python main.py hop-to-water`
  (`2026-08-21T14-52-25Z-hop-to-water`). Matching leftover
  `kspstuff-hop-valiant-east-pbc`. F-013 2HOT start unlocked on craft.
  Desk hangar PRELAUNCH was a lie. Bank 10.96 unchanged. Do not Hangar.
- **Symptom:** exit 2 `ABORT not recoverable`. Live leftover already
  flying MET frozen 13.8 fuel=0 thrust=0 EC=9.3 speed=0 q=0. Hop
  logged airborne and started thermo+TELEMETRY on the wreck. Crash UI
  Catastrophic Failure T+13 pad collision. `go_space_center` logged
  dismissed; Flight Results still up; tracking empty.
- **Cause:** matching leftover enters Flight and treats flying as an
  already-lit hop. Disk PRELAUNCH skipped the wreck gate. Fuel=0 +
  q=0 + speed=0 is crash UI, not a pad to light.
- **Fix:** Gate live sit/fuel/recoverable **before** light. Dry wreck
  leftover recovers if `recoverable`, else Close (`go_space_center` +
  `load_space_center`) and abort `not recoverable` — no Toggle. Pad
  leftover with fuel still lights. Modules: `hop.py`, `blocks.md`.

## 2026-08-21T14-52-25Z-hop-to-water — Flight Results is not KSC

- **When:** 2026-08-21 letsgrok `python main.py hop-to-water`
  (`2026-08-21T14-52-25Z-hop-to-water`). Gene
  `need_stack: hangar-flight-results`. F-013 2HOT start unlocked on
  craft. Bank 10.96 unchanged. Do not Hangar. Do not re-fly. Isolation
  none.
- **Symptom:** `go_space_center` logged dismissed. Stuck still
  `screenshots/stuck-flight-results.png`: Catastrophic Flight Results
  still modal over Tracking, no vessels, Revert / Space Center / Close
  live. Empty Tracking is not KSC. Os will not click. Never revert.
- **Cause:** kRPC `game_scene` can already read `space_center` while
  Flight Results sits on Tracking. Hangar treated that as KSC and
  would `launch_vessel` over the modal.
- **Fix:** `go_space_center` Closes (scene setter + `load_space_center`)
  until scene is KSC **and** `can_revert_to_launch` is false. Tracking
  is not KSC. Hangar raises `Hangar waits` and does not `launch_vessel`
  until then. Never `revert_to_launch`. Modules: `hangar.py`,
  `hop.py`, `blocks.md`.

## 2026-08-23T06-32-23Z-hop — launch_vessel hang poisons Session

- **When:** 2026-08-23 letsgrok `python main.py hop`
  (`2026-08-23T06-32-23Z-hop`). Lock live, jsonl events=`start`
  samples=0. Still: KSC overview, kRPC green, UT 3 Jan 1951 17:36,
  warp 1.5, no Flight Results. `ship.md` as_of 00:13Z sit=landed
  ec=0 — previous hop. Do not Hangar. Do not take the stick.
- **Symptom:** hop pid `launch_vessel` thread in `select` 4+ min
  past the 25 s watchdog. KSP.log pre-flight **PASS / Go for Launch**
  then `NullReferenceException` (SaveGame / StartWithNewLaunch).
  Scene stayed KSC. Tape never sampled.
- **Cause:** L-022 NRE did not raise on the Python client. In-flight
  `launch_vessel` holds the Session RPC lock. Watchdog abort (second
  client) cannot unblock it. Hangar then `go_space_center` on the
  same Session — deadlock. `ship.md` is Telem-only, so radio stayed
  the last hop.
- **Fix:** `_launch_watched` raises on hang (no 20 s join). Abort
  client connect is itself timed. Hangar does not retry RPCs on a
  poisoned Session. `publish_hangar_radio` writes sit=ksc; `python
  main.py ship` prints `stale: yes` when as_of predates lock.
  Modules: `hangar.py`, `flightlog.py`.

## 2026-08-23T06-44-54Z-hop — abort-to-KSC killed a live Flight load

- **When:** 2026-08-23 letsgrok `python main.py hop`
  (`2026-08-23T06-44-54Z-hop`) after T-116 and Hank leftover clean
  (`ksc_ready` true, vessels n=0). Do not Hangar. Do not take the stick.
- **Symptom:** jsonl `start,hangar` samples=0. Radio sit=ksc flags=preflight.
  Still KSC, warp 1.5, no Flight Results. Clock moved (17:38 vs 17:36).
- **Cause:** Pre-flight PASS, `Launching vessel from LaunchPad`, kRPC
  scene **Flight** at 08:45:04 (Kopernicus/Parallax load). T-116 25 s
  watchdog treated the still-open RPC as a pre-flight dialog and set
  `game_scene=space_center` at 08:45:31 — yanking a live launch back
  to KSC. Hop Session then `close()` blocked on that RPC until ~08:49.
- **Fix:** `launch_vessel` on a **side** client so the hop Session can
  poll scene. Scene `flight` waits (90 s grace) — do not abort to KSC.
  KSC-only stall still aborts. `Session.close` abandons a hung conn
  after 5 s. Modules: `hangar.py`, `session.py`.

## 2026-08-23T07-06-08Z-hop — broken is not shear

- **When:** 2026-08-23 letsgrok hops `2026-08-23T06-53-50Z-hop` and
  `2026-08-23T07-06-08Z-hop`. Tank+engine leave after burnout (q +
  attitude); OKTO+chute remain. Do not Hangar. Do not retune hop.py
  (Lars T-140).
- **Symptom:** landing skim `broken=none` wreck=no, ship.md flags
  `ec=0,empty tanks` sit=flying — same as a living coast. Jsonl
  already had mass 1677→270 / 1284→271 at stage 1.
- **Cause:** `reliability_broken` walks Kerbalism `broken`/`malfunction`
  module flags. Exploded/decoupled parts are not that. Mass lived on
  state rows but not ship, `_kin`, or the tape skim line.
- **Fix:** Log `parts_n`, `root`, `debris_n`. `stack_shear` (parts drop
  or mass remaining ≤50% beyond fuel, stage unchanged) → `kind=shear`
  + flag. Tape `stack: mass=… parts=… shear=yes`. ship.md mass/parts_n.
  Modules: `telem.py`, `tape.py`, `flightlog.py`.

## leftover-ksc — walk home, never a named reload

- **When:** 2026-08-23 letsgrok T-142. Os disabled Allow reverting
  flights. Live sit: KSC, `ksc_ready` true, `can_revert` false,
  vessels n=0. Do not Hangar. Do not recover Ast. XRL-564.
- **Symptom:** `--space-center` / `go_ksc` saved `leftover-ksc` then
  `load` to drop Flight Results. That is a reload.
- **Cause:** Overlay dismiss overfit KSP quirks (`can_revert` + named
  sfs). kRPC 0.6 UI does not expose Flight Results Close
  (`stock_canvas` children empty; `UI.clear` is client widgets).
- **Fix:** `walk_home`: recover leftover ships (enter Flight,
  `recover()`, wait gone), Close `game_scene=space_center` with
  `reload_save=False`. No `load_space_center`. `ksc_ready` is KSC +
  leftover ships n=0 + overlay not painted (`can_revert` is one bit,
  not the only). `load leftover-ksc` refused. Modules: `hangar.py`,
  `recover_probe.py`.

## 2026-08-23T07-50-48Z-hop — leftover can_revert is not overlay

- **When:** 2026-08-23 letsgrok hop `2026-08-23T07-50-48Z-hop` then
  Hank `recover-probe --space-center` (walk-home leftover n=1,
  Close `reload_save=False`). Still:
  `screenshots/stuck-flight-results-0750.png` — KSC overview, Tracking
  "no vessels", no Flight Results, no revert dialog. Do not Hangar.
  Never revert. Never leftover-ksc.
- **Symptom:** ships n=0, scene `space_center`, `ksc_ready` false
  (`flight results overlay`), `can_revert` / `can_revert_to_launch`
  true, active vessel UUID dead.
- **Cause:** `overlay_painted` was `_can_revert`. Os disabled
  Allow reverting flights; that leftover bit still reads true on a
  clean Space Center after recover. T-088 treated n=0 +
  `can_revert` as Revert painted; 07-50 is the same bits without a
  dialog.
- **Fix:** `overlay_painted` is false when scene is Space Center and
  leftover ships n=0. `ksc_ready` is KSC + leftover ships n=0.
  Disk sit: `ksc_ready` true wins over leftover `can_revert`. Close
  stays `game_scene` only. Modules: `hangar.py`, `ops.py`.
