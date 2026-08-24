using KRPC.Service.Attributes;

namespace KRPC.RealAntennas
{
    /// <summary>One hop in a RealAntennas control path (RACommLink).</summary>
    [KRPCClass (Service = "RealAntennas")]
    public class Link
    {
        readonly global::RealAntennas.RACommLink link;

        internal Link (global::RealAntennas.RACommLink link)
        {
            this.link = Util.NotNull (link, "link");
        }

        [KRPCProperty]
        public string StartName {
            get { return NodeName (link.start as global::RealAntennas.RACommNode, link.start); }
        }

        [KRPCProperty]
        public string EndName {
            get { return NodeName (link.end as global::RealAntennas.RACommNode, link.end); }
        }

        [KRPCProperty]
        public bool StartIsHome {
            get { return link.start != null && link.start.isHome; }
        }

        [KRPCProperty]
        public bool EndIsHome {
            get { return link.end != null && link.end.isHome; }
        }

        /// <summary>Forward data rate, bits/s.</summary>
        [KRPCProperty]
        public double FwdDataRate {
            get { return link.FwdDataRate; }
        }

        /// <summary>Reverse data rate, bits/s.</summary>
        [KRPCProperty]
        public double RevDataRate {
            get { return link.RevDataRate; }
        }

        /// <summary>Forward link metric (RA internal, typically SNR-like).</summary>
        [KRPCProperty]
        public double FwdMetric {
            get { return link.FwdMetric; }
        }

        [KRPCProperty]
        public double RevMetric {
            get { return link.RevMetric; }
        }

        [KRPCProperty]
        public double FwdCost {
            get { return link.FwdCost; }
        }

        [KRPCProperty]
        public double RevCost {
            get { return link.RevCost; }
        }

        [KRPCProperty]
        public string FwdTxAntenna {
            get { return AntennaName (link.FwdAntennaTx); }
        }

        [KRPCProperty]
        public string FwdRxAntenna {
            get { return AntennaName (link.FwdAntennaRx); }
        }

        static string AntennaName (global::RealAntennas.RealAntenna a)
        {
            if (a == null)
                return string.Empty;
            return a.Name ?? string.Empty;
        }

        static string NodeName (global::RealAntennas.RACommNode ra, CommNet.CommNode stock)
        {
            if (ra != null) {
                if (ra.ParentVessel != null)
                    return ra.ParentVessel.GetDisplayName () ?? ra.ParentVessel.vesselName ?? string.Empty;
                if (ra.ParentBody != null)
                    return ra.ParentBody.name ?? string.Empty;
                if (ra.isGroundStation && stock != null)
                    return stock.displayName ?? stock.name ?? string.Empty;
            }
            if (stock == null)
                return string.Empty;
            try {
                return stock.displayName ?? stock.name ?? string.Empty;
            } catch {
                return stock.name ?? string.Empty;
            }
        }
    }
}
