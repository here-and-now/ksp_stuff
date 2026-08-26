using System;
using System.Collections.Generic;
using HarmonyLib;
using UnityEngine;

namespace Kspstuff.Kerbalism
{
    /// <summary>
    /// VesselData ctor Dictionary.Add(part.flightID) throws on duplicate
    /// keys (OnSave / Close persist). Skip the second Add. Not a vessel-name
    /// dict. Never leftover-ksc. Never load persistent. Never revert.
    /// </summary>
    static class SkipDupFlightId
    {
        internal static bool Offer (Dictionary<uint, global::KERBALISM.PartData> parts, uint flightId)
        {
            if (parts == null)
                return true;
            if (!parts.ContainsKey (flightId))
                return true;
            Debug.LogWarning ("[kspstuff] Kerbalism skip-dup flightID " + flightId);
            return false;
        }
    }

    [HarmonyPatch (typeof (Dictionary<uint, global::KERBALISM.PartData>), "Add")]
    static class PatchPartDataAdd
    {
        static bool Prefix (Dictionary<uint, global::KERBALISM.PartData> __instance, uint key)
        {
            return SkipDupFlightId.Offer (__instance, key);
        }
    }

    [KSPAddon (KSPAddon.Startup.Instantly, true)]
    public class SkipDupBootstrap : MonoBehaviour
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
                var harmony = new Harmony ("kspstuff.kerbalism.skipdup");
                harmony.PatchAll (typeof (SkipDupBootstrap).Assembly);
                Debug.Log ("[kspstuff] Kerbalism skip-dup flightID: VesselData.parts Add is fail-open");
            } catch (Exception exc) {
                Debug.LogError ("[kspstuff] Kerbalism skip-dup Harmony failed: " + exc);
            }
        }
    }
}
