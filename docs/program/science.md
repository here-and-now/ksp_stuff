# Linus board — science dump

Query, then write. Do not copy Squad Start from memory.

```bash
python main.py science-scan
```

Desk leftover-science is the sit. Do not re-run `world` / `parts` if
`desk.md` is this sit.

kRPC 0.6 has `get_Science` only. Disk is the scan. F-013: bind
`geigerCounter` only on `kerbalism-geigercounter`, never Stayputnik
PAW. File experiments credit while recording. Do not transmit. PBC
unmanned. Mk1 locked (`simpleCommandModules`, 90). RW locked
(`stability`, 18). Barometer lives on that node — do not bind it.

Bind lives on **science-ticket payload**, not this file. Seated
**`kspstuff-hop-valiant-proc-stiff-pbc`** (`capable: yes`). T-089
chute-stiff-pbc / proc-tank-pbc / chute-pbc are prior hangs. east-t3
is **retired**.

Working goal **15** is **spent** (`survivability` owned). Next honest
CTT spend is **stability 18**. Bank **7.7748** → need **~10.23**.

Desk leftover-science lists only started leftover **>0.02**. **Missing
id = unstarted.** Capped ids do not appear there.

---

## Bound (this sit)

Craft **`kspstuff-hop-valiant-proc-stiff-pbc`** (OKTO + Mk16 + 2HOT
+ Goo). Do **not** bind east-t3 / chute-pbc / proc-tank-pbc.
recover_banks **yes**. Do not transmit. OKTO tape **16.28 MB**. Do
**not** co-run geiger (wait Gus T-113; OKTO PAW is not the part).
Do not bind Water. Do not bind FlyingHigh. T-019 / T-020 **wont**.
T-025..T-028 Water still **unbound** wait heading **090**. T-068
**done** (Forest FlyingLow thermo **remaining=0**). T-111 **done**
(duplicate of T-071). T-112 **done** (FlyingLow goo **remaining=0**).
T-150 **done** (same notice).

Os: not thermo-only. T-070 Grasslands FlyingLow thermo 2.10 + T-071
Grasslands TELEMETRY 1.40 still bound. Forest FlyingLow thermo
**capped** (T-068 11-11-21Z +2.10). Forest+Shores FlyingLow
TELEMETRY **capped**. Goo FlyingLow **capped**. Do not re-run goo.
Do not bind geiger. 11-11-21Z heading **299** biomes Shores,Forest
— not Water, not Grasslands.

| ticket | experiment_id | situation | biome | part | instrument | tech | unlocked | on_craft | duration_s | ec_rate | est | recover_banks | seq |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **T-070** | `temperatureScan` | FlyingLow | **Grasslands** | `sensorThermometer` | 2HOT Thermometer | start | yes | yes | **138** | 0.002 | **2.10** | yes | **1** |
| **T-071** | `kerbalism_TELEMETRY` | FlyingLow | **Grasslands** | `probeCoreOcto_v2` | OKTO PAW (no Science part) | start | yes | yes | **30** | 0.052 | **1.40** | yes | **2** |

---

## Banked (do not re-fly)

Live `sci = 7.7748` (desk; +2.103 T-068). Unlocked: **`start`,
`engineering101`, `basicRocketry`, `survivability`**. leftover
vessels n=0. Do not recover Ast. XRL-564. Mk16 / RC_cone
**Available**.

Save leftovers (cap − sci). Missing id = unstarted:

