# jebediah science card

science: card
flight: jebediah
craft: kspstuff-hop-flea-pbc
at: hop
body: Earth
need_builder: no
notes: Kerbalism Experiment on Gus-signed kspstuff-hop-flea-pbc. Recover the HD.
  Do not transmit. Not the 1235Z Cape landed goo+thermo card (spent, F-005).
  Uncrewed. No Mk1. No chute. hop_apo 15 km (FlyingLow < 50 km).
  HD: Stayputnik 0.5 + Engineer7500 0.5 = 1.0 MB data. TELEMETRY is 0.75 MB —
  needs the tape. Do not co-run geiger (1.25 MB). TELEMETRY 0.75 + thermo 0.45
  = 1.20 MB; both will not file on this HD. Thermo is best-effort (Gene: if it
  finishes). Goo is splash dwell (east Water), private sample, 1 slot. Do not
  start goo airborne — that spends the sample on incomplete FlyingLow (641 s
  will not finish on this hang). Helm hop starts every `- experiment:` line
  once airborne and recovers on first recoverable; splash dwell is Gene/Lars.

recover_banks: yes

## Flying (helm starts airborne)

- experiment: kerbalism_TELEMETRY
  experiment_id: kerbalism_TELEMETRY
  part: probeCoreSphere_v2
  situation: FlyingLow
  at: Shores
  duration_s: 30
  ec_rate: 0.052
- experiment: temperatureScan
  experiment_id: temperatureScan
  part: sensorThermometer
  situation: FlyingLow
  at: Shores
  duration_s: 138
  ec_rate: 0.002

## Splash (water bank if the probe lives; not a hop start)

- experiment_id: mysteryGoo
  part: GooExperiment
  situation: SrfSplashed
  at: Water
  duration_s: 641
  ec_rate: 0.18
