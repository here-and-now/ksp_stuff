# Briefing — Gene → jebediah

Earth. PBC. Living hop. Never revert. go: yes.

sci **4.49** (11-09-13Z **+0** false recover). Tree start + e101 +
basicRocketry. KSC empty. hangar: none. Gus `capable: yes`. craft
**kspstuff-hop-flea-pbc**. No chute. Hangar that file (empty KSC).
Do not Hangar `kspstuff-geiger-pbc` (hop refuses pad/geiger names).
Do not pad. Do not transmit. Never rails. Never WarpTo.

f013: `geigerCounter` instrument **kerbalism-geigercounter** (Geiger
Counter), tech **engineering101**, unlocked **yes**, on_craft **yes**,
host none. Never Stayputnik PAW.

Linus (bound):
- `geigerCounter` FlyingLow, part `kerbalism-geigercounter`,
  **duration_s 497 / ec_rate 0.005**, recover_banks **yes**.
  Catalog 497 is **not** a hang expect. FAR Flea apo **7.5 km**
  (10-42-32Z living 199 m EC 306; 10-47-59Z / 11-09-13Z lithobrake
  75 m EC 9.9). File while recording. Tape 0.5 vs Engineer7500 1.0.
  EC 2.5 vs ~310. Leftover **2.10 / 2.80**. Start again while aloft.
- Skip `temperatureScan` FlyingLow Shores leftover **0.045**.
- Skip `mysteryGoo` FlyingLow **641 s / 0.18**.
- FlyingLow TELEMETRY Shores **capped**. Cape Surface geiger **capped**.
  Landed TELEMETRY **capped**. Do not re-pad Cape.
- `recovery@EarthFlew` leftover **0.17** — HD recover when down.

Light the Flea. Start FlyingLow geiger on the **Geiger part** once
airborne. One Toggle per id. Empty tanks after the motor are expected.
hop_apo **18 km** is a cut wish (solids ignore it). OffPlan apo >
**50 km**, not the 18 km clamp. Ballistic peri is negative — not
OFFPLAN. Flying **≤250 m** (or already down): `recover()` **while
still Flight**. Do not wait recoverable=yes. Do not dismiss then
bank a `pre_launch` sit. Flight Results dismiss is not the bank.
1 Hz recover line names sit + recoverable. EC=0 with HD data
recovers. Last 1 Hz still flying at KSC range is a recover, not a
wreck.

Ast. XRL-564 is horizon. Do not recover the rock.

emergencies: hold, cut, no_warp, stage, recover, science, abort_pad
