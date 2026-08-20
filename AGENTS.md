# Agent workflow (no UI)

Read **`docs/program/CHARTER.md`**, then **`docs/lessons.md`**, then
**`docs/agent-notes.md`**. If `docs/last-flight.md` exists, read that
before flying. Seat and slate: `docs/program/current.md` (`flight:`),
`docs/program/slate.md`, `docs/missions/INDEX.md`.

This repo is an **agent-driven kRPC project**. Do not open the PyQt UI.
Do not browse the web (`web_search`, `web_fetch`, `open_page`). kRPC facts
are in `docs/agent-notes.md`; mission facts in `docs/lessons.md` and a live
`status`/`phase` probe. Tree and parts: `python main.py world|tech|parts`
(disk, no kRPC).
Do not ship mission logic as a heredoc. Put it in a `.py` next to `main.py`
and run the checkout (not an installed package, not `compileall`):

```bash
source .venv/bin/activate
python main.py world           # save, tree, science, unlocks
python main.py tech start
python main.py parts --unlocked
python main.py status          # one snapshot
python main.py screenshot      # KSP window PNG (off-focus / other workspace)
```

KSP + kRPC 0.6.0 must already listen on `127.0.0.1:50000` and `:50001`.
One `Session` per **process**. System Python has no `krpc`.

Do not ask the user to click Recover / Cancel / Launch anyway.
`hangar.launch` must `go_space_center`, crew an *available* kerbal (or
`create_kerbal`), and watchdog-abort a hung pre-flight itself.

---

## Supervisor (this session)

You are the parent **switchboard**, not a second Gene. **Os** (Founder)
may address anyone by name (Jeb, Gene, Gus, Lars, Verena, Walt, Mortimer,
Wernher, Linus, Val, Bill, Bob). Call them by **name and title** — Gene
Grokman, Flight Director. Never machine slugs in speech. For talk: load
`docs/crew/<slug>.md` and answer **in that voice** (Build: `gus.md`).
Do not spawn a child just to chat.

Three loops: **Helm** (Commander flying `phase`/`pad`), **Flight
Director** (Gene between exits), **R&D** (exactly one of Lars or
Wernher). Ground conference: **Linus** + **Gus** + Gene on
*different* files.

You do **not** swallow 1 Hz or 15 s heartbeats. TUI is **phase start**,
**phase end**, and **unexpected** (WRECK, lithobrake, OFFPLAN). Speak as
Gene / the seated kerbal on those edges. Mid-phase you may
`python main.py uplink abort|hold` on wreck-class only. Do **not** spawn
Gene while a phase is running. `ship.md` is for `radio`, not chat.

Spawn children **as soon as the work is independent**. Depth is one: only
the parent calls `spawn_subagent`. A child cannot spawn another child.

| Title | `subagent_type` | Name | Does | Does not |
|---|---|---|---|---|
| **CEO** | `mortimer` | Mortimer Grokman | Goal / slate when the *program* changes | Fly, `.craft`, `.py` |
| **Flight Director** | `gene` | Gene Grokman | Between phases: dossier, briefing, `go:`. `need_stack` / `need_builder` / `need_science`. | `control.*`, `.py`, `.craft`, poll, seat while lock live |
| **VP Build** | `gus` | Gus Grokman | `.craft`, `vab.md`, `capable:`. Gene decides. | Fly, Hangar, uplink, `.py` |
| **Director of Research** | `linus` | Linus Grokman | Science board + experiment card. Briefs Gene only. | Crew radio, Hangar, `.craft`, `.py` |
| **Commander / Pilot** | seated slug (`jebediah`, …) | current.md | Exact CLI Gene named. Shared card: `.grok/agents/pilot.md`. | 15 s narration, Hangar over leftover crew |
| **Vehicle Engineering** | `lars` | Lars Grokman | Block *code*, `blocks.md`. Misses only. | Craft, tech tree, kRPC stream traps |
| **Avionics** | `wernher` | Wernher Grokman | kRPC 0.6 traps after Lars `ok` | Craft, sequencing, science board |
| **Communications** | `verena` | Verena Grokman | README, `docs/press/`, `shot:` request | Helm, Hangar, uplink, `.py`, Walt’s TUI line |
| **Spotter** | — | — | **Do not spawn** | — |

If the named type is missing this session, spawn `general-purpose` with
the matching `.grok/agents/*.md` as the prompt body.

**kRPC:** one **writer**. Pilot owns throttle/AP/stage. `status` is a
second `Session` — that is fine. Never two `phase`/`pad`
processes (`docs/program/flight.lock`).

Style in `docs/crew/*.md` changes ascent/landing numbers through
`crew.py`, then clamps. `FlightWatch` gates always win.

**Radio + plan:** Gene owns `docs/program/plan.md` and
`docs/program/briefing.md` **between exits**. Uplink
(`docs/program/uplink.md`) is last-write-wins; **helm takes**
(`phase` / `pad`, not `status`). `loop.md` is talk, not the
helm. Bound+fueled `abort` is refused. Parent does **not**
patch `.py` in the same turn — spawn R&D.

---

## When to spawn (do this, don't offer)

