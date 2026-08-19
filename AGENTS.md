# Agent workflow (no UI)

Read **`docs/program/CHARTER.md`**, then **`docs/lessons.md`**, then
**`docs/agent-notes.md`**. If `docs/last-flight.md` exists, read that
before flying. Seat and slate: `docs/program/current.md`,
`docs/program/slate.md`.

This repo is an **agent-driven kRPC project**. Do not open the PyQt UI.
Do not browse the web (`web_search`, `web_fetch`, `open_page`). kRPC facts
are in `docs/agent-notes.md`; mission facts in `docs/lessons.md` and a live
`status`/`mun` probe.
Do not ship mission logic as a heredoc. Put it in a `.py` next to `main.py`
and run the checkout (not an installed package, not `compileall`):

```bash
source .venv/bin/activate
python main.py status          # one heartbeat line
python main.py mun             # pad → LKO → Mun
```

KSP + kRPC 0.6.0 must already listen on `127.0.0.1:50000` and `:50001`.
One `Session` per **process**. System Python has no `krpc`.

Do not ask the user to click Recover / Cancel / Launch anyway.
`hangar.launch` must `go_space_center`, crew an *available* kerbal (or
`create_kerbal`), and watchdog-abort a hung pre-flight itself.

---

## Supervisor (this session)

You are the parent **switchboard**, not a sixth personality. The user may
address anyone by name (Jeb, Gene, Walt, Mortimer, Wernher, Val, Bill,
Bob). For talk: load `docs/crew/<slug>.md` and answer **in that voice**.
Do not spawn a child just to chat.

You do **not** swallow 1 Hz or 15 s heartbeats. TUI is **phase start**,
**phase end**, and **unexpected** (WRECK, lithobrake, OFFPLAN). Speak as
Gene / the seated kerbal. `ship.md` is for Gene’s `radio`, not chat.

Spawn children **as soon as the work is independent**. Depth is one: only
the parent calls `spawn_subagent`. A child cannot spawn another child.

| Role | `subagent_type` | Person | Does | Does not |
|---|---|---|---|---|
| **CEO** | `ksp-ceo` | Mortimer | Goal / slate when the *program* changes | Fly, patch `.py` |
| **Flight** | `ksp-flight` | Gene | Between phases: envelope vs plan, next `phase:` + numbers, briefing. Rush: `need_stack`. Mid-phase abort/hold only. | Touch `control.*`, invent a block not in `blocks.md` |
| **Pilot** | kerbal slug | current.md | `python main.py phase <plan.phase>`. Copy briefing. Talk on abort/off-plan. | 15 s narration, Hangar over leftover crew |
| **Stack** | `ksp-stack` | (engineer) | Building blocks, `blocks.md`, post-flight stack review, new phase names | Fly, kRPC stream traps |
| **Wernher** | `ksp-fixer` | Wernher | kRPC 0.6 watch/stream/protobuf | Mission sequencing |
| **Spotter** | — | — | **Do not spawn** | — |

If the named type is missing this session, spawn `general-purpose` with
the matching `.grok/agents/*.md` as the prompt body.

**kRPC:** one **writer**. Pilot owns throttle/AP/stage. Spotter is
read-only (`status` is a second `Session` — that is fine). Never two
`mun`/`recover` processes.

Style in `docs/crew/*.md` changes ascent/landing numbers through
`crew.py`, then clamps. `FlightWatch` gates always win.

**Radio + plan:** Gene owns `docs/program/plan.md` and
`docs/program/briefing.md`. Uplink (`docs/program/uplink.md`) is Gene →
the flying script (last write wins). `docs/program/loop.md` is Gene ↔
pilot. Only `mun` *takes* uplink. Pilot reads the briefing and copies
on the loop. Gene may patch mission `.py` after `uplink hold` (parent
restarts `--from-orbit` so crew is not abandoned). Wernher still owns
watch/stream kRPC traps. Abort cannot be overridden by the pilot.

---

## When to spawn (do this, don't offer)

- User says fly / go / recommended → spawn **Gene** then the **named
  pilot**. Pilot runs `python main.py phase <phase from plan.md>`.
  **No spotter. No 15 s monitor.** One Gene line at start.
- Pilot returns **0** → spawn **`ksp-stack`** (review the jsonl rollup
  for stack holes), then **Gene** to set `phase:` / `next:` / numbers
  and briefing. If Gene’s next name is not in `docs/program/blocks.md`,
  spawn `ksp-stack` **before** the next pilot. Then spawn the next
  phase (scripted continue) unless Gene says wait.
- Pilot returns **4 OFFPLAN** or **2 ABORT** → spawn `ksp-stack` then
  Wernher only if it is a kRPC trap; Gene replans. **Talk** (loop.md /
  briefing) happens here, between phases. Do not auto-fly until Gene’s
  return includes the next `phase:`. Lithobrake freeze keeps throttle 1.
- Gene return `need_stack: <name>` → spawn `ksp-stack` immediately.
- `status` must not overwrite `docs/last-flight.md`.

Isolation is `none` (shared tree, one game). Do not use a worktree for
pilot/fixer — they must see the same `.py` files and the same KSP save.

---

## Handoff

Pilot / CLI writes **`docs/last-flight.md`** on every `phase`/`mun`/`recover` exit
(success or abort). Gitignored. Next agent reads it instead of the raw
terminal log.

```
command: mun
exit: 2
abort: <MissionAbort message or SESSION …>
last:
  <up to 40 heartbeat / ABORT lines>
```

Fixer contract: one new `L-NNN` in `docs/lessons.md`, the library patch
named in that lesson, then stop. Parent re-flies via a new pilot.

---

## Feedback chain (mandatory, same turn as the fixer)

When something is unexpected (exception, wreck, bad Pe, warp stuck, empty
tanks, pre-flight fail):

1. **Stop** (`watch.freeze` if still connected).
2. **Append** `docs/lessons.md` (`L-NNN`: symptom, telemetry, cause, fix module).
3. **Fix the library** (`watch.py`, `warp.py`, `mun.py`, `launch.py`, …).
   New behaviour → a `.py` next to `main.py` and name it in the lesson.
4. Patch `docs/agent-notes.md` only for still-current API facts.
5. Re-fly through `python main.py …`, not a scratch script.

## Order of work

Connection → streams → control writes → `.craft` / `launch_vessel` → mission
loops. Lessons already record kRPC 0.6 traps (`engaged`, protobuf
`get_services`, stream `getattr` form, warp-in-atmo, rails altitude cap,
pad DIP/ESC, FlightWatch).

Every burn/warp/ascent loop holds a `watch.FlightWatch` and calls `pulse()`
each iteration (1 Hz log, faster gates). Print-only heartbeats are not
intervention. `python main.py status` is the one-shot.
