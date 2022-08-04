import math
import time
import krpc

from utils.handle_vessels import (
    manipulate_engines_by_name,
    )

from utils.debug import print_parts

turn_start_altitude = 2500
turn_end_altitude = 50000
target_altitude = 150000

conn = krpc.connect(name='Launch into orbit')
vessel = conn.space_center.active_vessel
mj = conn.mech_jeb

class LaunchIntoOrbit():
    def __init__(self, target_altitude, turn_start_altitude, turn_end_altitude,inclination, roll):
        self.target_altitude = target_altitude
        self.turn_start_altitude = turn_start_altitude
        self.turn_end_altitude = turn_end_altitude
        self.inclination = inclination

        self.roll = roll

        self.vessel = conn.space_center.active_vessel

        self.ut = conn.add_stream(getattr, conn.space_center, 'ut')
        self.altitude = conn.add_stream(getattr, self.vessel.flight(), 'mean_altitude')
        self.apoapsis = conn.add_stream(getattr, self.vessel.orbit, 'apoapsis_altitude')
        self.periapsis = conn.add_stream(getattr, self.vessel.orbit, 'periapsis_altitude')
        self.eccentricity = conn.add_stream(getattr, self.vessel.orbit, 'eccentricity')
        self.speed = conn.add_stream(getattr, self.vessel.flight(), 'speed')
        self.apoapsis_speed = conn.add_stream(getattr, self.vessel.orbit, 'apoapsis_speed')
        self.periapsis_speed = conn.add_stream(getattr, self.vessel.orbit, 'periapsis_speed')
        self.mean_speed = conn.add_stream(getattr, self.vessel.orbit, 'speed_at_periapsis')
        self.mean_altitude = conn.add_stream(getattr, self.vessel.orbit, 'mean_altitude')
        self.mean_inclination = conn.add_stream(getattr, self.vessel.orbit, 'inclination')
        
                 
                 


# debug = False
# if debug:
    # print_parts('all')
    # print_parts('engines')
    # print_parts('resources')

# main_stage = 5
# main_seperated = False
# main_fuel_type = 'LqdHydrogen'
# manipulate_engines_by_name(vessel, 'cryoengine-erebus-1', {'active': True,
                                                           # 'thrust_limit': 0.3,
                                                           # 'gimbal_limit': 1,
                                                           # })
# # Booster stage settings
# booster_stage = 6
# booster_separated = False
# booster_fuel_type='LqdHydrogen'

# #boster and main stage setup
# main_seperation = vessel.resources_in_decouple_stage(stage=main_stage, cumulative=False)
# booster_seperation = vessel.resources_in_decouple_stage(stage=booster_stage, cumulative=False)

# main_fuel = conn.add_stream(main_seperation.amount, main_fuel_type)
# booster_fuel = conn.add_stream(booster_seperation.amount, booster_fuel_type)

# # Pre-launch setup
# vessel.control.sas = False
# vessel.control.rcs = False
# vessel.control.throttle = 1

# # Activate the first stage
# vessel.control.activate_next_stage()
# vessel.auto_pilot.engage()

# pitch = 90
# heading = 90 #0 is north, 90 is east, 180 is south, 270 is west
# vessel.auto_pilot.target_pitch_and_heading(pitch, heading)

# # Main ascent loop
# turn_angle = 0
# while True:
    # #ToDo: make this an expression?
    # twr = thrust() / (mass() * surface_gravity)


# # Plan circularization burn (using vis-viva equation)
# print('Planning circularization burn')
# mu = vessel.orbit.body.gravitational_parameter
# r = vessel.orbit.apoapsis
# a1 = vessel.orbit.semi_major_axis
# a2 = r
# v1 = math.sqrt(mu*((2./r)-(1./a1)))
# v2 = math.sqrt(mu*((2./r)-(1./a2)))
# delta_v = v2 - v1
# node = vessel.control.add_node(
    # ut() + vessel.orbit.time_to_apoapsis, prograde=delta_v)

# # Calculate burn time (using rocket equation)
# F = vessel.available_thrust
# Isp = vessel.specific_impulse * 9.82
# m0 = vessel.mass
# m1 = m0 / math.exp(delta_v/Isp)
# flow_rate = F / Isp
# burn_time = (m0 - m1) / flow_rate



