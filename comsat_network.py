import time
import krpc
import numpy as np
import pandas as pd

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

        
        self.mj = self.conn.mech_jeb

        # Telemetry
        self.ut = self.conn.add_stream(getattr, self.conn.space_center, 'ut')
        self.altitude = self.conn.add_stream(getattr, self.vessel.flight(), 'mean_altitude')
        self.apoapsis = self.conn.add_stream(getattr, self.vessel.orbit, 'apoapsis_altitude')
        self.periapsis = self.conn.add_stream(getattr, self.vessel.orbit, 'periapsis_altitude')
        self.eccentricity = self.conn.add_stream(getattr, self.vessel.orbit, 'eccentricity')
        self.inclination =self. conn.add_stream(getattr, self.vessel.orbit, 'inclination')



    def prepare(self):
        
        auto_pilot = self.vessel.auto_pilot

        auto_pilot.engage()
        # auto_pilot.target_roll = -90
        # auto_pilot.wait()
        auto_pilot.target_pitch_and_heading(0, 90)
        auto_pilot.wait()
        # auto_pilot.wait()
        # auto_pilot.disengage()

    def sats(self):
        ## orbit check blabla
        self.release_satellite()
        
        executor = self.mj.node_executor

            
        res_orbit = self.mj.maneuver_planner.operation_resonant_orbit
        res_orbit.resonance_numerator = 4
        res_orbit.resonance_denominator = 3

        res_orbit.make_node()
        executor.execute_one_node()

        with self.conn.stream(getattr, executor, 'enabled') as enabled:
            enabled.rate = 1
            with enabled.condition.wait():
                enabled.wait()



        recirc = self.mj.maneuver_planner.operation_circularize
        recirc.time_selector.time_reference = self.mj.TimeReference.periapsis
        recirc.make_node()

        with self.conn.stream(getattr, executor, 'enabled') as enabled:
            enabled.rate = 1
            with enabled.condition:
                while enabled():
                    enabled.wait()


    def release_satellite(self):
        self.vessel.control.activate_next_stage()


nw = ComSat_Network()
nw.prepare()
nw.sats()






# trash below

# #control block
# control = vessel.control
# control.sas = True
# control.sas_mode = sc.SASMode.prograde

# orientation = 'prograde'
# vessel = orientate_vessel(conn, vessel, orientation)

# #staging
# activated_engines = manipulate_engines_by_name(vessel, 'orbital-engine-0625')
# # decouple_by_name(vessel, 'proceduralStackDecoupler')

# # wait for satellites to spread apart
# time.sleep(10)

# # triple constellation stuff
# constellation_name = 'TripleOs'
# constellation_list = control.activate_next_stage()
# constellation_list.append(vessel)

# for i, vessel in enumerate(constellation_list):
    # vessel.name = constellation_name + '_' + str(i)
    # # sc.active_vessel = switch_vessel(sc.active_vessel, vessel)


# # satellite operations
# # result = [orientate_vessel(conn, vessel, 'retrograde', block=False) for vessel in constellation_list]

# #solar 
# # solar = [v.parts.solar_panels for v in constellation_list]
# # solar = [item for sublist in solar for item in sublist]
# # for panel in solar:
    # # panel.deployed = True


# # mechanical jebediah time <3

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
