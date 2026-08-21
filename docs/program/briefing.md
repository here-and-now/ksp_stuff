# Briefing — Gene → jebediah

Earth. PBC. Living hop. Never revert. go: yes. campaign: none.

sci **6.35** (12-22-36Z abort **+0**; 12-04-13Z abort **+0.30**
geiger in-flight; 11-52-45Z **+0.40** recover landed). Tree start +
e101 + basicRocketry. leftover **PRELAUNCH** `kspstuff-hop-flea-pbc`.
hangar: **phase** that vessel. Gus `capable: yes`. craft
**kspstuff-hop-flea-pbc**. No chute. Do **not** Hangar. Do **not**
`python main.py hop`. Do not Hangar `kspstuff-geiger-pbc` or
`kspstuff-hop-hammer-far-pbc`. Do not pad. Do not transmit. Never
rails. Never WarpTo.

f013: `geigerCounter` instrument **kerbalism-geigercounter** (Geiger
Counter), tech **engineering101**, unlocked **yes**, on_craft **yes**,
host none. Never Stayputnik PAW.

Linus (bound):
- `geigerCounter` FlyingLow, part `kerbalism-geigercounter`,
  **duration_s 497 / ec_rate 0.005**, recover_banks **yes**.
  Catalog 497 is **not** a hang expect. FAR Flea apo **7.4 km**
  (12-22-36Z MET 65.4 lithobrake crash UI alt 74.1; 12-04-13Z MET
  67.6; Os still peak 3149 m). File while recording. Tape 0.5 vs
  Engineer7500 1.0. EC 2.5 vs ~310. Leftover **0.32 / 2.80**. Start
  again while aloft.
- Skip `temperatureScan` FlyingLow Shores leftover **0.045**.
- Skip `mysteryGoo` FlyingLow **641 s / 0.18**.
- FlyingLow TELEMETRY Shores **capped**. Cape Surface geiger **capped**.
  Landed TELEMETRY **capped**. Do not re-pad Cape.
- `recovery@EarthFlew` leftover **gone**. Not a goal.

Enter Flight on the leftover. Light the Flea. Start FlyingLow geiger
on the **Geiger part** once airborne. One Toggle per id. Empty tanks
after the motor are expected. hop_apo **18 km** is a cut wish (solids
ignore it). OffPlan apo > **50 km**, not the 18 km clamp. Ballistic
peri is negative — not OFFPLAN.

Crash UI (12-22-36Z detect-now): frozen MET + flying + q=0 + ~74 m
is Catastrophic Failure — never `sit=landed`. One log line
(sit/recoverable/met/alt/q). `recover()` if recoverable. Else Space
Center / Close (not revert) and abort. Do **not** wait 600 s landed.
Do **not** unpause-spam recover after that fingerprint when
recoverable=no. Do **not** `go_space_center` on flying
recoverable=no until that fingerprint. Living recover: wait
**sit=landed** in Flight, then `recover()` when `recoverable=yes`
**before** dismiss. Low flying **≤250 m**: `recover()` only if
recoverable. Do not dismiss then bank a `pre_launch` sit. Flight
Results dismiss is not the bank. 1 Hz recover line names sit +
recoverable. EC=0 with HD data recovers.

Ast. XRL-564 is horizon. Do not recover the rock.

emergencies: hold, cut, no_warp, stage, recover, science, abort_pad
