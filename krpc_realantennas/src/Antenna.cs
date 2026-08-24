using System;
using System.Collections.Generic;
using KRPC.Service.Attributes;
using UnityEngine;
using SCPart = KRPC.SpaceCenter.Services.Parts.Part;
using SCVessel = KRPC.SpaceCenter.Services.Vessel;
using SCBody = KRPC.SpaceCenter.Services.CelestialBody;
using RATarget = global::RealAntennas.Targeting.AntennaTarget;
using RABand = global::RealAntennas.Antenna.BandInfo;

namespace KRPC.RealAntennas
{
    /// <summary>
    /// A RealAntennas ModuleRealAntenna on a part. Obtained via
    /// <see cref="M:KRPC.RealAntennas.Addon.Antenna"/> or <see cref="P:KRPC.RealAntennas.Comms.Antennas"/>.
    /// </summary>
    [KRPCClass (Service = "RealAntennas")]
    public class Antenna
    {
        readonly global::RealAntennas.ModuleRealAntenna module;

        internal Antenna (global::RealAntennas.ModuleRealAntenna module)
        {
            this.module = Util.NotNull (module, "antenna module");
        }

        internal global::RealAntennas.ModuleRealAntenna Module {
            get { return module; }
        }

        global::RealAntennas.RealAntenna RA {
            get { return Util.NotNull (module.RAAntenna, "RealAntenna backing object is null"); }
        }

        /// <summary>The part that owns this antenna.</summary>
        [KRPCProperty]
        public SCPart Part {
            get { return new SCPart (module.part); }
        }

        [KRPCProperty]
        public bool Enabled {
            get { return module._enabled; }
            set { module._enabled = value; }
        }

        /// <summary>Live comms tech level on this part (PAW "Tech Level").</summary>
        [KRPCProperty]
        public int TechLevel {
            get {
                if (module.RAAntenna != null && module.RAAntenna.TechLevelInfo != null)
                    return module.RAAntenna.TechLevelInfo.Level;
                try {
                    var f = module.Fields["TechLevel"];
                    if (f != null)
                        return Convert.ToInt32 (f.GetValue (module));
                } catch {
                }
                return 0;
            }
        }

        [KRPCProperty]
        public string RFBand {
            get { return module.RFBand ?? string.Empty; }
            set {
                var band = Util.BandOrNull (value);
                Util.Require (band != null, "Unknown RF band: " + value);
                module.RFBand = band.name;
                if (module.RAAntenna != null)
                    module.RAAntenna.RFBand = band;
            }
        }

        [KRPCProperty]
        public float Gain {
            get { return module.Gain; }
        }

        /// <summary>Transmit power, dBm.</summary>
        [KRPCProperty]
        public float TxPower {
            get { return module.TxPower; }
            set {
                float max = 0f;
                if (module.RAAntenna != null && module.RAAntenna.TechLevelInfo != null)
                    max = module.RAAntenna.TechLevelInfo.MaxPower;
                if (max > 0f && value > max)
                    value = max;
                if (value < 0f)
                    value = 0f;
                module.TxPower = value;
                if (module.RAAntenna != null)
                    module.RAAntenna.TxPower = value;
            }
        }

        [KRPCProperty]
        public float AntennaDiameter {
            get { return module.antennaDiameter; }
        }

        [KRPCProperty]
        public float ReferenceGain {
            get { return module.referenceGain; }
        }

        [KRPCProperty]
        public float AMWTemp {
            get { return module.AMWTemp; }
        }

        [KRPCProperty]
        public bool Deployable {
            get { return module.Deployable; }
        }

        [KRPCProperty]
        public bool Deployed {
            get { return module.Deployed; }
        }

        [KRPCProperty]
        public bool CanTarget {
            get { return module.RAAntenna != null && module.RAAntenna.CanTarget; }
        }

        [KRPCProperty]
        public bool IsTracking {
            get { return module.RAAntenna != null && module.RAAntenna.IsTracking; }
        }

        [KRPCProperty]
        public Shape Shape {
            get {
                if (module.RAAntenna == null)
                    return Shape.Auto;
                return Util.ShapeOf (module.RAAntenna.Shape);
            }
        }

        /// <summary>Current modulator data rate, bits/s (not the path-to-home rate).</summary>
        [KRPCProperty]
        public double DataRate {
            get { return module.RAAntenna != null ? module.RAAntenna.DataRate : 0.0; }
        }

        /// <summary>Max data rate from this antenna's TechLevelInfo, bits/s.</summary>
        [KRPCProperty]
        public float MaxDataRate {
            get {
                var tl = module.RAAntenna != null ? module.RAAntenna.TechLevelInfo : null;
                return tl != null ? tl.MaxDataRate : 0f;
            }
        }

