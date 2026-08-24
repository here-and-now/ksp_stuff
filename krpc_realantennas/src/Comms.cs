using System.Collections.Generic;
using CommNet;
using KRPC.Service.Attributes;
using SCVessel = KRPC.SpaceCenter.Services.Vessel;

namespace KRPC.RealAntennas
{
    /// <summary>RealAntennas communications for a vessel.</summary>
    [KRPCClass (Service = "RealAntennas")]
    public class Comms
    {
        readonly Vessel vessel;
        readonly SCVessel scVessel;

        internal Comms (SCVessel scVessel)
        {
            this.scVessel = Util.NotNull (scVessel, "vessel");
            vessel = Util.NotNull (scVessel.InternalVessel, "internal vessel");
        }

        global::RealAntennas.RACommNetVessel RAVessel {
            get {
                if (vessel.Connection == null)
                    return null;
                return vessel.Connection as global::RealAntennas.RACommNetVessel;
            }
        }

        global::RealAntennas.RACommNode RANode {
            get {
                var cv = vessel.Connection;
                if (cv == null || cv.Comm == null)
                    return null;
                return cv.Comm as global::RealAntennas.RACommNode;
            }
        }

        [KRPCProperty]
        public SCVessel Vessel {
            get { return scVessel; }
        }

        [KRPCProperty]
        public bool Powered {
            get {
                var ra = RAVessel;
                return ra != null && ra.powered;
            }
        }

        [KRPCProperty]
        public bool CanComm {
            get {
                var node = RANode;
                if (node == null)
                    return false;
                try {
                    return node.CanComm ();
                } catch {
                    return false;
                }
            }
        }

        /// <summary>Best path data rate to a home station, bits/s. 0 if none.</summary>
        [KRPCProperty]
        public double RateToHome {
            get {
                var net = global::RealAntennas.RACommNetScenario.RACN;
                var node = RANode;
                if (net == null || node == null)
                    return 0.0;
                try {
                    return net.MaxDataRateToHome (node);
                } catch {
                    return 0.0;
                }
            }
        }

        /// <summary>Hops to home on the current network graph. Negative if unknown.</summary>
        [KRPCProperty]
        public int HopsToHome {
            get {
                var net = global::RealAntennas.RACommNetScenario.RACN;
                var node = RANode;
                if (net == null || node == null)
                    return -1;
                try {
                    return net.HopsToHome (node);
                } catch {
                    return -1;
                }
            }
        }

        [KRPCProperty]
        public double IdlePowerDraw {
            get {
                var ra = RAVessel;
                if (ra == null)
                    return 0.0;
                try {
                    return ra.IdlePowerDraw ();
                } catch {
                    return 0.0;
                }
            }
        }

        [KRPCProperty]
        public IList<Antenna> Antennas {
            get {
                var list = new List<Antenna> ();
                if (vessel.parts == null)
                    return list;
                foreach (var part in vessel.parts) {
                    if (part == null)
                        continue;
                    foreach (var m in part.FindModulesImplementing<global::RealAntennas.ModuleRealAntenna> ()) {
                        if (m != null)
                            list.Add (new Antenna (m));
                    }
                }
                return list;
            }
        }

        [KRPCProperty (Nullable = true)]
        public Antenna BestTransmitter {
            get {
                var ra = RAVessel;
                if (ra == null)
                    return null;
                try {
                    var tx = ra.GetBestTransmitter ();
                    var mod = tx as global::RealAntennas.ModuleRealAntenna;
                    if (mod != null)
                        return new Antenna (mod);
                    var raAnt = tx as global::RealAntennas.RealAntenna;
                    if (raAnt != null && raAnt.Parent != null)
                        return new Antenna (raAnt.Parent);
                    if (ra.antennaList != null) {
                        foreach (var a in ra.antennaList) {
                            if (a != null && a.Parent != null)
                                return new Antenna (a.Parent);
                        }
                    }
                } catch {
                }
                return null;
            }
        }

        /// <summary>Live RA control path (empty if none / stock links only).</summary>
        [KRPCProperty]
        public IList<Link> ControlPath {
            get {
                var list = new List<Link> ();
                var cv = vessel.Connection;
                if (cv == null)
                    return list;
                try {
                    var path = cv.ControlPath;
                    if (path == null)
                        return list;
                    foreach (var hop in path) {
                        var ra = hop as global::RealAntennas.RACommLink;
                        if (ra != null)
                            list.Add (new Link (ra));
                    }
                } catch {
                }
                return list;
            }
        }

        public override bool Equals (object obj)
        {
            var other = obj as Comms;
            return other != null && other.vessel != null && vessel != null && other.vessel.id == vessel.id;
        }

        public override int GetHashCode ()
        {
            return vessel != null ? vessel.id.GetHashCode () : 0;
        }
    }
}
