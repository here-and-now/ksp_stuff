# Speed — desk snapshot and fewer Gene hires

The loop works. It is slow because Gene is hired as a **merge bus**
after every specialist, and every child re-runs `world` / `tech` /
`parts`. Honesty and `go: yes` stay Gene-only.

Five desk audits (helm, Gene, Linus/Gus, Lars/Wernher, parent) plus
an org plan. First slice is in: `python main.py desk`.

## A. Desk inputs

| Priority | What | Who stops looking it up |
|---|---|---|
| **P0** | `python main.py desk` — lock, sci, tree, capable, craft, card, last-flight, stack, helm-tech | Gene, Linus, Gus, Lars, helm |
| **P1** | leftover vessels from `persistent.sfs` (F-006) | Gene Hangar vs `phase` — **in desk** |
| **P1** | `python main.py helm-card` — eid, part, hang_s, do_not_toggle | Jeb loop — **in** |
| **P1** | Science leftovers (cap − sci) on desk | Linus — **in** |
| **P1** | sci_delta, f013, review path on desk | Lars — **in** |
| **P2** | `hangar.install_signed`; wait `file=recording` when rem=0 and run=1 | pad/hop — **in** |

Tape/EC: `catalog.ExperimentCfg` already has `size_mb` / `data_rate` /
`ec_rate`. P1 dumps it on desk so Linus/Gus stop napkin math.

## B. Org / comms

Replace Gene-after-every-`need_*` with:

1. Os go → specialists if last Gene already named them, else one Gene draft.
2. Same turn: Linus opportunities ∥ Gus capable (not bind).
3. Linus bind after `capable: yes`.
4. **One** Gene merge → only `go:`.
5. Helm. Learn = one Gene. Miss = Lars then one Gene.

Legal parallel stays file-split. Illegal: two helms, Gene+helm, two
desks on one file, bind before capable.

Packet: `docs/program/desk.md` (parent writes it) + ≤2 role paths.
Parent copies f013 (tree, instrument, unlocked, on_craft).

## C. First PR (this slice)

- `desk.py` + `python main.py desk` + `tests/test_desk.py`
- `AGENTS.md` spawn loop (skip Gene between specialists)

P1/P2 in: leftover vessels + Science leftovers on `desk`,
`python main.py helm-card`, Hangar `install_signed`, wait `file=recording`.

Expected: 5–7 Gene/sit → 1 draft + 1 merge (or 0 draft + 1 merge).

## D. Do not change

Gene only `go: yes`. One kRPC writer. Parent does not patch `.py`.
Depth 1. Honesty / F-013 / Lars XOR Wernher / helm copies CLI.
