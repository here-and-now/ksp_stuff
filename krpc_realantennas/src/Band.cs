using System;
using KRPC.Service.Attributes;
using RABand = global::RealAntennas.Antenna.BandInfo;

namespace KRPC.RealAntennas
{
    /// <summary>One RealAntennas RF band from the live BandInfo table.</summary>
    [KRPCClass (Service = "RealAntennas")]
    public class Band
    {
        readonly RABand band;

        internal Band (RABand band)
        {
            this.band = Util.NotNull (band, "band");
        }

        /// <summary>Band name (L, S, X, K, …).</summary>
        [KRPCProperty]
        public string Name {
            get { return band.name ?? string.Empty; }
        }

        /// <summary>Minimum comms tech level that may use this band.</summary>
        [KRPCProperty]
        public int TechLevel {
            get { return band.TechLevel; }
        }

        /// <summary>Center frequency in Hz.</summary>
        [KRPCProperty]
        public float Frequency {
            get { return band.Frequency; }
        }

        /// <summary>Channel width in Hz.</summary>
        [KRPCProperty]
        public float ChannelWidth {
            get { return band.ChannelWidth; }
        }

        /// <summary>Max symbol rate for this band at a given tech level, in symbols/s.</summary>
        [KRPCMethod]
        public float MaxSymbolRate (int techLevel)
        {
            return band.MaxSymbolRate (techLevel);
        }

        public override bool Equals (object obj)
        {
            var other = obj as Band;
            return other != null && string.Equals (Name, other.Name, StringComparison.Ordinal);
        }

        public override int GetHashCode ()
        {
            return Name.GetHashCode ();
        }
    }
}
