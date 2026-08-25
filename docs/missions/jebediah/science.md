# jebediah science dump (tickets)

science: tickets
flight: jebediah
craft: kspstuff-hop-valiant-t7-wheel-pbc
recover_banks: yes
notes: dump of bound tickets + fly `science_ids`. Retired splash hang is not live.
  fly: T-081 cli=python main.py hop
  science_ids: barometerScan,geigerCounter,mysteryGoo

## Flying

- experiment: kerbalism_TELEMETRY
  situation: SrfSplashed@Water
  experiment_id: kerbalism_TELEMETRY
  part: probeCoreSphere_v2
  duration_s: 30
  ec_rate: 0.052
  recover_banks: yes
  ticket: T-028
- experiment: temperatureScan
  situation: SrfSplashed@Water
  experiment_id: temperatureScan
  part: sensorThermometer
  duration_s: 138
  ec_rate: 0.002
  recover_banks: yes
  ticket: T-422
- experiment: barometerScan
  situation: SrfSplashed@Water
  experiment_id: barometerScan
  part: sensorBarometer
  duration_s: 305
  ec_rate: 0.05
  recover_banks: yes
  ticket: T-423
