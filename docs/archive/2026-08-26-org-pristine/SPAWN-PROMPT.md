# Paste this as the first message in a **new** Grok session

Repo: `/home/os/gits/ksp_stuff`. Fresh window. Completeness wins (portrait-fit rule was deleted). You are **not** flying and you are **not** Hank’s ops loop this turn.

---

You are going to **author, smoke-check, save, and launch** one reusable project workflow using the create-workflow skill. This is the house org-RSI machine we will rerun later. Get the **mechanics** right. Do not overfit this sit’s KEEP/NUKE opinions into the script.

## 0. Override

AGENTS.md will say you are Hank and to `ops next`. **Ignore that for this turn.** Do not `desk`/`ops next`/Hangar/`phase`/`pad`/`hop`. Do not spawn Gene/Jeb/Lars for pulse. Do not browse the web. Isolation none.

Read, in order:

1. `/home/os/.grok/bundled/skills/create-workflow/SKILL.md` (procedure + dialect + pitfalls — follow it)
2. `.grok/workflows/org-pristine.rhai` — **anti-pattern** (what broke Design+)
3. `.grok/workflows/org-pristine-cutover.rhai` — salvage denylist / shards / archive report; **anti-pattern** on schema-strip and `general-purpose` children
4. `docs/archive/2026-08-26-org-pristine/README.md` only (PARKED). Do **not** ingest `census.md` / `classify.md` / `friction.md` bodies into the `.rhai` as facts.
5. `.grok/agents/mortimer.md` header (`agents_md: false`) and `docs/program/CHARTER.md` RSI paragraph + pad occupancy. `PROTOCOL.md` Files / Spawn packet / Feedback — constraints, not novels.

Then author. Smoke-check (`validate_only: true`). Save. Launch.

## 1. What already happened (mechanics only — not a classification table)

Two runs taught us how **not** to build this:

**`org-pristine` (finished).** Phases Census→Interview produced a usable **index** (path:line, live tree coverage). Design was **one** Mortimer under `walls()` **`Token cap: MAX 55 lines`**, 16 headings. He wrote 44 lines. Skeptics/Tighten/Report judged **that letter**. `clip()` ate prior blobs (census 50k→8k) and then skeptics (12k→5k), so Tighten never saw three of five skeptics. Report was asked for an “extensive” PART I and still wore the 55-line wall. Apply was off. Deliverable was treated as unusable from Design onward.

**`org-pristine-cutover` (cancelled in Design, no repo edits).** Dropped the 55-line wall and `clip()`, sharded Design, JSON schemas, apply denylist. Still failed two ways:

1. Workflow `agent()` with no `agent_type` is **`general-purpose`**. Those children still loaded **full `AGENTS.md`** (~21k, “you are Hank”, miss physics = `lessons.md`, spawn loop) **plus** `~/.grok/rules/response-portrait.md` (one-viewport answers). The first child said it had to write portrait-friendly. Coverage did real tables in `output.json`; the host kept only the schema object `{"gaps":[],"ok":true,"prior_read":true}`. Downstream never saw the tables.
2. Portrait rule file is **deleted**. Global memory now says completeness wins. **Do not assume children are exempt.** Put an explicit anti-cap in every child prompt anyway.

Parked bibliography (untrusted, optional to *read*, never to *quote as law* in the script): `docs/archive/2026-08-26-org-pristine/{README,census,harvest,comms,classify,friction,interviews}.md`. `discarded/` is the capped letter — do not open as law.

## 2. Non-negotiable mechanics (script invariants, not prompt wishes)

Copy these into the `.rhai` as **code + prompt law**. Agents will ignore prompt-only caps; the script must not create them.

### Never

