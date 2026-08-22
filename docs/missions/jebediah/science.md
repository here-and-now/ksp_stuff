# jebediah science card

science: card
flight: jebediah
craft: kspstuff-hop-valiant-east-t3-pbc
at: splash
body: Earth
need_builder: no
recover_banks: yes
notes: Gus `capable: yes` **east-t3**. Not t7-splash. Bank **13.2632**
  need **~1.74**. Splash goo **2.40** closes **15**. Pair **3.20**
  overshoots. Sequential: splash TELEMETRY **first** (30 s), then goo
  **641 s**. Tape **1.0**. Do not transmit. Do not co-run geiger (not
  on hang). Do not Toggle TELEMETRY airborne (19-43 Forest FlyingHigh
  leftover **1.51** — 0.23 short, not this bind). Skip leftover
  FlyingLow geiger **0.32**. **Do not bind** FlyingLow@Water thermo or
  TELEMETRY until a hop-to-water jsonl holds heading **090**. 20×Z-100
  ~2050 EC.

## Splash
- experiment: kerbalism_TELEMETRY
  situation: SrfSplashed
  experiment_id: kerbalism_TELEMETRY
  part: probeCoreSphere_v2
  instrument: Stayputnik PAW (no Science part) — tech start — unlocked yes
  duration_s: 30
  ec_rate: 0.052
  recover_banks: yes
  est: 0.80
- experiment: mysteryGoo
  situation: SrfSplashed
  experiment_id: mysteryGoo
  part: GooExperiment
  instrument: Mystery Goo Containment Unit (GooExperiment) — tech start — unlocked yes
  duration_s: 641
  ec_rate: 0.18
  recover_banks: yes
  est: 2.40
