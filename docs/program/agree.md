# Agree — this sit (Lars / Gus / Linus)

Shared achievable plan. Not seated `plan.md`. Not last-miss leftovers.
Inner circle last-writes **only their section**. Gene does not merge.
Katherine last-writes **Dynamics** when pulled (`ops --tag ask --desk
katherine` or `--tag dynamics`) — not every pad.

```
sit: FlyingHigh
hang: C-504 kspstuff-hop-valiant-proc-loft-pbc
bind: none
duration_vs_high: MECO@50km ~260s FAR / loft-through ~56s; T-404 305s cannot pay; no High file ≤250s pays Shores
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
until `generalRocketry` 20 then one node after. C-477 blob is not
capable. t7-wheel-pbc lithobrake is not recover. T-428 / T-430 stay
alts, not this hang. Do not replace C-504 because the last hop sheared.

## Bind (Linus)

This-hop: **none**. Unbound T-404 FlyingHigh PresMat 305/0.05/2.70.
MECO-at-lid High is ~260 s FAR / ~271 s vac (Kepler ceiling 276 s);
loft-through ~56 s up. 305 s cannot pay. File rem=0 stays the High
shelf until a hang holds ≥305 s in 50–140 km. No High file ≤250 s
pays Shores: T-069 Forest TELEMETRY 25 s leftover cannot pay Shores
High (capped); thermo/geiger High capped; goo 641 s sample. Envelope
Shores heading 297 — not Forest, not Water, not Grasslands. T-460
FlyingLow 305 s unbound. InSpaceLow LITE S-514 10 s / 2.00 is shelf
(flying Toggle at 50 km does not retry in space). S-515 TELEMETRY
30 s / 2.00 + S-516 goo leftover 3.41 shelf. Not Surface. Not T-461.
Do not drop High for splash leftover — High itself cannot pay 305 s.

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
