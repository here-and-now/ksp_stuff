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
distance_dict = {}

for vessel in conn.space_center.vessels:
    if vessel.name == constellation_name:
        constellation_list.append(vessel)

#distance between each vesel in constellation_list
for vessel in constellation_list:
    distance_dict[vessel] = {}
    for target_vessel in constellation_list:
        if vessel is not target_vessel:
            sc.target_vessel = target_vessel
            distance = sc.target_vessel.orbit.distance_at_closest_approach(vessel.orbit)
            distance_dict[vessel].update({target_vessel: distance})


for vessel, distance_to_vessel_dict in distance_dict.items():
    sc.active_vessel = vessel

    sorted_distance_to_vessel_dict = sorted(distance_to_vessel_dict.items(), key=lambda x: x[1])
    antenna_parts = vessel.parts.with_tag('target_whatever')

    for i, antenna_part in enumerate(antenna_parts):
        antenna = conn.remote_tech.antenna(antenna_part)

        for module in antenna_part.modules:
            if module.name == 'ModuleRTAntenna':
                module.set_action('Activate')

        # even target nearest satellite
        if i % 2 == 0:
            antenna.target_vessel = sorted_distance_to_vessel_dict[0][0]
        # uneven target 2nd nearest satellite
        else:
            antenna.target_vessel = sorted_distance_to_vessel_dict[1][0]


