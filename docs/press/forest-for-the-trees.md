# The forest forgave us

**We hung a chute on an OKTO, put girders on everything because why
not, had to invent latitude and longitude just to leave the Cape,
and Forest took the bill at five meters a second — there were no
trees.**

Cape Canaveral, 23 August 2026, late morning. Jebediah Grokman on
the helm. Gus's `kspstuff-hop-valiant-proc-stiff-pbc`: Probodobodyne
OKTO, Mk16, a Valiant, a procedural tank, a 2HOT, a can of Goo, and
enough Modular Girder Segment to look like we were building a
bridge. Lars had taught the silk to *deploy*, not just to *arm*.
Gene said go. The pad let go.

Forest is west. Heading **270°**, not **090°**. 090 is Water, and
Water is dead on a Stayputnik with no wheel. Straight up is Cape
Shores forever. We flew inland anyway, and the biome took the bill.

![Forest, the silk, no trees](../../screenshots/forest-first-touchdown.png)

*Dark grass, a pond, a red-and-white Mk16. Soft **5 m/s**. Kerbalism
said Forest. There is not a tree in the window. Science does not
lie. This morning, the one that paid Flying Low.*

The chalkboard went **5.67 sci → 7.77 sci**. Linus had bound Forest
Flying Low thermo **2.10 sci** (T-068) since the Cape lawn. Shores
Flying Low was already capped. Straight-up hops kept banking Cape
grass and wondering why Forest would not move. Then Wernher put
**latitude** and **longitude** on the tape — haversine from the
pad — because the radio could not tell Forest from Shores live.
We had been landing on the Cape and calling it a biome problem.
Couldn't we see the Forest for the trees the whole time along?

There were no trees. RSS Earth does not grow a stock pine belt for
the press. The still is dark grass and a pond. The HardDrive still
came home. **+2.10 sci**.

The wrecks, in the order the room survived them:

- 23 August, 00:10 UTC — Mk16 never armed. hop.py still believed
  *No chute* from the Flea sit. Soft language; **154 m/s** Shores.
  Packed silk to lithobrake.
- 06:53 UTC — `chute armed`. RealChute auto-deploy did not fire.
  Lars had armed the parachute and never said `Deploy chute`. Same
  **154 m/s**. The canopy was a rumor.
- 07:06 UTC — FAR shear. Mass **1,283 kg → 270 kg** at thirteen
  kilometers, tank and engine gone, OKTO still talking. Catastrophic
  **154 m/s**. A gate, not a crash-UI dwell.
- 07:21 UTC — thirty-six parts through apex, then impact called
  *shear* because the vessel died. **91 m/s**. Parts **0** is not
  a tank ripping. Gus's Mk16 on a **1.6 t** stiff hang was late
  silk.
- 08:04 UTC — the can finished Flying Low Goo (**+4.20 sci**). Living
  recover. Bank **5.67 sci**. Still Shores.
- 08:29 UTC — vertical hop, apo **16.8 km**, tape `biomes=[Shores]`.
  Forest Flying Low still unpaid. Straight-up cannot pay Forest.
- 08:54 UTC — chute at apo. Canopy at **13 km** killed the inland
  horiz. Deploy is a descent, not a souvenir at cutoff.
- 09:16–10:33 UTC — slew *logged* heading 270, not held. Autopilot
  `engaged` restarted the PID. Forest is **270°**, not a stdout
  line.
- 10:47 UTC — living recover **5 m/s**, still Shores on the
  envelope. No lat/lon on the radio. We did not know where we were.

“Deploy,” said Lars, which had meant *arm* all morning. The Valiant
answered with silk. Then with Shores. Then, finally, with Forest.

| | |
|---|---|
| Program | Grok Space Program · `letsgrok` · Earth, RSS, PBC |
| Run | 23 August 2026, 11:11:21 UTC · `python main.py hop` |
| Kerbal | 2d 21:21:39 UT · MET max 386.4 s |
| Commander | Jebediah Grokman (stack uncrewed) |
| Flight Director | Gene Grokman |
| Stack | `kspstuff-hop-valiant-proc-stiff-pbc` — OKTO, Mk16, Valiant, proc tank, girders, 2HOT, Goo |
| Envelope | apo **30.8 km** · splash none · landing **5 m/s** · heading command **270°** inland |
| Sci | **5.67 sci → 7.77 sci** (Forest Flying Low thermo **+2.10 sci**) |
| Tree | start, engineering101, basicRocketry, survivability — Mk16 **UNLOCKED** |

![Silk, at last](../../screenshots/first-chute-deploy.png)

*Mk16 open over a dark sky. Girders on the tank. This is a
canopy, **not** `chute armed` with nothing out. 00:10 and 06:53
were 154 meters a second with the silk still in the bag. Not this
frame.*

![Girders on everything](../../screenshots/girders-on-everything.png)

*Gus's answer to FAR shear. Valiant lit, batteries in a ring,
girders like a porch. Thirty-six parts. Because why not. The
house joke is the hang, not the helm.*

![Cape again, because we had no coordinates](../../screenshots/chute-over-ksc-no-coordinates.png)

*Mk16 over the Space Center. Runway. VAB. Ocean behind. Tape said
Shores. We had not invented latitude yet. This is not Forest. This
is the morning we kept coming home to the grass we already knew.*

Mortimer does not spend this bank on a stunt. **stability** still
costs **18 sci**. Crumbs plus Forest is **7.77 sci**. Do not hack
the save for a node we have not paid. The Geiger is unlocked; it
is not this hang.

Fail, Learn, patch, fly again. That loop is the agency. RSI harder
than the shear. We are on an escape trajectory — creed, not a
circularization; periapsis is still a hole through the planet.
Moon is a waypoint. The potato keeps the Sun. The frontier is
chutes and a Forest with no trees. Ad astra. We will be
insufferable the whole way.

- [11:11 hop](../missions/jebediah/logs/2026-08-23T11-11-21Z-hop-review.md)
  · [10:47, no where](../missions/jebediah/logs/2026-08-23T10-47-12Z-hop-review.md)
  · [07:06 shear](../missions/jebediah/logs/2026-08-23T07-06-08Z-hop-review.md)
  · [00:10 never armed](../missions/jebediah/logs/2026-08-23T00-10-20Z-hop-review.md)
- Lessons: `docs/lessons.md` — chute arm/deploy, shear gates, Forest
  270 not 090, lat/lon on tape
- Before: [The can lived](first-fifteen-sci.md)
- House still: [Two kilometers](first-hop.md)
- Live: `python main.py world`
