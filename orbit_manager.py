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

class OrbitManager():
    def __init__(self):
        self.conn = krpc.connect(name="OrbitManager")
        print("OrbitManager connected to kRPC server")

        self.sc = self.conn.space_center
        self.vessel = self.sc.active_vessel
        self.vessel_name = self.vessel.name
        self.satellite_list = []
        self.period_mean = None

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

    def fine_tune_orbital_period(self):

        self.get_telemetry()
        accuracy_cutoff = 1e-3

        for vessel in self.satellite_list:
            self.sc.active_vessel = vessel
            vessel.control.rcs = False
            
            if vessel.orbit.period < self.period_mean:
                self.mj.smart_ass.autopilot_mode = self.mj.SmartASSAutopilotMode.prograde
                self.mj.smart_ass.update(False)
                orientate_vessel(self.conn, self.sc.active_vessel, 'prograde', accuracy_cutoff=accuracy_cutoff)
                while vessel.orbit.period < self.period_mean:
                    vessel.control.rcs = True
                    vessel.control.throttle = 0.05
            
            elif vessel.orbit.period > self.period_mean:
                self.mj.smart_ass.autopilot_mode = self.mj.SmartASSAutopilotMode.retrograde
                self.mj.smart_ass.update(False)
                orientate_vessel(self.conn, self.sc.active_vessel, 'retrograde', accuracy_cutoff=accuracy_cutoff)
                while vessel.orbit.period > self.period_mean:
                    vessel.control.rcs = True
                    vessel.control.throttle = 0.05
           
            vessel.control.rcs = False
            vessel.control.throttle = 0

        self.get_telemetry()

    def get_telemetry(self):

        if self.satellite_list:
            self.period_mean = sum(vessel.orbit.period for vessel in self.satellite_list) / len(self.satellite_list)
            print(f'Average period is {self.period_mean}')

            table = tabulate.tabulate([[i, v.name, v.orbit.body.name,
                                        v.orbit.apoapsis_altitude, v.orbit.periapsis_altitude,
                                        v.orbit.inclination, v.orbit.period,
                                        (v.orbit.period - self.period_mean)]
                                      for i, v in enumerate(self.satellite_list)],
                                      headers=['Index', 'Name', 'Body',
                                          'Apoapsis', 'Periapsis',
                                          'Inclination', 'Period',
                                          'Period deviation from mean'],
                                      tablefmt='fancy_grid')
            print(table)

    
    def set_altitude_and_circularize(self, desired_inclination, desired_altitude):

        if abs(self.inclination() * (180 / math.pi)  - desired_inclination) > 0.001:
            inclination_change = self.mj.maneuver_planner.operation_inclination
            # inclination_change.time_selector.time_reference = self.mj.TimeReference.apoapsis
            inclination_change.new_inclination = desired_inclination
            inclination_change.make_nodes()

            self.execute_nodes()

        if self.apoapsis() < desired_altitude:
            altitude_change = self.mj.maneuver_planner.operation_apoapsis
            altitude_change.new_apoapsis= desired_altitude
            altitude_change.make_nodes()

            self.execute_nodes()

        if self.eccentricity() > 0.001:
            eccentricity_change = self.mj.maneuver_planner.operation_circularize
            eccentricity_change.time_selector.time_reference = self.mj.TimeReference.apoapsis
            eccentricity_change.make_nodes()

            self.execute_nodes()

            # self.execute_nodes()
