# Ticket bus

Source of truth for Hank. Schema and dispatch: [`../OPS.md`](../OPS.md).
Spawn how-to: [`BRIEF.md`](BRIEF.md).

```
python main.py tickets list
python main.py tickets list --category bug --tag hard-splash
python main.py tickets inbox --desk lars
python main.py tickets open --type control --category bug --tag hard-splash \
  --title "…" --severity S2 --priority P1 --desk lars
python main.py tickets packet T-008
python main.py tickets packet T-008 --deep
python main.py tickets attach-run T-013 --path docs/missions/jebediah/logs/<run>.jsonl
python main.py tickets landing T-013
python main.py tickets from-need --need need_stack --title "hop-splash"
python main.py ops next
```

Skim packet: desk + board + BRIEF + landing one-liner. Jsonl / PNG /
reviews only on `--deep`. `ops next` prints `reasoning=` and the
packet command. Never xhigh. Mortimer always high.

Categories replace cards: `craft`, `science_opportunity`, `bug`,
`improvement`, plus `flight` / `recover` / `org`. Tags are free.
