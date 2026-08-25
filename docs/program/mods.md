# Mods — `~/Games/KSP-rss`

Disk, 2026-08-23. Save `letsgrok`. KSP **1.12.5**. CKAN
`installed-portable`. **Not Realism Overhaul** — that copy is
`~/Games/KSP-RO` and is parked.

The mods that change the world (RSS, Kerbalism, FAR, RealHeat,
RealChute, kRPC, PBC, CTT, RealFuels-as-names) are on the
[README](../../README.md#the-world). This page is the rest of
GameData: visuals, catalogs, HUD, glue.

Do not write GameData. Live tree: `python main.py world`.

## Visual

Pretty. Not physics. Not a headline.

| Mod | Version | Notes |
|---|---|---|
| RSSVE-HR | v3.1.0 | RSS visual pack (EVE + Scatterer configs for Earth). |
| EnvironmentalVisualEnhancements | — | Clouds / atmo overlay. Pulled by RSSVE. |
| Scatterer | — | Light / atmo scattering. Cache on disk. |
| Parallax + StockTextures | 2.0.8 | Terrain. Can stall Hangar on KSC load. |
| TUFX | 1.1.1 | Post-process. CKAN pulls **Shabby**. |
| Waterfall + WaterfallRestock | 0.2.3 | Engine plumes. |
| ReStock + ReStockPlus | 1.5.1 | Stock part art. Not a new tree. |
| RSS-Textures 16K | v18.6.1 | Earth / body textures. |

## Catalog / vehicle

On the shelf when the node is unlocked. Not RO.

| Mod | Version | Notes |
|---|---|---|
| ProceduralParts | v2.8.0.0 | Tanks, SRB, decoupler, heatshield — Gus prefers these when the node exists. |
| ProceduralFairings | v6.7.0.0 | Fairings. |
| NearFuture Construction / Electrical / Exploration / Propulsion / Solar / Spacecraft | 1.3–2.0 | Later catalog. Do not bind as Start parts. |
| RealAntennas | v2.12.0.0 | kRPC service live (`conn.real_antennas`, Os 2026-08-25). Early probes stay omni. Do not cheat a link. |
| KerbalJointReinforcementContinued | v3.8.7.0 | Joints. |
| DynamicBatteryStorage | — | EC helper. |
| SystemHeat | — | Present; not the hop physics we brief. |
| SolverEngines | — | Engine solver (RF stack). |
| RealPlume-RFStockalike / zzRFStockalike | — | RF stockalike plumes / patches. |
| B9PartSwitch | — | Part subtypes. |
| CommunityResourcePack | — | Resource defs RF/Kerbalism share. |

## HUD / tree cosmetics

| Mod | Version | Notes |
|---|---|---|
| KerbalEngineerRedux | 1.1.9.5 | KER on stills (drums, terrain). Not the tape. |
| HideEmptyTechNodes | 1.3.2 | CTT empty nodes hidden. |
| KerbalChangelog | v1.4.2 | Changelog popup. |
| RSSDateTimeFormatter | v1.12.1.0 | Kerbal clock on RSS. Also on the README table. |
| KSCSwitcher | v2.2.0.0 | Seats Cape Canaveral. Also on the README table. |

## Glue

Libraries the stack will not boot without. Not a story.

| Mod | Notes |
|---|---|
| ModuleManager 4.2.3 | Patches. ConfigCache is the live PART list. |
| Kopernicus | Planet plugin under RSS. |
| ModularFlightIntegrator | FAR / RSS integrator. |
| Harmony / KSPBurst / ClickThroughBlocker / ToolbarControl | UI / patch glue. |
| KSPCommunityFixes | Stock fixes. |
| KSPTextureLoader / Shabby | Texture / shader loaders (TUFX). |
| ROUtils | RF-adjacent util. Not a seated RO house. |
| 000_ / 999_ Scale_Redist | Load-order / rescale redistributable. |

kRPC **0.6.0** is in GameData and on the README. It is the hands,
not glue.
