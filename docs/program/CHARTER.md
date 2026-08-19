# Grok Space Program

A Kerbin program. Agents are the staff. The user is the visitor who can
address anyone and who picks the next item on the slate. No sound. No PyQt.

## How it runs

Three loops (L-037). Each has one owner. Everyone else is a file.

1. **Helm** — flying `python main.py phase`. Only kRPC writer. Takes
   `uplink.md`. Gates abort. `flight.lock` forbids a second writer.
2. **Flight** (Gene) owns the **plan** as a list of **blocks**
   (`docs/program/blocks.md`). He replans **between** `phase` exits.
   He does not invent a block, edit `.py`, or poll. Missing `go:` = wait.
3. **R&D** — exactly one patcher after an exit: `ksp-stack` first
   (sequencing / blocks); Wernher only for kRPC 0.6 stream traps if
   stack did not patch.
4. **CAPCOM** (Walt) is extra voice on events, not a substitute for Gene.
   The flying **agent name is the KSP kerbal name** (create if missing).
5. **Pilots** run one `phase`. Style in `docs/crew/*.md` still clamps
   ascent numbers. Gates always win. No spotter. No 15 s TUI stream.

Live handoff is still gitignored `docs/last-flight.md`. Every
`phase` / `mun` / `recover` writes `docs/flights/<utc>-<command>.md`, a
1 Hz `<utc>-<command>.jsonl`, and a `*-review.md` rollup (envelope, flag
timeline, events). Gene fills **Learn** after every exit — success,
abort, or crash. R&D reads the review before patching.

**Radio:** Gene talks to the **helm** and the **pilot file**,
not to a second kRPC session.

- `docs/program/ship.md` — last heartbeat + `as_of` the helm published
- `python main.py radio` — Gene's inbox (ship + uplink + loop)
- `docs/program/uplink.md` — stick command the helm *takes*
- `docs/program/briefing.md` + `loop.md` — plan told to the pilot
- `python main.py brief …` / `note Gene …` — Gene → pilot
- Bound+fueled abort is refused (L-033). Hold does not zero a lithobrake.
- Wall-clock SOI / `phase` timeouts do not dump crew (L-032 / L-037)

After you say **go**, the parent runs `phase` after `phase` until Gene
returns `go: wait` (or omits `go:`) or a phase aborts. Gene/Mortimer
still own `slate.md`. Parent does not patch `.py`.
