# VAB board — hardware vs Gene's draft

capable: yes
craft: kspstuff-hop-valiant-t7-wheel-pbc
alt: kspstuff-hop-valiant-t7-pbc (T-387 7×FL-T100 Valiant Stayputnik no wheel — 13-31-03Z 88.8 km / 275 km loft proof); kspstuff-hop-valiant-t7-wheel-proc-pbc (T-406 7× proc 1.25×0.625 Cylinder 767 L / 345 kero, 2415 kero same 4.375 m stack); kspstuff-hop-valiant-t7-wheel-oxstat-pbc (T-408 4× OX-STAT 0.35 EC/s); kspstuff-hop-valiant-t7-wheel-nose-pbc (T-409 OKTO+proceduralNoseCone 1.25-to-0 ×0.625 — no silk); kspstuff-hop-valiant-t7-wheel-hs-pbc (T-402 proc HS 1.25×0.2 Ablative disc, no silk); kspstuff-hop-valiant-t7-wheel-cone-pbc (T-403 OKTO+RC_cone 50m — do not Hangar this sit); kspstuff-hop-valiant-t7-chute-pbc (T-366/T-370 OKTO+Mk16 recover — 15-05-30Z alt 62 km once; 18-15-43Z vertical MET 28 alt 389 pitch=-85 rec=no — do not Hangar this sit); kspstuff-hop-valiant-t7-chute-cone-pbc (T-367 RC_cone Nylon 50m); kspstuff-hop-valiant-proc-stiff-dv-pbc (T-353 4x 1.427x0.5 1440 kero Valiant + 6x girder — 14-03-34Z Forest apo 33046 rec=yes q=24 kPa, not FlyingHigh 50 km); kspstuff-hop-valiant-proc-stiff-dv-cone-pbc (T-354); kspstuff-hop-valiant-proc-stiff-dv-hs-pbc (T-356); kspstuff-hop-valiant-proc-stiff-pbc (T-165/T-332 3x 1.25x0.65 1080 kero Forest 30.7 km); kspstuff-hop-valiant-proc-stiff-cone-pbc (T-286 3x proc 1080 kero + RC_cone 50m); kspstuff-hop-valiant-chute-stiff-pbc (T-153 3xT100 675 kero); kspstuff-hop-valiant-chute-cone-pbc (T-148/T-154 50m RC_cone minDeployment 2500); kspstuff-hop-valiant-geiger-oxstat-pbc (T-131); kspstuff-hop-valiant-geiger-polygon-pbc (T-136); kspstuff-hop-valiant-geiger-chute-pbc (T-113 Forest geiger); kspstuff-hop-valiant-geiger-cone-pbc (T-156 RC_cone Nylon 50m + Geiger part); kspstuff-hop-proc-srb-geiger-pbc (T-129); kspstuff-hop-proc-srb-pbc (T-098); kspstuff-hop-valiant-proc-hs-pbc (T-099); kspstuff-hop-valiant-proc-decoupler-pbc (T-100); kspstuff-hop-valiant-chute-pbc (T-054); kspstuff-hop-valiant-chute-t2-pbc (T-066 2xT100); kspstuff-hop-valiant-proc-stiff-dv-lite-pbc (T-362 do not Hangar — FAR 34-28 at 4x coast); kspstuff-hop-valiant-proc-stiff-dv-lite-cone-pbc (T-363 do not Hangar); kspstuff-hop-valiant-proc-stiff-dv-lite-hs-pbc (T-365 do not Hangar); kspstuff-hop-swivel-proc-stiff-dv5-pbc (T-359 do not Hangar); kspstuff-hop-swivel-proc-stiff-dv5-cone-pbc (T-360 do not Hangar); kspstuff-hop-swivel-proc-stiff-dv5-hs-pbc (T-361 do not Hangar); kspstuff-hop-valiant-proc-4t-pbc (T-318 do not Hangar); kspstuff-hop-valiant-proc-4t-cone-pbc (T-319 do not Hangar); kspstuff-hop-valiant-proc-4t-hs-pbc (T-320 do not Hangar); kspstuff-hop-valiant-proc-tank-pbc (T-097 do not Hangar)
notes: T-400 hang **t7-wheel-pbc**: t7-pbc + sasModule (stability
  0.625m inline wheel) + PresMat. Same 7×FL-T100 Valiant Stayputnik,
  no chute. t7-pbc 13-31-03Z apo 88.8 km shear=no / 275 km loft is
  the ≥50 km proof; +0.08 t wheel/PresMat/tape. 4×Engineer7500 HD=2.5
  vs PresMat file 1.17 + TELEMETRY 0.75 + geiger 0.5. 5×Z-100 (~500);
  PresMat 305×0.05=15.25; leftover TELEMETRY 25×0.052; geiger ~296×0.005;
  wheel 0.25 EC/s if used. Do **not** Hangar t7-chute / t7-wheel-cone
  this sit (silk/4×/pitch). Alt T-402 t7-wheel-hs 1.25 disc no silk.
  Shelf T-406 t7-wheel-proc: 7× proceduralTankRealFuels 1.25×0.625 /
  767 L / 345 kero (volumeMax 0.8 kL) — 2415 kero vs 7×T100 1575 at
  the same 4.375 m as the 88.8 km proof. Not girderless lite / dv5
  1.427×0.5 / 4t 1.25×0.65. T-408 4× OX-STAT on tank 2 vs t7 3×Z-100
  EC=0 MET 440 and Goo 641×0.18. T-409 proceduralNoseCone (stability,
  Stayputnik has no top node — OKTO). Do not Hangar T-409 as silk.
  Do **not** Hangar lite / lite-cone T-363 / lite-hs T-365 (FAR 34-28
  at 4x coast, no girders). Do **not** Hangar dv5 / dv5-cone T-360 /
  dv5-hs T-361 (14-22-29Z FAR 44→8 at pitch q=46 kPa apo 16 km Shores
  rec=no). Do **not** Hangar proc-4t / 4t-cone / 4t-hs (10-31-47Z FAR
  40→8 first 4x coast q=29.5 kPa apo 8.8 km). Do **not** Hangar
  proc-long / long-cone / long-hs (1231 L — ProceduralPartsTank1500L
  generalRocketry LOCKED). Do **not** Hangar proc-tank-pbc (T+38 shear).
  stiff-dv 1440 kero / 6x girder 14-03-34Z Forest apo 33046 rec=yes —
  not FlyingHigh 50 km. f013: 2HOT start unlocked=yes on_craft=yes;
  Goo start unlocked=yes on_craft=yes; geiger e101 unlocked=yes
  on_craft=yes; PresMat stability unlocked=yes on_craft=yes;
  TELEMETRY Stayputnik on_craft=yes. Thin tape T-284.
  fingerprint bigger-dv. Not a Flea.
