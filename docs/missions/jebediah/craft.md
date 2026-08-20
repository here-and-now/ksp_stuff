# jebediah stack

status: signed
craft: kspstuff-geiger-pbc
parts:
  - probeCoreSphere_v2
  - kerbalism-geigercounter
  - Engineer7500
  - batteryPack
  - batteryPack
  - batteryPack
  - SurfAntenna
  - GooExperiment
  - sensorThermometer
  - solidBooster_sm_v2
  - basicFin
  - basicFin
  - basicFin
hosted:
  - kerbalism_TELEMETRY on probeCoreSphere_v2 (Stayputnik PAW, no Science part, not locked) — bind this
  - geigerCounter on kerbalism-geigercounter (e101 UNLOCKED) — Cape Surface **spent**; do not bind
  - geigerCounter also PAW on Stayputnik — do not bind PAW (F-013)
  - temperatureScan on sensorThermometer — Shores landed capped
  - mysteryGoo on GooExperiment — F-005 spent
notes: File crafts/kspstuff-geiger-pbc.craft. Engineer7500 + Stayputnik.
  Flea istg=0. Landed TELEMETRY 29 s / 0.052 / 0.75 MB vs tape 1.0.
  EC 1.51 + command ~1.5 vs 310. Do not co-run geiger. Uncrewed. No Mk1.
