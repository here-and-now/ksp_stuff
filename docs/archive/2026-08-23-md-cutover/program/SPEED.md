# Speed — desk snapshot and fewer Gene hires

The loop works. It was slow because Gene was hired as a **merge bus**
after every specialist, and every child re-ran `world` / `tech` /
`parts`. Honesty and `go: yes` stay Gene-only. Kernel now batches
Wernher on systems tickets; Learn is a fly-ticket field.

Five desk audits (Commander, Gene, Linus/Gus, Lars/Wernher, parent) plus
an org plan. First slice is in: `python main.py desk`.

## A. Desk inputs

| Priority | What | Who stops looking it up |
|---|---|---|
| **P0** | `python main.py desk` — lock, sci, tree, capable, craft, card, last-flight, stack, note-tech | Gene, Linus, Gus, Lars, Commander |
| **P1** | leftover vessels from `persistent.sfs` (F-006) | Gene Hangar vs `phase` — **in desk** |
| **P1** | `python main.py sit-card` — eid, part, hang_s, do_not_toggle | Jeb loop — **in** |
| **P1** | Science leftovers (cap − sci) on desk | Linus — **in** |
| **P1** | sci_delta, f013, review path on desk | Lars — **in** |
| **P2** | `hangar.install_signed`; wait `file=recording` when rem=0 and run=1 | pad/hop — **in** |

Tape/EC: `catalog.ExperimentCfg` already has `size_mb` / `data_rate` /
`ec_rate`. P1 dumps it on desk so Linus/Gus stop napkin math.

## B. Org / comms

Replace Gene-after-every-`need_*` with:

1. Os go → specialists if last Gene already named them, else Gene only if `ops next` names him.
2. Same turn: Linus opportunities ∥ Gus capable (not bind); Wernher on systems.
3. Linus bind after `capable: yes`.
4. Gene `go:` only when `ops next` hires him — not a merge after specialists.
5. Commander. Learn = `payload.learn` (Gene hire only if `needs_learn`). Miss = Lars; Wernher iff kRPC trap or open systems.

Legal parallel stays file-split. Illegal: two Commanders, Gene+flight, two
desks on one file, bind before capable.

Packet: `docs/program/desk.md` + `tickets packet T-NNN` + BRIEF (no BOARD.md).
Parent copies f013 (tree, instrument, unlocked, on_craft).

## C. First PR (this slice)

- `desk.py` + `python main.py desk` + `tests/test_desk.py`
- `AGENTS.md` spawn loop (skip Gene between specialists)

P1/P2 in: leftover vessels + Science leftovers on `desk`,
`python main.py sit-card`, Hangar `install_signed`, wait `file=recording`.

Expected: 5–7 Gene/sit → 1 draft + 1 merge (or 0 draft + 1 merge).

## D. Do not change

Gene only `go: yes`. One kRPC writer. Parent does not patch `.py`.
Depth 1. Honesty / F-013 / Lars XOR Wernher / Commander copies CLI.

## E. RSI-JUMP kernel (2026-08-22)

Loop shape stays. `needing_go` batches systems / Wernher. Learn is
`payload.learn`, not a TYPE. Skim is desk + BRIEF + this ticket (no
BOARD.md). Reasoning floors (Os 2026-08-23): Jeb/Lars low, Wernher
medium, Mortimer medium. `rsi_loop=software` → Wernher.
Do not hire Gene as a merge bus.

## F. Pad occupancy (Os 2026-08-23)

Tape is the product. An idle pad is a miss. Inventory (Linus shelf,
Gus many signed hangs) fills **during** lock live. Uncrewed miss:
Hank leftover (seconds; `recover()` + Close, never leftover-ksc load,
never revert) → Lars on the **live** control file if it broke →
re-fly last `cli:` or the next already-signed alt. **Do not hire
Gene to consider.** Wernher standing `type=systems`. Expected: pad
flying; Gene 1 stamp per sit, not a 15 min conference after the hop.

## G. Live watch (Os 2026-08-23)

`ship.md` is the live eye (disk). Commander reacts in-flight. Hank
reads it from time to time — no `status`, no jsonl. Off-nominal:
hire the owning desk (Gene/Lars/Wernher). Nominal: silent ground.
After-flight review stays Hank. Do not spawn a spotter.

## H. RSI (Os 2026-08-23)

Stumble → ticket. Thin tape is first-class (`type=systems`). Log more
kRPC. Bind science side-by-side. **Idle pad is a sin** — a letter
does not stop the batch.
