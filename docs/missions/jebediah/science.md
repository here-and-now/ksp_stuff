# jebediah science card

science: card
flight: jebediah
craft: kspstuff-hop-valiant-east-pbc
at: hop
body: Earth
need_builder: no
recover_banks: yes
notes: Gus capable yes. Bind **FlyingLow@Water shorts** on
  **kspstuff-hop-valiant-east-pbc** (2× FL-T100 + Valiant gimbal east).
  Do **not** re-bind spent Shores FlyingHigh. Do not Hangar. 13-08-57Z
  same motor apo **12.3 km** — FlyingLow/splash, not ≥50 km. Tape **1.0**.
  TELEMETRY **0.75 MB** — do **not** co-run geiger. Skip leftover
  FlyingLow geiger **0.32** (crumbs). Skip goo **641 s**. Do not
  transmit. F-013: Geiger is `kerbalism-geigercounter` (on craft, **not
  bound**). TELEMETRY is Stayputnik PAW (no Science part) — not a Geiger.
  Cape is Shores; file **Water**, not T+1 Shores (FlyingLow Shores
  thermo+TELEMETRY capped). Pair **2.10+1.40=3.50** if finished over
  Water — **0.54 short** of ~4.04. Splash TELEMETRY **0.80** is the close
  if the core lives — same `experiment_id`, not a second dashed bind.

## FlyingLow
- experiment_id: temperatureScan
  situation: FlyingLow
  part: sensorThermometer
  instrument: sensorThermometer (2HOT Thermometer); tech start; unlocked yes; on_craft yes
  duration_s: 138
  ec_rate: 0.002
  recover_banks: yes
  est: 2.10 FlyingLow@Water if finished; catalog 138 s is not a hang expect

- experiment_id: kerbalism_TELEMETRY
  situation: FlyingLow
  part: probeCoreSphere_v2
  instrument: hosted PAW (no Science-category part); tech start; unlocked yes; on_craft yes
  duration_s: 30
  ec_rate: 0.052
  recover_banks: yes
  est: 1.40 FlyingLow@Water if finished

# skip kerbalism_TELEMETRY FlyingHigh@Water 30 s / 1.80 — 2×T100 does not loft ≥50 km; Shores FlyingHigh spent
# skip kerbalism_TELEMETRY SrfSplashed@Water 30 s / 0.80 — same experiment_id; tape 0.75; close if core lives
# skip temperatureScan Surface@Water 138 s / 0.90 — same experiment_id; splash is not Surface
# skip geigerCounter 497 s / tape vs TELEMETRY / leftover FlyingLow 0.316 crumbs
# skip mysteryGoo FlyingLow/SrfSplashed 641 s / 0.18 (hang wall)
# spent Shores FlyingHigh thermo (global 2.70) + TELEMETRY@Shores 1.80
# spent Cape Surface geiger / landed TELEMETRY / landed goo / Shores thermo / FlyingLow Shores TELEMETRY+thermo
