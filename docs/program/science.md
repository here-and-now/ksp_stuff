# Linus board — science dump

Dump of **science tickets**, not dispatch. Bind is ticket payload.
Catalog (`unbound`) is the shelf. This-hop work is **bound**.

Craft `kspstuff-hop-valiant-proc-long-pbc`. Tree `start,engineering101,basicRocketry,survivability`. Bank **8.7721**. Next CTT
`stability` 18 → need ~**9.23**. Recover banks for hops; transmit is a radio (rate on `comms`), not the hop path. F-013:
instrument part, never Stayputnik PAW as Geiger.

```bash
python main.py science-scan
python main.py comms
python main.py tickets list --type science
```

---

## Bound (this hop)

| ticket | experiment_id | situation | biome | part | duration_s | ec_rate | est | recover_banks |
|---|---|---|---|---|---|---|---|---|
| **T-069** | `kerbalism_TELEMETRY` | FlyingHigh@Forest | Forest | `probeCoreOcto_v2` | 25 | 0.052 | 1.512 | yes |
| **T-077** | `temperatureScan` | SrfLanded@Forest | Forest | `sensorThermometer` | 83 | 0.002 | 0.54 | yes |
| **T-287** | `kerbalism_TELEMETRY` | SrfLanded@Forest | Forest | `probeCoreOcto_v2` | 30 | 0.052 | 0.6 | yes |
| **T-288** | `kerbalism_TELEMETRY` | SrfSplashed@Forest | Forest | `probeCoreOcto_v2` | 6 | 0.052 | 0.16 | yes |
| **T-313** | `temperatureScan` | SrfSplashed@Forest | Forest | `sensorThermometer` | 138 | 0.002 | 0.9 | yes |

## Catalog (unbound shelf — not `ops next` / not hop bind)

