# jebediah science card

science: card
flight: jebediah
craft: kspstuff-hop-flea
at: hop
body: Kerbin
need_builder: no
notes: VAB signed. Mk1 + chute + 2×Goo + Flea. No thermometer.
  Recover the pod. Do not transmit. Not Mun.

## Experiments

- experiment: crewReport
  part: mk1pod_v2
  biome: LaunchPad
  situation: landed
  at: hop
  when: pad, before ignition

- experiment: mysteryGoo
  part: GooExperiment
  biome: LaunchPad
  situation: landed
  at: hop
  when: can 1, pad, before ignition

- experiment: evaReport
  part: kerbal
  biome: LaunchPad
  situation: landed
  at: hop
  when: only if safe — hatch on the pad before light, or after chute
    and a stop. No flying EVA.

- experiment: crewReport
  part: mk1pod_v2
  biome: LaunchPad
  situation: flying
  at: hop
  when: FlyingLow after liftoff. If they leave KSC, Shores is the
    neighbor — take that instead, still new.

- experiment: mysteryGoo
  part: GooExperiment
  biome: Kerbin
  situation: flying
  at: hop
  when: can 2, FlyingLow (not biome-split). Recover — do not transmit.

## Gene

Pad sounding only. Recover the pod. `blocks.md` has no hop yet —
that is Gene → stack, not this card.