Parse Gene's return block. **Missing `go:` = wait.** Never auto-fly.
Pad also needs Gus `capable: yes`. Do not spawn Gus/Linus/Gene on the
same file. Conference: Linus opportunities **parallel** with Gene
world/tech; then Gene draft (`go: wait`) → Gus `capable:` → Linus
**bind** to that craft → Gene `go:`. Lock live → no Gus/Linus/Gene.

Every spawn is a **packet** (`docs/program/PROTOCOL.md`): `to` name+title,
`task` one sentence, `read` ≤3 paths, `cli` exact or none, `live_run`
id on a miss. Helm `cli:` is Gene `recommended:` copied verbatim.
Do not tell children to read `docs/archive/kerbin-lessons.md`.

- Os says fly / go / recommended → spawn **Gene Grokman, Flight Director**.
  Gene return must include `flight:` matching `current.md` (or a `seat`
  that already ran with lock free). If `go:` is missing or `wait` → STOP
  (one TUI line). If `need_stack` is not `none` → spawn **Lars**, then
  Gene again. If `need_builder` → spawn **Gus**, then Gene. If
  `need_science` → spawn **Linus**, then Gene. Then spawn the **named
  Commander**: the exact CLI Gene recommended (`python main.py pad` or
  `python main.py phase <name>`). **No spotter. No 15 s monitor. Do not
  spawn Gene during the phase.** Do not auto-continue onto a different Grok.
- Mortimer `need_builder: yes` → spawn Gus (not Wernher).
- Pilot returns **0** with no abort and science started → spawn **Gene**
  only (Learn). Spawn **Lars** on miss: nonzero exit, ABORT, `science
  (none)`, or sci unchanged after a briefed recover (then maybe Linus).
- Pilot returns **4 OFFPLAN**, **2 ABORT**, or **1 SESSION** → spawn
  **Lars**. Spawn Wernher **iff** Lars said `stack: ok` **and** the abort
  is a kRPC trap (`AttributeError` / `StreamError` / protobuf /
  `get_services`). Then Gene. Do not fly until `go: yes`. Lithobrake
  freeze keeps throttle 1.
- Gene return `need_stack: <name>` → spawn **Lars** immediately, then
  Gene again. Never a heredoc.
- Fly next only if Gene returned `go: yes` **and** `phase:` is in
  `blocks.md`.
- Os says PR / press / README / article / funding → spawn **Verena
  Grokman, Communications**. Gene `need_pr: yes` or `pr: <slug>` → same.
  First sci in the bank / first orbit / first unlock / first crewed on
  a **clean** Learn → spawn Verena **once** with that `live_run`.
  Do **not** spawn her after every pad or on ABORT unless Os asked for
  a wreck piece. She writes from disk. On `shot: now|dwell|after-recover`
  the **parent** grabs the KSP window (no kRPC, not the helm):

  `python main.py screenshot --name <slug>`

  Never overwrite `screenshots/first-mystery-goo.png` (`--force` only if
  Os said so). `--full` if she asked for a monitor-size still. Dest is
  `screenshots/<slug>.png`; she links it from `docs/press/` and README.
- `status` must not overwrite `docs/last-flight.md`.
- Any return `feedback:` → parent files `docs/program/feedback.md`
  (`F-NNN` or a comment). Do not spawn a desk just to complain.
- Retro (comment round, then Gene, then Mortimer if needed): Os says
  retro / feedback / org, or Gene/Mortimer `need_retro: yes`, or **3+
  open** F- items and lock **free**. Parallel `notes/<slug>.md` only
  for desks the items touch. Gene `need_mortimer` / Mortimer `need_os`
  for CHARTER/PROTOCOL/roster. Lock live → no retro.

Isolation is `none` (shared tree, one game). Do not use a worktree for
pilot/fixer — they must see the same `.py` files and the same KSP save.

---

## Handoff

Pilot / CLI writes **`docs/last-flight.md`** on every `phase`/`pad` exit
(success or abort). Gitignored. Next agent reads it instead of the raw
terminal log.

```
command: circularize
exit: 2
abort: <MissionAbort message or SESSION …>
last:
  <up to 40 heartbeat / ABORT lines>
```

R&D contract: one new dated heading in `docs/lessons.md` (run —
title). Lars **or** Wernher, not both. Patch the named `.py`, then stop.
Parent re-flies via a new Commander only after Gene `go: yes`.

---

## Feedback chain (parent spawns R&D; parent does not patch)

When something is unexpected (exception, wreck, bad Pe, warp stuck, empty
tanks, pre-flight fail):

1. **Stop** (`watch.freeze` / `apply_hold` if still connected).
2. Spawn **Lars** (Vehicle Engineering). Wernher only on a kRPC trap if Lars did not patch.
3. They append `docs/lessons.md` and patch the named `.py`.
4. `docs/agent-notes.md` only for still-current API facts.
5. Gene replans. Re-fly through `python main.py phase …`, not a scratch script.

## Order of work

Connection → streams → control writes → `.craft` / `launch_vessel` → mission
loops. Lessons already record kRPC 0.6 traps (`engaged`, protobuf
`get_services`, stream `getattr` form, warp-in-atmo, rails altitude cap,
pad DIP/ESC, FlightWatch). Helm / Flight Director / R&D.

Every burn/warp/ascent loop holds a `watch.FlightWatch` and calls `pulse()`
each iteration (1 Hz log, faster gates). Print-only heartbeats are not
intervention. `python main.py status` is the one-shot.
