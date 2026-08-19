# Grok Space Program

A Kerbin program. Agents are the staff. The user is the visitor who can
address anyone and who picks the next item on the slate. No sound. No PyQt.

## How it runs

Three loops (L-037). Each has one owner. Everyone else is a file.
Many **missions**, one seated helm (L-038).

1. **Helm** — flying `python main.py phase` on the **seated** mission
   (`docs/program/current.md` `flight:`). Only kRPC writer. Takes
   `uplink.md`. Gates abort. `flight.lock` forbids a second writer.
   Crew on the active vessel must match the seated pilot. Rails warp
   scans other crewed stacks (unloaded ships still die on rails).
2. **Flight** (Gene) owns the **seated dossier**
   (`docs/missions/<id>/plan.md`). He replans **between** `phase` exits.
   To change ship: lock free → `python main.py seat <id>` → brief that
   dossier. He does not invent a block, edit `.py`, or poll. Missing
   `go:` = wait. Return includes `flight:`.
3. **R&D** — exactly one patcher after an exit: `ksp-stack` first
   (sequencing / blocks); Wernher only for kRPC 0.6 stream traps if
   stack did not patch.
4. **CAPCOM** (Walt) is extra voice on events, not a substitute for Gene.
   The flying **agent name is the KSP kerbal name** (create if missing).
5. **Pilots** run one `phase`. Style in `docs/crew/*.md` still clamps
   ascent numbers. Gates always win. No spotter. No 15 s TUI stream.

Live handoff is still gitignored `docs/last-flight.md`. Sorties write
under `docs/missions/<id>/sorties/`. Gene fills **Learn** after every
exit. R&D reads the review before patching.

**Radio:** Gene talks to the **helm** and the **pilot file**,
not to a second kRPC session.

- `docs/program/ship.md` — last heartbeat + `as_of` the helm published
- `python main.py radio` — Gene's inbox (ship + uplink + loop)
- `docs/program/uplink.md` — stick command the helm *takes*
- `docs/missions/<id>/briefing.md` + `loop.md` — plan told to that pilot
- `python main.py brief …` / `note Gene …` — Gene → seated dossier
- `python main.py seat <id>` / `missions` — switch / board
- Bound+fueled abort is refused (L-033). Hold does not zero a lithobrake.
- Wall-clock SOI / `phase` timeouts do not dump crew (L-032 / L-037)

After you say **go**, the parent runs `phase` after `phase` until Gene
returns `go: wait` (or omits `go:`) or a phase aborts. Gene/Mortimer
still own `slate.md`. Parent does not patch `.py`.
