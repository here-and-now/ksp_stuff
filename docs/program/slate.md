# Slate

**Recommended:** Wernher — hangar must recover/clear the occupied pad on "Launch site not clear" (do not fall through to `recover=False`). Then Val `python main.py mun`.

Last `mun` (Val, 1829Z, 0 s): crew resolved, craft installed, then SESSION Launch site not clear. No ignition. The 1823Z lander is still on the pad (Kerbin landed alt=82, 12 parts, LF=3568, stg=2). Uplink was empty (L-026). Not a wreck.

- Wernher: hangar pad-clear on occupied LaunchPad, keep `recover=True`. Then Val mun.
- Recover the leftover pad lander from KSC (do not `python main.py recover` — that is periapsis), then Val mun.
- Val mun again from space_center anyway — will SESSION the same until the pad is empty.

Pick a line or say **do the recommended one**.
