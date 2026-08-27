# slice 1 — leftover-ksc auto-RSI clock

owner: wernher
commit: org-rsi-delta slice 1 leftover-ksc auto-RSI clock

`_rebuild` fps increments only on work (open + first-set patch). `type=rsi`
does not bump. `maybe_open_rsi`: n is work-only; no-dup while an rsi for
that stem is open; remint only after 3 work tickets created after the last
rsi open/close. `ops.py` hire path unchanged (`_org_rsi_tickets` no stem
skip; fly_ready still parallel-hires Mortimer; lock-live skip Mortimer).
Practice leftover-ksc last-write 6 work-only. Do not reopen T-561 as pulse.
Do not patch pulse compose.

| path | change |
|---|---|
| tickets.py `_rebuild` | skip fps increment when type=rsi |
| tickets.py `maybe_open_rsi` | work-only clock + 3 new work after last rsi |
| ops.py `_org_rsi_tickets` | docstring only; no leftover-ksc skip |
| tests/test_tickets.py | rsi open does not raise count; close+1 no remint; 3rd after close remints |
| docs/program/world-model.md | Practice leftover-ksc 6 work-only |
