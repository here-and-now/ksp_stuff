# RealAntennas live rate — C# first (Os 2026-08-25)

Packet for the desk that Harmony-patches RA. Do **not** hop. Do **not**
MM TechLevel. Do **not** treat Align as finished RF. Dump header is
second. This wreck pulse is a different ticket.

## Measured this pad (Cape, GSTL=2, high SNR)

| Knob | Value | Meaning |
|---|---|---|
| PAW / `tech_level` / GSTL / `diff_max` | **2** | `AlignTechLevel` worked |
| `TechLevelInfo.MaxDataRate` (commsTL2) | **64** | cfg **table** only |
| L `ChannelWidth` | 31.5 kHz | `RealAntennasCommNetParams` |
| kRPC `Comms.RateToHome` | **31500 bps** | = channel width; honest path |
| Kerbalism | **3.9375 kB/s** | 31500/8000; Os: DataRate 63000 × ½ coding |

`MaxDataRateToHome` is `min(link.FwdDataRate, link.RevDataRate)`. It
**never** reads `TechLevelInfo.MaxDataRate`. High SNR over Cape →
1 bit/s/Hz on L → 31.5 kbps. **64 bps is a label.**

Tree / GSTL / PAW are coherent. RF and Kerbalism are not. Last
flight’s 3.94 kB/s is this, **not** leftover TL10.

## What went wrong (do not lose this)

1. Sandbox GSTL defaults to **MaxTL**. House `ra_align` stamps owned
   comms TL (2 = survivability). **That stamp is real.** Keep it.
2. We then treated “owned TL2 64 bps” as live RF. `python main.py
   comms` prints ConfigCache `MaxDataRate` as `rate_bps`. Tests assert
   `2 survivability 64`. Gus/Linus packets run that dump and will plan
   **hours**. Reality at Cape is ~4 kB/s (baro in minutes). Files still
   credit while recording — they can fly without TX — but any **radio
   reasoning from that dump is wrong**.
3. Our wrapper repeats the mix: `Antenna.MaxDataRate` /
   `TechLevel.MaxDataRate` = table. `Comms.RateToHome` = path (honest).
   Hop tape **does not log** `RateToHome`.
4. Hank was about to patch the dump header only and keep the pad
   moving. Os: **patch the C# first.** Making RA 64 bps is
   `RateBoundaries` / `FwdDataRate` (channel), **not** GSTL. Not an MM
   `TechLevel` patch. Align did **not** finish the job.
5. Encoder table (same cfg): TL2 only has `None` (CodingRate=1).
   Reed-Solomon 255/223 is TL3. Os still measured 63000 × ½ coding.
   Do not flatten that — measure after the Harmony patch.

## C# to touch (house plugin, not RA.dll)

Harmony is already in GameData (`000_Harmony/0Harmony.dll`).

| Where | Fact |
|---|---|
| Source | `krpc_realantennas/src/*.cs` |
| Installed | `GameData/kRPC/KRPC.RealAntennas.dll` (Os copy; `build.sh` does **not** install) |
| Refs | `GameData/RealAntennas/Plugins/RealAntennas.dll` |
| RA types in the DLL | `RateBoundariesJob`, `MaxDataRateToHome`, `FwdDataRate`, `RevDataRate`, `RAKerbalismLinkHandler`, `ModulationBits`, `ChannelWidth` |
| Wrapper already honest | `Comms.RateToHome` → `RACommNetScenario.RACN.MaxDataRateToHome(node)` |
| Wrapper table (do not sell as path) | `TechLevel.MaxDataRate`, `Antenna.MaxDataRate` |

**Job:** Harmony-patch `RateBoundariesJob` (and/or the
`FwdDataRate`/`RevDataRate` setters) so live link rate **cannot exceed**
that antenna’s `TechLevelInfo.MaxDataRate` (TL2 → 64 bps). Kerbalism
then follows (`RAKerbalismLinkHandler`, bits/8000).

**Do not:** edit `GameData/RealAntennas/`, CKAN-owned cfg, stamp MaxTL,
raise TxPower, `SetTarget*` to fake a path, MM `@TechLevel`, restart
KSP for a Python dump-only change (C# **does** need a restart after
Os copies the DLL).

**Build:** `krpc_realantennas/build.sh` then Os copies DLL into
`GameData/kRPC`. CHARTER: never write GameData from the desk.

## Prove it

Same pad, Cape, GSTL still 2:

- `conn.real_antennas.comms(vessel).rate_to_home` ≈ **64** (not 31500)
- Kerbalism kB/s ≈ 64/8000 = **0.008** (not 3.94)
- `TechLevelInfo.MaxDataRate` still 64 (table unchanged)
- PAW / GSTL / `diff_max` still 2

Then (second): dump header — 64 is table, not path. Tape: log
`RateToHome`. Neither of those is the RF fix.

## Not this ticket (still open — do not hop)

`2026-08-25T06-57-16Z-hop` exit 2: splash bind dropped `hop_apo` to
**18 km**, pitch 25 from pad, `hop coast physics 4x` at ~3 km, crash UI
`sit=flying rec=no`. Close persist → Tracking → KSC. Leftover **0**.
Bank still **2.29**. T-424 Lars `hop_factory.py` (`flyinghigh-lid`).
T-426 Wernher `physics_warp.py` (`hop-coast-phys-warp`). Science bank
does **not** need 64 bps. Control is Cape + `can_communicate`. That
wreck is the lid, not the radio.

## Read

- this file
- `krpc_realantennas/src/Comms.cs` (`RateToHome`)
- `krpc_realantennas/src/Align.cs` (GSTL — leave it)
- `krpc_realantennas/src/TechLevel.cs` / `Antenna.cs` (`MaxDataRate` table)
- `comms_catalog.py` `format_ra_tables` (the dump lie)
- `GameData/RealAntennas/RealAntennasCommNetParams.cfg` TL2 MaxDataRate=64, L ChannelWidth=31.5e3
- `patches/kspstuffComms/kspstuffComms.cfg` (Cape L TL0; do not retarget)
