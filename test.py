from google.protobuf.internal.wire_format import IsTypePackable
from vessels import VesselManager

ves = VesselManager(name='OsCom_0.4_Test Relay')
ves = VesselManager()
ves.search_by_name(name='OsCom_0.4_Test', exact=True)


print(ves.df)