| subject | sci/cap | left | honest |
|---|---|---|---|
| `geigerCounter@EarthSrfLandedShores` | 1.20/1.20 | 0 | **capped** — not Cape again |
| `mysteryGoo@EarthSrfLanded` | 1.80/1.80 | 0 | **capped** Earth-global (F-005) |
| `mysteryGoo@EarthSrfSplashed` | 2.40/2.40 | 0 | **capped global** — T-019 spent |
| `kerbalism_TELEMETRY@EarthSrfLandedShores` | 0.60/0.60 | 0 | **capped** |
| `kerbalism_TELEMETRY@EarthSrfLandedForest` | 0.60/0.60 | 0 | **capped** Forest pad |
| `kerbalism_TELEMETRY@EarthSrfSplashedShores` | 0.80/0.80 | 0 | **capped** — T-020 spent |
| `kerbalism_TELEMETRY@EarthFlyingLowShores` | 1.40/1.40 | 0 | **capped** |
| `kerbalism_TELEMETRY@EarthFlyingLowForest` | 1.40/1.40 | 0 | **capped** |
| `temperatureScan@EarthSrfLandedShores` | 0.90/0.90 | 0 | **capped** |
| `temperatureScan@EarthFlyingLowShores` | 2.10/2.10 | 0 | **capped** |
| `temperatureScan@EarthFlyingLowForest` | 2.10/2.10 | 0 | **capped** — T-068 spent |
| `temperatureScan@EarthSrfLandedForest` | 0.063/0.90 | **0.837** | leftover crumbs — **T-077** |
| `temperatureScan@EarthFlyingHigh` | 2.70/2.70 | 0 | **capped global** — no other-biome FlyingHigh thermo |
| `kerbalism_TELEMETRY@EarthFlyingHighShores` | 1.80/1.80 | 0 | **capped Shores** |
| `mysteryGoo@EarthFlyingLow` | 4.20/4.20 | 0 | **capped global** — T-112 spent |
| `recovery@EarthFlew` | 6.00/6.00 | 0 | **gone** — living recover does not re-pay Flew |
| `geigerCounter@EarthFlyingLow` | 2.484/2.80 | **0.316** | crumbs — not a node |
| `kerbalism_TELEMETRY@EarthFlyingHighForest` | 0.288/1.80 | **1.512** | leftover — **T-069** |

Splash goo **2.40** + Shores splash TELEMETRY **0.80** were the 15
close. They are in the save as capped. **Do not re-fly.**

Scan marks `*@Biomes` **capped** when one biome leftover is 0, and
**left=sum** when any biome leftover exists. **Sibling biomes with no
id are unstarted**, not spent.

Caps from Kerbalism value × situation (surface 0.3, splash 0.4,
FlyingLow 0.7, FlyingHigh 0.9): geiger 4, thermo 3, TELEMETRY 2,
goo 6.

RSS Earth biomes: Shores, Grasslands, Tundra, Mountains, Desert,
Tropics, Ice Caps, Water, Taiga, Forest, Savanna. FlyingLow <50 km.
FlyingHigh 50 km → Space ~140 km. InSpace is orbit, not this hop.

---

## Paying remaining (unbound)

`recover_banks` **yes**. Do not transmit. OKTO tape **16.28 MB**. Do
**not** co-run geiger. TELEMETRY host is **OKTO PAW**, not Stayputnik.

Cape **Shores** pad/splash/FlyingLow on thermo + TELEMETRY, Surface
geiger, landed/splash goo, and FlyingLow goo are **capped**. Same-pad
is not more science (F-005).

