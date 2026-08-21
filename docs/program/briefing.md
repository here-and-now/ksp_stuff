# Briefing — Gene → jebediah

Earth. PBC. Water sit. go: yes. campaign: uncrewed.

sci **10.96** (+0). Tree start + e101 + basicRocketry. Need **~4.04**
for survivability 15. leftover **unmatched** `kspstuff-hop-valiant-east-bare-pbc`
(desk `hangar: phase … sit=PRELAUNCH`; last live was landed Shores 71 m
EC=0 crash UI) vs seated **`kspstuff-hop-valiant-east-one-pbc`**. hop
recovers leftover **without lighting**, then Hangars **east-one**. Do
**not** light east-bare. Do **not** light the finned hang. Disk
PRELAUNCH is a lie. Dry wreck: recover if yes, else Close, **no Toggle**.
Do **not** revert / VAB / rewind UT. Os will not click. Do not Hangar
from Gene. Gus `capable: yes` **`kspstuff-hop-valiant-east-one-pbc`**
(Stayputnik stack-only, radials on **upper FL-T100**, 2× FL-T100 +
Valiant **Boattail**, gimbal **7.5°**, **no fins**, no geiger part, no
stack decoupler). Not east-bare. Not east-pbc. Not t7. Not Flea. No
chute. Do not pad. Do not transmit. Never rails. Never WarpTo. Never
revert.

f013: `temperatureScan` instrument **sensorThermometer** (2HOT
Thermometer), tech **start**, unlocked **yes**, on_craft **yes**, host
none. `kerbalism_TELEMETRY` hosted PAW on **probeCoreSphere_v2**,
on_craft **yes** (no Science-category part). Geiger
`kerbalism-geigercounter` is **not** on this stack. Never
Stayputnik-as-Geiger.

Linus (bound FlyingLow@Water shorts on **east-one** — **not** spent
Shores FlyingHigh):
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

Helm: `python main.py hop-to-water`. Unmatched leftover — recover, do
not light, then Hangar seated. Light **vertical**. After **left_pad**,
slew **10°/s** to `target_pitch=65` heading **90** (east) at throttle
**0.4**. **Do not slam 65 at light** (16-11-58Z TWR 5 sheared east-bare,
apo 5.3 km, no decoupler). **Hold AP through burnout** (`engaged=True`).
Do not disengage at fuel=0. Release when down. Stayputnik has no torque
after cutoff. Start the flying card once airborne. **Do not recover**
while flying. Wait **splashed**, then splash dwell + HD recover. Pad
`sit=landed` after light is hop-off — keep burning; abort landed only
after **left_pad**. Landed Shores after airborne is abort `not splashed`.
Flea still **refused**. Do not light east-bare or the finned hang.

hop_apo **18 km** (FlyingLow clamp). **Not 80 km** — 13-08-57Z same
motor apo **12.3 km**; 15-50-45Z apo **10.3 km**; 16-11-58Z apo **5.3 km**
was a dump, not a loft. OffPlan apo > **50 km**. Ballistic peri is
negative — not OFFPLAN. Do not brief Space.

Crash UI: frozen MET + (flying **or landed**) + recoverable=no is
Catastrophic Failure. One log line (sit/recoverable/met/alt/q).
`recover()` only if recoverable. Else Space Center / Close (not revert)
until the window is KSC (`can_revert` false). Do **not** unpause-spam.
Living recover: wait sit=landed **or splashed**, then `recover()` when
recoverable=yes **before** dismiss.

Ast. XRL-564 is horizon. Do not recover the rock.

emergencies: hold, cut, no_warp, stage, recover, science, abort_pad
