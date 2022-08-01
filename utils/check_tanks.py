import math
import time
import krpc

turn_start_altitude = 250
turn_end_altitude = 45000
target_altitude = 150000

conn = krpc.connect(name='Launch into orbit')
vessel = conn.space_center.active_vessel

# Set up streams for telemetry
ut = conn.add_stream(getattr, conn.space_center, 'ut')
altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
stage_4_resources = vessel.resources_in_decouple_stage(stage=3, cumulative=False)
stage_4_fuel = conn.add_stream(stage_4_resources.amount, 'LiquidFuel')

# print(stage_4_resources.names)
print(stage_4_fuel())

