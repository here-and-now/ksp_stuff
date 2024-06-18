import math
import time
import krpc
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tabulate
import operator
from orbits import OrbitManager
from nodes import NodeManager
from vessels import VesselManager, Vessel

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
        self.sc = self.conn.space_center
        self.mj = self.conn.mech_jeb

        self.vessel = self.sc.active_vessel
        self.vessel_name = self.vessel.name
        self.constellation_name = self.vessel_name
        print("ComSatNetwork connected ...")

        self.vessel_list = [self.vessel]
        if self.vessel_list:
            self.df = self.update_df()


        self.resonance_numerator = 2
        self.resonance_denominator = 3


        self.executor = self.conn.mech_jeb.node_executor
        self.executor.tolerance = 0.1
        self.executor.lead_time = 10


    def update_df(self):
        ves = VesselManager(orbit_flag=True, node_flag=False, vessel_list=self.vessel_list)
        self.df = ves.df.apply(lambda x: x .apply(
            lambda y: y() if callable(y) else y))

        self.df['period_diff'] = self.df['period'] - self.df['period'].mean()
        print(tabulate.tabulate(self.df[['name', 'body', 'inclination',
                                         'apoapsis', 'periapsis', 'period', 'period_diff' ]],
              headers='keys', tablefmt='fancy_grid'))

        return self.df
    def return_antennas(self, vessel):
        '''
        Switches to vessel and returns all
        remote tech antennas
        '''
        self.sc.active_vessel = vessel
        return self.conn.remote_tech.comms(vessel).antennas
    def resonant_orbit(self):
        res_orbit = self.mj.maneuver_planner.operation_resonant_orbit

        res_orbit.resonance_denominator = self.resonance_denominator
        res_orbit.resonance_numerator = self.resonance_numerator


        # res_orbit.time_selector.time_reference = self.mj.TimeReference.apoapsis
        res_orbit.time_selector.time_reference = self.mj.TimeReference.x_from_now
        res_orbit.time_selector.lead_time = 30

        res_orbit.make_nodes()
        NodeManager().execute_all_nodes()

    def exec_burn(self, vessel):
        self.sc.active_vessel = vessel
        # Check for active engines
        engines = self.sc.active_vessel.parts.engines
        active_engines = [engine for engine in engines if engine.active]

        if not active_engines:
            vessel.control.rcs = True
            # Enable Fore by Throttle for RCS
            for rcs in self.sc.active_vessel.parts.rcs:
                rcs.enabled = True  # Make sure RCS is enabled
                rcs.fore_by_throttle = True  # Enable Fore by Throttle for RCS
                print(f'RCS {rcs} enabled and set to fore by throttle')
            print(f'Using RCS for vessel {vessel.name}')
        else:
            print(f'Using engines for vessel {vessel.name}')
        
        NodeManager().execute_node()



    def recircularize_multiple_sats(self):
        node_list = []
        for i, vessel in enumerate(self.df.index):
            self.sc.active_vessel = vessel

            recirc = self.mj.maneuver_planner.operation_circularize
            if self.resonance_numerator > self.resonance_denominator:
                recirc.time_selector.time_reference = self.mj.TimeReference.periapsis
            else:
                recirc.time_selector.time_reference = self.mj.TimeReference.apoapsis

            node = recirc.make_nodes()[0]
            node.ut = node.ut + (vessel.orbit.period * i)
            node_list.append(node)

        ves = VesselManager(vessel_list=self.df.index, orbit_flag=True, node_flag=True)

        self.df = ves.df.apply(lambda x: x.apply(
            lambda y: y() if callable(y) else y))
        self.df = self.df.sort_values(by='next_node_time_to', ascending=True)

        print(tabulate.tabulate(self.df[['name', 'body', 'inclination',
                                        'apoapsis', 'periapsis', 'period',
                                        'next_node_time_to', 'next_node_remaining_dv']],
                                headers='keys', tablefmt='fancy_grid'))
        for vessel in self.df.index:
            self.sc.active_vessel = vessel
            time.sleep(2)
            self.mj.smart_ass.autopilot_mode = self.mj.SmartASSAutopilotMode.node
            self.mj.smart_ass.update(True)

        for vessel in self.df.index:
            print(f'Burning {vessel}')
            self.exec_burn(vessel)


        def fine_tune_orbital_period(self):
            print("Fine tuning orbital period ...")
            self.df = self.update_df()
            period_mean = self.df['period'].mean()

            for vessel in self.df.index:
                self.sc.active_vessel = vessel
                vessel.control.rcs = False

                if vessel.orbit.period < period_mean:
                    self.mj.smart_ass.autopilot_mode = self.mj.SmartASSAutopilotMode.prograde
                    new_orientation = 'prograde'
                elif vessel.orbit.period >= period_mean:
                    self.mj.smart_ass.autopilot_mode = self.mj.SmartASSAutopilotMode.retrograde
                    new_orientation = 'retrograde'
                # vessel.control.rcs = True
                self.mj.smart_ass.force_roll = True
                self.mj.smart_ass.update(False)

                orientate_vessel(self.conn, vessel, new_orientation, accuracy_cutoff=1e-3)
                print(f'{vessel}: SmartASS mode on {self.mj.smart_ass.autopilot_mode}')

            for vessel in self.df.index:
                self.sc.active_vessel = vessel
                prev_orbital_period = vessel.orbit.period
                if vessel.orbit.period < period_mean:
                    operator_selection = operator.lt
                elif vessel.orbit.period >= period_mean:
                    operator_selection = operator.gt

                while operator_selection(vessel.orbit.period, period_mean):
                    vessel.control.rcs = True
                    vessel.control.throttle = 0.01

                vessel.control.rcs = False
                vessel.control.throttle = 0
                print(f'{vessel}: Orbital period adjusted from {prev_orbital_period} to {vessel.orbit.period}')

            print("Orbit after fine tuning: ")
            self.update_df()

    def release_all_satellites(self, nr_sats, time_between=5):
        self.vessel_list = []

        
        for s in self.vessel.parts.solar_panels:
            s.deployed = False
            print(f'Solar panels retracted for Satellite seperations')

        self.mj.smart_ass.autopilot_mode = self.mj.SmartASSAutopilotMode.normal_minus
        self.mj.smart_ass.update(False)
        # orientate_vessel(self.conn, self.vessel, 'anti_normal', accuracy_cutoff=1e-3)
        time.sleep(time_between)
        for i in range(nr_sats):
            released_satellite = self.vessel.control.activate_next_stage()
            self.vessel_list.append(released_satellite[0])
            time.sleep(time_between)

        print(f'{len(self.vessel_list)} ComSats deployed')

        print('Waiting for 10sec ... safespace for satellites')
        time.sleep(30)
        self.prepare_vessels()
        print('Vessels prepared')
        self.update_df()

    def prepare_vessels(self):        # Prepare command stuff
        for vessel in self.vessel_list:
            self.sc.active_vessel = vessel
            command_part = vessel.parts.with_module('ModuleCommand')[0]
            for mod in command_part.modules:
                if mod.name == 'ModuleCommand':
                    mod.trigger_event('Control From Here')

            for engine in vessel.parts.engines:
                engine.active = True

            for antenna in self.conn.remote_tech.comms(vessel).antennas:
                # if antenna.part.name == 'RTGitaDish2':
                #     antenna.target_body = self.conn.space_center.bodies['Kerbin']

                if antenna.part.name == 'restock-relay-radial-2.v2':
                    antenna.target_body = self.conn.space_center.bodies['Kerbin']

                for module in antenna.part.modules:
                    if module.name == 'ModuleRTAntenna':
                        module.set_action('Activate')
                    if module.name == 'ModuleDeployableAntenna':
                        module.set_action('Extend Antenna')
            for s in vessel.parts.solar_panels:
                s.deployed = True
                print(f'Solar panels deployed at')
                # pass

            self.mj.smart_ass.autopilot_mode = self.mj.SmartASSAutopilotMode.node
            self.mj.smart_ass.update(False)

    def setup_communications(self, connection_list):
        '''
        Based on distance between satellites, sets up
        communication links between them in a triangular orbit.
        One antenna will always target Kerbin.
        connection_list is a list of specific vessel names to connect to.
        '''

        # Get the vessel objects for the names in connection_list with exact name match
        vessel_name_to_object = {v.name: v for v in self.conn.space_center.vessels}
        connection_vessels = []
        for name in connection_list:
            if name in vessel_name_to_object:
                connection_vessels.append(vessel_name_to_object[name])
            else:
                print(f"Warning: Vessel named '{name}' not found.")

        distance_dict = {}
        for vessel in self.df.index:
            distance_dict[vessel] = {}
            for target_vessel in self.df.index:
                if vessel is not target_vessel:
                    self.sc.target_vessel = target_vessel
                    time.sleep(0.2)
                    distance = self.sc.target_vessel.orbit.distance_at_closest_approach(vessel.orbit)
                    distance_dict[vessel].update({target_vessel: distance})

        for vessel, distance_to_vessel_dict in distance_dict.items():
            self.sc.active_vessel = vessel
            time.sleep(2)
            antenna_parts = vessel.parts.with_name('RelayAntenna5')

            sorted_distance_to_vessel_dict = sorted(distance_to_vessel_dict.items(), key=lambda x: x[1])

            # Connect to the two nearest satellites to form a triangular communication link
            nearest_vessels = [sorted_distance_to_vessel_dict[0][0], sorted_distance_to_vessel_dict[1][0]]

            # Add vessels from connection_list if they are not already in nearest_vessels
            for conn_vessel in connection_vessels:
                if conn_vessel not in nearest_vessels:
                    nearest_vessels.append(conn_vessel)

            for i, antenna_part in enumerate(antenna_parts):
                antenna = self.conn.remote_tech.antenna(antenna_part)
                for module in antenna_part.modules:
                    if module.name == 'ModuleRTAntenna':
                        module.set_action('Activate')
                    if module.name == 'ModuleDeployableAntenna':
                        module.set_action('Extend Antenna')

                if i == 0:
                    # The first antenna targets Kerbin
                    antenna.target_body = self.conn.space_center.bodies['Kerbin']
                elif i < len(nearest_vessels) + 1:
                    # Subsequent antennas target the nearest satellites or specified vessels
                    antenna.target_vessel = nearest_vessels[i - 1]

            # Log errors if any antennas are not set properly
            if not antenna_parts or len(antenna_parts) < 3:
                print(f"Warning: Not enough antennas on vessel {vessel.name}.")
            if i >= len(antenna_parts):
                print(f"Warning: Antenna part {i} is not available for vessel {vessel.name}.")
            if nearest_vessels[0] is None or nearest_vessels[1] is None:
                print(f"Warning: Nearest vessels not properly identified for vessel {vessel.name}.")

    def init_existing_network(self, constellation_name):
        self.constellation_name = constellation_name
        self.vessel_list = []

        for vessel in self.conn.space_center.vessels:
            if vessel.name == constellation_name:
                self.vessel_list.append(vessel)

        print(
            f'{len(self.vessel_list)} preexisting satellites found with name {constellation_name}')

        self.update_df()
    def release_sats_triangle_orbit(self,nr_sats=5):
            # reset vessel list, release satelittes will create updated one
            self.release_satellite()

            for i in range(nr_sats-1):
                self.resonant_orbit()
                self.recircularize()
                self.release_satellite()

            self.update_df()

    def recircularize(self):
        recirc = self.mj.maneuver_planner.operation_circularize
        if self.resonance_numerator > self.resonance_denominator:
            recirc.time_selector.time_reference = self.mj.TimeReference.periapsis
        else:
            recirc.time_selector.time_reference = self.mj.TimeReference.apoapsis
        recirc.make_nodes()
        # NodeManager().execute_node()


    def release_satellite(self):
        '''
        Orientates the spacecraft, activates next stage and adds
        released satellite to a list
        '''
        print('Deploying ComSat')

        for s in self.vessel.parts.solar_panels:
            s.deployed = False
            print(f'Solar panels retracted for Satellite seperations')

        self.mj.smart_ass.autopilot_mode = self.mj.SmartASSAutopilotMode.normal_minus
        self.mj.smart_ass.update(False)

        orientate_vessel(self.conn, self.vessel, 'normal_minus', accuracy_cutoff=1e-2)

        released_satellite = self.vessel.control.activate_next_stage()
        self.vessel_list.append(released_satellite[0])

        print('ComSat deployed')
        self.update_df()
