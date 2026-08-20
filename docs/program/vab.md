# VAB board — hardware vs Gene's draft

capable: yes
craft: kspstuff-hop-flea-pbc
notes: PBC hop, not pad. File `crafts/kspstuff-hop-flea-pbc.craft`.
  Stayputnik + Engineer7500 (HD 0.5+0.5 MB) + 3×Z-100 (300 EC) + Stayputnik 10
  + 16-S + 2HOT + Goo + 3× basicFin + RT-5 Flea (`solidBooster_sm_v2`).
  No Mk1, no chute, no procedural SRB. Uncrewed. Not archived hop-flea
  (Mk1+Mk16). Do not Hangar `kspstuff-pad-pbc`.
  Wet ~1.66 t (Flea 1.50 + payload 0.16). Flea 192 kN, Isp 140/165, SF 1.05 t,
  burn ~7.5 s, TWR_SL ~12, Δv ~1.38 km/s SL / 1.63 vac. hop_apo 15 km is Gene;
  SRB has no throttle. Size1 drag is the 50 km lid — not a meter.
  EC (Linus): TELEMETRY 30×0.052=1.6; thermo 138×0.002=0.3; splash goo
  641×0.18=115. Command ~0.05/s (1204Z). Hang+splash ~840 s → ~170 EC.
  310 EC covers overlapping draws. One Z-100 is not enough if goo runs.
  Goo is splash dwell (east Water, wreck-recoverable). FlyingLow goo 641 s
  will not finish on this hang. TELEMETRY 0.75 MB needs the tape; do not
  co-run geiger (1.25 MB). Mite TWR ~2.4 with this payload — left on the
  shelf. Query `python main.py parts --unlocked` before changing the stack.
