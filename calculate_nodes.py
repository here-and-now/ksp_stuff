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

debug = True
if debug:
    print_parts('all')
    print_parts('engines')
    print_parts('resources')


# Set up streams for telemetry

# Constants
mu = vessel.orbit.body.gravitational_parameter

# Time
ut = conn.add_stream(getattr, conn.space_center, 'ut')
# Orbital parameters
a1 = vessel.orbit.apoapsis
p1 = vessel.orbit.periapsis
r1 = vessel.orbit.radius
sma1 = vessel.orbit.semi_major_axis
v1 = vessel.orbit.velocity

# Target orbit
a2 = 165820
p2 = a2

v2 = math.sqrt(mu*(2./)



#Vessel
F = vessel.available_thrust

# Plan circularization burn (using vis-viva equation)
print('Planning circularization burn')

r = vessel.orbit.apoapsis
a1 = vessel.orbit.semi_major_axis
a2 = r
v1 = math.sqrt(mu*((2./r)-(1./a1)))
v2 = math.sqrt(mu*((2./r)-(1./a2)))
delta_v = v2 - v1
node = vessel.control.add_node(
    ut() + vessel.orbit.time_to_apoapsis, prograde=delta_v)

# Calculate burn time (using rocket equation)
F = vessel.available_thrust
Isp = vessel.specific_impulse * 9.82
m0 = vessel.mass
m1 = m0 / math.exp(delta_v/Isp)
flow_rate = F / Isp
burn_time = (m0 - m1) / flow_rate



