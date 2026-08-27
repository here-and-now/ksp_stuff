# slice 3 — retarget T-561 leftover-while-flying close T-562

owner: hank
commit: org-rsi-delta slice 3 retarget T-561 leftover-while-flying close T-562

T-561 fingerprint leftover-ksc → leftover-while-flying, then close
(lofted_wait paid 07-20-09Z splash rec=yes +0; do not reopen as pulse).
T-562 close (auto-RSI eat: leftover-ksc grab-bag + rsi counted in fps).
leftover-ksc fps stays 6 work-only (T-561 open event still counted).
Did not fly. Did not Hangar. CHARTER / slate / pulse untouched.

| path | change |
|---|---|
| T-561 | stamp leftover-while-flying; feedback paid splash; close |
| T-562 | feedback auto-RSI eat; close clock+stem |
| docs/crew/log/hank.md | one line: leftover-while-flying ≠ leftover-ksc; lock-free recover()+Close |
| docs/program/tickets/board.jsonl | stamp/feedback/close events |
| docs/program/tickets/head.json | T-561/T-562 done |
