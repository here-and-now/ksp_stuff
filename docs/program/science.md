# Linus board — science program

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

**Unbound.** Os east Water campaign. Gus **T-014** east Valiant in
parallel — **do not bind** until `capable: yes` on **that** craft.
**Do not bind** `kspstuff-hop-valiant-t7-splash-pbc`. T-008 vertical
splash **parked**. **Do not bind FlyingLow@Water or any Water biome**
until a new hop-to-water **jsonl** holds **heading 090**. 16-57 / 16-33
tapes **never 090**. last-flight is **hop-splash abort**, not that
tape.

Working goal **15**. Bank **13.2632** → need **~1.74**. FlyingLow
geiger leftover **0.32** crumbs — not a node. FlyingHigh Forest
TELEMETRY leftover **1.51** does not close (13.26+1.51=14.77, **0.23
short**).

Desk leftover-science lists only started leftover **>0.02**. **Missing
id = unstarted.** Do not treat the leftover block as the REACH board.
**T-004** is that rule.

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
splash TELEMETRY have **no save id** — unstarted, even though leftover
does not list them. Splash goo is **global**.

Caps from Kerbalism value × situation (surface 0.3, splash 0.4,
FlyingLow 0.7, FlyingHigh 0.9): geiger 4, thermo 3, TELEMETRY 2,
goo 6.

---

## Unstarted (missing id) — leftover hid these

| experiment_id | situation | duration_s | ec_rate | est. | honest |
|---|---|---|---|---|---|
| `mysteryGoo` | SrfSplashed **global** | **641** | 0.18 | **2.40** | **pays 15** if sit=splashed — **unbound** (not t7) |
| `kerbalism_TELEMETRY` | SrfSplashed@Biomes | **30** | 0.052 | **0.80** | **T-009** unstarted; sequential first after splash; tape 0.75 |
| `geigerCounter` | FlyingHigh **global** | **497** | 0.005 | **3.60** | unlocked e101; 497 s will not finish on a hop recover |
| `mysteryGoo` | FlyingLow **global** | **641** | 0.18 | **4.20** | scan REACH; **will not finish** airborne |
| `kerbalism_TELEMETRY` | FlyingHigh@Water (etc.) | **30** | 0.052 | **1.80** | unstarted sibling of Forest leftover; **090 first** |
| `temperatureScan` | FlyingLow@Water | **138** | 0.002 | **2.10** | unstarted; **do not bind** until heading **090** |
| `kerbalism_TELEMETRY` | FlyingLow@Water | **30** | 0.052 | **1.40** | same; Water needs heading |

---

## East campaign — opportunities, no bind

T-013 hop-to-water blocked on Gus **T-014**. Prior east stacks often
carried **2HOT + Stayputnik**, **no Goo**. Do not assume goo on the
unsigned east craft.

| path | est. | vs gap ~1.74 | bind |
|---|---|---|---|
| splash goo **global** | **2.40** | **closes 15** | **no** — wait T-014 + Goo on stack + sit=splashed |
| splash TELEMETRY (T-009) | **0.80** | 0.94 short alone | **no** — keep ticket; payload after Water too |
| splash pair sequential | **3.20** | overshoots | **no** — TELEMETRY **30 s** then goo **641 s**; not airborne |
| FlyingLow@Water thermo+TELEMETRY | **2.10+1.40=3.50** | **closes 15** | **no** — tape must hold **090** |
| FlyingHigh Forest TELEMETRY leftover | **1.51** | **0.23 short** | **no** — not this hang |
| FlyingLow geiger leftover | **0.32** | crumbs | **no** |

Do **not** co-run geiger with TELEMETRY **0.75 MB**. Do **not** Toggle
TELEMETRY airborne (19-43 Forest leftover). recover_banks **yes**. Do
not transmit.

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

## Instruments (tree, not a bind)

Seated desk craft is **t7-splash** (parked). f013 on that stack is
not a Water bind. Stayputnik PAW is **not** the Geiger.

| experiment_id | instrument | tech | unlocked | on seated t7 | bind |
|---|---|---|---|---|---|
| `mysteryGoo` | `GooExperiment` | start | **yes** | **yes** | **no** |
| `kerbalism_TELEMETRY` | Stayputnik PAW | start | **yes** | hosted | **no** — T-009 keep |
| `temperatureScan` | `sensorThermometer` (2HOT) | start | **yes** | **yes** | **no** — Water needs 090 |
| `geigerCounter` | `kerbalism-geigercounter` | e101 | **yes** | **yes** | **no** — tape vs TELEMETRY |

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

One line of future: splash goo **2.40** (if goo flies) or FlyingLow@Water
thermo+TELEMETRY **3.50** (if heading **090**) is the 15-sci node.
Not Forest High TELEMETRY 1.51, not leftover geiger 0.32, not 497 s,
not scan-REACH crew, not a t7-splash bind.
