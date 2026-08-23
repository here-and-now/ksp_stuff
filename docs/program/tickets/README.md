# Ticket bus

Source of truth for Hank. Schema and dispatch: [`../OPS.md`](../OPS.md).
Spawn how-to: [`BRIEF.md`](BRIEF.md). Sit object is the fly ticket +
`desk.md`. Seated `plan.md` is a Gene **render** (`hop_apo` /
`expect_*` stay there). `python main.py protocol fly` prefers the
seated fly ticket (`go` / `cli` / `campaign`) and falls back to
plan + science dump so a missing board does not brick.

Eleven types: `fly` `science` `vehicle` `control` `systems` `org`
`rsi` `ctt` `recover` `press` `ops`. Ask / itch / friction:
`--type ops --tag ask|feedback|explore`. Paid node: `--type ctt`.
Press: `--type press`. Desks `tickets open --type …`. Do not emit
`need_*` / `card:` / `recommended:` / `ask:` as return keys.

```
python main.py tickets list
python main.py tickets list --category bug --tag hard-splash
python main.py tickets inbox --desk lars
python main.py tickets open --type control --category bug --tag hard-splash \
  --title "…" --severity S2 --priority P1 --desk lars
python main.py tickets open --type ops --tag ask --title "…" --desk gene
python main.py tickets packet T-008
python main.py tickets packet T-008 --deep
python main.py tickets attach-run T-013 --path docs/missions/jebediah/logs/<run>.jsonl
python main.py tickets landing T-013
python main.py telem docs/missions/jebediah/logs/<run>.jsonl
python main.py telem docs/missions/jebediah/logs/<run>.jsonl --window impact
python main.py ops next
python main.py protocol fly
```

Skim packet: desk + this ticket + BRIEF + landing envelope (pad/last
heading, apo, hz). No BOARD.md. Jsonl stays on disk — query `telem` /
`tickets landing`. `--deep` is PNG / craft / last-flight / tape CLI,
not rows. Reasoning: **low** Walt/S4; **high** Mortimer/rsi/org/S1;
else **medium**. `ops next` prints `reasoning=` and
the packet command (skim; no auto `--deep`). Never xhigh.

Categories replace cards: `craft`, `science_opportunity`, `bug`,
`improvement`, plus `flight` / `recover` / `org`. Tags are free.
`ops --tag ask|feedback|explore`. Commander `cli` is fly `payload.cli`.
