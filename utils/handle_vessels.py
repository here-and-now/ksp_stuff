# import krpc
import tabulate
# import numpy as np
# import matplotlib.pyplot as plt
# import pandas as pd
# import time

# conn = krpc.connect(name="Launch into orbit")
# print("Connected to kRPC")

# mj = conn.mech_jeb
# sc = conn.space_center
# vessels = sc.vessels

def select_vessel_and_duplicates_by_name(vessels, vessel_name):
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

def switch_vessel(active_vessel, vessel):
    if vessel != active_vessel:
        backup_vessel = active_vessel
        sc.active_vessel = vessel
        print("Switched to vessel: " + vessel.name + " from " + backup_vessel.name)
        return sc.active_vessel
    else:
        print("Vessel is already active: " + vessel.name)
        return vessel