        [KRPCProperty]
        public float Frequency {
            get { return module.RAAntenna != null ? module.RAAntenna.Frequency : 0f; }
        }

        [KRPCProperty]
        public float Beamwidth {
            get { return module.RAAntenna != null ? module.RAAntenna.Beamwidth : 0f; }
        }

        [KRPCProperty]
        public double Bandwidth {
            get { return module.RAAntenna != null ? module.RAAntenna.Bandwidth : 0.0; }
        }

        [KRPCProperty]
        public double SymbolRate {
            get { return module.RAAntenna != null ? module.RAAntenna.SymbolRate : 0.0; }
        }

        /// <summary>Transmit draw, EC/s (RA PowerDraw).</summary>
        [KRPCProperty]
        public float PowerDraw {
            get { return module.PowerDraw; }
        }

        [KRPCProperty]
        public float IdlePowerDraw {
            get { return module.RAAntenna != null ? module.RAAntenna.IdlePowerDraw : 0f; }
        }

        [KRPCProperty]
        public float MinimumDistance {
            get { return module.RAAntenna != null ? module.RAAntenna.MinimumDistance : 0f; }
        }

        [KRPCProperty]
        public bool CanComm {
            get {
                try {
                    return module.CanComm ();
                } catch {
                    return false;
                }
            }
        }

        [KRPCProperty]
        public bool CanTransmit {
            get {
                try {
                    return module.CanTransmit ();
                } catch {
                    return false;
                }
            }
        }

        [KRPCProperty]
        public TargetMode TargetMode {
            get { return Util.ModeOf (module.Target); }
        }

        /// <summary>RA target ToString, empty if none.</summary>
        [KRPCProperty]
        public string TargetName {
            get {
                var t = module.Target;
                return t != null ? t.ToString () : string.Empty;
            }
        }

        [KRPCProperty (Nullable = true)]
        public SCVessel TargetVessel {
            get {
                var tv = module.Target as global::RealAntennas.Targeting.AntennaTargetVessel;
                if (tv == null || tv.vessel == null)
                    return null;
                return new SCVessel (tv.vessel);
            }
        }

        [KRPCProperty (Nullable = true)]
        public SCBody TargetBody {
            get {
                var lla = module.Target as global::RealAntennas.Targeting.AntennaTargetLatLonAlt;
                if (lla == null || lla.body == null)
                    return null;
                return new SCBody (lla.body);
            }
        }

        /// <summary>Lat, lon, alt of a BodyLatLonAlt / BodyCenter target. Empty otherwise.</summary>
        [KRPCProperty]
        public IList<double> TargetLatLonAlt {
            get {
                var lla = module.Target as global::RealAntennas.Targeting.AntennaTargetLatLonAlt;
                if (lla == null)
                    return new List<double> ();
                var v = lla.latLonAlt;
                return new List<double> { v.x, v.y, v.z };
            }
        }

        [KRPCProperty]
        public IList<double> TargetAzEl {
            get {
                var az = module.Target as global::RealAntennas.Targeting.AntennaTargetAzEl;
                if (az == null)
                    return new List<double> ();
                return new List<double> { az.azimuth, az.elevation };
            }
        }

        void RequireTargetable ()
        {
            Util.Require (CanTarget, "Antenna cannot target (omni / no dish)");
        }

        /// <summary>Point at a vessel. Fails on omni.</summary>
        [KRPCMethod]
        public void SetTargetVessel (SCVessel vessel)
        {
            RequireTargetable ();
            Util.NotNull (vessel, "vessel");
            var kv = vessel.InternalVessel;
            Util.NotNull (kv, "internal vessel");
            var node = Util.TargetNode (global::RealAntennas.Targeting.AntennaTarget.TargetMode.Vessel.ToString ());
            node.AddValue ("vesselId", kv.id.ToString ());
            Util.LoadTarget (RA, node);
        }

        /// <summary>Point at a body's center (implemented as lat/lon/alt 0,0,0).</summary>
        [KRPCMethod]
        public void SetTargetBody (SCBody body)
        {
            RequireTargetable ();
            Util.NotNull (body, "body");
            var kb = body.InternalBody;
            Util.NotNull (kb, "internal body");
            var node = Util.TargetNode (global::RealAntennas.Targeting.AntennaTarget.TargetMode.BodyLatLonAlt.ToString ());
            node.AddValue ("bodyName", Util.BodyName (kb));
            node.AddValue ("latLonAlt", new Vector3 (0f, 0f, 0f));
            Util.LoadTarget (RA, node);
        }

