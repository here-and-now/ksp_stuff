# Slate

**Recommended:** Wernher L-023, then Mun from the pad — Val.

Last `mun` (Jeb) made LKO and TLI. Mun SOI arrived hyperbolic: planned Pe 23 km, actual peri −109 km. Warp-to-Pe lithobraked (~2.8 km, `parts=-1`). FlightWatch did not abort; process hung until SIGTERM (exit 143). Wreck → Val. Do not re-fly until warp/watch refuse a subsurface Pe.

- Wernher L-023 (`warp.py` / `watch.py`): no rails-to-Pe if peri < 12 km; abort on `parts<=0` / lithobrake. Then Val `python main.py mun` (hangar must leave the wreck first, L-022).
- Leave-flight / recover the Mun wreck only, then hold for L-023.
- Stand down (Mortimer) if the leftover wreck still NREs the pad.

Pick a line or say **do the recommended one**.
