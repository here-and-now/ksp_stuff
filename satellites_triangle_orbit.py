import krpc
import tabulate
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time
from utils.handle_vessels import switch_vessel, select_vessel_and_duplicates_by_name, activate_engines_by_name, decouple_by_name
from utils.handle_orientation import orientate_vessel

# init
conn = krpc.connect(name="Satellites Triangle Orbit")
print("Connected to kRPC")

sc = conn.space_center
vessels = sc.vessels
mj = conn.mech_jeb

# vessel
vessel_name = 'OsNet_1.0_Ring_1'
vessel = select_vessel_and_duplicates_by_name(vessels, vessel_name)
sc.active_vessel = switch_vessel(sc.active_vessel, vessel)
vessel = sc.active_vessel

#control block
control = vessel.control
control.sas = True
control.sas_mode = sc.SASMode.prograde

orientation = 'prograde'
vessel = orientate_vessel(conn, vessel, orientation)

#staging
activated_engines = activate_engines_by_name(vessel, 'orbital-engine-0625')
# decouple_by_name(vessel, 'proceduralStackDecoupler')

# wait for satellites to spread apart
time.sleep(10)

# triple constellation stuff
constellation_name = 'TripleOs'
constellation_list = control.activate_next_stage()
constellation_list.append(vessel)

for i, vessel in enumerate(constellation_list):
    vessel.name = constellation_name + '_' + str(i)
    # sc.active_vessel = switch_vessel(sc.active_vessel, vessel)


# satellite operations
# result = [orientate_vessel(conn, vessel, 'retrograde', block=False) for vessel in constellation_list]

#solar 
# solar = [v.parts.solar_panels for v in constellation_list]
# solar = [item for sublist in solar for item in sublist]
# for panel in solar:
    # panel.deployed = True


# mechanical jebediah time <3

def execute_nodes():
    print("Executing nodes")
    executor = mj.node_executor
    # executor.execute_all_nodes()
    executor.execute_one_node()


    with conn.stream(getattr, executor, 'enabled') as enabled:
        enabled.rate = 1
        with enabled.condition:
            while enabled():
                enabled.wait()

node_list = []
for vessel in constellation_list:
    sc.active_vessel = switch_vessel(sc.active_vessel, vessel)

    planner = mj.maneuver_planner
    aps = planner.operation_circularize
    # aps.new_apoapsis = 200000
    aps.make_nodes()
    
    no = vessel.control.nodes
    print(no)
    node_list.append(no)
    execute_nodes()

print(node_list)



# execute_nodes()

# for vessel in constellation_list:



# # Set up streams for telemetry
# ut = conn.add_stream(getattr, conn.space_center, 'ut')
try:
    time.sleep(30)
except KeyboardInterrupt:
    sc.quickload()
finally:
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
