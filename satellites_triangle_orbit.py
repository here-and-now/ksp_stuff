import krpc
import tabulate
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time
from utils.handle_vessels import switch_vessel, select_vessel_and_duplicates_by_name, activate_engines_by_name, decouple_by_name
from utils.handle_orientation import orientate_vessel

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

orientation = 'prograde'
vessel = orientate_vessel(conn, vessel, orientation)
activated_engines = activate_engines_by_name(vessel, 'orbital-engine-0625')
# decouple_by_name(vessel, 'proceduralStackDecoupler')

constellation_name = 'TripleOs'
constellation_list = control.activate_next_stage()
constellation_list.append(vessel)

for i, vessel in enumerate(constellation_list):
    vessel.name = constellation_name + '_' + str(i)
    # sc.active_vessel = switch_vessel(sc.active_vessel, vessel)


time.sleep(10)


result = [orientate_vessel(conn, vessel, 'normal', block=False) for vessel in constellation_list]
# throttle = [0.5 for vessel in constellation_list]

# mechanical jebediah time <3

planner = mj.maneuver_planner
aps = planner.operation_apoapsis
aps.new_apoapsis = 5000000
aps.make_nodes()





# # Set up streams for telemetry
# ut = conn.add_stream(getattr, conn.space_center, 'ut')
time.sleep(10)
sc.quickload()
conn.close()


# direction = conn.add_stream(getattr, vessel.flight(), 'direction')
# prograde = conn.add_stream(getattr, vessel.flight(), 'prograde')

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
