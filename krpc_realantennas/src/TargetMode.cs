using KRPC.Service.Attributes;

namespace KRPC.RealAntennas
{
    /// <summary>RealAntennas dish pointing mode. Omni antennas cannot target.</summary>
    [KRPCEnum (Service = "RealAntennas")]
    public enum TargetMode
    {
        None = 0,
        Vessel = 1,
        BodyCenter = 2,
        BodyLatLonAlt = 3,
        AzEl = 4,
        OrbitRelative = 5
    }
}
