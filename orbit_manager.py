import math
import time

import krpc
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tabulate
import operator

from node_manager import NodeManager
from utils.handle_orientation import orientate_vessel
from utils.handle_vessels import (
    decouple_by_name,
    manipulate_engines_by_name,
    select_vessel_and_duplicates_by_name,
    switch_vessel,
)


class OrbitManager():
    def __init__(self, instance_name='OrbitManager'):
        self.conn = krpc.connect(name=instance_name)
        print(f"OrbitManager: {instance_name} connected.")
        self.sc = self.conn.space_center

        self.vessel = self.sc.active_vessel
        self.vessel_name = self.vessel.name
        self.vessel_list = [self.vessel]

        self.mj = self.conn.mech_jeb
        self.auto_pilot = self.vessel.auto_pilot

        # Telemetry
        self.ut = self.conn.add_stream(getattr, self.conn.space_center, 'ut')
        self.apoapsis = self.conn.add_stream(
            getattr, self.vessel.orbit, 'apoapsis_altitude')
        self.periapsis = self.conn.add_stream(
            getattr, self.vessel.orbit, 'periapsis_altitude')

        # keplerian elements
        self.eccentricity = self.conn.add_stream(
            getattr, self.vessel.orbit, 'eccentricity')
        self.semi_major_axis = self.conn.add_stream(
            getattr, self.vessel.orbit, 'semi_major_axis')
        self.inclination = self.conn.add_stream(
            getattr, self.vessel.orbit, 'inclination')
        self.longitude_of_ascending_node = self.conn.add_stream(
            getattr, self.vessel.orbit, 'longitude_of_ascending_node')
        self.argument_of_periapsis = self.conn.add_stream(
            getattr, self.vessel.orbit, 'argument_of_periapsis')
        self.true_anomaly = self.conn.add_stream(
            getattr, self.vessel.orbit, 'true_anomaly')

    def fine_tune_orbital_period(self):
        """
        Fine tune orbital period for each satelitte in satellite list
        to the mean orbital period with RCS thrusters 
        """
        print("Fine tuning orbital period ...")
        print("Orbit before fine tuning: ")
        print(self.print_telemetry())

        period_mean = self.get_orbital_period_mean()

        for vessel in self.vessel_list:
            self.sc.active_vessel = vessel
            vessel.control.rcs = False

            if vessel.orbit.period < period_mean:
                self.manage_orientation(
                    self.mj.SmartASSAutopilotMode.prograde, 'prograde')
                operator_selection = operator.lt
            elif vessel.orbit.period >= period_mean:
                self.manage_orientation(
                    self.mj.SmartASSAutopilotMode.retrograde, 'retrograde')
                operator_selection = operator.gt

            # while abs(vessel.orbit.period - period_mean) > 0:
            while operator_selection(vessel.orbit.period, period_mean):
                vessel.control.rcs = True
                vessel.control.throttle = 0.05

            vessel.control.rcs = False
            vessel.control.throttle = 0

        print("Orbit after fine tuning: ")
        print(self.print_telemetry())

    def get_orbital_period_mean(self):
        """Get mean orbital period of all satellites in satellite list"""
        period_mean = sum(
            vessel.orbit.period for vessel in self.vessel_list) / len(self.vessel_list)
        return period_mean

    def manage_orientation(self, autopilot_mode, direction):

        self.mj.smart_ass.autopilot_mode = autopilot_mode
        self.mj.smart_ass.update(False)
        orientate_vessel(self.conn, self.sc.active_vessel,
                         direction, accuracy_cutoff=1e-3)

    def setup_df(self):
        """Setup pandas dataframe for telemetry"""

        data = [[v, v.name, v.orbit.body.name, v.orbit.eccentricity, v.orbit.semi_major_axis,
                 v.orbit.inclination, v.orbit.longitude_of_ascending_node, v.orbit.argument_of_periapsis, v.orbit.true_anomaly,
                 ] for v in self.vessel_list]



        df = pd.DataFrame(data, columns=[
            'vessel', 'name', 'body', 'eccentricity', 'semi_major_axis',
            'inclination', 'longitude_of_ascending_node', 'argument_of_periapsis', 'true_anomaly',
        ])
        df.set_index('vessel', inplace=True)
        # print(df)
        return df




    def print_telemetry(self):
        """ Prints telemetry data in a fancy table """
        df = self.setup_df()
        table = tabulate.tabulate(df, headers='keys', tablefmt='fancy_grid')
        print(table)


    def set_altitude_and_circularize(self, desired_inclination, desired_altitude):
        # inclination
        if abs(self.inclination() * (180 / math.pi) - desired_inclination) > 0.001:
            inclination_change = self.mj.maneuver_planner.operation_inclination
            # inclination_change.time_selector.time_reference = self.mj.TimeReference.apoapsis
            inclination_change.new_inclination = desired_inclination

            inclination_change.make_nodes()
            NodeManager().execute_node()

        # set apoapsis
        if self.apoapsis() < desired_altitude:
            altitude_change = self.mj.maneuver_planner.operation_apoapsis
            altitude_change.new_apoapsis = desired_altitude

            altitude_change.make_nodes()
            NodeManager().execute_node()

        # circularize
        if self.eccentricity() > 0.001:
            eccentricity_change = self.mj.maneuver_planner.operation_circularize
            eccentricity_change.time_selector.time_reference = self.mj.TimeReference.apoapsis

            eccentricity_change.make_nodes()
            NodeManager().execute_node()
