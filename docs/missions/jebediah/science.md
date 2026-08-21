# jebediah science card

science: card
flight: jebediah
craft: kspstuff-hop-flea-pbc
at: hop
body: Earth
need_builder: no
recover_banks: yes
notes: Living hop. Start FlyingLow geiger on the Geiger part; file whatever
  records aloft. Catalog duration_s 497 is not a hang expect — Flea ~75 s
  stock, FAR unflown, 50 km lid ~202 s. Tape 0.5 / EC 2.5 vs Engineer7500
  1.0 / ~310 EC. Payoff is recovery@EarthFlew leftover 1.00 on a living
  recover. Skip thermo crumbs 0.045. Do not bind 641 s goo. Do not re-pad
  Cape. Do not transmit. F-013: never Stayputnik PAW.

## Flying
- experiment_id: geigerCounter
  situation: FlyingLow
  part: kerbalism-geigercounter
  instrument: kerbalism-geigercounter (Geiger Counter); tech engineering101; unlocked yes; on_craft yes
  duration_s: 497
  ec_rate: 0.005
  recover_banks: yes

# skip temperatureScan FlyingLow@Shores leftover 0.045 / 3 s / 0.002
# skip mysteryGoo FlyingLow 641 s / 0.18 (hang wall)
# skip kerbalism_TELEMETRY FlyingLow Shores — capped
# spent Cape Surface geigerCounter duration_s 497 / ec_rate 0.005
# spent landed TELEMETRY duration_s 29 / ec_rate 0.052
# recovery@EarthFlew leftover 1.00 is HD recover, not a Toggle
