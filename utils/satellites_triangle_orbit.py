import krpc
import tabulate
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time

conn = krpc.connect(name="Launch into orbit")
print("Connected to kRPC")

mj = conn.mech_jeb
sc = conn.space_center
vessels = sc.vessels

def select_vessel_and_duplicates_by_name(vessel_name):
    vessel_list = []
    for v in vessels:
        if v.name == vessel_name:
            vessel_list.append(v)

    if len(vessel_list) == 0:
        print("No vessel found with name: " + vessel_name)
        return False
    elif len(vessel_list) == 1:
        print("Vessel found: " + vessel_list[0].name)
        return vessel_list[0]
    else:
        vessel_list.sort(key=lambda v: v.met)
        print("Multiple vessels found:")
        print(tabulate.tabulate([[i, v.name, v.met] for i, v in enumerate(vessel_list)], headers=['Index', 'Name', 'MET']))
        # vessel_index = int(input("Select vessel by index: "))
        vessel_index = 0
        print("Vessel selected: " + vessel_list[vessel_index].name)

        return vessel_list[vessel_index]

    return None

def switch_vessel(vessel):
    if vessel != sc.active_vessel:
        backup_vessel = sc.active_vessel
        sc.active_vessel = vessel
        print("Switched to vessel: " + vessel.name + " from " + backup_vessel.name)
        return sc.active_vessel
    else:
        print("Vessel is already active: " + vessel.name)
        return vessel


vessel_name = 'OsNet_1.0_Ring_1'

vessel = select_vessel_and_duplicates_by_name(vessel_name)
vessel = switch_vessel(vessel)

control = vessel.control
control.sas = True
control.sas_mode = sc.SASMode.prograde

direction = conn.add_stream(getattr, vessel.flight(), 'direction')
prograde = conn.add_stream(getattr, vessel.flight(), 'prograde')

motion = True
while motion:
    diff = np.abs(np.subtract(direction(), prograde())) < 1e-3
    print(diff)
    motion = np.any(diff==False)
    print(motion)
    time.sleep(1)


for engine in vessel.parts.engines:
    if engine.part == "rwpsAnt":
        engine.active = True
        print("Engine activated: " + engine.name)

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
