# Gene ↔ Jeb. Not the helm.
Gene: Hop. Pad sounding ~15 km. Kerbin. Not Mun. Not orbit.

Pad, landed, before you light: crew report. Helm takes Goo can 1.

Light the Flea.

FlyingLow: crew report (LaunchPad biome; Shores if you leave KSC). Helm takes Goo can 2. Do not transmit.

Chute. EVA report only if you are stopped on the ground — hatch on the pad before light, or after you stop. No flying EVA.

Recover the pod. That is the science. That is the flight.
Jebediah: copy, hop, recover
Gene: go: pad. Uncrewed kspstuff-pad-pbc. mysteryGoo + temperatureScan. Recover HD. Do not transmit. Not hop. Not mun.
Jebediah: copy, pad science, uncrewed
Gene: Earth. Science sandbox. PBC. Uncrewed Stayputnik pad science. Not hop. Not Mun.

Helm: `python main.py pad`. Craft `kspstuff-pad-pbc`. No kerbal on the stack.

1101Z recovered science (none). L-042 is in. Re-fly the same card. Pad, landed, before you throw the SRB: start Kerbalism `mysteryGoo` (`GooExperiment`) and `temperatureScan` (`sensorThermometer`). Keep on the HD. Do not transmit. Empty start is abort, not recover.

Do not light for orbit. This is pad science. Recover the probe. That is the flight.

emergencies: hold, cut, no_warp, stage, recover, science, abort_pad
Gene: 1101Z empty recover. L-042 in. Save sci 0. Re-fly pad same card. go: yes.
Jebediah: copy, pad re-fly L-042
Gene: Earth. Science sandbox. PBC. Uncrewed Stayputnik pad science. Not hop. Not Mun.

Helm: `python main.py pad`. Craft `kspstuff-pad-pbc`. No kerbal on the stack.

1119Z started mysteryGoo + temperatureScan then Toggle-stopped them (L-043). Recovered. Save sci 0. Stayputnik extras skipped — not on the card. Re-fly the same card. Pad, landed, before you throw the SRB: start Kerbalism `mysteryGoo` (`GooExperiment`) and `temperatureScan` (`sensorThermometer`) once. Keep on the HD. Do not transmit. Empty start is abort, not recover.

Do not light for orbit. This is pad science. Recover the probe. That is the flight.

emergencies: hold, cut, no_warp, stage, recover, science, abort_pad
Gene: 1119Z double Toggle. L-043 in. Save sci 0. Re-fly pad same card. go: yes.
Jebediah: copy, pad L-043, once
Gene: Earth. Science sandbox. PBC. Uncrewed Stayputnik pad science is done for this slice. Not hop. Not Mun.

1136Z pad exit 0. Started mysteryGoo (GooExperiment) once and temperatureScan (2HOT + Stayputnik core). L-042/L-043 held. Recovered HD. Save sci 0 — Kerbalism samples need dwell; helm recovered on Start. No re-fly unless Os says so.

Hold. Wait for Os. Do not light the SRB. Do not hop. Do not mun.
Gene: 1136Z pad exit 0. Goo+thermo started once. L-043 held. Recovered. Save sci 0. go: wait. Os next.
Gene: Earth. Science sandbox. PBC. Os: go for science.

Save sci 0. 1136Z pad started mysteryGoo + temperatureScan once (L-042/L-043) then recovered the same tick. Kerbalism HD got no dwell. Another identical pad will not buy science.

Need stack: pad-dwell. Helm starts the card, waits until samples finish on the HD, then recovers. Do not Toggle twice. Do not light the SRB. Do not hop. Do not mun. Disk Kerbalism: mysteryGoo ~641 s, temperatureScan ~138 s — wait running→done, not a wall-clock guess.

Linus card (kspstuff-pad-pbc, landed pad, recover HD, no transmit):
- mysteryGoo on GooExperiment
- temperatureScan on sensorThermometer

VAB capable: yes. Catalog pad as written recovers on Start. go: wait.

emergencies: hold, cut, no_warp, stage, recover, science, abort_pad
Gene: need_stack pad-dwell. world sci 0. pad recovers on Start. go: wait. Not hop/mun.
Gene: Earth. Science sandbox. PBC. Os: go for science.

Helm: `python main.py pad`. Hangar uncrewed `kspstuff-pad-pbc`. Start the card, dwell on the pad until the HD has it, then recover. Do not recover on Start. Do not Toggle twice (L-043). Do not light the SRB. Not hop. Not mun.

Goo dwell is minutes (~10–12 min catalog size/data_rate), not a tick. Thermo ~2 min. Helm waits Has Data / remaining 0 / stopped-after-running, else that wall. Abort on empty start, EC=0, reliability, wreck, or uplink abort_pad / hold / recover.

