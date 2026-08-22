# Linus board — science dump

Query, then write. Do not copy Squad Start from memory.

```bash
python main.py science-scan
python main.py world
python main.py parts --unlocked --search geiger
```

kRPC 0.6 has `get_Science` only. Disk is the scan. F-013: bind
`geigerCounter` only on `kerbalism-geigercounter`, never Stayputnik
PAW. File experiments credit while recording. Do not transmit. PBC
unmanned. Mk1 locked (`simpleCommandModules`, 90). Chute locked
(`survivability`, 15). RW locked (`stability`, 18).

Bind lives on **science-ticket payload**, not this file. Gus **T-014**
`capable: yes` **`kspstuff-hop-valiant-east-t3-pbc`**. Do **not** bind
`kspstuff-hop-valiant-t7-splash-pbc`. T-008 parked.

Working goal **15**. Bank **13.2632** → need **~1.74**. FlyingLow
geiger leftover **0.32** crumbs — not a node. FlyingHigh Forest
TELEMETRY leftover **1.51** does not close (13.26+1.51=14.77, **0.23
short**).

Desk leftover-science lists only started leftover **>0.02**. **Missing
id = unstarted.** **T-004** closed that rule.

---

## Bound (east-t3, this sit)

Craft **`kspstuff-hop-valiant-east-t3-pbc`**. Sequential after
`sit=splashed`: **T-020** then **T-019**. recover_banks **yes**. Do
not transmit. Tape **0.75 MB** — do **not** co-run geiger. Do not
Toggle TELEMETRY airborne (19-43 Forest leftover). 23-15-52Z abort
wanted mysteryGoo: airborne skip (not flying ids), then splash skip
**no Experiment modules** after **220 m/s** Shores heading **304**.
That is Lars **T-024** / **T-016**, not an unbind. Chute still LOCKED.

| ticket | experiment_id | situation | biome | part | instrument | tech | unlocked | on_craft | duration_s | ec_rate | est | recover_banks | seq |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **T-020** | `kerbalism_TELEMETRY` | SrfSplashed | **Shores** | `probeCoreSphere_v2` | Stayputnik PAW (no Science-category part) | start | yes | yes | **30** | 0.052 | **0.80** | yes | **0** |
| **T-019** | `mysteryGoo` | SrfSplashed | **global** | `GooExperiment` | Mystery Goo Containment Unit | start | yes | yes | **641** | 0.18 | **2.40** | yes | **1** |

Splash goo **2.40** closes **15**. Pair **3.20** overshoots. Goo is
**global** — do **not** wait heading **090** to run T-019. TELEMETRY
is biome-tagged: honest bind is **Shores** (23-15 / 22-57 / 22-03
tapes; never 090). **Do not fake Water.**

---

## Banked (do not re-fly)

Live `sci = 13.2632` (desk). Unlocked: **`start`, `engineering101`,
`basicRocketry`**. leftover vessels n=0. Do not recover Ast. XRL-564.

Save leftovers (cap − sci). Missing id = unstarted:

| subject | sci/cap | left | honest |
|---|---|---|---|
| `geigerCounter@EarthSrfLandedShores` | 1.20/1.20 | 0 | **capped** — not Cape again |
| `mysteryGoo@EarthSrfLanded` | 1.80/1.80 | 0 | **capped** Earth-global (F-005) |
| `kerbalism_TELEMETRY@EarthSrfLandedShores` | 0.60/0.60 | 0 | **capped** |
| `kerbalism_TELEMETRY@EarthSrfLandedForest` | 0.60/0.60 | 0 | **capped** Forest pad |
| `kerbalism_TELEMETRY@EarthFlyingLowShores` | 1.40/1.40 | 0 | **capped** |
| `kerbalism_TELEMETRY@EarthFlyingLowForest` | 1.40/1.40 | 0 | **capped** |
| `temperatureScan@EarthSrfLandedShores` | 0.90/0.90 | 0 | **capped** |
| `temperatureScan@EarthFlyingLowShores` | 2.10/2.10 | 0 | **capped** |
| `temperatureScan@EarthFlyingHigh` | 2.70/2.70 | 0 | **capped global** — no other-biome FlyingHigh thermo |
| `kerbalism_TELEMETRY@EarthFlyingHighShores` | 1.80/1.80 | 0 | **capped Shores** |
| `recovery@EarthFlew` | 5.999/6.00 | ~0 | **gone** |
| `geigerCounter@EarthFlyingLow` | 2.484/2.80 | **0.316** | crumbs — not a node |
| `kerbalism_TELEMETRY@EarthFlyingHighForest` | 0.288/1.80 | **1.512** | leftover — **0.23 short** of 15 |

