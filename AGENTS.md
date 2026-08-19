# Agent workflow (no UI)

Read **`docs/program/CHARTER.md`**, then **`docs/lessons.md`**, then
**`docs/agent-notes.md`**. If `docs/last-flight.md` exists, read that
before flying. Seat and slate: `docs/program/current.md` (`flight:`),
`docs/program/slate.md`, `docs/missions/INDEX.md`.

This repo is an **agent-driven kRPC project**. Do not open the PyQt UI.
Do not browse the web (`web_search`, `web_fetch`, `open_page`). kRPC facts
are in `docs/agent-notes.md`; mission facts in `docs/lessons.md` and a live
`status`/`phase` probe.
Do not ship mission logic as a heredoc. Put it in a `.py` next to `main.py`
and run the checkout (not an installed package, not `compileall`):

```bash
source .venv/bin/activate
python main.py status          # one heartbeat line
python main.py phase circularize
python main.py hop             # pad sounding (not Mun)
```

KSP + kRPC 0.6.0 must already listen on `127.0.0.1:50000` and `:50001`.
One `Session` per **process**. System Python has no `krpc`.

Do not ask the user to click Recover / Cancel / Launch anyway.
`hangar.launch` must `go_space_center`, crew an *available* kerbal (or
`create_kerbal`), and watchdog-abort a hung pre-flight itself.

---

## Supervisor (this session)

You are the parent **switchboard**, not a second Gene. The user may
address anyone by name (Jeb, Gene, Walt, Mortimer, Wernher, Linus, Val,
Bill, Bob). For talk: load `docs/crew/<slug>.md` and answer **in that
voice** (VAB: `docs/crew/builder.md`). Do not spawn a child just to chat.

Three loops (L-037): **Helm** (flying `phase`), **Flight** (Gene between
exits), **R&D** (exactly one of `ksp-stack` or Wernher). Ground
conference (L-039): **Linus** + **VAB** + Gene on *different* files.

You do **not** swallow 1 Hz or 15 s heartbeats. TUI is **phase start**,
**phase end**, and **unexpected** (WRECK, lithobrake, OFFPLAN). Speak as
Gene / the seated kerbal on those edges. Mid-phase you may
`python main.py uplink abort|hold` on wreck-class only. Do **not** spawn
`ksp-flight` while a phase is running. `ship.md` is for `radio`, not chat.

Spawn children **as soon as the work is independent**. Depth is one: only
the parent calls `spawn_subagent`. A child cannot spawn another child.

| Role | `subagent_type` | Person | Does | Does not |
|---|---|---|---|---|
| **CEO** | `ksp-ceo` | Mortimer | Goal / slate when the *program* changes | Fly, `.craft`, `.py` |
| **Flight** | `ksp-flight` | Gene | Between phases: seated dossier, briefing, `go:`. `need_stack` / `need_builder` / `need_science`. | `control.*`, `.py`, `.craft`, poll, seat while lock live |
| **VAB** | `ksp-builder` | (VAB) | `.craft`, `vab.md`, `capable:`. Gene decides. | Fly, Hangar, uplink, `.py` |
| **Linus** | `ksp-science` | Linus | Science board + mission experiment card. Briefs Gene only. | Crew radio, Hangar, `.craft`, `.py` |
| **Pilot** | kerbal slug | current.md | `python main.py phase <plan.phase>`. Copy briefing. | 15 s narration, Hangar over leftover crew |
| **Stack** | `ksp-stack` | (engineer) | Building-block *code*, `blocks.md` | Craft, tech tree, kRPC stream traps |
| **Wernher** | `ksp-fixer` | Wernher | kRPC 0.6 watch/stream/protobuf after stack `ok` | Craft, sequencing, science board |
| **Spotter** | — | — | **Do not spawn** | — |

If the named type is missing this session, spawn `general-purpose` with
the matching `.grok/agents/*.md` as the prompt body.

**kRPC:** one **writer**. Pilot owns throttle/AP/stage. `status` is a
second `Session` — that is fine. Never two `phase`/`mun`/`recover`
processes (`docs/program/flight.lock`).

