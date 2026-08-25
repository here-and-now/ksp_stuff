# Press voice (Os 2026-08-25)

Verena Grokman, Communications. Locked with Os. This file is the law
for `docs/press/`, `INDEX.md`, and README prose. Facts still true.
Never invent orbit. No CDN. Repo-relative `screenshots/` only.

A reader may know Kerbal Space Program in outline (apoapsis, periapsis,
probes, science points buy the tree) and not be watching the hop.
Keplerian elements and basic physics do not need a primer. Kerbal
sit-band names, house slang, and part nicknames do. Advanced maneuvers
(gravity assist, Oberth, first real heat) get a short headed aside.

## Numbers

The tables hold the digits. Prose almost never quotes a figure.

A number may appear in the story only if it is a **first** or a
**paid node**. Spell it in words. Bold it only if it is THE first
this piece exists to announce.

Allowed in prose (words): we lofted two hundred and seventy-five
kilometers. Earth paid five. The can sat down at nine meters a second.
Mortimer paid stability.

Table only: leftover 0.29 / 1.80, heading 270°, MET 440.5, EC, q,
parts 28 → 1, 9.47 → 18.19, 274.5 km, 3.4 / 4.0, drums 002423.

Do not glue a joke to a figure. Do not bold a box score.

`sci` is a table word. Prose says science, the bank, Earth paid.

## Two tables

Every article gets a **this hop** table. Add a **campaign records**
table only for rows that are firsts or that moved this week. Omit a
row if tape does not have it. Do not reprint last week's highest apo
on a piece that did not take it.

This hop, always:

| Field | Value |
|---|---|
| Date | Earth UTC from the review |
| Craft | italic nickname + `filename` |
| Peak apoapsis | km, suborbital/orbit honest |
| Peak speed | if tape has it |
| Landing | splash / land / leftover, where |
| Science | in → out |

Optional rows: Sit (Kerbal band @ biome), Tree, Paid node, Load
`rd-<node>`, Next node cost. Kerbal UT / MET live here, not in prose.

Records, only if moved: Highest apoapsis, Highest speed, Softest
landing, Peak science bank, First \<thing\>.

The old unlabeled two-column dump (Program / Run / Kerbal / Commander /
Envelope as one cell) is retired.

## Wrecks

Short punchy owns. No digits in the bullets. The wreck is funny
because **we** walked into it — never a joke at Lars, Gus, Gene, Jeb,
or Os.

If the string is the plot, a small wrecks table may hold When / What
happened / Peak / End. That table is allowed to have digits. The
bullets above it are not.

Two house-owns per piece: one in the dek or the wrecks, one in the
close. Chaos is the weather. Do not blame.

## Dek

Bold open. Story plus one joke. No digits. Title-as-words are allowed
when they are the myth ("two kilometers"), not a box score of wreck
speeds. Then the hero still.

## Punchlines

README may keep the house drums: periapsis is a hole through the
planet; we will be insufferable the whole way; fail, Learn, patch,
fly again.

Each press piece invents a **new** joke. Do not recycle those drums
in articles. Do not use them as captions. "Not orbit" / "not a circle"
only when the still could lie — italic stress, no apo glued to it.

Fail / Learn / patch may appear in an article when the piece is about
the loop, not as a default stamp closer.

## Names and gloss

First mention: italic name plus a one-line gloss. Later: italic only.
No invented ship names (_Curse Thief_ is forbidden until Os names a
hang). Call the stack by the engine or core people already know:
_Valiant seven-tank_, the _Flea_. Filenames live in the this-hop table
as `code`, never in a sentence.

Parachute is the default word. Silk (or another word) is a punchline,
not the name of the part. The part is the _Mk16_.

_Stayputnik_ — black probe core, no steering wheel of its own.
_2HOT_ — thermometer.
_Mystery Goo_ — the can; you observe it after you leave it running.
_Geiger_ — radiation counter.
_Mk16_ — parachute.

## Jargon

