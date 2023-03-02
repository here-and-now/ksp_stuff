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


    def update_df(self):
        '''
        Creates a pandas dataframe to store
        telemetry data and antennas
        '''
        ves = VesselManager(orbit_flag=True, node_flag=False, vessel_list=self.vessel_list)

        # self.df = ves.setup_df()

        self.df = ves.df.apply(lambda x: x.apply(
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
        self.res_orbit = self.mj.maneuver_planner.operation_resonant_orbit
        self.res_orbit.time_selector.time_reference = self.mj.TimeReference.apoapsis

        self.res_orbit.resonance_numerator = 6
        self.res_orbit.resonance_denominator = 5

        self.res_orbit.make_nodes()
        # NodeManager().execute_all_nodes()

    def recircularize(self):
        recirc = self.mj.maneuver_planner.operation_circularize
        if self.res_orbit.resonance_numerator > self.res_orbit.resonance_denominator:
            recirc.time_selector.time_reference = self.mj.TimeReference.periapsis
        else:
            recirc.time_selector.time_reference = self.mj.TimeReference.apoapsis

        recirc.make_nodes()
        # NodeManager().execute_node()

    def release_sats_triangle_orbit(self,nr_sats=5):
        # reset vessel list, release satelittes will create updated one
        self.release_satellite()

        for i in range(nr_sats-1):
            self.resonant_orbit()
            self.recircularize()
            self.release_satellite()

        self.update_df()

    def init_sat_burns(self):
        for vessel in self.df.index:
            self.sc.active_vessel = vessel
            self.resonant_orbit()
    def fine_tune_orbital_period(self):
        """
        Fine tune orbital period for each satelitte in satellite list
        to the mean orbital period with RCS thrusters
        """
        print("Fine tuning orbital period ...")
        self.df = self.update_df()
        period_mean = self.df['period'].mean()

        for vessel in self.df.index:
            self.sc.active_vessel = vessel
            vessel.control.rcs = False

            if vessel.orbit.period < period_mean:
                self.mj.smart_ass.autopilot_mode = self.mj.SmartASSAutopilotMode.prograde
            elif vessel.orbit.period >= period_mean:
                self.mj.smart_ass.autopilot_mode = self.mj.SmartASSAutopilotMode.retrograde
            # vessel.control.rcs = True
            self.mj.smart_ass.update(False)

            print(f'{vessel} smartass on {self.mj.smart_ass.autopilot_mode}')

        time.sleep(15)

        for vessel in self.df.index:
            self.sc.active_vessel = vessel
            if vessel.orbit.period < period_mean:
                operator_selection = operator.lt
            elif vessel.orbit.period >= period_mean:
                operator_selection = operator.gt

            while operator_selection(vessel.orbit.period, period_mean):
                vessel.control.rcs = True
                vessel.control.throttle = 0.05
                print(f'{vessel} RCS activated and throttled to 0.05')

            vessel.control.rcs = False
            vessel.control.throttle = 0
            print(f'{vessel} RCS deactivated and throttled to 0')

        print("Orbit after fine tuning: ")

        self.update_df()

    def release_all_satellites(self, nr_sats, time_between=2):
        self.vessel_list = []

        self.mj.smart_ass.autopilot_mode = self.mj.SmartASSAutopilotMode.prograde
        self.mj.smart_ass.update(False)

        time.sleep(20)
        for i in range(nr_sats):
            released_satellite = self.vessel.control.activate_next_stage()
            self.vessel_list.append(released_satellite[0])
            time.sleep(time_between)

        print(f'{len(self.vessel_list)} ComSats deployed')

        self.update_df()

    def release_satellite(self):
        '''
        Orientates the spacecraft, activates next stage and adds
        released satellite to a list
        '''
        print('Deploying ComSat')

        self.mj.smart_ass.autopilot_mode = self.mj.SmartASSAutopilotMode.normal_minus
        self.mj.smart_ass.update(False)
        time.sleep(10)

        released_satellite = self.vessel.control.activate_next_stage()
        self.vessel_list.append(released_satellite[0])

        print('ComSat deployed')
        self.update_df()

    def init_existing_network(self, constellation_name):
        self.constellation_name = constellation_name
        self.vessel_list = []

        for vessel in self.conn.space_center.vessels:
            if vessel.name == constellation_name:
                self.vessel_list.append(vessel)

        print(
            f'{len(self.vessel_list)} preexisting satellites found with name {constellation_name}')

        self.update_df()
