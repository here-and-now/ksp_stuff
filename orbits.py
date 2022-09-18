import math
import time

import krpc
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tabulate
import operator


from nodes import NodeManager
# from vessels import VesselManager


from utils.handle_orientation import orientate_vessel
from utils.handle_vessels import (
    decouple_by_name,
    manipulate_engines_by_name,
    select_vessel_and_duplicates_by_name,
    switch_vessel,
)


class OrbitManager():
    def __init__(self, df=None, instance_name='OrbitManager'):
        self.conn = krpc.connect(name=instance_name)
        self.sc = self.conn.space_center
        self.mj = self.conn.mech_jeb
        print(f"OrbitManager: {instance_name} connected.")

        # Telemetry
        self.ut = self.conn.add_stream(getattr, self.conn.space_center, 'ut')

        # Dataframe 
        self.df = df
        self.orbital_telemetry_dataframe()

    def orbital_telemetry_dataframe(self):
        """ Returns orbital telemetry data in a dataframe """
        # streaming approach, probably inconvenient
        df = pd.DataFrame([{
            'vessel': v,
            'name': v.name,
            'body': self.conn.add_stream(getattr, v.orbit.body, 'name'),
            'eccentricity': self.conn.add_stream(getattr, v.orbit, 'eccentricity'),
            'semi_major_axis': self.conn.add_stream(getattr, v.orbit, 'semi_major_axis'),
            'inclination': self.conn.add_stream(getattr, v.orbit, 'inclination'),
            'longitude_of_ascending_node': self.conn.add_stream(getattr, v.orbit, 'longitude_of_ascending_node'),
            # 'argument_of_periapsis': self.conn.add_stream(getattr, v.orbit, 'argument_of_periapsis'),
            # # 'true_anomaly': self.conn.add_stream(getattr, v.orbit, 'true_anomaly'),
        }
            for v in self.df.index.values])

        df = df.set_index('vessel')
        self.df = pd.merge(self.df, df, how='left', left_index=True)
        print(self.df)
        # call streams in dataframe
        self.df = self.df.apply(lambda x: x.apply(
            lambda y: y() if callable(y) else y))
        # end streaming approach

        return self.df

    def print_orbit_data(self):
        table=tabulate.tabulate(self.df, headers='keys', tablefmt='fancy_grid')
        print(table)

    def fine_tune_orbital_period(self):
        """
        Fine tune orbital period for each satelitte in satellite list
        to the mean orbital period with RCS thrusters
        """
        print("Fine tuning orbital period ...")
        print("Orbit before fine tuning: ")
        print(self.print_telemetry())

        period_mean=self.get_orbital_period_mean()

        for vessel in self.vessel_list:
            self.sc.active_vessel=vessel
            vessel.control.rcs=False

            if vessel.orbit.period < period_mean:
                self.manage_orientation(
                    self.mj.SmartASSAutopilotMode.prograde, 'prograde')
                operator_selection=operator.lt
            elif vessel.orbit.period >= period_mean:
                self.manage_orientation(
                    self.mj.SmartASSAutopilotMode.retrograde, 'retrograde')
                operator_selection=operator.gt

            # while abs(vessel.orbit.period - period_mean) > 0:
            while operator_selection(vessel.orbit.period, period_mean):
                vessel.control.rcs=True
                vessel.control.throttle=0.05

            vessel.control.rcs=False
            vessel.control.throttle=0

        print("Orbit after fine tuning: ")
        print(self.print_telemetry())

    def get_orbital_period_mean(self):
        """Get mean orbital period of all satellites in satellite list"""
        period_mean=sum(
            vessel.orbit.period for vessel in self.vessel_list) / len(self.vessel_list)
        return period_mean

    def manage_orientation(self, autopilot_mode, direction):

        self.mj.smart_ass.autopilot_mode = autopilot_mode
        self.mj.smart_ass.update(False)
        orientate_vessel(self.conn, self.sc.active_vessel,
                         direction, accuracy_cutoff=1e-3)

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

class Orbit():
    def __init__(self, vessel):
        self.conn = krpc.connect(name=f'Orbit: {vessel.name}')
        self.sc = self.conn.space_center
        self.vessel = vessel

        # keplerian elements
        self.eccentricity = self.conn.add_stream(
            getattr, self.vessel.orbit, 'eccentricity')
        self.inclination = self.conn.add_stream(
            getattr, self.vessel.orbit, 'inclination')
        self.semi_major_axis = self.conn.add_stream(
            getattr, self.vessel.orbit, 'semi_major_axis')
        self.longitude_of_ascending_node = self.conn.add_stream(
            getattr, self.vessel.orbit, 'longitude_of_ascending_node')
        self.argument_of_periapsis = self.conn.add_stream(
            getattr, self.vessel.orbit, 'argument_of_periapsis')
        self.true_anomaly = self.conn.add_stream(
            getattr, self.vessel.orbit, 'true_anomaly')

        self.df = self.setup_orbit_df()
    
    def setup_orbit_df(self):
        df = pd.DataFrame([{
            'vessel': self.vessel,
            # 'name': self.vessel.name,
            'eccentricity': self.eccentricity,
            'inclination': self.inclination,
            'semi_major_axis': self.semi_major_axis,
            'longitude_of_ascending_node': self.longitude_of_ascending_node,
            'argument_of_periapsis': self.argument_of_periapsis,
            'true_anomaly': self.true_anomaly,
        }])
        df = df.set_index('vessel')
        return df 
