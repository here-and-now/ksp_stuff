# Grok Space Program

An Earth program (RSS + Kerbalism Default, science sandbox, PBC probes
first). Agents are the staff. The user is the visitor who can address
anyone and who picks the next item on the slate. No sound. No PyQt.

Environment memory is **query tools**, not this file:

```bash
python main.py world
python main.py tech
python main.py parts --unlocked
```

## How it runs

Three loops (L-037). Many **missions**, one seated helm (L-038).
Planning is a **conference on files** (L-039). Flying is Gene → helm.

| Who | Owns | Never |
|---|---|---|
| **Helm** | flying `phase`; `uplink.md`; `flight.lock` | a second writer |
| **Gene** | seated dossier plan + briefing; `go:` | `.py`, `.craft` |
| **VAB** | `.craft`, `vab.md` | Hangar, uplink, `.py` |
| **Linus** | `science.md`, mission experiment card | crew radio, Hangar |
| **Stack** | `phases.py`, `hop.py`, `science.py`, `blocks.md` | craft, tech tree |
| **Wernher** | kRPC 0.6 traps | craft, sequencing |
| **Mortimer** | goal / slate | fly, craft, `.py` |
| **Walt** | TUI voice on phase edges | planning |
| **Pilot** | one `phase` | rewrite the plan |

Linus briefs **Gene** (what / when / which part). Gene copies that into
the pilot briefing. Linus has **no** `uplink` / `loop` / `note`.

Gene last-writes the **plan**. VAB last-writes the **`.craft`**. Linus
last-writes **science.md**. Disagreement → Gene `go: wait`.

**Conference (parent, depth 1, different files):** Linus opportunities →
Gene draft (`go: wait`) → VAB `capable:` → Linus binds experiments to
that craft → Gene briefing + `go:`. Do not spawn them on one file.
Do not spawn VAB/Linus while `flight.lock` is live.

Pad needs VAB `capable: yes` and a real `craft:` file. PBC probes launch
**uncrewed**. Leftover crew flies `phase` on the vessel they have.

Crew on the active vessel must match the seated pilot. Rails warp scans
other crewed stacks (unloaded ships still die on rails).

Live handoff is gitignored `docs/last-flight.md`. Sorties write under
`docs/missions/<id>/sorties/`. Gene fills **Learn**. Stack then Gene
after every exit; Wernher only on a kRPC trap.

**Radio (flight):**

- `docs/program/ship.md` — last heartbeat + `as_of` + flight id
- `python main.py radio` — Gene's inbox
- `docs/program/uplink.md` — helm *takes*
- `docs/missions/<id>/briefing.md` + `loop.md` — Gene → that pilot
- `python main.py seat <id>` / `missions` / `vab` / `science` / `pad`

Bound+fueled abort is refused (L-033). Hold does not zero a lithobrake.
Missing `go:` = wait. Parent does not patch `.py`.
