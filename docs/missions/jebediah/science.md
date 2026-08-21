# jebediah science card

science: card
flight: jebediah
craft: kspstuff-hop-valiant-pbc
at: hop
body: Earth
need_builder: no
recover_banks: yes
notes: Gus capable yes. Bind **FlyingHigh shorts** on Valiant, not 497 s
  complete, not spent Cape. hop_apo **18 km** is a real cut (FlyingLow).
  These file FlyingHigh **only if Gene lofts ≥50 km**. hop.py OffPlan lid
  **50 km** — dwell above that is Lars if Gene picks this. Tape **1.0**.
  TELEMETRY **0.75 MB** — do **not** co-run geiger. Skip leftover FlyingLow
  geiger **0.32** (crumbs, not a node). Skip thermo FlyingLow Shores **0.045**.
  Skip goo **641 s**. leftover PRELAUNCH flea is Gene hangar, not this card.
  Do not transmit. F-013: Geiger is `kerbalism-geigercounter` (on craft,
  not bound). TELEMETRY is Stayputnik PAW (no Science part) — not a Geiger.

## FlyingHigh
- experiment_id: temperatureScan
  situation: FlyingHigh
  part: sensorThermometer
  instrument: sensorThermometer (2HOT Thermometer); tech start; unlocked yes; on_craft yes
  duration_s: 138
  ec_rate: 0.002
  recover_banks: yes
  est: 2.70 if finished; catalog 138 s is not a hang expect

- experiment_id: kerbalism_TELEMETRY
  situation: FlyingHigh
  part: probeCoreSphere_v2
  instrument: hosted PAW (no Science-category part); tech start; unlocked yes; on_craft yes
  duration_s: 30
  ec_rate: 0.052
  recover_banks: yes
  est: 1.80 FlyingHigh@Shores if finished

# skip geigerCounter FlyingHigh 497 s / 0.005 / 3.60 — will not finish; tape vs TELEMETRY
# skip geigerCounter FlyingLow leftover 0.316 / 2.80 — crumbs, not a node
# skip temperatureScan FlyingLow@Shores leftover 0.045
# skip mysteryGoo FlyingLow/FlyingHigh 641 s / 0.18 (hang wall)
# skip kerbalism_TELEMETRY FlyingLow Shores — capped
# spent Cape Surface geigerCounter / landed TELEMETRY / landed goo / Shores thermo
# Water splash+FlyingLow ~9.1 if Gene pitches east — not this card