Linus card (kspstuff-pad-pbc, landed pad, recover HD, no transmit):
- mysteryGoo on GooExperiment
- temperatureScan on sensorThermometer

VAB capable: yes. L-044 in. world sci 0. go: yes.

emergencies: hold, cut, no_warp, stage, recover, science, abort_pad
Gene: L-044 in. Pad go. Uncrewed kspstuff-pad-pbc. mysteryGoo + temperatureScan. Goo dwell is minutes, then recover HD. Not hop. Not mun. go: yes.
Jebediah: copy, pad dwell L-044
Gene: Earth. Science sandbox. PBC. Os: go for science.

1204Z pad exit 2 ABORT ec=0 at T+483 s. Card started, dwelled, Z-100 died. abort_pad recovered a partial — world sci 0.80. L-045 in: dwell caps to remaining EC; recover if HD has data. Empty HD + EC=0 still aborts.

Helm: `python main.py pad`. Hangar uncrewed `kspstuff-pad-pbc`. Start the card, dwell until HD done or EC budget, then recover. Do not recover on Start. Do not Toggle twice (L-043). Do not light the SRB. Not hop. Not mun.

Stayputnik+Z-100 (~110 EC) cannot finish goo (~641–739 s at 0.18 EC/s). Same stack banks a partial. Hold for VAB more battery (start batteryPack). Then pad.

Linus card (kspstuff-pad-pbc, landed pad, recover HD, no transmit):
- mysteryGoo on GooExperiment
- temperatureScan on sensorThermometer

VAB capable: yes on current stack — not enough EC. need_builder. world sci 0.80. go: wait.

emergencies: hold, cut, no_warp, stage, recover, science, abort_pad
Gene: 1204Z EC=0 T+483s. L-045 in. world sci 0.80. need_builder more EC for full goo. go: wait. Not hop/mun.
Gene: Earth. Science sandbox. PBC. Os: go for science.

1204Z pad exit 2 ABORT ec=0 at T+483 s. Card started, one Z-100 died. abort_pad recovered a partial — world sci 0.80. 1221Z is a unit-test fake. L-045 in: dwell caps to remaining EC; recover if HD has data. Empty HD + EC=0 still aborts.

Helm: `python main.py pad`. Hangar uncrewed `kspstuff-pad-pbc` (Stayputnik + 3×Z-100 ~310 EC). Start the card, dwell until HD done or EC budget, then recover. Do not recover on Start. Do not Toggle twice (L-043). Do not light the SRB. Not hop. Not mun.

Goo dwell is minutes (~641–739 s). 3×Z-100 should finish (~1360 s at 0.228 EC/s). Thermo is short.

Linus card (kspstuff-pad-pbc, landed pad, recover HD, no transmit):
- mysteryGoo on GooExperiment
- temperatureScan on sensorThermometer

VAB capable: yes. world sci 0.80. go: yes.

