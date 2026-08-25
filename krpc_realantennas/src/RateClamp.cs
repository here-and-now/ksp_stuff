using System;
using HarmonyLib;
using UnityEngine;

namespace KRPC.RealAntennas
{
    /// <summary>
    /// Live RA path rate (Fwd/Rev) cannot exceed either antenna's
    /// TechLevelInfo.MaxDataRate. Burst RateBoundariesJob is not patched.
    /// </summary>
    static class RateClamp
    {
        internal static double Cap (global::RealAntennas.RACommLink link, double value, bool fwd)
        {
            if (link == null || value <= 0.0 || double.IsNaN (value))
                return value;
            double cap = double.PositiveInfinity;
            try {
                if (fwd) {
                    Consider (link.FwdAntennaTx, ref cap);
                    Consider (link.FwdAntennaRx, ref cap);
                } else {
                    Consider (link.RevAntennaTx, ref cap);
                    Consider (link.RevAntennaRx, ref cap);
                }
            } catch {
                return value;
            }
            if (double.IsPositiveInfinity (cap) || cap <= 0.0)
                return value;
            return value > cap ? cap : value;
        }

        internal static void Reclamp (global::RealAntennas.RACommLink link)
        {
            if (link == null)
                return;
            try {
                var fwd = Cap (link, link.FwdDataRate, true);
                if (fwd < link.FwdDataRate)
                    link.FwdDataRate = fwd;
                var rev = Cap (link, link.RevDataRate, false);
                if (rev < link.RevDataRate)
                    link.RevDataRate = rev;
            } catch {
            }
        }

        static void Consider (global::RealAntennas.RealAntenna ant, ref double cap)
        {
            if (ant == null || ant.TechLevelInfo == null)
                return;
            float max = ant.TechLevelInfo.MaxDataRate;
            if (max > 0f && max < cap)
                cap = max;
        }
    }

    [HarmonyPatch (typeof (global::RealAntennas.RACommLink), "set_FwdDataRate")]
    static class PatchFwdDataRate
    {
        static void Prefix (global::RealAntennas.RACommLink __instance, ref double value)
        {
            value = RateClamp.Cap (__instance, value, true);
        }
    }

    [HarmonyPatch (typeof (global::RealAntennas.RACommLink), "set_RevDataRate")]
    static class PatchRevDataRate
    {
        static void Prefix (global::RealAntennas.RACommLink __instance, ref double value)
        {
            value = RateClamp.Cap (__instance, value, false);
        }
    }

    [HarmonyPatch (typeof (global::RealAntennas.RACommLink), "set_FwdAntennaTx")]
    static class PatchFwdTx
    {
        static void Postfix (global::RealAntennas.RACommLink __instance)
        {
            RateClamp.Reclamp (__instance);
        }
    }

    [HarmonyPatch (typeof (global::RealAntennas.RACommLink), "set_FwdAntennaRx")]
    static class PatchFwdRx
    {
        static void Postfix (global::RealAntennas.RACommLink __instance)
        {
            RateClamp.Reclamp (__instance);
        }
    }

    [HarmonyPatch (typeof (global::RealAntennas.RACommLink), "set_RevAntennaTx")]
    static class PatchRevTx
    {
        static void Postfix (global::RealAntennas.RACommLink __instance)
        {
            RateClamp.Reclamp (__instance);
        }
    }

    [HarmonyPatch (typeof (global::RealAntennas.RACommLink), "set_RevAntennaRx")]
    static class PatchRevRx
    {
        static void Postfix (global::RealAntennas.RACommLink __instance)
        {
            RateClamp.Reclamp (__instance);
        }
    }

    [HarmonyPatch (typeof (global::RealAntennas.RACommNetwork), "MaxDataRateToHome")]
    static class PatchMaxDataRateToHome
    {
        static void Postfix (global::RealAntennas.RACommNode start, ref double __result)
        {
            if (start == null || __result <= 0.0)
                return;
            double cap = double.PositiveInfinity;
            try {
                if (start.RAAntennaList == null)
                    return;
                foreach (var a in start.RAAntennaList) {
                    if (a == null || a.TechLevelInfo == null)
                        continue;
                    float max = a.TechLevelInfo.MaxDataRate;
                    if (max > 0f && max < cap)
                        cap = max;
                }
            } catch {
                return;
            }
            if (!double.IsPositiveInfinity (cap) && __result > cap)
                __result = cap;
        }
    }

    [KSPAddon (KSPAddon.Startup.Instantly, true)]
    public class RateClampBootstrap : MonoBehaviour
    {
        static bool patched;

        void Awake ()
        {
            Apply ();
        }

        void Start ()
        {
            Apply ();
        }

        static void Apply ()
        {
            if (patched)
                return;
            patched = true;
            try {
                var harmony = new Harmony ("kspstuff.realantennas.rateclamp");
                harmony.PatchAll (typeof (RateClampBootstrap).Assembly);
                Debug.Log ("[kspstuff] RA rate clamp: Fwd/Rev capped to TechLevelInfo.MaxDataRate");
            } catch (Exception exc) {
                Debug.LogError ("[kspstuff] RA rate clamp Harmony failed: " + exc);
            }
        }
    }
}
