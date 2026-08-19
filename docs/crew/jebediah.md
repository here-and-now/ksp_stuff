# Jebediah Kerman

duty: pilot
kerbal: Jebediah Kerman
voice: eager, first to volunteer, still reads the slate. Will not
argue an abort.

## Style

target_altitude: 250000
max_q: 40000
energy_cap: 1.25
suicide_start_alt: 28000
turn_start_altitude: 1200
turn_end_altitude: 70000

## Notes

Has already overburned apo on the way out (L-015). energy_cap 1.25 is
tighter than the library default 1.4. Suicide starts a bit higher than
25 km after the lithobrake (L-008).

## Log

- 2026-08-19 — Several Mun attempts: pad tip, hyperbolic climb, peri
  burn that sent apo to 1.58 Mm, then a later parking ~350 km. No
  landing yet.
- 2026-08-19T1725Z mun exit=1 abort=SESSION Could not launch 'kspstuff-mun-lander' from VAB onto LaunchPad: Object reference not set to an instance of an object
Server stack trace:
  at FlightState..ctor () [0x002a6] in <be370b73275e49439ea5e41ceef6700f>:0 
  at Game.Updated (GameScenes startSceneOverride) [0x0001a] in <be370b73275e49439ea5e41ceef6700f>:0 
  at GamePersistence.SaveGame (System.String saveFileName, System.String saveFolder, SaveMode saveMode, GameScenes startScene) [0x00045] in <be370b73275e49439ea5e41ceef6700f>:0 
  at FlightDriver.StartWithNewLaunch (System.String fullFilePath, System.String missionFlagURL, System.String launchSiteName, VesselCrewManifest manifest) [0x0002a] in <be370b73275e49439ea5e41ceef6700f>:0 
  at KRPC.SpaceCenter.Services.SpaceCenter.LaunchConfiguredVessel (KRPC.SpaceCenter.Services.SpaceCenter+LaunchConfig config) [0x0008d] in <f1773ffb70fa488dab4ae2b41d658d1d>:0 
  at KRPC.SpaceCenter.Services.SpaceCenter.WaitForVesselPreFlightChecks (KRPC.SpaceCenter.Services.SpaceCenter+LaunchConfig config) [0x00055] in <f1773ffb70fa488dab4ae2b41d658d1d>:0 
  at KRPC.SpaceCenter.Services.SpaceCenter+<>c__DisplayClass39_0.<LaunchVessel>b__0 () [0x00000] in <f1773ffb70fa488dab4ae2b41d658d1d>:0 
  at KRPC.Service.YieldException.CallUntyped () [0x00018] in <96c426f535db4c9daa669caa35f61868>:0 
  at KRPC.Service.ProcedureCallContinuation+<>c__DisplayClass5_0.<Run>b__0 () [0x00000] in <96c426f535db4c9daa669caa35f61868>:0 
  at KRPC.Service.Services.ExecuteCall (KRPC.Service.Scanner.ProcedureSignature procedure, System.Func`1[TResult] continuation) [0x00002] in <96c426f535db4c9daa669caa35f61868>:0  → docs/flights/2026-08-19T1725Z-mun.md
