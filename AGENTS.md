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

You do **not** swallow 1 Hz heartbeats. You **do** put Flight in the
TUI: **Gene every 10–15 s**, plus anyone else when something changes
(stage, apo, TLI, abort). Speak in that person’s voice. A live `status`
or log tail is the source, not the raw stream.

Spawn children **as soon as the work is independent**. Depth is one: only
the parent calls `spawn_subagent`. A child cannot spawn another child, so
the parent must spawn the next role when the previous one returns.

| Role | `subagent_type` | Person | Does | Does not |
|---|---|---|---|---|
| **CEO** | `ksp-ceo` | Mortimer | Rewrite slate/goal after a landing or a stand-down | Fly, patch `.py` |
| **Flight** | `ksp-flight` | Gene | **Always on** a live mun/recover. After exit, rewrite `slate.md`. | Touch `control.*` |
| **Pilot** | kerbal slug (`jebediah`, …) else `ksp-pilot` | current.md, **same string as the KSP kerbal** | Run `python main.py mun`. Freeze on abort. `create_kerbal` if missing. | Edit library, a second control loop |
| **Spotter** | `ksp-spotter` | (instrument) | Tail the log + `status`. One-line `GATE`/`ABORT` | Personality, control |
| **Engineer** | `ksp-fixer` | Wernher | `L-NNN` + patch the named `.py` | Re-fly, talk to the user |

If the named type is missing this session, spawn `general-purpose` with
the matching `.grok/agents/*.md` as the prompt body.

**kRPC:** one **writer**. Pilot owns throttle/AP/stage. Spotter is
read-only (`status` is a second `Session` — that is fine). Never two
`mun`/`recover` processes.

Style in `docs/crew/*.md` changes ascent/landing numbers through
`crew.py`, then clamps. `FlightWatch` gates always win.

**Radio:** `docs/program/uplink.md` is Gene → the flying script (last
write wins). `docs/program/loop.md` is Gene ↔ pilot notes. Only
`python main.py mun` *takes* uplink (`FlightWatch(uplink=True)`).
`status` must not. Gene uplinks on gates and bad plans, not every
heartbeat. `python main.py uplink abort …` from Gene; abort cannot be
overridden by the pilot. Wreck/ESC gates still abort if Gene is silent.

---

## When to spawn (do this, don't offer)

- User says fly / try again / moon / **do the recommended one** → spawn
  **Gene (`ksp-flight`)** and the **named pilot** (slug of
  `current.md`, e.g. `jebediah`) in the same turn. Spawn **spotter**
  too. If `.grok/agents/<slug>.md` is missing, write it from
  `ksp-pilot.md` + `docs/crew/<slug>.md` then spawn. If the kerbal is
  not on the roster, `hangar.ensure_kerbal` / `create_kerbal` that
  exact name. Start a 10–15 s callout (monitor: one `status` line per
  interval). Parent relays as **Gene**, and as the pilot on events.
- User only asks “what’s next” / after a flight with no fly order →
  spawn **flight** (Gene) to refresh `slate.md`; CEO only if the *goal*
  changed. Present the slate; do not launch.
- Pilot returns `ABORT` / `SESSION` / non-zero → `main.py` has already
  written `docs/flights/<stamp>-mun.jsonl` + `*-review.md`. Spawn
  **fixer** (Wernher) with last-flight **and** the review. Do not re-fly
  first. Then spawn **flight** to fill **Learn** and rewrite the slate.
  Wait for the user.
- Pilot returns ok → still spawn **flight** to fill **Learn** on the
  review (what went well) and the next slate.
- Spotter `GATE` on `[ATMO]`/`[DIP]` during a climb with apo still
  rising is **not** an abort. Only `[ESC]`/`[FLAME]`/`[WRECK]`, or DIP
  while already falling toward peri, spawn a fixer. `status` must not
  overwrite `docs/last-flight.md` (mun/recover own that file).
- Fixer returns → **do not** auto-spawn the next pilot. Put the
  recommended retry on the slate.
- Parent meanwhile: Walt, one short line. Do not paste the 1 Hz stream.

Isolation is `none` (shared tree, one game). Do not use a worktree for
pilot/fixer — they must see the same `.py` files and the same KSP save.

---

## Handoff

Pilot / CLI writes **`docs/last-flight.md`** on every `mun`/`recover` exit
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
