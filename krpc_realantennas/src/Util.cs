using System;
using System.Globalization;
using UnityEngine;
using RABand = global::RealAntennas.Antenna.BandInfo;
using RATarget = global::RealAntennas.Targeting.AntennaTarget;

namespace KRPC.RealAntennas
{
    static class Util
    {
        internal static void Require (bool ok, string message)
        {
            if (!ok)
                throw new InvalidOperationException (message);
        }

        /// <summary>
        /// Flight / KSC / Tracking only. Main menu + loading + PSystemSpawn
        /// is when Kopernicus unloads Kerbin; do not touch RACommNetHome there.
        /// </summary>
        internal static bool PlayableScene ()
        {
            try {
                if (HighLogic.LoadedSceneIsFlight)
                    return true;
                var s = HighLogic.LoadedScene;
                return s == GameScenes.SPACECENTER || s == GameScenes.TRACKSTATION;
            } catch {
                return false;
            }
        }

        internal static bool NetworkReady ()
        {
            if (!PlayableScene ())
                return false;
            try {
                return global::RealAntennas.RACommNetScenario.RACN != null;
            } catch {
                return false;
            }
        }

        internal static T NotNull<T> (T obj, string message) where T : class
        {
            if (obj == null)
                throw new InvalidOperationException (message);
            return obj;
        }

        internal static Shape ShapeOf (global::RealAntennas.AntennaShape s)
        {
            switch (s) {
            case global::RealAntennas.AntennaShape.Omni:
                return Shape.Omni;
            case global::RealAntennas.AntennaShape.Dish:
                return Shape.Dish;
            default:
                return Shape.Auto;
            }
        }

        internal static TargetMode ModeOf (RATarget target)
        {
            if (target == null)
                return TargetMode.None;
            if (target is global::RealAntennas.Targeting.AntennaTargetVessel)
                return TargetMode.Vessel;
            if (target is global::RealAntennas.Targeting.AntennaTargetAzEl)
                return TargetMode.AzEl;
            if (target is global::RealAntennas.Targeting.AntennaTargetOrbitRelative)
                return TargetMode.OrbitRelative;
            if (target is global::RealAntennas.Targeting.AntennaTargetLatLonAlt) {
                var lla = (global::RealAntennas.Targeting.AntennaTargetLatLonAlt)target;
                var v = lla.latLonAlt;
                if (Math.Abs (v.x) < 1e-4 && Math.Abs (v.y) < 1e-4 && Math.Abs (v.z) < 1e-4)
                    return TargetMode.BodyCenter;
                return TargetMode.BodyLatLonAlt;
            }
            return TargetMode.None;
        }

        internal static RATarget LoadTarget (global::RealAntennas.RealAntenna ra, ConfigNode node)
        {
            var t = RATarget.LoadFromConfig (node, ra);
            Require (t != null, "RealAntennas rejected the target node");
            ra.Target = t;
            return t;
        }

        internal static ConfigNode TargetNode (string modeName)
        {
            var node = new ConfigNode ("TARGET");
            node.AddValue ("name", modeName);
            return node;
        }

        internal static string BodyName (CelestialBody body)
        {
            if (body == null)
                return string.Empty;
            try {
                return body.name;
            } catch {
                return body.bodyName ?? string.Empty;
            }
        }

        internal static void LatLon (global::RealAntennas.Network.RACommNetHome home, out double lat, out double lon)
        {
            lat = 0.0;
            lon = 0.0;
            if (home == null || !PlayableScene ())
                return;
            global::CelestialBody body = null;
            try {
                if (home.Comm != null)
                    body = home.Comm.ParentBody;
            } catch {
            }
            if (body == null && Planetarium.fetch != null)
                body = Planetarium.fetch.Home;
            if (body == null)
                return;
            try {
                var pos = (Vector3d)home.transform.position;
                lat = body.GetLatitude (pos);
                lon = body.GetLongitude (pos);
            } catch {
            }
        }

        internal static RABand BandOrNull (string name)
        {
            if (string.IsNullOrEmpty (name) || !RABand.initialized || RABand.All == null)
                return null;
            RABand band;
            if (RABand.All.TryGetValue (name, out band))
                return band;
            return RABand.Get (name);
        }
    }
}
