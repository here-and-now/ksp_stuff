# Briefing — Gene → jebediah

Earth. PBC. Living hop. Never revert. go: yes. campaign: none.

sci **6.35** (12-30-03Z abort **+0**; 12-22-36Z abort **+0**; 12-04-13Z
abort **+0.30** geiger in-flight). Tree start + e101 + basicRocketry.
Need **~8.65** for survivability. leftover **PRELAUNCH**
`kspstuff-hop-flea-pbc`. hangar: **phase** that vessel. Unmatched
leftover **recovers without lighting**, then Hangars seated
**`kspstuff-hop-valiant-pbc`**. Do **not** fly the Flea. Do **not**
Hangar from this desk. Gus `capable: yes`. No chute. Do not Hangar
`kspstuff-geiger-pbc` or `kspstuff-hop-hammer-far-pbc`. Do not pad.
Do not transmit. Never rails. Never WarpTo. If unmatched leftover
is not recoverable: abort — do not Hangar over it.

f013: `temperatureScan` instrument **sensorThermometer** (2HOT
Thermometer), tech **start**, unlocked **yes**, on_craft **yes**, host
none. `kerbalism_TELEMETRY` hosted PAW on **probeCoreSphere_v2**,
on_craft **yes** (no Science-category part). Geiger
`kerbalism-geigercounter` is on the stack, **not bound**. Never
Stayputnik-as-Geiger.

Linus (bound FlyingHigh shorts — loft ≥50 km):
- `temperatureScan` FlyingHigh, part `sensorThermometer`,
  **duration_s 138 / ec_rate 0.002**, recover_banks **yes**. est **2.70**
  if finished. Catalog 138 s is **not** a hang expect.
- `kerbalism_TELEMETRY` FlyingHigh@Shores, part `probeCoreSphere_v2`,
  **duration_s 30 / ec_rate 0.052**, recover_banks **yes**. est **1.80**
  if finished. Tape **1.0**. Do **not** co-run geiger.
- Skip `geigerCounter` FlyingHigh **497 s / 0.005**. Skip leftover
  FlyingLow geiger **0.32**. Skip thermo FlyingLow Shores **0.045**.
  Skip goo **641 s**. FlyingLow TELEMETRY Shores **capped**. Cape
  Surface geiger **capped**. Landed TELEMETRY **capped**. Do not re-pad
  Cape. `recovery@EarthFlew` leftover **gone**. Water splash+FlyingLow
  ~9.1 east pitch — **not this card**.

hop_apo **80 km** is the Valiant cut (real throttle). OffPlan apo >
**140 km** Space. FlyingLow 8–18 km clamp does **not** apply. File
FlyingHigh only ≥50 km. Ballistic peri is negative — not OFFPLAN.

Crash UI (12-30-03Z same as 12-22-36Z): frozen MET + flying + q=0 +
~74 m is Catastrophic Failure — never `sit=landed`. One log line
(sit/recoverable/met/alt/q). `recover()` if recoverable. Else Space
Center / Close (not revert) and abort. Do **not** wait 600 s landed.
Do **not** unpause-spam recover after that fingerprint when
recoverable=no. Living recover: wait **sit=landed** in Flight, then
`recover()` when `recoverable=yes` **before** dismiss. Low flying
**≤250 m**: `recover()` only if recoverable. Flight Results dismiss is
not the bank. EC=0 with HD data recovers.

Ast. XRL-564 is horizon. Do not recover the rock.

emergencies: hold, cut, no_warp, stage, recover, science, abort_pad
