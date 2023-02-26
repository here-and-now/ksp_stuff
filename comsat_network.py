import math
import time
import krpc
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tabulate

from orbits import OrbitManager
from nodes import NodeManager

class ComSatNetwork():
    def __init__(self):
        self.conn = krpc.connect(name="ComSat_Network")
        print("ComSatNetwork connected ...")

        self.sc = self.conn.space_center

        self.vessel = self.sc.active_vessel
        self.vessel_name = self.vessel.name
        self.constellation_name = self.vessel_name

        self.vessel_list = [self.vessel]
        if self.vessel_list:
            self.df = self.setup_df()

        #self.orbit_manager = OrbitManager(df=self.df)
        #self.node_manager = NodeManager()

        
        # self.vessel_list = []

        self.mj = self.conn.mech_jeb
        self.auto_pilot = self.vessel.auto_pilot



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
            vessel.orbit.period for vessel in self.vessel_list) / len(self.vessel_list)

        data = [[v, v.name, v.orbit.body.name, v.orbit.apoapsis_altitude, v.orbit.periapsis_altitude,
                 v.orbit.inclination, v.orbit.period, (
                     v.orbit.period - self.period_mean),
                self.return_antennas(v)] for v in self.vessel_list]

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
    def resonant_orbit(self):
        self.res_orbit = self.mj.maneuver_planner.operation_resonant_orbit
        self.res_orbit.time_selector.time_reference = self.mj.TimeReference.apoapsis

        self.res_orbit.resonance_numerator = 4
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
        # reset vessel list, release satelittes will create updated one
        self.vessel_list = []
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
        self.vessel_list.append(released_satellite[0])
        print(self.vessel_list)
        print('Releaqsed sat', released_satellite[0])

        print('ComSat deployed')
        time.sleep(30)

    def init_existing_network(self, constellation_name):
        self.constellation_name = constellation_name
        self.vessel_list = []

        for vessel in self.conn.space_center.vessels:
            if vessel.name == constellation_name:
                self.vessel_list.append(vessel)

        print(
            f'{len(self.vessel_list)} preexisting satellites found with name {constellation_name}')

        # print("Fucking up satellite list for testing purposes ... ")
        # self.satellite_list = [self.sc.active_vessel]

        self.setup_df()