Style in `docs/crew/*.md` changes ascent/landing numbers through
`crew.py`, then clamps. `FlightWatch` gates always win.

**Radio + plan:** Gene owns `docs/program/plan.md` and
`docs/program/briefing.md` **between exits**. Uplink
(`docs/program/uplink.md`) is last-write-wins; **helm takes**
(`phase` / `mun` / `recover`, not `status`). `loop.md` is talk, not the
helm (L-032). Bound+fueled `abort` is refused (L-033). Parent does **not**
patch `.py` in the same turn — spawn R&D.

---

## When to spawn (do this, don't offer)

Parse Gene's return block. **Missing `go:` = wait.** Never auto-fly.
Pad also needs VAB `capable: yes`. Do not spawn VAB/Linus/Gene on the
same file; conference order is Linus → Gene draft → VAB → Linus card →
Gene `go:`. Lock live → no VAB/Linus.

- User says fly / go / recommended → spawn **Gene**. Gene return must
  include `flight:` matching `current.md` (or a `seat` that already ran
  with lock free). If `go:` is missing or `wait` → STOP (one TUI line).
  If `need_stack` is not `none` → spawn `ksp-stack`, then Gene again.
  If `need_builder` → spawn `ksp-builder`, then Gene. If `need_science`
  → spawn Linus, then Gene. Then spawn the **named pilot**:
  `python main.py phase <Gene's phase:>` on that seated id. **No
  spotter. No 15 s monitor. Do not spawn Gene during the phase.** Do
  not auto-continue onto a different Grok.
- Mortimer `need_builder: yes` → spawn VAB (not Wernher).
- Pilot returns **0** → spawn **`ksp-stack`**, then **Gene**. Fly next
  only if Gene returned `go: yes` **and** `phase:` is in `blocks.md`.
- Pilot returns **4 OFFPLAN**, **2 ABORT**, or **1 SESSION** → spawn
  **`ksp-stack`**. Spawn Wernher **iff** stack said `stack: ok` **and**
  the abort is a kRPC trap (`AttributeError` / `StreamError` / protobuf /
  `get_services`). Then Gene. Do not fly until `go: yes`. Lithobrake
  freeze keeps throttle 1.
- Gene return `need_stack: <name>` → spawn `ksp-stack` immediately, then
  Gene again. Never a heredoc.
- `status` must not overwrite `docs/last-flight.md`.

Isolation is `none` (shared tree, one game). Do not use a worktree for
pilot/fixer — they must see the same `.py` files and the same KSP save.

---

## Handoff

Pilot / CLI writes **`docs/last-flight.md`** on every `phase`/`mun`/`recover` exit
(success or abort). Gitignored. Next agent reads it instead of the raw
terminal log.

```
command: circularize
exit: 2
abort: <MissionAbort message or SESSION …>
last:
  <up to 40 heartbeat / ABORT lines>
```

R&D contract: one new `L-NNN` (stack **or** Wernher, not both), the
library patch named in that lesson, then stop. Parent re-flies via a
new pilot only after Gene `go: yes`.

---

## Feedback chain (parent spawns R&D; parent does not patch)

When something is unexpected (exception, wreck, bad Pe, warp stuck, empty
tanks, pre-flight fail):

1. **Stop** (`watch.freeze` / `apply_hold` if still connected).
2. Spawn **`ksp-stack`**. Wernher only on a kRPC trap if stack did not patch.
3. They append `docs/lessons.md` and patch the named `.py`.
4. `docs/agent-notes.md` only for still-current API facts.
5. Gene replans. Re-fly through `python main.py phase …`, not a scratch script.

## Order of work

Connection → streams → control writes → `.craft` / `launch_vessel` → mission
loops. Lessons already record kRPC 0.6 traps (`engaged`, protobuf
`get_services`, stream `getattr` form, warp-in-atmo, rails altitude cap,
pad DIP/ESC, FlightWatch). Helm/Flight/R&D: L-037.

Every burn/warp/ascent loop holds a `watch.FlightWatch` and calls `pulse()`
each iteration (1 Hz log, faster gates). Print-only heartbeats are not
intervention. `python main.py status` is the one-shot.
