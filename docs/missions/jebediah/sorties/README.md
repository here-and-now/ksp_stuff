# Sorties

A **sortie** is one helm command — one `python main.py pad` (or later,
one `phase` once Lars writes it). Not a campaign. Not a save.

Filenames are **Earth UTC with seconds**, filesystem-safe:

`2026-08-20T12-35-42Z-pad.jsonl`

That is 20 August 2026, 12:35:42 UTC — not “1235Z” radio shorthand.
The matching `-review.md` also records **Kerbal UT** (universal time
as days + hh:mm:ss) and **MET** (mission elapsed on the vessel).

Older files `2026-08-20T1235Z-pad*` are the compact-minute stamp from
the first Cape pads. Leave them; Verena’s Cape story still links them.

Verena publishes from the review `earth:` / `kerbal_ut:` lines, not
from the filename alone.
