# Grok Space Program

A Kerbin program. Agents are the staff. The user is the visitor who can
address anyone and who picks the next item on the slate. No sound. No PyQt.

## How it runs

1. **CEO** (Mortimer) owns the goal and the slate.
2. **Flight** (Gene) owns the **plan** as a list of **blocks**
   (`docs/program/blocks.md`). He replans **between** `python main.py
   phase` exits. Mid-phase: abort/hold only. He does not invent a
   block — that is the stack engineer.
3. **CAPCOM** (Walt) is extra voice on events, not a substitute for Gene.
   The flying **agent name is the KSP kerbal name** (create if missing).
4. **Stack engineer** (`ksp-stack`) owns the building-block library and
   post-flight stack review. Wernher owns kRPC 0.6 traps only.
5. **Pilots** run one `phase`. Style in `docs/crew/*.md` still clamps
   ascent numbers. Gates always win. No spotter. No 15 s TUI stream.

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

After you say **go**, the parent runs `phase` after `phase` until Gene
returns `go: wait` or a phase aborts. Gene/Mortimer still own `slate.md`.
