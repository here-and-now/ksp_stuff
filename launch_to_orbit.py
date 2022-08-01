import math
import time
import krpc

from utils.handle_vessels import (
    manipulate_engines_by_name,
    )

turn_start_altitude = 2500
turn_end_altitude = 50000
target_altitude = 150000

conn = krpc.connect(name='Launch into orbit')
vessel = conn.space_center.active_vessel

# Set up streams for telemetry
ut = conn.add_stream(getattr, conn.space_center, 'ut')
altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
thrust = conn.add_stream(getattr, vessel, 'thrust')
mass = conn.add_stream(getattr, vessel, 'mass')

surface_gravity = vessel.orbit.body.surface_gravity


# Decoupling stages
main_stage = 4
main_fuel_type = 'LqdHydrogen'
booster_stage = 5
booster_fuel_type='LqdHydrogen'

main_seperation = vessel.resources_in_decouple_stage(stage=main_stage, cumulative=False)
main_fuel = conn.add_stream(main_seperation.amount, main_fuel_type)

booster_seperation = vessel.resources_in_decouple_stage(stage=booster_stage, cumulative=False)
booster_fuel = conn.add_stream(booster_seperation.amount, booster_fuel_type)

# Pre-launch setup
vessel.control.sas = False
vessel.control.rcs = False
vessel.control.throttle = 1


# Activate the first stage
vessel.control.activate_next_stage()
vessel.auto_pilot.engage()
vessel.auto_pilot.target_pitch_and_heading(90, 90)

# Main ascent loop
main_seperated = False
booster_separated = False
turn_angle = 0
while True:

    #ToDo: make this an expression?
    twr = thrust() / (mass() * surface_gravity)

    # set TWR limit by altitude and set TWR accordingly
    inrement = 0.005
    twr_limit = 1.6 if altitude() < 15000 else (1.8 if altitude() > 15000 else 2)
    vessel.control.throttle = vessel.control.throttle + inrement \
                                if twr < twr_limit \
                                else vessel.control.throttle - inrement
    print(twr)
    
    # Gravity turn
    if altitude() > turn_start_altitude and altitude() < turn_end_altitude:
        frac = ((altitude() - turn_start_altitude) /
                (turn_end_altitude - turn_start_altitude))
        new_turn_angle = frac * 90
        if abs(new_turn_angle - turn_angle) > 0.5:
            turn_angle = new_turn_angle
            vessel.auto_pilot.target_pitch_and_heading(90-turn_angle, 90)
    
    if not main_seperated:
        if main_fuel() < 0.1:
            vessel.control.activate_next_stage()
            time.sleep(2)
            vessel.control.activate_next_stage()
            main_seperated = True
            print('Stage separated')

    if not booster_separated:
        if booster_fuel() < 0.1:
            vessel.control.activate_next_stage()
            booster_separated = True
            print('Booster separated')

        pass
    # Decrease throttle when approaching target apoapsis
    if apoapsis() > target_altitude*0.9:
        print('Approaching target apoapsis')
        break

# Disable engines when target apoapsis is reached
vessel.control.throttle = 0.25
while apoapsis() < target_altitude:
    pass
print('Target apoapsis reached')
vessel.control.throttle = 0.0

# Wait until out of atmosphere
print('Coasting out of atmosphere')
while altitude() < 70500:
    pass


# Plan circularization burn (using vis-viva equation)
print('Planning circularization burn')
mu = vessel.orbit.body.gravitational_parameter
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
