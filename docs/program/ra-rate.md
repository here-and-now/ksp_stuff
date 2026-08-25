# RealAntennas live rate — prove passed (Os 2026-08-25)

Harmony clamp is in the house DLL. Os radio prove **passed**. Do **not**
hop. Do **not** MM TechLevel. Do **not** open a second **control**
Session while hangar pid is the writer. Dump is disk (`python main.py comms`).

## Proved this pad (Cape, GSTL=2)

| Knob | Value | Meaning |
|---|---|---|
| PAW / `tech_level` / GSTL / `diff_max` | **2** | `AlignTechLevel` still real |
| `TechLevelInfo.MaxDataRate` (commsTL2) | **64** | cfg **table** |
| kRPC `Comms.RateToHome` | **64 bps** | live Cape **path** (clamped) |
| Kerbalism | **0.008 kB/s** | 64/8000 |

**64 is the table and now the path at Cape.** Dump `rate_bps` is still
ConfigCache `MaxDataRate`; after the clamp that number is also
`RateToHome` here. L ChannelWidth is still 31.5 kHz — the job no
longer uses it as the uncapped path.

Pre-clamp forensics (do not treat as current): high SNR over Cape used
to report RateToHome **31500** bps (channel × 1 bit/s/Hz) and Kerbalism
**3.94 kB/s**. That was the unclamped `RateBoundariesJob`. Not leftover
TL10. Not GSTL.

## What went wrong (do not lose this)

1. Sandbox GSTL defaults to **MaxTL**. House `ra_align` stamps owned
   comms TL (2 = survivability). **That stamp is real.** Keep it.
2. We then treated “owned TL2 64 bps” as live RF. `python main.py
   comms` prints ConfigCache `MaxDataRate` as `rate_bps`. Tests assert
   `2 survivability 64`. Gus/Linus packets run that dump and will plan
   **hours**. Pre-clamp Cape was ~4 kB/s (baro in minutes). Files still
   credit while recording — they can fly without TX — but any **radio
   reasoning from the dump as if it were RateToHome was wrong then**.
   Now table and Cape path match at 64.
3. Wrapper: `Antenna.MaxDataRate` / `TechLevel.MaxDataRate` = table.
   `Comms.RateToHome` = path. Tape logs `rate_bps` (slow RPC).
4. Making RA 64 bps is `FwdDataRate`/`RevDataRate` (channel), **not**
   GSTL. Not an MM `TechLevel` patch. Align did **not** finish RF;
   Harmony did.
5. Burst `RateBoundariesJob` is **not** patched. Encoder table: TL2
   only has `None` (CodingRate=1). Reed-Solomon 255/223 is TL3.

## C# (house plugin, not RA.dll)

Harmony is already in GameData (`000_Harmony/0Harmony.dll`).

| Where | Fact |
|---|---|
| Source | `krpc_realantennas/src/RateClamp.cs` |
| Installed | `GameData/kRPC/KRPC.RealAntennas.dll` (Os copy; `build.sh` does **not** install) |
| Refs | `GameData/RealAntennas/Plugins/RealAntennas.dll` + `000_Harmony/0Harmony.dll` |
| Prefix | `RACommLink` `set_FwdDataRate` / `set_RevDataRate` |
| Postfix | antenna setters reclamp; `RACommNetwork.MaxDataRateToHome` |
| Cap | `TechLevelInfo.MaxDataRate` |
| Not patched | burst `RateBoundariesJob` |

**Do not:** edit `GameData/RealAntennas/`, CKAN-owned cfg, stamp MaxTL,
raise TxPower, `SetTarget*` to fake a path, MM `@TechLevel`. CHARTER:
never write GameData from the desk.

**Build:** `krpc_realantennas/build.sh` then Os copies DLL into
`GameData/kRPC`.

## Dump / tape (second)

Dump header: 64 is table **and** the live Cape path. Tape: `rate_bps`
is `Comms.RateToHome`, not table MaxDataRate. Neither is a new RF fix.

## Not this ticket (T-426 — do not hop)

`2026-08-25T06-57-16Z-hop` exit 2: splash bind dropped `hop_apo` to
**18 km**, pitch 25 from pad, `hop coast physics 4x` at ~3 km, crash UI
`sit=flying rec=no`. Close persist → Tracking → KSC. Bank still
**2.29**. T-424 Lars `hop_factory.py` (`flyinghigh-lid`). T-426 Wernher
`physics_warp.py` (`hop-coast-phys-warp`). Science bank does **not**
need 64 bps. That wreck is the lid, not the radio.

## Read

- this file
- `krpc_realantennas/src/RateClamp.cs`
- `krpc_realantennas/src/Comms.cs` (`RateToHome`)
- `krpc_realantennas/src/Align.cs` (GSTL — leave it)
- `comms_catalog.py` `format_ra_tables`
- `GameData/RealAntennas/RealAntennasCommNetParams.cfg` TL2 MaxDataRate=64
