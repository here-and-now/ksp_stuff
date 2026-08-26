# Agree — this sit (Lars / Gus / Linus)

Shared achievable plan. Not seated `plan.md`. Not last-miss leftovers.
Inner circle last-writes **only their section**. Gene does not merge.
Katherine last-writes **Dynamics** when pulled (`ops --tag ask --desk
katherine` or `--tag dynamics`) — not every pad. Eleanor last-writes
**Constellation** when pulled (`ops --tag ask --desk eleanor` or
`--tag constellation`) — not every pad. Hank talks to her directly.

```
sit: InSpaceLow
hang: C-534 kspstuff-hop-valiant-proc-redstone-pbc
bind: S-514 kerbalism_LITE InSpaceLow 10/0.03
duration_vs_high: High cannot pay; C-534 loft sits InSpaceLow ~249–300 km; LITE 10s finishes; lid-MECO 137 km High cannot pay LITE; S-516 InSpaceLow goo capped (paid)
recover: yes
meco: python main.py ascent; this-hop Valiant loft RF live until 50 km lid MECO + independent off (vacuum_stage_sit false); Terrier two-stage later no lid-MECO — gravity turn east while thrusting, circ Pe>140 km
dynamics: this-hop loft-only yes; C-534 ascent = Valiant lid MECO apo~118–140 km High leftover~450–530 horiz~15 m/s; hop tape still loft-through 213–276 km apex horiz 17–30 m/s; circularize still Terrier east gravity turn after 45
constellation: Cape LIVE 64 bps omni SurfAntenna; loft stays Cape sky; DSN L LIVE TL2; minRelayTL=3 no sat
agreed: yes
blocker: none
```

Wreck rec=no re-flies last `cli:` — do **not** reopen this file.
Change hang / bind / recover / MECO only on an `ops --tag plan`
hire (three in parallel on that ticket, then split).

## Hang (Gus)

This tree pad: C-534 `kspstuff-hop-valiant-proc-redstone-pbc`. Flies
`python main.py ascent` now (T-552). FED (last tank attN
bottom=Valiant). Nylon `RC_cone` 50 m payload-side on OKTO
(Stayputnik has no top; cone `srfAttach=0`). Engine `istg=0`
`sqor=0` first fire; chute `istg=1` `sqor=0` last. No girders. 4×
proc 1.25×1.222 Cylinder `RedstoneStripes` 1500 L Default 2700 kero.
Stack Heaviest/rigid. No HS. Recover: silk. `capable: yes`. Pad until
`advRocketry` 45. 268 km loft is not orbit — Pe on the ground. Did
not replace C-534. Did not Hangar C-534.

Orbit donor on disk until 45, not pad: C-544
`kspstuff-hop-valiant-proc-orbit-pbc`. Clone C-534 + 2 extra
`sasModule` (3 total, Heaviest/rigid) for FAR heading. Same Valiant
5° gimbal (cfg; FAR ×1.5 may read 7.5 — tape still HDG 297). Same
4×1500 L Redstone 2700 kero, no girders, no HS, silk, engine first
fire. `craft fuel` FED. Terrier `liquidEngine3_v2` **LOCKED**
`advRocketry` 45 — not on the file; do not Hangar a locked part.
Reliant has no gimbal. Swivel gimbal 3° is worse. `capable: no`
(first-stage donor, not two-stage circularize). Helper T-546:
two-stage compose (extra wheel CLI, proc decoupler + upper tanks +
Terrier after unlock; `liquid` must not flatten the split; staging
Valiant first / decoupler / Terrier / chute last). After 45: splice
Terrier vacuum upper, Pe above ~140 km High lid. rec=no is honest if
orbiting. Do not Hangar the donor until the node. Do not Hangar
C-477. C-504 loft-pbc stays shelf. Leftover High / Forest / splash
hangs wait a living orbit.

## Bind (Linus)

This-hop: S-514 kerbalism_LITE InSpaceLow 10/0.03/2.00 seq0 (file,
scan still unstarted ~2.00) on C-534
`kspstuff-hop-valiant-proc-redstone-pbc` OKTO PAW. T-552 ascent loft
still sits InSpaceLow (apo 249–300 km); LITE 10 s finishes; recover
HD 0.25 MB. Leftover High later — do not re-pin T-404 305 s. Lid-MECO
apo 137 km is High — cannot pay LITE; do not unbind S-514. Closed
S-516 InSpaceLow goo — capped (paid). Closed S-515 TELEMETRY
InSpaceLow — capped (paid). Thermo InSpaceLow capped; PresMat has no
InSpaceLow sit. High / Forest / splash leftover stays shelf — keep
an eye; do not unbind forever; not this-hop: T-368 FlyingHigh goo
leftover 0.293 (crumbs), T-069 Forest High TELEMETRY leftover 1.512,
T-404 High PresMat 2.70 (305 s cannot pay). Bank 8.29 need ~36.71
for advRocketry 45. This-hop LITE ~2.00 still leaves ~34.71. Not
Water. Not Grasslands. Not Surface. Pulse Toggle in space. f013 LITE
hosted OKTO PAW on_craft=yes.

## Pulse (Lars)