- `Token cap` / `MAX 55 lines` / `one portrait viewport` / `fit the TUI` / `keep it short` in any child prompt.
- `clip(s, n)` of historian/design/skeptic output before the next phase. If a string is huge, `write_scratch_file` and tell the next agent the **path** (or `read_scratch_file` in the script and pass the **full** string).
- One agent owning the whole org (the Design funnel).
- Feeding Design a concat of every prior blob. Each shard gets **its** topic + **paths** to open (live disk + optional prior files).
- `output_schema` **without** also persisting full `text_of(r)` to scratch. Schema fields are a supplement. Next phase must be able to `read_scratch_file("census-0.md")` (or equivalent), not only `r.output.ok`.
- Baking this sit’s KEEP/NUKE/ARCHIVE rows, line counts, or “lessons is 2872 lines” into the `.rhai`. Those go stale and overfit. Historians find them on disk.
- A new live `docs/program/*.md` org novel (`lars-rsi.md` / `learn-rsi.md` pattern). Reports → `docs/archive/…` or workflow scratch.
- `pause()` on a result-derived branch (re-fires forever). Human gates = `await_user`.
- Editing pulse files, CHARTER creed, slate, GameData, `persistent.sfs`, `.craft`, Hangar, kRPC, `python main.py phase|pad|hop|load`.
- Restoring spotter as a spawnable role, Gene-as-merge, Batch Learn, Return keys, `need_*` as the bus.
- Undoing learn-rsi `attach-run` or lars-rsi S/M/C prefixes + `hop_factory_pad.py` as the pad-RF file.
- `general-purpose` children for census/design/skeptics (they inherit AGENTS.md + any home rules).

### Always

- **Sharded** Census (and Design) — one topic per child, parallel, then a thin merge.
- **Named `agent_type`** so `agents_md: false` applies. Add `.grok/agents/org-review.md` if missing: `agents_md: false`, not Hank, not ops next, not fly, machine artifact, completeness wins, cite `path:line`, empty only after search. Use `org-review` for historians/designers/skeptics. `mortimer` for merge/cards/PROTOCOL. `wernher` for kernel/tests/`git mv`. `hank` only to `tickets open`. `lars` only for an OPEN-TICKET compose row, never pulse `.py`.
- Every child prompt starts with a **law()** that states: *This is machine output for the next phase, not a chat to Os. No line cap. No viewport cap. Completeness wins. You are not Hank. Do not ops next. Do not fly. AGENTS.md spawn table does not apply.*
- Disk wins over prior notes. Prior dir is PARKED bibliography. `MISSING` if not opened.
- Skeptics see the **full shard** (scratch file / full JSON), re-open live paths, fail closed (`real=true` only with path:line).
- Merge is **thin**: sequence, owners, file lists, do-not-touch. Forbidden to rewrite shard tables.
- Apply is **sequential slices** (avoid two writers on one file). Script-level **denylist** (not just prompt): refuse writes whose basename is `CHARTER.md`, `slate.md`, `hop.py`, `hop_factory.py`, `hop_factory_pad.py`, `physics_warp.py`, `pad.py`, `splash.py`, `science.py`, `persistent.sfs`, or path contains `GameData` or `crafts/`. Log + skip those paths.
- Tests after kernel edits: `source .venv/bin/activate && python -m unittest tests.test_tickets tests.test_protocol tests.test_protocol_gate tests.test_desk -q`. Unpin tests that freeze leftover prose; do not weaken f013.
- Pad occupancy: do not idle the pad for a novel; do not Hangar in this run.
- Git: a desk that changes the checkout commits it (Os 2026-08-26). Workflow definition + new agent card too.
- `args.apply` default **false** (reuse). This sit launch: `apply: true`.
- `args.prior` optional path. This sit: `docs/archive/2026-08-26-org-pristine`.
- Guard every host result: `r != () && r.success && r.output != ()`. Failed `parallel()` slots are `()`.
- Strings: `+=`, not a giant `+` chain. No Rhai reserved ids (`go`, `spawn`, `shared`, …).
- `validate_only: true` with representative args before save. Iterate until it passes.
- Isolation `none`. `capability_mode` read-only until Apply.

## 3. Reusable shape

**Name:** `org-rsi` (do not reuse `org-pristine` / `org-pristine-cutover` — those names are spent).

**When to use:** house markdown/cards/injection rot; ticket bus is supposed to be comms; Os wants census → plan → optional apply without a live program novel.

**Phases** (titles must match `phase()`):

