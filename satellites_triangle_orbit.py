import krpc
import tabulate
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time
from utils.handle_vessels import switch_vessel, select_vessel_and_duplicates_by_name, activate_engines_by_name

conn = krpc.connect(name="Launch into orbit")
print("Connected to kRPC")

mj = conn.mech_jeb
sc = conn.space_center
vessels = sc.vessels


vessel_name = 'OsNet_1.0_Ring_1'

vessel = select_vessel_and_duplicates_by_name(vessels, vessel_name)
sc.active_vessel = switch_vessel(sc.active_vessel, vessel)
vessel = sc.active_vessel

control = vessel.control
control.sas = True
control.sas_mode = sc.SASMode.prograde

direction = conn.add_stream(getattr, vessel.flight(), 'direction')
prograde = conn.add_stream(getattr, vessel.flight(), 'prograde')

motion = True
while motion:
    diff = np.abs(np.subtract(direction(), prograde())) < 1e-1
    print(diff)
    motion = np.any(diff==False)
    print(motion)
    time.sleep(1)

activated_engines = activate_engines_by_name(vessel, 'orbital-engine-0625')

new_vessels = control.activate_next_stage()

print(new_vessels)

for v in new_vessels:
    print(v.name)
    print(v.met)
    v.control.throttle = 0.2

# Set up streams for telemetry
ut = conn.add_stream(getattr, conn.space_center, 'ut')

conn.close()



# vessel.auto_pilot.engage()
# vessel.auto_pilot.sas = True
# auto_pilot.sas_mode = sc.SASMode.retrograde
# vessel.auto_pilot.wait()

# ut = 500
# control.add_node(ut, prograde=1.0)
# print(control.throttle)

#change apoapsis to desired value
# vessel.
# planner = mj.maneuver_planner
# apo = planner.operation_apoapsis
# apo.new_apoapsis = 1000000000
# apo.make_nodes()
