# Briefing — Gene → jebediah

Earth. PBC. Living hop. Never revert. go: wait.

sci **5.33** (11-40-22Z **+0.54**, recover landed before dismiss).
Tree start + e101 + basicRocketry. KSC empty. hangar: **none**. Gus
`capable: yes`. craft **kspstuff-hop-flea-pbc**. No chute. Next hop
Hangars that file. Do **not** `python main.py phase hop` (no leftover).
Do not Hangar `kspstuff-geiger-pbc`. Do not pad. Do not transmit.
Never rails. Never WarpTo.

f013: `geigerCounter` instrument **kerbalism-geigercounter** (Geiger
Counter), tech **engineering101**, unlocked **yes**, on_craft **yes**,
host none. Never Stayputnik PAW.

Linus (bound):
- `geigerCounter` FlyingLow, part `kerbalism-geigercounter`,
  **duration_s 497 / ec_rate 0.005**, recover_banks **yes**.
  Catalog 497 is **not** a hang expect. FAR Flea apo **7.7 km**
  (11-40-22Z lithobrake landed 76 m MET 67 EC 275). File while
  recording. Tape 0.5 vs Engineer7500 1.0. EC 2.5 vs ~275. Leftover
  **1.40 / 2.80**. Start again while aloft.
- Skip `temperatureScan` FlyingLow Shores leftover **0.045**.
- Skip `mysteryGoo` FlyingLow **641 s / 0.18**.
- FlyingLow TELEMETRY Shores **capped**. Cape Surface geiger **capped**.
  Landed TELEMETRY **capped**. Do not re-pad Cape.
- `recovery@EarthFlew` leftover **0.028** — crumbs. Skip as a goal.

Light the Flea. Start FlyingLow geiger on the **Geiger part** once
airborne. One Toggle per id. Empty tanks after the motor are expected.
hop_apo **18 km** is a cut wish (solids ignore it). OffPlan apo >
**50 km**, not the 18 km clamp. Ballistic peri is negative — not
OFFPLAN. Wait **sit=landed** in Flight, then `recover()` when
`recoverable=yes` **before** dismiss. Low flying **≤250 m**:
`recover()` only if recoverable. Do **not** `go_space_center` on
flying recoverable=no. Do not dismiss then bank a `pre_launch` sit.
Flight Results dismiss is not the bank. 1 Hz recover line names sit +
recoverable. EC=0 with HD data recovers.

Ast. XRL-564 is horizon. Do not recover the rock.

emergencies: hold, cut, no_warp, stage, recover, science, abort_pad
