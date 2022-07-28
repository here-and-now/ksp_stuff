import krpc
import tabulate
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

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
        #sort vessel list by attribute met
        vessel_list.sort(key=lambda v: v.met)

        #ask for input which vessel to use, default 0
        print("Multiple vessels found:")
        #print vessel list names and met in tabulated format with index
        print(tabulate.tabulate([[i, v.name, v.met] for i, v in enumerate(vessel_list)], headers=['Index', 'Name', 'MET']))
        # vessel_index = int(input("Select vessel by index: "))
        vessel_index = 0
        print("Vessel selected: " + vessel_list[vessel_index].name)


        return vessel_list[vessel_index]

    return None

def select_vessel_by_id(vessel_id):
    for v in vessels:
        if v.id == vessel_id:
            return v
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

# vessel_name = 'Kerbin_Goresat/VS-3/Magneto/MSIP'
vessel_name = 'OsNet_1.0_Ring_1'

vessel = select_vessel_and_duplicates_by_name(vessel_name)
vessel = switch_vessel(vessel)

control = vessel.control
control.sas = True
control.sas_mode = sc.SASMode.prograde
print(vessel.control.sas_mode)
#activate next stage returns list of vesse
# vessels = control.activate_next_stage()

print(vessels)


# Set up streams for telemetry
ut = conn.add_stream(getattr, conn.space_center, 'ut')
altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
periapsis = conn.add_stream(getattr, vessel.orbit, 'periapsis_altitude')
orbit_period = conn.add_stream(getattr, vessel.orbit, 'period')
orbit_speed = conn.add_stream(getattr, vessel.orbit, 'speed')
orbit_inclination = conn.add_stream(getattr, vessel.orbit, 'inclination')
orbit_eccentricity = conn.add_stream(getattr, vessel.orbit, 'eccentricity')

conn.close()

# control stuff
# control = vessel.control
# print(control)
# control.throttle = 1.0

# ut = 500
# control.add_node(ut, prograde=1.0)
# print(control.throttle)

#change apoapsis to desired value
# vessel.
# planner = mj.maneuver_planner
# apo = planner.operation_apoapsis
# apo.new_apoapsis = 1000000000
# apo.make_nodes()
