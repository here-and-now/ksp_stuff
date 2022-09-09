import math
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

class ComSatNetwork():
    def __init__(self):
        self.conn = krpc.connect(name="ComSat_Network")
        print("ComSatNetwork connected to KSP")

        self.sc = self.conn.space_center

        self.vessel = self.sc.active_vessel
        self.vessel_name = self.vessel.name
        self.constellation_name = self.vessel_name
        self.satellite_list = []

        self.mj = self.conn.mech_jeb
        self.auto_pilot = self.vessel.auto_pilot

        # Telemetry
        self.ut = self.conn.add_stream(getattr, self.conn.space_center, 'ut')
        self.altitude = self.conn.add_stream(getattr, self.vessel.flight(), 'mean_altitude')
        self.apoapsis = self.conn.add_stream(getattr, self.vessel.orbit, 'apoapsis_altitude')
        self.periapsis = self.conn.add_stream(getattr, self.vessel.orbit, 'periapsis_altitude')
        self.eccentricity = self.conn.add_stream(getattr, self.vessel.orbit, 'eccentricity')
        self.inclination = self. conn.add_stream(getattr, self.vessel.orbit, 'inclination')
        
    def execute_nodes(self):
        executor = self.mj.node_executor
        executor.tolerance = 0.001
        executor.lead_time = 3
        executor.execute_one_node()

        with self.conn.stream(getattr, executor, 'enabled') as enabled:
            enabled.rate = 1
            with enabled.condition:
                while enabled():
                    enabled.wait()

    
    def resonant_orbit(self):
        self.res_orbit = self.mj.maneuver_planner.operation_resonant_orbit
        self.res_orbit.time_selector.time_reference = self.mj.TimeReference.apoapsis

        self.res_orbit.resonance_numerator = 2
        self.res_orbit.resonance_denominator = 3

        self.res_orbit.make_nodes()
        self.execute_nodes()

   
    def recircularize(self):
        recirc = self.mj.maneuver_planner.operation_circularize
        if self.res_orbit.resonance_numerator > self.res_orbit.resonance_denominator:
            recirc.time_selector.time_reference = self.mj.TimeReference.periapsis
        else:
            recirc.time_selector.time_reference = self.mj.TimeReference.apoapsis

        recirc.make_nodes()
        self.execute_nodes()

    def release_sats_triangle_orbit(self):
        # fix this, just jump resonant orbit start position before releasing
        # self.resonant_orbit()
        # self.recircularize()
        # end bullshit

        self.release_satellite()

        self.resonant_orbit()
        self.recircularize()
        self.release_satellite()

        self.resonant_orbit()
        self.recircularize()
        self.release_satellite()

       
    def release_satellite(self):
        '''
        Orientates the spacecraft, activates next stage and adds
        released satellite to a list
        '''
        print('Deploying ComSat')
        
        self.mj.smart_ass.autopilot_mode = self.mj.SmartASSAutopilotMode.normal_minus
        self.mj.smart_ass.update(False)
        time.sleep(15)

        released_satellite = self.vessel.control.activate_next_stage()
        self.satellite_list.append(released_satellite)

        print('ComSat deployed')
        time.sleep(10)

    def setup_communications(self):
        distance_dict = {}
        
        print(self.satellite_list)
        for vessel in self.satellite_list:
            distance_dict[vessel] = {}
            for target_vessel in self.satellite_list:

                print('tarvessel', target_vessel)
                if vessel is not target_vessel:
                    self.sc.target_vessel = target_vessel
                    print('Target', self.sc.target_vessel)
                    distance = self.sc.target_vessel.orbit.distance_at_closest_approach(vessel.orbit)
                    distance_dict[vessel].update({target_vessel: distance})


        for vessel, distance_to_vessel_dict in distance_dict.items():
            self.sc.active_vessel = vessel
            antenna_parts = vessel.parts.with_tag('target_whatever')

            sorted_distance_to_vessel_dict = sorted(distance_to_vessel_dict.items(), key=lambda x: x[1])

            for i, antenna_part in enumerate(antenna_parts):
                antenna = self.conn.remote_tech.antenna(antenna_part)
                for module in antenna_part.modules:
                    if module.name == 'ModuleRTAntenna':
                        module.set_action('Activate')
                # even target nearest satellite
                if i % 2 == 0:
                    antenna.target_vessel = sorted_distance_to_vessel_dict[0][0]
                # uneven target 2nd nearest satellite
                else:
                    antenna.target_vessel = sorted_distance_to_vessel_dict[1][0]
    
    def get_antennas(self):
        antennas = []
        for vessel in self.satellite_list:
            antenna_parts = vessel.parts.with_name('RelayAntenna5')
            for antenna_part in antenna_parts:
                antennas.append(self.conn.remote_tech.antenna(antenna_part))


        print(antennas)
        return antennas

    
    def preexisting_network(self, constellation_name):
        self.constellation_name = constellation_name
        self.satellite_list = []
        for vessel in self.conn.space_center.vessels:
            if vessel.name == constellation_name:
                self.satellite_list.append(vessel)
        print(f'{len(self.satellite_list)} preexisting satellites found with name {constellation_name}')
        self.get_comm_status()


    def get_comm_status(self):
        for vessel in self.satellite_list:
            antennas = self.conn.remote_tech.comms(vessel).antennas
            table = tabulate.tabulate([[i,
                                        self.constellation_name,
                                        vessel.name,
                                        a.target_body.name if a.target.name == 'celestial_body' else a.target,
                                        a.has_connection
                                        ]
                                        for i, a in enumerate(antennas)],
                                        headers=['Index',
                                            'Constellation',
                                            'Vessel name',
                                            'Target',
                                            'Connection status',
                                            ],
                                    tablefmt='fancy_grid')
        #list and count antennas that have no target
            no_target_antennas = [a for a in antennas if a.target is self.conn.remote_tech.Target.none]

            print('Vessel name: ', self.vessel.name)
            print(table)
            print(no_target_antennas)


