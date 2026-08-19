# Gene ↔ pilot notes. One line each. Not the stick.
# script: acked … is written by mun when it takes an uplink.
Gene: abort hyperbolic Pe
script: acked abort hyperbolic Pe
Gene: set mun_pe 20000
script: acked set mun_pe 20000
Gene: hold
script: acked hold
Gene: resume
script: acked resume
Gene: abort ESC lithobrake leftover wreck peri=-109172 parts=-1
Gene: ESC leftover Mun wreck parts=-1 peri=-109 km — abort, hangar must leave wreck
Gene: ESC leftover Mun wreck parts=-1 peri=-109 km — abort, hangar must leave wreck
script: acked abort ESC lithobrake leftover wreck peri=-109172 parts=-1
Gene: resume
Gene: pad fresh LF=3600 stg=3 — holding radio, no leftover abort
Gene: 4761 from-orbit live; L-030 no high-flyby abort; radio quiet unless ESC/hyperbolic/stuck 1x
Grok: copy, from-orbit, rails to apo
Gene: 4761 from-orbit L-031: rails to apo if no Mun patch; radio quiet unless ESC/hyperbolic/subsurface Pe
Gene: capture
Gene: Mun SOI Pe=22km hyperbolic — capture now, do not 1000x into Pe
Gene: Grok 4761 Mun SOI Pe 22 km. Capture now. No rails into peri.
script: acked capture
Gene: abort FLAME captured Mun 22x1161 engine dry
script: acked abort FLAME captured Mun 22x1161 engine dry
Gene: FLAME on capture circularize; Pe 22 km apo 1161 — abort hung node, keep the orbit
Grok: copy, Mun orbit, relight, land
Gene: 4761 live Mun 22x1161. FLAME is relight, do not abort. Land. Radio quiet unless ESC/subsurface/WRECK.
Gene: L-034 live: 4761 ~3 km Mun, Pe buried, 60 kN LF~200. Throttle 1 until touchdown. Do not abort. Do not Hangar.
Gene: 1958Z suicide timeout 5.7 km LF=202. Falling. --from-orbit now, throttle 1 to touchdown. Do not abort ESC.
