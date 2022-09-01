import time
import krpc
import numpy as np
import pandas as pd
import tabulate

import matplotlib.pyplot as plt
from utils.handle_orientation import orientate_vessel
from utils.handle_vessels import (
    manipulate_engines_by_name,
    decouple_by_name,
    select_vessel_and_duplicates_by_name,
    switch_vessel,
)

class ComSat_Network():
    def __init__(self):
        self.conn = krpc.connect(name="ComSat_Network")
        print("Connected to kRPC")

        self.sc = self.conn.space_center
        self.vessel = self.sc.active_vessel
        self.vessel_name = self.vessel.name
        self.auto_pilot = self.vessel.auto_pilot

        self.satellite_list = []
        
        self.mj = self.conn.mech_jeb

        # Telemetry
        self.ut = self.conn.add_stream(getattr, self.conn.space_center, 'ut')
        self.altitude = self.conn.add_stream(getattr, self.vessel.flight(), 'mean_altitude')
        self.apoapsis = self.conn.add_stream(getattr, self.vessel.orbit, 'apoapsis_altitude')
        self.periapsis = self.conn.add_stream(getattr, self.vessel.orbit, 'periapsis_altitude')
        self.eccentricity = self.conn.add_stream(getattr, self.vessel.orbit, 'eccentricity')
        self.inclination =self. conn.add_stream(getattr, self.vessel.orbit, 'inclination')


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

    def sats(self):
        # fix this, just jump resonant orbit start position before releasing
        self.resonant_orbit()
        self.recircularize()
        # end bullshit

        self.release_satellite()

        self.resonant_orbit()
        self.recircularize()
        self.release_satellite()

        self.resonant_orbit()
        self.recircularize()
        self.release_satellite()

       
    def release_satellite(self):

        print('Deploying ComSat')
        
        self.mj.smart_ass.autopilot_mode = self.mj.SmartASSAutopilotMode.normal_minus
        self.mj.smart_ass.update(False)
        time.sleep(15)

        released_satellite = self.vessel.control.activate_next_stage()
        self.satellite_list.append(released_satellite)
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


    def preexisting_network(self, constellation_name):
        self.satellite_list = []
        for vessel in self.conn.space_center.vessels:
            if vessel.name == constellation_name:
                self.satellite_list.append(vessel)
        print(f'{len(self.satellite_list)} preexisting satellites found with name {constellation_name}')
        self.get_telemetry()


    def get_comm_status(self):
        for vessel in self.satellite_list:
            print(vessel.name)
            
            table = tabulate.tabulate([[i,antenna.target]
                                              for i, antenna in enumerate(self.conn.remote_tech.comms(vessel).antennas)],
                                              headers=['Index,', 'Target'],
                                              tablefmt='fancy_grid')
            print(table)


network = ComSat_Network()
# network.sats()
network.preexisting_network(constellation_name='Comsat_0.4_RingZero')
# network.fine_tune_orbital_period()

# network.setup_communications()
network.get_antennas()

network.get_comm_status()











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