| ticket | experiment_id | situation | biome | part | duration_s | ec_rate | est | recover_banks |
|---|---|---|---|---|---|---|---|---|
| **T-025** | `` | FlyingLow@Water | Water | `sensorThermometer` | 138 | 0.002 | 2.1 | yes |
| **T-026** | `` | FlyingLow@Water | Water | `probeCoreOcto_v2` | 30 | 0.052 | 1.4 | yes |
| **T-027** | `` | FlyingHigh@Water | Water | `probeCoreOcto_v2` | 30 | 0.052 | 1.8 | yes |
| **T-028** | `kerbalism_TELEMETRY` | SrfSplashed@Water | Water | `probeCoreOcto_v2` | 30 | 0.052 | 0.8 | yes |
| **T-070** | `temperatureScan` | FlyingLow@Grasslands | Grasslands | `sensorThermometer` | 138 | 0.002 | 2.1 | yes |
| **T-071** | `kerbalism_TELEMETRY` | FlyingLow@Grasslands | Grasslands | `probeCoreOcto_v2` | 30 | 0.052 | 1.4 | yes |
| **T-072** | `temperatureScan` | FlyingLow@Tropics | Tropics | `sensorThermometer` | 138 | 0.002 | 2.1 | yes |
| **T-073** | `temperatureScan` | FlyingLow@Savanna | Savanna | `sensorThermometer` | 138 | 0.002 | 2.1 | yes |
| **T-074** | `kerbalism_TELEMETRY` | FlyingLow@Tropics | Tropics | `probeCoreOcto_v2` | 30 | 0.052 | 1.4 | yes |
| **T-075** | `kerbalism_TELEMETRY` | FlyingLow@Savanna | Savanna | `probeCoreOcto_v2` | 30 | 0.052 | 1.4 | yes |
| **T-076** | `` | FlyingHigh@Grasslands | Grasslands | `probeCoreOcto_v2` | 30 | 0.052 | 1.8 | yes |
| **T-078** | `temperatureScan` | SrfLanded@Grasslands | Grasslands | `sensorThermometer` | 138 | 0.002 | 0.9 | yes |
| **T-079** | `kerbalism_TELEMETRY` | SrfLanded@Grasslands | Grasslands | `probeCoreOcto_v2` | 30 | 0.052 | 0.6 | yes |
| **T-090** | `temperatureScan` | SrfLanded@Tropics | Tropics | `sensorThermometer` | 138 | 0.002 | 0.9 | yes |
| **T-091** | `temperatureScan` | SrfLanded@Savanna | Savanna | `sensorThermometer` | 138 | 0.002 | 0.9 | yes |
| **T-092** | `kerbalism_TELEMETRY` | SrfLanded@Tropics | Tropics | `probeCoreOcto_v2` | 30 | 0.052 | 0.6 | yes |
| **T-093** | `kerbalism_TELEMETRY` | SrfLanded@Savanna | Savanna | `probeCoreOcto_v2` | 30 | 0.052 | 0.6 | yes |
| **T-117** | `temperatureScan` | FlyingLow@Tundra | Tundra | `sensorThermometer` | 138 | 0.002 | 2.1 | yes |
| **T-118** | `kerbalism_TELEMETRY` | FlyingLow@Tundra | Tundra | `probeCoreOcto_v2` | 30 | 0.052 | 1.4 | yes |
| **T-119** | `temperatureScan` | FlyingLow@Mountains | Mountains | `sensorThermometer` | 138 | 0.002 | 2.1 | yes |
| **T-120** | `kerbalism_TELEMETRY` | FlyingLow@Mountains | Mountains | `probeCoreOcto_v2` | 30 | 0.052 | 1.4 | yes |
| **T-121** | `temperatureScan` | FlyingLow@Desert | Desert | `sensorThermometer` | 138 | 0.002 | 2.1 | yes |
| **T-122** | `kerbalism_TELEMETRY` | FlyingLow@Desert | Desert | `probeCoreOcto_v2` | 30 | 0.052 | 1.4 | yes |
| **T-123** | `temperatureScan` | FlyingLow@Ice Caps | Ice Caps | `sensorThermometer` | 138 | 0.002 | 2.1 | yes |
| **T-124** | `kerbalism_TELEMETRY` | FlyingLow@Ice Caps | Ice Caps | `probeCoreOcto_v2` | 30 | 0.052 | 1.4 | yes |
| **T-125** | `temperatureScan` | FlyingLow@Taiga | Taiga | `sensorThermometer` | 138 | 0.002 | 2.1 | yes |
| **T-126** | `kerbalism_TELEMETRY` | FlyingLow@Taiga | Taiga | `probeCoreOcto_v2` | 30 | 0.052 | 1.4 | yes |
| **T-289** | `temperatureScan` | SrfLanded@Tundra | Tundra | `sensorThermometer` | 138 | 0.002 | 0.9 | yes |
| **T-290** | `kerbalism_TELEMETRY` | SrfLanded@Tundra | Tundra | `probeCoreOcto_v2` | 30 | 0.052 | 0.6 | yes |
| **T-292** | `temperatureScan` | SrfLanded@Mountains | Mountains | `sensorThermometer` | 138 | 0.002 | 0.9 | yes |
| **T-293** | `kerbalism_TELEMETRY` | SrfLanded@Mountains | Mountains | `probeCoreOcto_v2` | 30 | 0.052 | 0.6 | yes |
| **T-295** | `temperatureScan` | SrfLanded@Desert | Desert | `sensorThermometer` | 138 | 0.002 | 0.9 | yes |
| **T-296** | `kerbalism_TELEMETRY` | SrfLanded@Desert | Desert | `probeCoreOcto_v2` | 30 | 0.052 | 0.6 | yes |
| **T-298** | `temperatureScan` | SrfLanded@Ice Caps | Ice Caps | `sensorThermometer` | 138 | 0.002 | 0.9 | yes |
| **T-299** | `kerbalism_TELEMETRY` | SrfLanded@Ice Caps | Ice Caps | `probeCoreOcto_v2` | 30 | 0.052 | 0.6 | yes |
| **T-301** | `temperatureScan` | SrfLanded@Taiga | Taiga | `sensorThermometer` | 138 | 0.002 | 0.9 | yes |
| **T-302** | `kerbalism_TELEMETRY` | SrfLanded@Taiga | Taiga | `probeCoreOcto_v2` | 30 | 0.052 | 0.6 | yes |
| **T-080** | `geigerCounter` | SrfLanded@Forest | Forest | `kerbalism-geigercounter` | 497 | 0.005 | 1.2 | yes |
| **T-094** | `` | FlyingHigh@Tropics | Tropics | `probeCoreOcto_v2` | 30 | 0.052 | 1.8 | yes |
| **T-095** | `` | FlyingHigh@Savanna | Savanna | `probeCoreOcto_v2` | 30 | 0.052 | 1.8 | yes |
| **T-291** | `` | FlyingHigh@Tundra | Tundra | `probeCoreOcto_v2` | 30 | 0.052 | 1.8 | yes |
| **T-294** | `` | FlyingHigh@Mountains | Mountains | `probeCoreOcto_v2` | 30 | 0.052 | 1.8 | yes |
| **T-297** | `` | FlyingHigh@Desert | Desert | `probeCoreOcto_v2` | 30 | 0.052 | 1.8 | yes |
| **T-300** | `` | FlyingHigh@Ice Caps | Ice Caps | `probeCoreOcto_v2` | 30 | 0.052 | 1.8 | yes |
| **T-303** | `` | FlyingHigh@Taiga | Taiga | `probeCoreOcto_v2` | 30 | 0.052 | 1.8 | yes |
| **T-316** | `geigerCounter` | FlyingLow |  | `kerbalism-geigercounter` | 56 | 0.005 | 0.316 | yes |

Desk leftover vessels n=0. Query desk leftover-science.
