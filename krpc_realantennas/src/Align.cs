using System;
using System.Reflection;
using CommNet;
using RATL = global::RealAntennas.TechLevelInfo;

namespace KRPC.RealAntennas
{
    static class Align
    {
        internal static int ClampLevel (int level)
        {
            if (level < 0)
                return 0;
            int max = 9;
            try {
                max = RATL.MaxTL;
            } catch {
            }
            if (level > max)
                return max;
            return level;
        }

        internal static int GetGroundStationTechLevel ()
        {
            try {
                return global::RealAntennas.RACommNetScenario.GroundStationTechLevel;
            } catch {
                return 0;
            }
        }

        internal static void SetGroundStationTechLevel (int level)
        {
            level = ClampLevel (level);
            global::RealAntennas.RACommNetScenario.GroundStationTechLevel = level;
            try {
                var scn = CommNetScenario.Instance as global::RealAntennas.RACommNetScenario;
                if (scn != null)
                    scn.UpdateTLHomes ();
            } catch {
            }
        }

        internal static int GetDifficultyMaxTechLevel ()
        {
            try {
                var node = RaParameters ();
                if (node == null)
                    return 0;
                var f = node.GetType ().GetField ("MaxTechLevel", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
                if (f == null)
                    return 0;
                return Convert.ToInt32 (f.GetValue (node));
            } catch {
                return 0;
            }
        }

        internal static void SetDifficultyMaxTechLevel (int level)
        {
            level = ClampLevel (level);
            var node = RaParameters ();
            if (node == null)
                return;
            var f = node.GetType ().GetField ("MaxTechLevel", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
            if (f == null)
                return;
            f.SetValue (node, level);
        }

        internal static void ClampLoadedVessels (int level)
        {
            level = ClampLevel (level);
            RATL info = null;
            try {
                info = RATL.GetTechLevel (level);
            } catch {
                return;
            }
            if (info == null)
                return;
            Vessel[] vessels = null;
            try {
                if (FlightGlobals.Vessels != null) {
                    vessels = FlightGlobals.Vessels.ToArray ();
                }
            } catch {
                return;
            }
            if (vessels == null)
                return;
            foreach (var v in vessels) {
                if (v == null)
                    continue;
                try {
                    var mods = v.FindPartModulesImplementing<global::RealAntennas.ModuleRealAntenna> ();
                    if (mods == null)
                        continue;
                    foreach (var m in mods) {
                        if (m == null || m.RAAntenna == null)
                            continue;
                        var cur = m.RAAntenna.TechLevelInfo;
                        if (cur != null && cur.Level <= level)
                            continue;
                        m.RAAntenna.TechLevelInfo = info;
                    }
                } catch {
                }
            }
        }

        internal static void Apply (int level)
        {
            level = ClampLevel (level);
            SetDifficultyMaxTechLevel (level);
            SetGroundStationTechLevel (level);
            ClampLoadedVessels (level);
        }

        static object RaParameters ()
        {
            try {
                if (HighLogic.CurrentGame == null || HighLogic.CurrentGame.Parameters == null)
                    return null;
                var asm = typeof (global::RealAntennas.ModuleRealAntenna).Assembly;
                var t = asm.GetType ("RealAntennas.RAParameters", false);
                if (t == null)
                    return null;
                var p = HighLogic.CurrentGame.Parameters;
                foreach (var m in p.GetType ().GetMethods (BindingFlags.Instance | BindingFlags.Public)) {
                    if (m.Name != "CustomParams" || !m.IsGenericMethodDefinition)
                        continue;
                    var gm = m.MakeGenericMethod (t);
                    return gm.Invoke (p, null);
                }
            } catch {
            }
            return null;
        }
    }
}
