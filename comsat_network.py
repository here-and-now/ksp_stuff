import math
import time

import krpc
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tabulate
from node_manager import NodeManager
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
        print("ComSatNetwork connected ...")

        self.sc = self.conn.space_center

        self.vessel = self.sc.active_vessel
        self.vessel_name = self.vessel.name
        self.constellation_name = self.vessel_name
        self.satellite_list = []

        self.mj = self.conn.mech_jeb
        self.auto_pilot = self.vessel.auto_pilot

        if self.satellite_list:
            self.setup_df()

        # Telemetry
        self.ut = self.conn.add_stream(getattr, self.conn.space_center, 'ut')
        self.altitude = self.conn.add_stream(
            getattr, self.vessel.flight(), 'mean_altitude')
        self.apoapsis = self.conn.add_stream(
            getattr, self.vessel.orbit, 'apoapsis_altitude')
        self.periapsis = self.conn.add_stream(
            getattr, self.vessel.orbit, 'periapsis_altitude')
        self.eccentricity = self.conn.add_stream(
            getattr, self.vessel.orbit, 'eccentricity')
        self.inclination = self. conn.add_stream(
            getattr, self.vessel.orbit, 'inclination')

    def setup_df(self):
        '''
        Creates a pandas dataframe to store
        telemetry data and antennas
        '''
        self.period_mean = sum(
            vessel.orbit.period for vessel in self.satellite_list) / len(self.satellite_list)

        data = [[v, v.name, v.orbit.body.name, v.orbit.apoapsis_altitude, v.orbit.periapsis_altitude,
                 v.orbit.inclination, v.orbit.period, (
                     v.orbit.period - self.period_mean),
                 self.return_antennas(v)] for v in self.satellite_list]

        self.df = pd.DataFrame(data, columns=['Vessel', 'Name', 'Body', 'Apoapsis', 'Periapsis',
                                              'Inclination', 'Period', 'Period diff', 'Antennas'])
        self.df.set_index('Vessel', inplace=True)

        print(tabulate.tabulate(self.df.drop('Antennas', axis=1),
              headers='keys', tablefmt='fancy_grid'))

        return self.df

    def return_antennas(self, vessel):
        '''
        Switches to vessel and returns all
        remote tech antennas
        '''
        self.sc.active_vessel = vessel
        return self.conn.remote_tech.comms(vessel).antennas


    def manage_antennas(self):
        '''
        Manage antennas of all vessels in constellation.
        Currrently only activates RT antenna part modules.
        WIP: Targeting
        '''

        self.df['Antennas'].to_frame().apply(lambda x: self.activate_antennas(x.index, x.values))


    def activate_antennas(self, vessel, antennas):
        '''
        Activates all RT antennas in list
        '''
        print(vessel[0])
        # print(antennas.values)
        self.sc.active_vessel = vessel[0]
        for antenna in antennas[0]:
            print(antenna)
            # self.sc.active_vessel = antenna.part.vessel
            for module in antenna.part.modules:
                if module.name == 'ModuleRTAntenna':
                    
                    module.set_action('Activate')
                    print('Antenna activated on ')

    def resonant_orbit(self):
        self.res_orbit = self.mj.maneuver_planner.operation_resonant_orbit
        self.res_orbit.time_selector.time_reference = self.mj.TimeReference.apoapsis

        self.res_orbit.resonance_numerator = 2
        self.res_orbit.resonance_denominator = 3

        self.res_orbit.make_nodes()
        NodeManager().execute_node()

    def recircularize(self):
        recirc = self.mj.maneuver_planner.operation_circularize
        if self.res_orbit.resonance_numerator > self.res_orbit.resonance_denominator:
            recirc.time_selector.time_reference = self.mj.TimeReference.periapsis
        else:
            recirc.time_selector.time_reference = self.mj.TimeReference.apoapsis

        recirc.make_nodes()
        NodeManager().execute_node()

    def release_sats_triangle_orbit(self):
        self.release_satellite()

        self.resonant_orbit()
        self.recircularize()
        self.release_satellite()

        self.resonant_orbit()
        self.recircularize()
        self.release_satellite()

        self.setup_df()


    def release_satellite(self):
        '''
        Orientates the spacecraft, activates next stage and adds
        released satellite to a list
        '''
        print('Deploying ComSat')

        self.mj.smart_ass.autopilot_mode = self.mj.SmartASSAutopilotMode.normal_minus
        self.mj.smart_ass.update(False)
        time.sleep(30)

        released_satellite = self.vessel.control.activate_next_stage()
        self.satellite_list.append(released_satellite)

        print('ComSat deployed')
        time.sleep(30)

    def setup_communications(self):
        '''
        Outdated, use manage_antennas instead.
        Based on distance between satellites, sets up
        communication links between them
        '''

        distance_dict = {}
        print(self.satellite_list)
        for vessel in self.satellite_list:
            distance_dict[vessel] = {}
            for target_vessel in self.satellite_list:

                print('tarvessel', target_vessel)
                if vessel is not target_vessel:
                    self.sc.target_vessel = target_vessel
                    print('Target', self.sc.target_vessel)
                    distance = self.sc.target_vessel.orbit.distance_at_closest_approach(
                        vessel.orbit)
                    distance_dict[vessel].update({target_vessel: distance})

        for vessel, distance_to_vessel_dict in distance_dict.items():
            self.sc.active_vessel = vessel
            antenna_parts = vessel.parts.with_tag('target_whatever')

            sorted_distance_to_vessel_dict = sorted(
                distance_to_vessel_dict.items(), key=lambda x: x[1])

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

    def init_existing_network(self, constellation_name):
        self.constellation_name = constellation_name
        self.satellite_list = []

        for vessel in self.conn.space_center.vessels:
            if vessel.name == constellation_name:
                self.satellite_list.append(vessel)

        print(
            f'{len(self.satellite_list)} preexisting satellites found with name {constellation_name}')

        # print("Fucking up satellite list for testing purposes ... ")
        # self.satellite_list = [self.sc.active_vessel]

        self.setup_df()
