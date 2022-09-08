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

    
    def desired_orbit(self, desired_inclination, desired_altitude):

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
            eccentricity_change = self.mj.maneuver_planner.operation_ellipticize
            eccentricity_change.new_periapsis= 10e5
            eccentricity_change.new_apoapsis= 10e5
            eccentricity_change.make_nodes()

            self.execute_nodes()

        # if self.apoapsis() < desired_altitude:
            # altitude_change = self.mj.maneuver_planner.operation_apoapsis
            # altitude_change.new_apoapsis = desired_altitude
            # altitude_change.make_nodes()

            # self.execute_nodes()
        # if self.periapsis() < desired_altitude:
            # altitude_change = self.mj.maneuver_planner.operation_periapsis
            # altitude_change.new_periapsis = desired_altitude
            # altitude_change.make_nodes()

            # self.execute_nodes()



network = ComSat_Network()
desired_orbit(desired_inclination=90, desired_altitude=10e5)
# network.sats()
# network.preexisting_network(constellation_name='Comsat_0.4_RingZero')
# network.fine_tune_orbital_period()

# network.setup_communications()
# network.get_antennas()
# network.get_comm_status()











# orbital period mean of constellation_list





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
