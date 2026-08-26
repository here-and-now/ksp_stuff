# Agree — this sit (Lars / Gus / Linus)

Shared achievable plan. Not seated `plan.md`. Not last-miss leftovers.
Inner circle last-writes **only their section**. Gene does not merge.
Katherine last-writes **Dynamics** when pulled (`ops --tag ask --desk
katherine` or `--tag dynamics`) — not every pad.

```
sit: FlyingHigh
hang: C-504 kspstuff-hop-valiant-proc-loft-pbc
bind: T-404 barometerScan FlyingHigh 305/0.05
duration_vs_high: 305s file does not finish tens-of-seconds loft-through (~42s then InSpaceLow ~268 km, four hops +0); pays iff MECO/dwell ≥305s in 50–140 km
recover: yes
meco: lid 50 km live; independent off; High dwell coast
dynamics: none
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

This-hop: T-404 PresMat FlyingHigh 305/0.05/2.70 only. File rem=0
is still the card. Envelope Shores heading 297 — not Forest, not
Water, not Grasslands. Four loft-throughs (16-23-52Z / 16-49-02Z /
17-01-10Z / 17-13-14Z) spent High in tens of seconds then
InSpaceLow ~268 km rec=no sci +0. **Nothing this hang finishes
that High window:** T-404 305 s does not; T-069 Forest TELEMETRY
25 s leftover cannot pay Shores High (capped); thermo/geiger High
capped; T-368 goo 641 s sample rec=no loses the can. T-404 pays
iff pulse MECO/dwells ≥305 s in 50–140 km. T-460 FlyingLow same
eid one Toggle — stays unbound. InSpaceLow LITE S-514 10 s / 2.00
+ TELEMETRY S-515 30 s / 2.00 + goo leftover S-516 3.41 stay
unbound shelf (flying Toggle at 50 km does not retry in space).
Do not drop High for splash leftover. Not Surface. Not T-461.
recover HD 1.17 MB not TX 41 h.

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

none — pull when High-band time / FAR Q / weathercock is the fight.
Stamp `verify` after the window; do not sit every `ops next`.
