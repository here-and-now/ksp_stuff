# Start RO — when Os says go

Team boards were wiped 2026-08-21 (gym tape in
`docs/archive/letsgrok-2026-08-21/`). Do **not** seat this tree until
a **new science sandbox** exists and KSP has finished the first
ModuleManager boot. No Gene / Commander / Mortimer against RO until
`desk` sees that save.

## Already on disk (`~/Games/KSP-RO`)

Express applied. **RONoCareer** (no RP-1 GameData). Kerbalism
**Profile = RealismOverhaul**. kRPC present. FAR / RealHeat /
RealChute / AJE / ROEngines / ROTanks / ROCapsules / ROSolar.

Steam **saves copied with the tree** (`Os' Rocketry`, `Grok`, …). Do
**not** fly those. They are not RO sandbox.

CKAN may still be open on this instance. Close it before launching
KSP.

## First boot (you)

1. Launch **`~/Games/KSP-RO/KSP.x86_64`** (not Steam). First MM pass
   is long. Wait until the main menu.
2. **New game → Science sandbox** (not career, not the copied saves).
   Name it **`letsgrok`** so `KSPSTUFF_SAVE` can stay default.
3. Confirm Earth, Kerbalism, no RP-1 contracts. Drop to Space Center.
   Quit once so `persistent.sfs` exists.
4. kRPC listening `127.0.0.1:50000` / `:50001` (same as gym).

## Then parent

```bash
export KSPSTUFF_KSP="$HOME/Games/KSP-RO"
export KSPSTUFF_SAVE=letsgrok
source .venv/bin/activate
python main.py desk
```

Desk must show this root (RO parts, Kerbalism-RO, leftover none). Then
conference: Linus opportunities ∥ Gus capable → bind → Gene `go:` or
wait. Empty missions, new `blocks.md` from parts that exist. Do not
port Flea/pad recipes.

## Switch back to gym

```bash
unset KSPSTUFF_KSP
# or: export KSPSTUFF_KSP="$HOME/Games/KSP-rss"
```

Discover still prefers `KSP-rss` when the env is unset.

## Notes

Graphics pulled Parallax (Express High-ish). 8GB VRAM — if the client
stutters, CKAN graphics down later; not a fly blocker.

`load persistent` still refused. RO CTT/RP-1 spend is N/A (sandbox +
RONoCareer).
