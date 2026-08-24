using KRPC.Service.Attributes;
using RATL = global::RealAntennas.TechLevelInfo;

namespace KRPC.RealAntennas
{
    /// <summary>One RealAntennas comms tech level from the live TechLevelInfo table.</summary>
    [KRPCClass (Service = "RealAntennas")]
    public class TechLevel
    {
        readonly RATL info;

        internal TechLevel (RATL info)
        {
            this.info = Util.NotNull (info, "tech level");
        }

        [KRPCProperty]
        public int Level {
            get { return info.Level; }
        }

        [KRPCProperty]
        public string Name {
            get { return info.name ?? string.Empty; }
        }

        [KRPCProperty]
        public string Description {
            get { return info.Description ?? string.Empty; }
        }

        /// <summary>Minimum data rate at this level, bits/s.</summary>
        [KRPCProperty]
        public float MinDataRate {
            get { return info.MinDataRate; }
        }

        /// <summary>Maximum data rate at this level, bits/s.</summary>
        [KRPCProperty]
        public float MaxDataRate {
            get { return info.MaxDataRate; }
        }

        /// <summary>Maximum transmit power, dBm.</summary>
        [KRPCProperty]
        public float MaxPower {
            get { return info.MaxPower; }
        }

        [KRPCProperty]
        public float PowerEfficiency {
            get { return info.PowerEfficiency; }
        }

        [KRPCProperty]
        public float ReceiverNoiseTemperature {
            get { return info.ReceiverNoiseTemperature; }
        }

        public override bool Equals (object obj)
        {
            var other = obj as TechLevel;
            return other != null && other.Level == Level;
        }

        public override int GetHashCode ()
        {
            return Level;
        }
    }
}
