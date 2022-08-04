import math
import time
import krpc
import utils.pid

from utils.handle_vessels import (
    manipulate_engines_by_name,
    )

from utils.debug import print_parts
from utils.pid import PID

class LaunchIntoOrbit():
    def __init__(self, target_altitude, turn_start_altitude, turn_end_altitude,inclination, roll, max_q):
        self.conn = krpc.connect(name='Launch into orbit')
        self.vessel = self.conn.space_center.active_vessel

        self.target_altitude = target_altitude
        self.turn_start_altitude = turn_start_altitude
        self.turn_end_altitude = turn_end_altitude
        self.target_inclination = inclination

        self.max_q = max_q
        self.roll = roll

        self.ut = self.conn.add_stream(getattr, self.conn.space_center, 'ut')
        self.altitude = self.conn.add_stream(getattr, self.vessel.flight(), 'mean_altitude')
        self.apoapsis = self.conn.add_stream(getattr, self.vessel.orbit, 'apoapsis_altitude')
        self.periapsis = self.conn.add_stream(getattr, self.vessel.orbit, 'periapsis_altitude')
        self.eccentricity = self.conn.add_stream(getattr, self.vessel.orbit, 'eccentricity')
        self.inclination =self. conn.add_stream(getattr, self.vessel.orbit, 'inclination')
        
    def ascent(self):
        # set up PID controllers
        thrust_controller = PID(P=.001, I=0.0001, D=0.01)
        thrust_controller.ClampI = self.max_q
        thrust_controller.setpoint(self.max_q)

        # set ut auto_pilot
        self.vessel.auto_pilot.engage()
        self.vessel.auto_pilot.target_roll = self.roll

        # logic for desired inclination to compass heading
        if self.target_inclination >= 0:
            self.vessel.auto_pilot.target_heading = 90 - self.target_inclination

        elif self.target_inclination < 0:
            self.vessel.auto_pilot.target_heading = -(self.target_inclination - 90) + 360
            
        while self.apoapsis() < self.target_altitude * .95:
            # quadratic gravity turn_start_altitude
            flight = self.vessel.flight(self.vessel.orbit.body.non_rotating_reference_frame)
            frac = flight.mean_altitude / self.turn_end_altitude
            self.vessel.auto_pilot.target_pitch = 90 - (-90 * frac * (frac - 2))

            # linit max q
            self.vessel.control.throttle = thrust_controller.update(flight.dynamic_pressure)

            print('Altitude: %.2f' % self.altitude())
            print('throttle: %.2f' % self.vessel.control.throttle)


target_altitude = 100000
turn_start_altitude = 2500
turn_end_altitude = 60000
inclination = 0
roll = 90
max_q = 10000

launch = LaunchIntoOrbit(target_altitude, turn_start_altitude, turn_end_altitude,inclination, roll, max_q)
launch.ascent()




# monsters below
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



