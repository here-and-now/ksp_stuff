# jebediah science dump (tickets)

science: tickets
flight: jebediah
craft: kspstuff-hop-valiant-t7-wheel-pbc
recover_banks: yes
notes: dump of bound tickets + fly `science_ids`. Retired splash hang is not live.
  fly: T-081 cli=python main.py hop
  science_ids: barometerScan,geigerCounter,mysteryGoo

## Flying

- experiment: barometerScan
  situation: FlyingHigh
  experiment_id: barometerScan
  part: sensorBarometer
  duration_s: 305
  ec_rate: 0.05
  recover_banks: yes
  ticket: T-404
- experiment: barometerScan
  situation: FlyingLow
  experiment_id: barometerScan
  part: sensorBarometer
  duration_s: 305
  ec_rate: 0.05
  recover_banks: yes
  ticket: T-460
- experiment: barometerScan
  situation: SrfSplashed@Shores
  experiment_id: barometerScan
  part: sensorBarometer
  duration_s: 305
  ec_rate: 0.05
  recover_banks: yes
  ticket: T-461