Assume basic KSP and Kepler. Do not explain apoapsis.

Kerbal sit-bands (`Flying High`, `Flying Low`, `In Space High`) are
**table-only**. Prose describes once in Earth words, then a short
house phrase: fifty kilometers and up, the first band that is actually
space-ish on this Earth; later "the High band" / "over the Forest,
high". Never `FlyingHigh` in a sentence.

Biome names (Forest, Shores, Water, Cape) may appear in prose as
places. If the window and the lab disagree, say so.

Prefer rocket / stack in prose. "Hang" is house — translate once or
skip.

Prefer **science bank** for the scoreboard moving. If you say
chalkboard, the same sentence must make obvious that we are gathering
science. Never "the chalkboard went 9.47 → 18.19".

## House law in the body

F-014 and F-015 stay in the story; they are myth. Tell the trap.
Put 18.19 → 0.19 and the node cost in the table.

kRPC will not sell a node. Mortimer edits the bank and loads a named
copy — never the live save. Load the live save and the spend vanishes.
That trap is F-014. The potato around the Sun is F-015: an asteroid
we did not fly, seated because the window was honest.

Do not rewind the clock. The crash window is not a time machine.
Those sentences may stay.

## Images

No CDN. No remote hosts. Repo-relative `screenshots/<slug>.png` only.
Never overwrite `first-mystery-goo.png`.

One full-width **hero**. Supporting stills in scaled side-by-side
pairs (HTML, ~50% width, local paths). Later stills may go full-width
again only if the caption is a **feeling**, not evidence. A Geiger
panel, a toolbar, a Mission Summary: pair or omit. Os's motor-lit
_Flea_, a limb pretty enough to lie about: poster is allowed.

Pattern (press paths are `../../screenshots/`):

```html
<p align="center">
  <img src="../../screenshots/hero.png" alt="feeling, not a box score">
</p>
<p align="center"><em>One visual sentence. No digits.</em></p>

<table>
<tr>
<td width="50%"><img src="../../screenshots/a.png" alt=""></td>
<td width="50%"><img src="../../screenshots/b.png" alt=""></td>
</tr>
<tr>
<td><em>Caption a. No digits.</em></td>
<td><em>Caption b. No digits.</em></td>
</tr>
</table>
```

A local collage PNG under `screenshots/` is allowed if a pair still
looks wrong. Do not fetch images. Do not invent a peak.

## Captions

One visual sentence. No digits. If the still could be mistaken for
orbit, italic _not a circle_ — no apo in the caption.

## INDEX and README

INDEX: title, one-line joke, date, optional hero thumb. Science
deltas live in a **column**, not inside the joke.

README: same number law as press. History table is the scoreboard
(sci deltas belong there). README prose may keep the drums. Checkout
box stays last.

## Deep dive

When the news is a maneuver a basic-KSP reader will not have
(gravity assist, Oberth, first real heat), a short `##` aside. Teach
the idea. Digits stay in the envelope table. No digit storm in the
aside. Firsts in the aside still follow the words-and-bold rule.

## Emphasis

- Italic `_name_` for parts and stacks after the gloss.
- Italic one stress clause if a still could lie (`_not_ a landing`).
- Bold only THE first this piece announces.
- `code` for filenames, named loads, F-ids.
- No underline. No ALL CAPS. Do not italic five things in a graf.

## Dates

Earth UTC from the review (`earth:`). Kerbal UT / MET in the table,
not “1235Z” in a sentence.

## Order when rewriting the corpus

1. `first-space.md` (gold template)
2. README + `INDEX.md`
3. The other six: `forest-for-the-trees.md`, `first-fifteen-sci.md`,
   `asteroid-xrl-564.md`, `first-five-sci.md`, `first-hop.md`,
   `pad-goo.md`

Do not clobber `screenshots/first-mystery-goo.png`. Do not invent
orbit. After press / README, `git add` those paths and `git commit`
a sentence. Do not commit gitignored tape.
