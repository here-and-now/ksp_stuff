# Flight archive

Every `mun` / `recover` exit (ok, abort, session, crash) writes:

| File | What |
|---|---|
| `<UTC>-<command>.md` | Handoff (last ~40 lines) |
| `<UTC>-<command>.jsonl` | ~1 Hz snapshots + uplink/events. Flag changes are immediate. |
| `<UTC>-<command>-review.md` | Envelope, flag timeline, events. Gene fills **Learn**. |

`python main.py review [jsonl]` rebuilds the rollup. Do not paste the
jsonl into a chat. Crew logs get a pointer to the review.
