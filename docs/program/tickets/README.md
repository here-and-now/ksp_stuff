# Ticket bus

Source of truth for Hank. Schema and dispatch: [`../OPS.md`](../OPS.md).

```
python main.py tickets list
python main.py tickets open --type fly --title "…" --severity S2 --priority P0 --desk gene
python main.py tickets packet T-008
python main.py tickets packet T-008 --deep
python main.py tickets from-need --need need_stack --title "hop-splash"
python main.py ops next
```

Skim packet: desk + board + type-specific one-pagers. Jsonl / PNG /
reviews only on `--deep`. `ops next` prints `reasoning=` and the
packet command. Never xhigh. Mortimer always high.
