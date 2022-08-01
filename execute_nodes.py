import math
import time
import krpc

from utils.handle_vessels import (
    manipulate_engines_by_name,
    )

from utils.debug import print_parts

conn = krpc.connect(name='Execute nodes')
vessel = conn.space_center.active_vessel

debug = True
if debug:
    print_parts('all')
    print_parts('engines')
    print_parts('resources')

# Set up streams for telemetry
ut = conn.add_stream(getattr, conn.space_center, 'ut')
altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
thrust = conn.add_stream(getattr, vessel, 'thrust')
mass = conn.add_stream(getattr, vessel, 'mass')

surface_gravity = vessel.orbit.body.surface_gravity



# Pre-launch setup
vessel.control.sas = False
vessel.control.rcs = False
vessel.control.throttle = 1

# # Activate the first stage
# vessel.control.activate_next_stage()
# vessel.auto_pilot.engage()
# vessel.auto_pilot.target_pitch_and_heading(90, 90)


# #ToDo: make this an expression?
# twr = thrust() / (mass() * surface_gravity)

# # set TWR limit by altitude and set TWR accordingly
# inrement = 0.001
# twr_limit = 1.6 if altitude() < 15000 else (1.8 if altitude() > 15000 else 2)
# vessel.control.throttle = vessel.control.throttle + inrement \
                            # if twr < twr_limit \
                            # else vessel.control.throttle - inrement




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
