using System;
using System.Collections.Generic;
using KRPC.Service;
using KRPC.Service.Attributes;
using SCPart = KRPC.SpaceCenter.Services.Parts.Part;
using SCVessel = KRPC.SpaceCenter.Services.Vessel;
using RABand = global::RealAntennas.Antenna.BandInfo;
using RATL = global::RealAntennas.TechLevelInfo;

namespace KRPC.RealAntennas
{
    /// <summary>
    /// Live RealAntennas data. Catalog (bands, tech levels, ground stations) plus
    /// per-vessel comms and per-part antennas, including dish targeting.
    /// Does not wrap Kerbalism science dumps.
    /// </summary>
    [KRPCService (Name = "RealAntennas", GameScene = GameScene.Flight | GameScene.TrackingStation | GameScene.SpaceCenter)]
    public static class Addon
    {
        static bool Probe ()
        {
            try {
                return typeof (global::RealAntennas.ModuleRealAntenna) != null;
            } catch {
                return false;
            }
        }

        static void Check ()
        {
            if (!Probe ())
                throw new InvalidOperationException ("RealAntennas is not available");
            if (!Util.PlayableScene ())
                throw new InvalidOperationException ("RealAntennas kRPC is not available in this scene");
        }

        /// <summary>Assembly loaded. Does not touch Kopernicus / RACommNetHome.</summary>
        [KRPCProperty]
        public static bool Available {
            get { return Probe () && Util.PlayableScene (); }
        }

        /// <summary>RA minRelayTL (relays below this tech level are not used).</summary>
        [KRPCProperty]
        public static int MinRelayTechLevel {
            get {
                if (!Util.NetworkReady ())
                    return 0;
                try {
                    return global::RealAntennas.RACommNetScenario.minRelayTL;
                } catch {
                    return 0;
                }
            }
        }

        /// <summary>RACommNetScenario.MaxTL (table ceiling, not the live cap).</summary>
        [KRPCProperty]
        public static int MaxTechLevel {
            get {
                if (!Util.NetworkReady ())
                    return 0;
                try {
                    return global::RealAntennas.RACommNetScenario.MaxTL;
                } catch {
                    try {
                        return RATL.MaxTL;
                    } catch {
                        return 0;
                    }
                }
            }
        }

        /// <summary>
        /// Live ground-station tech level (GSTL). Sandbox defaults this to MaxTL.
        /// Antennas with cfg TechLevel &gt; GSTL do not spawn.
        /// </summary>
        [KRPCProperty]
        public static int GroundStationTechLevel {
            get { return Align.GetGroundStationTechLevel (); }
            set {
                Check ();
                Align.SetGroundStationTechLevel (value);
            }
        }

        /// <summary>
        /// Difficulty RAParameters.MaxTechLevel (craft PAW cap). Sandbox
        /// ignores CTT commsTL upgrades; this is the craft knob.
        /// </summary>
        [KRPCProperty]
        public static int DifficultyMaxTechLevel {
            get { return Align.GetDifficultyMaxTechLevel (); }
            set {
                Check ();
                Align.SetDifficultyMaxTechLevel (value);
            }
        }

        /// <summary>
        /// Set difficulty cap + GSTL to <paramref name="level"/>, rebuild
        /// ground antennas, clamp loaded vessels down. House stamps owned comms TL.
        /// </summary>
        [KRPCProcedure]
        public static void AlignTechLevel (int level)
        {
            Check ();
            Align.Apply (level);
        }

        [KRPCProcedure]
        public static Comms Comms (SCVessel vessel)
        {
            Check ();
            Util.Require (Util.NetworkReady (), "RealAntennas network is not live yet");
            return new Comms (vessel);
        }

        [KRPCProcedure]
        public static Antenna Antenna (SCPart part)
        {
            Check ();
            Util.NotNull (part, "part");
            var p = Util.NotNull (part.InternalPart, "internal part");
            var m = p.FindModuleImplementing<global::RealAntennas.ModuleRealAntenna> ();
            Util.Require (m != null, "Part has no ModuleRealAntenna");
            return new Antenna (m);
        }

        /// <summary>Live RA ground stations. Empty until the network exists.</summary>
        [KRPCProperty]
        public static IList<GroundStation> GroundStations {
            get {
                var list = new List<GroundStation> ();
                if (!Util.NetworkReady ())
                    return list;
                try {
                    var table = global::RealAntennas.RACommNetScenario.GroundStations;
                    if (table == null)
                        return list;
                    foreach (var kv in table) {
                        if (kv.Value != null)
                            list.Add (new GroundStation (kv.Value));
                    }
                } catch {
                }
                return list;
            }
        }

        [KRPCProperty]
        public static IList<Band> Bands {
            get {
                var list = new List<Band> ();
                if (!Util.PlayableScene ())
                    return list;
                try {
                    if (!RABand.initialized || RABand.All == null)
                        return list;
                    foreach (var kv in RABand.All) {
                        if (kv.Value != null)
                            list.Add (new Band (kv.Value));
                    }
                } catch {
                }
                return list;
            }
        }

        [KRPCProperty]
        public static IList<TechLevel> TechLevels {
            get {
                var list = new List<TechLevel> ();
                if (!Util.PlayableScene ())
                    return list;
                try {
                    if (!RATL.initialized || RATL.All == null)
                        return list;
                    foreach (var kv in RATL.All) {
                        if (kv.Value != null)
                            list.Add (new TechLevel (kv.Value));
                    }
                } catch {
                }
                return list;
            }
        }
    }
}
