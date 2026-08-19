# Slate

**Recommended:** Wernher — TLI `execute_node` lost the patched-conic (Pe=None after node-done, apo=11.17 Mm). Keep or recorrect the 12–50 km Mun encounter through the finite burn; do not abort a live 304×11170 km ellipse. Then Val `python main.py mun`.

Last `mun` (Val, 1839Z, 1114 s): L-027 pad recover worked. Parking 300×305 km. TLI burned, then ABORT `TLI lost Mun encounter Pe=None`. Frozen in Kerbin ellipse LF=429 parts=7. Not a wreck. Review `docs/flights/2026-08-19T1839Z-mun-review.md`.

- Wernher: recorrect TLI when `_next_pe` is None after the node (mid-course / replan), keep Pe 12–50 km. Then Val mun (hangar will recover this ellipse).
- Val mun from pad now — same TLI abort until the library holds the intercept.
- Leave this ship, wait — 11 Mm Kerbin apo with no Mun Pe is a dead transfer.

Pick a line or say **do the recommended one**.
