# Agree — this sit (Lars / Gus / Linus)

Shared achievable plan. Not seated `plan.md`. Not last-miss leftovers.
Inner circle last-writes **only their section**. Gene does not merge.
Katherine last-writes **Dynamics** when pulled (`ops --tag ask --desk
katherine` or `--tag dynamics`) — not every pad.

```
sit: InSpaceLow
hang: C-504 kspstuff-hop-valiant-proc-loft-pbc
bind: S-514 kerbalism_LITE InSpaceLow 10/0.03; S-515 kerbalism_TELEMETRY InSpaceLow 30/0.052
duration_vs_high: High cannot pay (T-404 305s vs ~260s); this loft sits InSpaceLow ~268 km; LITE 10s + TELEMETRY 30s finish
recover: yes
meco: lid 50 km live; independent off; High dwell coast
dynamics: MECO@50km ~271s vac / ~260s FAR in 50–140 (vz 1.29 km/s apo 137 km); T-404 305s cannot pay
agreed: yes
blocker: none
```

Wreck rec=no re-flies last `cli:` — do **not** reopen this file.
Change hang / bind / recover / MECO only on an `ops --tag plan`
hire (three in parallel on that ticket, then split).

## Hang (Gus)

C-504 `kspstuff-hop-valiant-proc-loft-pbc`. FED. Nylon `RC_cone` 50 m
payload-side on OKTO (Stayputnik has no top; cone `srfAttach=0`).
Engine `istg=0` `sqor=0` first fire; chute `istg=1` `sqor=0` last.
No HS (C-477 blob). Recover: silk. `capable: yes`. Iterate this hang
until `advRocketry` 45. C-477 blob is not
capable. t7-wheel-pbc lithobrake is not recover. T-428 / T-430 stay
alts, not this hang. Do not replace C-504 because the last hop sheared.

## Bind (Linus)

This-hop: S-514 kerbalism_LITE InSpaceLow 10/0.03/2.00 seq0 + S-515
kerbalism_TELEMETRY InSpaceLow 30/0.052/2.00 seq1. Files. Stayputnik
PAW. Envelope Shores heading 297 loft ~268 km is InSpaceLow every
hop — High cannot pay (T-404 305 s vs ~260 s FAR). 10 s + 30 s finish
in space. T-404 High PresMat unbound. T-069 Forest High TELEMETRY
same eid as S-515 — stays unbound (Shores High capped). S-516 goo
leftover 3.41 sample 641 s shelf. Not Water. Not Grasslands. Not
Surface. Pulse must Toggle in space; 50 km High lid skip-latch does
not retry. recover HD 0.25+0.75 MB not TX.

## Pulse (Lars)

`hop_factory.py` inland compose. Pad-RF `hop_factory_pad.py` (one
sit). Throttle 1 + SAS vertical until lid. MECO at 50 km **live**
alt: MainThrottle 0, setpoint 0, independent off. Then High dwell
coast — not a burn, not inland-through-burnout. 17-01-10Z printed
that sit at 55 km throttle 1. After that gate, 17-13-14Z still
emptied tanks by MET 153 alt 98 km apo 270 km; PresMat dwell in
space, sci +0. `_hold_lid` after lid is MECO. Log must not print
hold inland through burnout after High lid. Residual vz at lid
still exits 140 km — that is the fight; 305 s in 50–140 km is not
MECO-at-lid alone. Hang owns recover. Do not retune MECO / lid /
silk to the last shear.

## Dynamics (Katherine, opt-in)

Four loft-throughs agree at the lid: 50 km live vz 1.29 km/s (16-23-52Z
1.32), pitch 87–89, heading 299–302, Q_max ~23 kPa, Shores, throttle 1
through High. MECO at that state: vacuum apo 137 km, 50→apo→50 = 271 s
(16-23-52Z 249 s if apo 141 km nicks InSpaceLow). FAR Q ~1.1 kPa at lid
shaves a few seconds (~260 s), not 45. Kepler ceiling in-band (kiss
140 km) is 276 s. MECO earlier is worse (42 km vz 1.10 → apo 106 km →
216 s in High). Lid leftover ~290 kg hovers ~38 s, not 305. Loft-through
High is ~56 s up / ~50 s down (17-01-10Z). T-404 305 s cannot pay. Silk
is recover, not a High drogue.