This-hop ``python main.py ascent`` on C-534. Helper ``ascent.py``.
Live RF ``rf_throttle.py`` (independent, not UI MainThrottle).
``hop.py`` parked. ``vacuum_stage_sit`` is false (no Terrier) —
loft path: ``RF.apply`` live 1 from light until ``loft_lid_sit`` /
``loft_meco_sit`` (50 km **live** alt), then ``RF.cut`` independent
off. While independent still 1: ``turn_live_sit`` SAS off, AP engage
once, surface heading 90 (``_steer_east``). SAS Stability is not a
heading. Do not wait Terrier. After lid, Toggle InSpaceLow
(``space_low_sit`` / ``sit_matches``). Coast ``apply_sit_warp``. Arm
Nylon on ``chute_arm_sit`` — recover yes when down. Do not
circularize this hang: Pe stays on the ground. Pulse never writes
gimbal. Do not retune MECO / lid / silk to High 305 s.

When ``vacuum_stage_sit`` is true (Terrier on the hang): keep live
through first-stage burnout — same east turn while thrusting, no
lid MECO — then stage, vacuum apply live near apo until Pe ≥
~140 km High lid. rec=no is honest if orbiting. Same compose —
not a stamp helper. Forest / Grasslands: same.

## Dynamics (Katherine, opt-in)

This-hop loft-only yes. C-534 on `python main.py ascent` is
Valiant lid MECO — not circularize. Terrier later is east gravity
turn (no lid MECO), Pe ≥ ~140 km, after `advRocketry` 45.

C-534 pad **7.47 t** / 2700 kero / parts 25. Five hops
(20-18-43Z / 20-41-53Z / 20-54-37Z / 21-05-13Z / 21-10-50Z)
plus 19-48-52Z / 20-07-41Z agree. Hop tape is loft-through, not
the ascent cut: 50 km live is still throttle 1 / ~100 kN
(21-10-50Z 51.7 km leftover **458** vz **1.30 km/s** apo
**140 km**; 20-18-43Z 49.1 km leftover **493** vz **1.24 km/s**
apo **129 km**). First MECO is **81–92 km**, leftover
**169–277**. Apex sit=sub_orbital apo **213–276 km**, horiz
**17–30 m/s** vs circular **7.75–7.82 km/s**. Pe through the
planet (~−6360 km). Q_max **22.7–22.9 kPa**. FAR at apo is
zero. Burnout pitch **65** heading **297** — weathercock, not
090. Short **~7.7 km/s** of circular speed.

Ascent Valiant lid MECO is that 50 km live state: apo
**~118–140 km** High, leftover **~450–530** unused, horiz
**~14–17 m/s**, pitch **~88**. Same family as C-504 T-523
(vz 1.29 km/s apo 137 km). Extra 1500 L vs C-504 has not burned
yet at the lid. InSpaceLow may not pay. T-404 PresMat 305 s
cannot pay (lid-MECO High ~260 s; loft-through High up
**~37–46 s**, space hundreds).

Cannot circularize this hang. Gravity-turning leftover after
lid still leaves Pe on the ground — need ~7.8 km/s horiz; mass
ratio for 7.7 km/s at 270 s is ~18; this hang is ~6. 7×1500
Valiant TWR ~0.78 sits; 7×1500 Reliant Δv ~4.5 km/s is still
sub-orbital. Both 1 ignition.

Descent vs last-flight recover: last-flight is abort/exit, not
sit. 21-10-50Z tape cuts flying **90.7 km** chute armed (ship.md
same). Envelope landing catastrophic rec=no; 20-41-53Z
envelope rec=yes sit=splashed is synthesized vs last flying
46 km vz −2.0 km/s. Do not Learn recover from those exits.

Phase 2 remains Terrier vacuum upper, AP east while thrusting.
Do not Hangar a circularize claim on this tree.

## Constellation (Eleanor, opt-in)

Cape is **live** for C-534. Dump: `US - Cape Canaveral` L 1.5 dBi
Tx 40 dBm need_TL=0 **LIVE**. GSTL=2. TL2 **64 bps** is table and
Cape path (T-427). Hang omni `SurfAntenna` (Communotron 16-S,
start, gain=2, L). Last flying snap of this craft: `link: yes`
`rate_bps: 64` `via: US - Cape Canaveral`. Hangar none this sit —
that snap is the path, not a live RateToHome. Loft is vertical
over Cape (apex horiz tens of m/s); silk recover stays Cape sky.
Do not cheat a link. Do not plan dump hours as RateToHome.

Also LIVE at GSTL=2 (need_TL=0): Wallops, Bermuda, DSN L
Goldstone / Canberra / Madrid (gain 8). Rest of the map is
**SILENT** until commsTL3 / `basicScience`. `minRelayTL = 3`.
Every relay part is **LOCKED**. T-065: keep 16-S on the chute
hang. HG-5 is `basicScience` locked. Omni until a hop goes deaf.

A future orbit craft needs a path that is **not Cape-only**. This
hang never leaves Cape sky and does not stay up. Ground DSN L is
already LIVE at TL2 — that is the candidate, not a satellite.
Dump LIVE is need_TL, not close at LEO range from 16-S. A sat
cannot relay until `minRelayTL` and a relay part. Do not invent a
constellation. Antenna on the hang is Gus when omni is the miss
— it is not the miss here.