        /// <summary>Point at a lat/lon/alt on a body. Altitude in meters.</summary>
        [KRPCMethod]
        public void SetTargetLatLonAlt (SCBody body, double latitude, double longitude, double altitude)
        {
            RequireTargetable ();
            Util.NotNull (body, "body");
            var kb = body.InternalBody;
            Util.NotNull (kb, "internal body");
            var node = Util.TargetNode (global::RealAntennas.Targeting.AntennaTarget.TargetMode.BodyLatLonAlt.ToString ());
            node.AddValue ("bodyName", Util.BodyName (kb));
            node.AddValue ("latLonAlt", new Vector3 ((float)latitude, (float)longitude, (float)altitude));
            Util.LoadTarget (RA, node);
        }

        /// <summary>Point at a named ground station by aiming at its lat/lon.</summary>
        [KRPCMethod]
        public void SetTargetGroundStation (string name)
        {
            RequireTargetable ();
            Util.Require (!string.IsNullOrEmpty (name), "ground station name");
            var stations = global::RealAntennas.RACommNetScenario.GroundStations;
            Util.Require (stations != null, "Ground station table is not live");
            global::RealAntennas.Network.RACommNetHome home = null;
            foreach (var kv in stations) {
                if (string.Equals (kv.Key, name, StringComparison.OrdinalIgnoreCase) ||
                    (kv.Value != null && (
                        string.Equals (kv.Value.nodeName, name, StringComparison.OrdinalIgnoreCase) ||
                        string.Equals (kv.Value.displaynodeName, name, StringComparison.OrdinalIgnoreCase)))) {
                    home = kv.Value;
                    break;
                }
            }
            Util.Require (home != null, "Unknown ground station: " + name);
            var body = home.Comm != null ? home.Comm.ParentBody : null;
            if (body == null && Planetarium.fetch != null)
                body = Planetarium.fetch.Home;
            Util.NotNull (body, "ground station body");
            var node = Util.TargetNode (global::RealAntennas.Targeting.AntennaTarget.TargetMode.BodyLatLonAlt.ToString ());
            node.AddValue ("bodyName", Util.BodyName (body));
            double lat, lon;
            Util.LatLon (home, out lat, out lon);
            node.AddValue ("latLonAlt", new Vector3 ((float)lat, (float)lon, 0f));
            Util.LoadTarget (RA, node);
        }

        /// <summary>Azimuth/elevation relative to a vessel.</summary>
        [KRPCMethod]
        public void SetTargetAzEl (SCVessel vessel, float azimuth, float elevation)
        {
            RequireTargetable ();
            Util.NotNull (vessel, "vessel");
            var kv = vessel.InternalVessel;
            Util.NotNull (kv, "internal vessel");
            var node = Util.TargetNode (global::RealAntennas.Targeting.AntennaTarget.TargetMode.AzEl.ToString ());
            node.AddValue ("vesselId", kv.id.ToString ());
            node.AddValue ("azimuth", azimuth.ToString (System.Globalization.CultureInfo.InvariantCulture));
            node.AddValue ("elevation", elevation.ToString (System.Globalization.CultureInfo.InvariantCulture));
            Util.LoadTarget (RA, node);
        }

        /// <summary>Orbit-relative pointing on a vessel (forward, elevation).</summary>
        [KRPCMethod]
        public void SetTargetOrbitRelative (SCVessel vessel, float forward, float elevation)
        {
            RequireTargetable ();
            Util.NotNull (vessel, "vessel");
            var kv = vessel.InternalVessel;
            Util.NotNull (kv, "internal vessel");
            var node = Util.TargetNode (global::RealAntennas.Targeting.AntennaTarget.TargetMode.OrbitRelative.ToString ());
            node.AddValue ("vesselId", kv.id.ToString ());
            node.AddValue ("forward", forward.ToString (System.Globalization.CultureInfo.InvariantCulture));
            node.AddValue ("elevation", elevation.ToString (System.Globalization.CultureInfo.InvariantCulture));
            Util.LoadTarget (RA, node);
        }

        /// <summary>RA default target (home body center).</summary>
        [KRPCMethod]
        public void SetDefaultTarget ()
        {
            RequireTargetable ();
            RA.SetDefaultTarget ();
        }

        public override bool Equals (object obj)
        {
            var other = obj as Antenna;
            return other != null && other.module.part != null && module.part != null
                && other.module.part.flightID == module.part.flightID;
        }

        public override int GetHashCode ()
        {
            return module.part != null ? (int)module.part.flightID : 0;
        }
    }
}
