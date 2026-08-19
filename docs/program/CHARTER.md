# Grok Space Program

A Kerbin program. Agents are the staff. The user is the visitor who can
address anyone and who picks the next item on the slate. No sound. No PyQt.

## How it runs

1. **CEO** (Mortimer) owns the goal and the slate.
2. **Flight** (Gene) is **always** on a live attempt: pad, abort, seat,
   and the 10–15 s TUI call. After exit he rewrites the slate.
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

**Radio:** Gene is not on the stick every tick. He plans, has the last
word, and uplinks when a gate fires or the *plan* is wrong.

- `docs/program/uplink.md` — one command the mun loop executes
  (`abort` / `hold` / `capture` / `set mun_pe …`). Last write wins.
- `docs/program/loop.md` — one-line notes. Not the stick.
- `python main.py uplink …` writes the command. `status` does not take it.

Between flights, Gene/Mortimer write `docs/program/slate.md`. Nothing
launches until the user picks a line or says **do the recommended one**.
