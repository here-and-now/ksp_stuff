import time

import krpc
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tabulate

from utils.handle_orientation import orientate_vessel
from utils.handle_vessels import (
    decouple_by_name,
    manipulate_engines_by_name,
    select_vessel_and_duplicates_by_name,
    switch_vessel,
)
# init
conn = krpc.connect(name="Satellite Management")
sc = conn.space_center
mj = conn.mech_jeb

# constellation stuff setup
constellation_name = 'Comsat_0.38_RingZero Relay'
constellation_list = []

for vessel in conn.space_center.vessels:
    if vessel.name == constellation_name:
        constellation_list.append(vessel)

# orbital period mean of constellation_list
period_mean = sum(
    vessel.orbit.period for vessel in constellation_list) / len(constellation_list)
print('Average period is {}'.format(period_mean))


def get_telemetry():

    table = tabulate.tabulate([[i, v.name, v.orbit.body.name, v.orbit.apoapsis_altitude, v.orbit.periapsis_altitude, v.orbit.inclination, v.orbit.period, (v.orbit.period - period_mean)]
                              for i, v in enumerate(constellation_list)], headers=['Name', 'Body', 'MET', 'Apo', 'Per', 'Inclination', 'Period', 'Deviation'], tablefmt='fancy_grid')
    print(table)


get_telemetry()

# for i, vessel in enumerate(constellation_list):
    # # ccvessel.name = constellation_name + '_' + str(i)
    # sc.active_vessel = switch_vessel(sc.active_vessel, vessel)


#distance between each vesel in constellation_list
for vessel in constellation_list:
    for target_vessel in constellation_list:
        if vessel is not target_vessel:
            sc.target_vessel = target_vessel
            dist = sc.target_vessel.orbit.distance_at_closest_approach(vessel.orbit)
            print('{} - {}: {}'.format(vessel.name, target_vessel.name, dist))


# or vessel in constellation_list:

    # for target_vessel in constellation_list[:-1]:



        # if vessel.name != target_vessel.name:

            # for part in vessel.parts.with_tag('relay'):
                # antenna = conn.remote_tech.antenna(part)
                # antenna.target_vessel = target_vessel


    

get_telemetry()










# satellite operations
#result = [orientate_vessel(conn, vessel, 'retrograde', block=False) for vessel in constellation_list]

# solar
# solar = [v.parts.solar_panels for v in constellation_list]
# solar = [item for sublist in solar for item in sublist]
# for panel in solar:
# panel.deployed = True


# mechanical jebediah time <3

# def execute_nodes():
# print("Executing nodes")
# executor = mj.node_executor
# # executor.execute_all_nodes()
# executor.execute_one_node()

# with conn.stream(getattr, executor, 'enabled') as enabled:
# enabled.rate = 1
# with enabled.condition:
# while enabled():
# enabled.wait()

# node_list = []
# for vessel in constellation_list:
# sc.active_vessel = switch_vessel(sc.active_vessel, vessel)

# planner = mj.maneuver_planner
# man = planner.operation_circularize
# # man.time_selector.time_reference = mj.TimeReference.
# man.time_selector.circularize_altitude = 100000

# ut = conn.add_stream(getattr, conn.space_center, 'ut')
# # aps.ut = ut() + 100000

# # aps.new_apoapsis = 200000

# man.make_nodes()

# no = vessel.control.nodes

# for x in no:
# print(x.ut)
# node_list.append(no)
# execute_nodes()

# #print node list attributes delta_v, ut, remaining_burn_vector sort by ut
# # node_list = sorted(node_list, key=lambda x: x.ut)
# # for node in node_list:
# # print(node.delta_v, node.ut, node.remaining_burn_vector)


# # execute_nodes()

# # for vessel in constellation_list:


# # # Set up streams for telemetry
# try:
# time.sleep(30)
# except KeyboardInterrupt:
# sc.quickload()
# finally:
# conn.close()


# # vessel.auto_pilot.engage()
# # vessel.auto_pilot.sas = True
# # auto_pilot.sas_mode = sc.SASMode.retrograde
# # vessel.auto_pilot.wait()

# # ut = 500
# # control.add_node(ut, prograde=1.0)
# # print(control.throttle)

# #change apoapsis to desired value
# # vessel.
# # planner = mj.maneuver_planner
# # apo = planner.operation_apoapsis
# # apo.new_apoapsis = 1000000000
# # apo.make_nodes()
