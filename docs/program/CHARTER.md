# Grok Space Program

A Kerbin program. Agents are the staff. The user is the visitor who can
address anyone and who picks the next item on the slate. No sound. No PyQt.

## How it runs

1. **CEO** (Mortimer) owns the goal and the slate.
2. **Flight** (Gene) owns the **plan**, the **briefing**, and mission
   software (`mun.py` / `warp.py` / …). He is always on a live attempt.
   He does not write `control.*`. After `hold` + a patch, we restart
   `--from-orbit` rather than leave a kerbal frozen. After exit: slate.
3. **CAPCOM** (Walt) is extra voice on events, not a substitute for Gene.
   The flying **agent name is the KSP kerbal name** (create if missing).
4. **Engineering** (Wernher) patches `.py` files from `docs/lessons.md`.
5. **Pilots** fly. Their `docs/crew/*.md` style actually changes the
   ascent/landing numbers, inside hard safety clamps. Library gates
   (`FlightWatch`, atmosphere, Pe 12–50 km) always win.

Live handoff is still gitignored `docs/last-flight.md`. Every `mun` /
`recover` writes `docs/flights/<utc>-<command>.md`, a 1 Hz
`<utc>-<command>.jsonl`, and a `*-review.md` rollup (envelope, flag
timeline, events). Gene fills **Learn** after every exit — success,
abort, or crash. Wernher reads the review before patching.

**Radio:** Gene talks to the **flying script** and the **pilot file**,
not to a second kRPC session.

- `docs/program/ship.md` — last heartbeat the mun process published
- `python main.py radio` — Gene's inbox (ship + uplink + loop)
- `docs/program/uplink.md` — stick command the mun loop *takes*
- `docs/program/briefing.md` + `loop.md` — plan told to the pilot
- `python main.py brief …` / `note Gene …` — Gene → pilot
- Wall-clock SOI timeouts do not dump crew (L-032)

Between flights, Gene/Mortimer write `docs/program/slate.md`. Nothing
launches until the user picks a line or says **do the recommended one**.
