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
        active_vessel = vessel
        print("Switched to vessel: " + vessel.name + " from " + backup_vessel.name)
        return vessel
    else:
        print("Vessel is already active: " + vessel.name)
        return active_vessel

def manipulate_engines_by_name(vessel, engine_name,action_dict=None):
    engine_list = []
    for engine in vessel.parts.engines:
        print(engine.part.name)
        print(engine.part.resources.all)
        if engine.part.name == engine_name:
            if action == None:
                print('No action selected. ' + engine.part.name + " is " + ("on" if engine.active else "off"))
            if 'active' in action_dict.keys():
                engine.active = action_dict['active']
                print(engine.part.name + " is " + ("on" if engine.active else "off"))
            if 'throttle' in action_dict.keys():
                engine.throttle = action_dict['throttle']
                print(engine.part.name + " throttle is " + str(engine.throttle))
            engine_list.append(engine)

    return engine_list

def decouple_by_name(vessel, decoupler_name):
    decoupler_list = []
    for decoupler in vessel.parts.decouplers:
        print(decoupler.part.name)
        if decoupler.part.name == decoupler_name:
            decoupler.decouple()
            decoupler_list.append(decoupler)
            print("Decoupled: " + decoupler.part.name + " on vessel: " + vessel.name)

    return decoupler_list