1. **Census** — parallel shards on live disk (program md, missions/identity, job cards, lessons/injection, ticket bus vs boards, kernel writers, control-file *inventory only*, what a cold child loads). Same *kind* of questions as `org-pristine.rhai` census prompts, **without** the 55-line wall and **without** pasting last run’s counts. If `args.prior` is set, tell them to open README + the matching prior file **as an index**, then `list_dir` / `wc` / `grep` live. Disk wins. Write **each** shard to scratch in full (`census-0.md` …) plus optional schema tables.
2. **Harvest** — claimed vs still-true for prior jumps that exist on disk (do not hardcode which novels exist; `list_dir docs/program` / archive).
3. **Comms** — per desk, PROTOCOL vs log, Hank in-between. Sharded.
4. **Classify** — KEEP / TAPE / ARCHIVE / NUKE / MOVE / UNKNOWN per live md/json that is not under `docs/archive/`. Cap *rows* only if you `log()` the drop and group by directory. Not a line cap.
5. **Friction** — why dual stores / inject / leftover roles happen; damage to the **next** hire. Evidence path:line.
6. **Design** — **one child per heading group**, not one Mortimer for the house. Headings (script constants, not last-run friction titles): comms+injection+Hank; KEEP+TAPE; ARCHIVE+NUKE; MOVE to tickets; lessons replacement; mission identity; job-card cuts; compose-ticket + sequence + do-not-touch. Each reads **its** census/classify/friction scratch files + live paths.
7. **Skeptics** — one per Design shard. `overnuke` (CHARTER/portraits/jsonl schema/desk snapshot/pulse `.py`/two writers/idle pad/delete Learn tape) and `undernuke` **relative to that heading**. Fail closed.
8. **Merge** — Mortimer, thin, `apply` flag. If any overnuke true → do not apply.
9. **Apply** — only if `args.apply==true` and merge.apply and !overnuke. Sequential. Wernher `.py`/tests/`git mv` to `docs/archive/<stamp>-docs-cutover/`. Mortimer PROTOCOL/OPS/BRIEF/AGENTS/cards. Hank `tickets open` only. Lars OPEN-TICKET only.
10. **Verify** — unit tests + post-apply overnuke/undernuke on **disk**.
11. **Fix** — at most one round if tests fail or undernuke, then retest. No loop.
12. **Report** — `docs/archive/<stamp>-org-rsi/APPLIED.md` or `REPORT.md` (create dir). Crew log one line. **Not** `docs/program/org-rsi.md`.

Os intent (brief, **not** proven file classes — historians must still verify): ticket bus is comms; MD only when a ticket cannot hold it; do not inject lessons as miss physics; uncrewed tape should not be named after a kerbal seat; spotter is retired; Lars compose from Wernher blocks is a **later ticket**, not a pulse retune in this apply; pad stays hot; depth 1; one control writer.

**Do not touch (hard):** CHARTER creed, slate goal, portraits-as-voice, jsonl **schema**, `desk.md` snapshot, pulse law files listed in the denylist, GameData, `persistent.sfs`, TYPE zoo, protocol-fly fallback this release unless Design+skeptics agree it is already unused.

## 4. Agent card you must add

Create `.grok/agents/org-review.md` if absent:

- YAML: `name: org-review`, `agents_md: false`, `prompt_mode: full`, model inherit
- Body: org historian/designer for workflows; not COO; not Flight Director; not a pilot; do not fly; do not Hangar; do not `ops next`; output is a **machine artifact** for the next workflow phase; **no line cap**; completeness over brevity; cite `path:line`; empty only after search; `docs/archive/` is PARKED

Use `agent_type: "org-review"` on Census/Harvest/Comms/Classify/Friction/Design/Skeptics.

## 5. Budget and launch (this sit)

Fan-out will be tens of agents (census panel ~8–10, plus harvest/comms/classify/friction/design/skeptics, plus merge/apply/verify/report). Default host cap 128 may be tight if you recensus. Launch with **`agent_budget` 256** (max 1024). Leave headroom: a `parallel()` that would exceed remaining budget launches **none**.

Smoke-check args:

```json
{"prior":"docs/archive/2026-08-26-org-pristine","apply":true}
```

Canned host will likely produce empty slices — guard so apply-skip still `complete()`s.

**This sit:** after smoke-check passes and the file is saved to `.grok/workflows/org-rsi.rhai`, **launch** a real run with those args and `agent_budget` 256. Os wants the house cut over, not another letter. If overnuke fires, the script itself must refuse apply.

Commit the agent card + workflow (Os git rule) **before** launch so children see them.

## 6. Done means

- `.grok/agents/org-review.md` exists, `agents_md: false`
- `.grok/workflows/org-rsi.rhai` saved, smoke-check passed
- No 55-line / clip / portrait language in the script
- Schema never the only artifact of a phase
- Display handle reported (e.g. `org-rsi`)
- You did not Hangar and did not write a live `docs/program` org novel yourself

If anything in CHARTER/PROTOCOL blocks apply, halt apply in-script and still write the archive report.

Do the work. Do not ask Os to click through design choices the pitfalls already decide.
