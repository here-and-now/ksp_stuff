# Briefing — Gene → jebediah

Earth. PBC. Water sit. go: yes. campaign: uncrewed.

sci **10.96** (+0). Tree start + e101 + basicRocketry. Need **~4.04**
for survivability 15. hangar **none**. Tracking **no vessels**. Flight
Results may still be up (Catastrophic Failure T+13 pad collision) —
stuck still `screenshots/stuck-flight-results.png`. Hangar **Close-polls**
until scene is KSC **and** `can_revert_to_launch` is false. Do **not**
`launch_vessel` over the modal. Do **not** revert / VAB / rewind UT.
Os will not click. Do not Hangar from Gene. Gus `capable: yes`
**`kspstuff-hop-valiant-east-pbc`** (2× FL-T100 + Valiant gimbal
**7.5°** authority). Not t7. Not Flea. No chute. Do not pad. Do not
transmit. Never rails. Never WarpTo. Never revert.

f013: `temperatureScan` instrument **sensorThermometer** (2HOT
Thermometer), tech **start**, unlocked **yes**, on_craft **yes**, host
none. `kerbalism_TELEMETRY` hosted PAW on **probeCoreSphere_v2**,
on_craft **yes** (no Science-category part). Geiger
`kerbalism-geigercounter` is on the stack, **not bound**. Never
Stayputnik-as-Geiger.

Linus (bound FlyingLow@Water shorts — **not** spent Shores FlyingHigh):
- `temperatureScan` FlyingLow@Water, part `sensorThermometer`,
  **duration_s 138 / ec_rate 0.002**. est **2.10** if finished.
- `kerbalism_TELEMETRY` FlyingLow@Water, part `probeCoreSphere_v2`,
  **duration_s 30 / ec_rate 0.052**. est **1.40** if finished.
- Pair **3.50** — **0.54 short** of ~4.04. Splash TELEMETRY **0.80**
  is the close if the core lives (same `experiment_id`, not a second
  dashed bind). Tape **1.0**. Do **not** co-run geiger.
- Skip leftover FlyingLow geiger **0.32**. Skip goo **641 s**. Skip
  FlyingHigh@Water (2×T100 does not loft ≥50 km). Cape Surface geiger
  **capped**. FlyingHigh Shores shorts **spent**.

Helm: `python main.py hop-to-water`. Hangar **fresh**
`kspstuff-hop-valiant-east-pbc` after Close lands KSC. 14-52-25Z leftover
was flying MET 13.8 fuel=0 — disk PRELAUNCH is a lie. Gate
sit/fuel/recoverable before light. Dry wreck: recover if yes, else
Close, **no Toggle**. Pitch **25°** from vertical (`target_pitch=65`),
heading **90** (east) during the **one burn**. Gimbal 7.5° is not the
hop. Stayputnik has no torque after cutoff — do not coast-SAS. Start
the flying card once airborne. **Do not recover** while flying. Wait
**splashed**, then splash dwell + HD recover. Pad `sit=landed` after
light is hop-off — keep burning; abort landed only after **left_pad**.
Landed Shores after airborne is abort `not splashed`. Flea still
**refused**.

hop_apo **18 km** (FlyingLow clamp). **Not 80 km** — 13-08-57Z same
motor apo **12.3 km**. OffPlan apo > **50 km**. Ballistic peri is
negative — not OFFPLAN. Do not brief Space.

Crash UI: frozen MET + (flying **or landed**) + recoverable=no is
Catastrophic Failure. One log line (sit/recoverable/met/alt/q).
`recover()` only if recoverable. Else Space Center / Close (not revert)
until the window is KSC (`can_revert` false). Do **not** unpause-spam.
Living recover: wait sit=landed **or splashed**, then `recover()` when
recoverable=yes **before** dismiss.

Ast. XRL-564 is horizon. Do not recover the rock.

emergencies: hold, cut, no_warp, stage, recover, science, abort_pad