| ticket | wait_experiment_id | situation | duration_s | ec_rate | est | honest |
|---|---|---|---|---|---|---|
| **T-072** | `temperatureScan` | FlyingLow@Tropics | **138** | 0.002 | **2.10** | not this hop |
| **T-073** | `temperatureScan` | FlyingLow@Savanna | **138** | 0.002 | **2.10** | not this hop |
| **T-074** | `kerbalism_TELEMETRY` | FlyingLow@Tropics | **30** | 0.052 | **1.40** | not this hop |
| **T-075** | `kerbalism_TELEMETRY` | FlyingLow@Savanna | **30** | 0.052 | **1.40** | not this hop |
| **T-117** | `temperatureScan` | FlyingLow@Tundra | **138** | 0.002 | **2.10** | not this Cape hop |
| **T-118** | `kerbalism_TELEMETRY` | FlyingLow@Tundra | **30** | 0.052 | **1.40** | not this Cape hop |
| **T-119** | `temperatureScan` | FlyingLow@Mountains | **138** | 0.002 | **2.10** | not this Cape hop |
| **T-120** | `kerbalism_TELEMETRY` | FlyingLow@Mountains | **30** | 0.052 | **1.40** | not this Cape hop |
| **T-121** | `temperatureScan` | FlyingLow@Desert | **138** | 0.002 | **2.10** | not this Cape hop |
| **T-122** | `kerbalism_TELEMETRY` | FlyingLow@Desert | **30** | 0.052 | **1.40** | not this Cape hop |
| **T-123** | `temperatureScan` | FlyingLow@Ice Caps | **138** | 0.002 | **2.10** | not this Cape hop |
| **T-124** | `kerbalism_TELEMETRY` | FlyingLow@Ice Caps | **30** | 0.052 | **1.40** | not this Cape hop |
| **T-125** | `temperatureScan` | FlyingLow@Taiga | **138** | 0.002 | **2.10** | not this Cape hop |
| **T-126** | `kerbalism_TELEMETRY` | FlyingLow@Taiga | **30** | 0.052 | **1.40** | not this Cape hop |
| **T-069** | `kerbalism_TELEMETRY` | FlyingHigh@Forest | **30** | 0.052 | **1.51** left | **not this hop** — ≥50 km |
| **T-076** | `kerbalism_TELEMETRY` | FlyingHigh@Grasslands | **30** | 0.052 | **1.80** | **not this hop** — ≥50 km |
| **T-077** | `temperatureScan` | SrfLanded@Forest | **138** | 0.002 | **0.84** left | leftover 0.063/0.90 — wait chute land |
| **T-078** | `temperatureScan` | SrfLanded@Grasslands | **138** | 0.002 | **0.90** | wait chute land |
| **T-079** | `kerbalism_TELEMETRY` | SrfLanded@Grasslands | **30** | 0.052 | **0.60** | wait chute land |
| **T-090** | `temperatureScan` | SrfLanded@Tropics | **138** | 0.002 | **0.90** | wait chute land |
| **T-091** | `temperatureScan` | SrfLanded@Savanna | **138** | 0.002 | **0.90** | wait chute land |
| **T-092** | `kerbalism_TELEMETRY` | SrfLanded@Tropics | **30** | 0.052 | **0.60** | wait chute land |
| **T-093** | `kerbalism_TELEMETRY` | SrfLanded@Savanna | **30** | 0.052 | **0.60** | wait chute land |
| **T-080** | `geigerCounter` | SrfLanded@Forest | **497** | 0.005 | **1.20** | wait Gus T-113 `kerbalism-geigercounter` |
| **T-094** | `kerbalism_TELEMETRY` | FlyingHigh@Tropics | **30** | 0.052 | **1.80** | **not this hop** — ≥50 km |
| **T-095** | `kerbalism_TELEMETRY` | FlyingHigh@Savanna | **30** | 0.052 | **1.80** | **not this hop** — ≥50 km |

T-069 needs loft **≥50 km** over Forest (last hop apo **30.8 km**).
T-080 waits a **Geiger Science part** on the chute stack (F-013; tree
**survivability** unlocked, **on_craft no**). 138 s thermo is a
**chute hang**, not a lithobrake. Forest landed TELEMETRY already
capped.

---

## Unbound (090 tape) — not flying ids

**Do not bind FlyingLow@Water or any Water biome** until a hop-to-water
**jsonl** holds heading **090**. 23-15 / 22-57 / 22-03 / 16-57 / 16-33
tapes **never 090**. These tickets have **no `experiment_id`**. Craft
east-t3 stripped.

