using KRPC.Service.Attributes;

namespace KRPC.RealAntennas
{
    /// <summary>RealAntennas antenna geometry.</summary>
    [KRPCEnum (Service = "RealAntennas")]
    public enum Shape
    {
        Auto = 0,
        Omni = 1,
        Dish = 2
    }
}
