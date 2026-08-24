using System.Collections.Generic;
using KRPC.Service.Attributes;
using RAHome = global::RealAntennas.Network.RACommNetHome;

namespace KRPC.RealAntennas
{
    /// <summary>A RealAntennas ground station (Kopernicus City2 / RACommNetHome).</summary>
    [KRPCClass (Service = "RealAntennas")]
    public class GroundStation
    {
        readonly RAHome home;

        internal GroundStation (RAHome home)
        {
            this.home = Util.NotNull (home, "ground station");
        }

        [KRPCProperty]
        public string Name {
            get {
                try {
                    if (!string.IsNullOrEmpty (home.nodeName))
                        return home.nodeName;
                    return home.displaynodeName ?? string.Empty;
                } catch {
                    return string.Empty;
                }
            }
        }

        [KRPCProperty]
        public double Latitude {
            get {
                double lat, lon;
                Util.LatLon (home, out lat, out lon);
                return lat;
            }
        }

        [KRPCProperty]
        public double Longitude {
            get {
                double lat, lon;
                Util.LatLon (home, out lat, out lon);
                return lon;
            }
        }

        [KRPCProperty]
        public bool IsKsc {
            get { return home.isKSC; }
        }

        /// <summary>True if this station is in the live EnabledStations set.</summary>
        [KRPCProperty]
        public bool Enabled {
            get {
                var enabled = global::RealAntennas.RACommNetScenario.EnabledStations;
                if (enabled == null)
                    return false;
                foreach (var h in enabled) {
                    if (ReferenceEquals (h, home))
                        return true;
                }
                return false;
            }
        }

        /// <summary>Live RA antennas on this station (band, gain, tech level).</summary>
        [KRPCProperty]
        public IList<string> AntennaSummary {
            get {
                var list = new List<string> ();
                var node = home.Comm;
                if (node == null || node.RAAntennaList == null)
                    return list;
                foreach (var a in node.RAAntennaList) {
                    if (a == null)
                        continue;
                    var band = a.RFBand != null ? a.RFBand.name : "?";
                    var tl = a.TechLevelInfo != null ? a.TechLevelInfo.Level : -1;
                    list.Add (string.Format ("{0} band={1} gain={2:g} tl={3} tx={4:g}",
                        a.Name ?? "antenna", band, a.Gain, tl, a.TxPower));
                }
                return list;
            }
        }

        public override bool Equals (object obj)
        {
            var other = obj as GroundStation;
            return other != null && other.Name == Name;
        }

        public override int GetHashCode ()
        {
            return Name.GetHashCode ();
        }
    }
}
