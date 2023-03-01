from google.protobuf.internal.wire_format import IsTypePackable
from vessels import VesselManager

ves = VesselManager(name='OsCom_0.4_Test Relay')
ves = VesselManager()
ves.fuzzy_search_by_name(name='OsCom')


print(ves.df)