Scan marks `*@Biomes` **capped** when one biome leftover is 0, and
**left=sum** when any biome leftover exists. **Sibling biomes with no
id are unstarted**, not spent. Forest FlyingHigh leftover **hides**
unstarted FlyingHigh TELEMETRY at Water and others. Splash goo /
splash TELEMETRY have **no save id** — unstarted until this bind
credits. Splash goo is **global**.

Caps from Kerbalism value × situation (surface 0.3, splash 0.4,
FlyingLow 0.7, FlyingHigh 0.9): geiger 4, thermo 3, TELEMETRY 2,
goo 6.

---

## Unbound (090 tape) — not flying ids

**Do not bind FlyingLow@Water or any Water biome** until a hop-to-water
**jsonl** holds heading **090**. 23-15 / 22-57 / 22-03 / 16-57 / 16-33
tapes **never 090**. last-flight is **23-15 abort**, not that tape.
These tickets have **no `experiment_id`** so hop does not start them.

| experiment_id | situation | duration_s | ec_rate | est. | honest |
|---|---|---|---|---|---|
| `kerbalism_TELEMETRY` | SrfSplashed@Water | **30** | 0.052 | **0.80** | sibling of T-020 Shores; **090 first** |
| `temperatureScan` | FlyingLow@Water | **138** | 0.002 | **2.10** | 2HOT on stack; **090 first** |
| `kerbalism_TELEMETRY` | FlyingLow@Water | **30** | 0.052 | **1.40** | same; Water needs heading |
| `kerbalism_TELEMETRY` | FlyingHigh@Water | **30** | 0.052 | **1.80** | unstarted sibling of Forest leftover; **090 first** |
| `geigerCounter` | FlyingHigh **global** | **497** | 0.005 | **3.60** | unlocked e101; 497 s will not finish on a hop recover |
| `mysteryGoo` | FlyingLow **global** | **641** | 0.18 | **4.20** | scan REACH; **will not finish** airborne |

---

## Scan REACH that is not a bind

Scan `in_reach` is pad Shores / FlyingLow hop only. Crew rows are a
lie on PBC. Locked instruments are not a pad/hop sit.

| experiment_id | scan | est. | honest |
|---|---|---|---|
| `evaReport` Surface | REACH ~3.00 | — | **skip** — Mk1 locked, no crew |
| `evaScience` Surface | REACH ~3.00 | — | **skip** — Mk1 locked |
| `surfaceSample` SrfLanded | REACH ~6.60 | — | **skip** — Mk1 locked |
| `telemetryReport` Surface | REACH ~0.60 | — | **skip** — Cape/other biomes no site; 0.60 does not close 1.74 |
| `mysteryGoo` FlyingLow | REACH ~4.20 | 641 s | hang wall — do not brief finished |
| `geigerCounter` FlyingLow | REACH left 0.32 | 497 s | crumbs |
| `seismicScan` | locked landing | — | **do not bind** |
| `ROCScience` | locked advExploration | — | **do not bind** |
| `barometerScan` | locked stability | — | **do not bind** |

---

## Instruments (tree, east-t3)

Stayputnik PAW is **not** the Geiger. Hosted `geigerCounter` on
Stayputnik is **not** bind hardware this sit.

| experiment_id | instrument | tech | unlocked | on east-t3 | bind |
|---|---|---|---|---|---|
| `mysteryGoo` | `GooExperiment` | start | **yes** | **yes** | **T-019** splash global |
| `kerbalism_TELEMETRY` | Stayputnik PAW (no Science part) | start | **yes** | hosted | **T-020** splash Shores |
| `temperatureScan` | `sensorThermometer` (2HOT) | start | **yes** | **yes** | **no** — Water needs 090; Shores FlyingLow capped |
| `geigerCounter` | `kerbalism-geigercounter` | e101 | **yes** | PAW only | **no** — not a Science-category part on hang |

`seismicScan` landing LOCKED. LITE InSpace (e101, ~10 s) — orbit /
Space ~140 km, not this hop. MITE `generalRocketry` LOCKED. SITE
`advRocketry` LOCKED. Crew eva/sample: Mk1 locked.

---

## Out of reach / locked

InSpace LITE/TELEMETRY/geiger/thermo/goo — orbit (Space ~140 km).
LITE **unlocked** e101; envelope is the lock. MITE/SITE tree LOCKED.
`seismicScan` `sensorAccelerometer` **landing** LOCKED. Barometer
`stability` 18 LOCKED (wheel lives on the same node). ROCScience
**advExploration** LOCKED. Crew reports: Mk1 locked. Chute
**survivability** 15 LOCKED.

---

## Horizon, not a second bind

Ast. XRL-564 — InSpace someday. Do not recover the rock. Chute is
still 15.

One line of future: splash goo **2.40** on a living can closes 15.
FlyingLow@Water thermo+TELEMETRY **3.50** only if heading **090**.
Not Forest High TELEMETRY 1.51, not leftover geiger 0.32, not 497 s,
not scan-REACH crew, not a t7-splash bind.