| ticket | wait_experiment_id | situation | duration_s | ec_rate | est |
|---|---|---|---|---|---|
| **T-025** | `temperatureScan` | FlyingLow@Water | **138** | 0.002 | **2.10** |
| **T-026** | `kerbalism_TELEMETRY` | FlyingLow@Water | **30** | 0.052 | **1.40** |
| **T-027** | `kerbalism_TELEMETRY` | FlyingHigh@Water | **30** | 0.052 | **1.80** |
| **T-028** | `kerbalism_TELEMETRY` | SrfSplashed@Water | **30** | 0.052 | **0.80** |

Water splash TELEMETRY still **unstarted** (Shores splash TELEMETRY is
the capped sibling). Thermo has **no splash** situation.

---

## Hang wall / skip (not a chute-hop finish)

| experiment_id | situation | duration_s | ec_rate | est | honest |
|---|---|---|---|---|---|
| `mysteryGoo` | FlyingLow **global** | **641** | 0.18 | **4.20** | **T-112 banked remaining=0** — do not re-fly |
| `mysteryGoo` | FlyingHigh **global** | **641** | 0.18 | **5.40** | hang wall — **not this hop** |
| `geigerCounter` | FlyingLow **global** | **497** | 0.005 | left **0.32** | crumbs |
| `geigerCounter` | FlyingHigh **global** | **497** | 0.005 | **3.60** | 497 s will not finish |

---

## Scan REACH that is not a bind

Crew rows are a lie on PBC. Locked instruments are not a pad/hop sit.

| experiment_id | scan | est. | honest |
|---|---|---|---|
| `evaReport` Surface | REACH ~3.00 | — | **skip** — Mk1 locked, no crew |
| `evaScience` Surface | REACH ~3.00 | — | **skip** — Mk1 locked |
| `surfaceSample` SrfLanded | REACH ~6.60 | — | **skip** — Mk1 locked |
| `telemetryReport` Surface | REACH ~0.60 | — | **skip** — Cape no new site |
| `seismicScan` | locked landing | — | **do not bind** |
| `ROCScience` | locked advExploration | — | **do not bind** |
| `barometerScan` | locked stability | — | **do not bind** — the 18 node |

---

## Instruments (tree)

Stayputnik PAW is **not** the Geiger. Hosted `geigerCounter` on
Stayputnik is **not** bind hardware.

| experiment_id | instrument | tech | unlocked | on stiff-pbc | bind |
|---|---|---|---|---|---|
| `temperatureScan` | `sensorThermometer` (2HOT) | start | **yes** | **yes** | **T-068** / **T-070** FlyingLow |
| `kerbalism_TELEMETRY` | OKTO PAW (no Science part) | start | **yes** | hosted `probeCoreOcto_v2` | **T-071** Grasslands FlyingLow |
| `mysteryGoo` | `GooExperiment` | start | **yes** | **yes** | **no** — FlyingLow banked T-112; landed/splash capped |
| `geigerCounter` | `kerbalism-geigercounter` | survivability | **yes** | **no** (OKTO PAW is not the part) | **no** — wait T-113 |

`seismicScan` landing LOCKED. LITE InSpace (e101, ~10 s) — orbit /
Space ~140 km, not this hop. MITE `generalRocketry` LOCKED. SITE
`advRocketry` LOCKED. Crew eva/sample: Mk1 locked.

---

## Out of reach / locked

InSpace LITE/TELEMETRY/geiger/thermo/goo — orbit (Space ~140 km).
LITE **unlocked** e101; envelope is the lock. MITE/SITE tree LOCKED.
`seismicScan` `sensorAccelerometer` **landing** LOCKED. Barometer
`stability` 18 LOCKED (wheel lives on the same node). ROCScience
**advExploration** LOCKED. Crew reports: Mk1 locked.

---

## Horizon, not a second bind

Ast. XRL-564 — InSpace someday. Do not recover the rock.

One line of future: Forest/Grasslands FlyingLow thermo **2.10** +
Grasslands TELEMETRY **1.40** toward stability **18**. FlyingLow
goo is spent. Not Water until heading **090**. Not 497 s. Not
scan-REACH crew.
