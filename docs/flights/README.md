# Flight archive

Every `phase` / `mun` / `recover` exit (ok, abort, session, crash) writes:

| File | What |
|---|---|
| `<UTC>-<command>.md` | Handoff (last ~40 lines) |
| `<UTC>-<command>.jsonl` | Telem tape. Cruise ~5 Hz, ~20 Hz below 2 km / time-to-impact. `kind=state` plus `kind=landing` on splash/land. |
| `<UTC>-<command>-review.md` | Envelope, flag timeline, events. Uncrewed Learn is Hank `attach-run`. |
| `docs/flights/index.jsonl` | Run index: path, landing class, impact_ms, heading. |

Link a run to the fly ticket:

```
python main.py tickets attach-run T-013 --path docs/missions/<id>/logs/<run>.jsonl
python main.py tickets landing T-013
```

Skim packet prints `landing: catastrophic impact=233 m/s …`. The jsonl
stays `--deep`. Do not paste the tape into a chat.

`python main.py review [jsonl]` rebuilds the rollup.