emergencies: hold, cut, no_warp, stage, recover, science, abort_pad
Gene: Pad go. 3×Z-100 kspstuff-pad-pbc. mysteryGoo + temperatureScan. Dwell minutes, recover HD. Not hop/mun. go: yes.
Jebediah: copy, pad 3xZ-100 dwell
Gene: 1235Z pad exit 0. Dwell timeout 740s. Recovered. 3xZ-100 held. world sci 2.22. Still start. Same card done. go: wait. Not hop/mun.
Gene: Os continue. Cape landed goo+thermo capped. Next hop. Do not pad. need_stack hop, need_builder, need_science. go: wait.
Gene: Linus opportunities. Hop. Not pad. Not pad-geiger. Card none. need_stack hop. need_builder. need_science. go: wait.
Gene: Hop conference in. Gus capable kspstuff-hop-flea-pbc. Linus flying card bound. hop does not Hangar. go wait. Do not pad.
Gene: Lars Hangar in. hop go. Uncrewed kspstuff-hop-flea-pbc. TELEMETRY 30/0.052 + thermo 138/0.002 airborne. Splash goo off. hop_apo 15 km. Recover HD. Do not pad. Do not Hangar pad-pbc. go: yes.
Jebediah: copy, hop Flea, flying card, recover
Jebediah: copy, holding hop Flea uncrewed FlyingLow
Gene: 155812Z hop timeout. leftover flying 73 m EC=0. sci 3.20 partial FlyingLow. phase hop recover. Do not Hangar. go: yes.
Jebediah: copy, leftover hop recover, skip Hangar, no light, no splash goo
Gene: 162437Z leftover abort no science. modules gone. HD not taken. sci 3.20. Lars keep-HD in. phase hop recover. skip Hangar. no light. no Toggle. go: yes.
Jebediah: copy, leftover hop recover. skip Hangar. no light. recover HD.
Gene: abort wreck flight results
script: acked abort wreck flight results
Gene: 163639Z leftover abort. paused Flight Results. HD not taken. sci 3.20. Os Escape hid modal. still paused 72 m not KSC. Lars frozen-MET in. phase hop recover debris. skip Hangar. no light. go: yes.
Gene: 163639Z leftover abort. paused wreck. phase hop recover debris. skip Hangar. no light. go yes.
Jebediah: copy, leftover hop recover, skip Hangar, keep HD
Gene: 170213Z leftover recover. exit 0. KSC. sci 3.20 unchanged. FlyingLow credited in-flight 15-58, not wreck recover. Verena. go: wait. Do not fly.
Jebediah: copy, hop Flea kspstuff-hop-flea-pbc, TELEMETRY+thermo airborne, recover HD, hop_apo 15000, no pad
Jebediah: copy, leftover pad Flea, no Hangar
Jebediah: copy, leftover tracking Flea, enter Flight, no Hangar
Jebediah: copy, leftover pad Flea, one Toggle per id
Jebediah: copy, pad geiger, not goo
Jebediah: copy, pad geiger, MET must move
Jebediah: copy, fresh Hangar, pad geiger, MET must move
Jebediah: copy, dry-launch pad, MET must tick, Stayputnik geiger PAW
Jebediah: copy, ad astra, named clocks
Gene: abort_pad
script: acked abort_pad
Jebediah: copy, Flea TELEMETRY, named clocks, no geiger
Jebediah: copy, Geiger part, rem/UT not MET, rails 0
Gene: abort
script: acked abort
Jebediah: copy, Geiger part not PAW
Jebediah: copy, Hammer thermo, 2HOT not PAW
Gene: Merge. hop go. Uncrewed kspstuff-hop-flea-pbc. FlyingLow geiger 497/0.005 on the part. Recover HD. hop_apo 18 km cut wish. FAR Learn after. Do not pad. Do not Hangar geiger-pbc. go: yes.
Jebediah: copy, landed TELEMETRY, skip geiger
Jebediah: copy, Hangar hop-flea-pbc, FlyingLow geiger on kerbalism-geigercounter, recover HD
Jebediah: copy, living hop, Hangar kspstuff-hop-flea-pbc, FlyingLow geiger on kerbalism-geigercounter, recover HD
Gene: 10-30-35Z hop miss: dismiss was not recover. sci 2.96. FAR apo 7.6 km. hop go.
Jebediah: copy, fresh Hangar hop-flea-pbc, FlyingLow geiger on kerbalism-geigercounter, living recover() not Flight Results dismiss
Gene: 10-42-32Z living recover. sci +1.13. FlyingLow geiger leftover 2.45. Same hop. python main.py hop.
Jebediah: copy, fresh Hangar hop-flea-pbc, start FlyingLow geiger on kerbalism-geigercounter, recover() HD after hop down
Jebediah: copy, fresh Hangar hop-flea-pbc, FlyingLow geiger on kerbalism-geigercounter, recover HD, MET-still+q=0 is down now
Gene: 11-09-13Z hop miss. exit 0 recovered lied (pre_launch after dismiss). sci 4.49. Lars recover() while Flight ≤250 m. Same hop. python main.py hop.
Jebediah: copy, fresh Hangar hop-flea-pbc, FlyingLow geiger on kerbalism-geigercounter, recover() still Flight at <=250 m
Jebediah: copy, fresh Hangar hop-flea-pbc, FlyingLow geiger on kerbalism-geigercounter, recover in Flight
Jebediah: copy, leftover hop-flea-pbc PRELAUNCH, phase hop skip Hangar, FlyingLow geiger on kerbalism-geigercounter, wait sit=landed then recover() before dismiss
Jebediah: copy, fresh Hangar hop-flea-pbc, FlyingLow geiger on kerbalism-geigercounter, wait sit=landed then recover before dismiss
Jebediah: copy, fresh Hangar hop-flea-pbc, FlyingLow geiger on kerbalism-geigercounter, wait sit=landed then recover() recoverable=yes before dismiss, catalog 497 not hang
Jebediah: copy, leftover hop debris recover, phase hop, no Hangar, sit=landed then recover() in Flight
Jebediah: copy, Hangar hop-flea-pbc, light Flea, geiger on kerbalism-geigercounter FlyingLow, wait sit=landed recover before dismiss
Gene: abort
script: acked abort
Jebediah: copy, fresh Hangar flea-pbc, hop geiger on kerbalism-geigercounter, crash UI detect-now
Jebediah: copy, leftover PRELAUNCH hop-flea-pbc, skip Hangar, phase hop, geigerCounter on kerbalism-geigercounter, MET must move
