import math
import time
import krpc
from pkg_resources import get_importer
import utils.pid
from apscheduler.schedulers.background import BackgroundScheduler

from utils.handle_vessels import (
    manipulate_engines_by_name,
    )

# from utils.debug import print_parts
from utils.pid import PID

class LaunchIntoOrbit():
    def __init__(self, target_altitude, turn_start_altitude, turn_end_altitude, end_stage,inclination, roll, max_q, staging_options):
        # initilize vessel
        self.conn = krpc.connect(name='Launch into orbit')
        self.vessel = self.conn.space_center.active_vessel

         # ascent parameters
        self.roll = roll
        self.max_q = max_q
        self.target_altitude = target_altitude
        self.turn_start_altitude = turn_start_altitude
        self.turn_end_altitude = turn_end_altitude
        self.target_inclination = inclination
        self.node = None
        self.precision = 0.1

        self.fuels = ['LqdHydrogen', 'LiquidFuel']
        self.end_stage = end_stage
        self.staging_done_for_current_stage = False

        self.staging_options = staging_options

        # set up PID controllers
        self.thrust_controller = PID(P=.001, I=0.0001, D=0.01)
        self.thrust_controller.ClampI = self.max_q
        self.thrust_controller.setpoint(self.max_q)

        # telemetry
        self.ut = self.conn.add_stream(getattr, self.conn.space_center, 'ut')
        self.flight_mean_altitude = self.conn.add_stream(getattr, self.vessel.flight(self.vessel.orbit.body.non_rotating_reference_frame), 'mean_altitude')
        self.flight_dynamic_pressure = self.conn.add_stream(getattr, self.vessel.flight(self.vessel.orbit.body.non_rotating_reference_frame), 'dynamic_pressure')
        self.altitude = self.conn.add_stream(getattr, self.vessel.flight(), 'mean_altitude')
        self.apoapsis = self.conn.add_stream(getattr, self.vessel.orbit, 'apoapsis_altitude')
        self.periapsis = self.conn.add_stream(getattr, self.vessel.orbit, 'periapsis_altitude')
        self.eccentricity = self.conn.add_stream(getattr, self.vessel.orbit, 'eccentricity')
        self.inclination =self. conn.add_stream(getattr, self.vessel.orbit, 'inclination')


    def staging(self):
        current_stage = self.vessel.control.current_stage

        # staging special needs
        if not self.staging_done_for_current_stage and staging_options != None:
            for k,v in staging_options.items():
                if current_stage == k:
                    for k2,v2 in v.items():
                        manipulate_engines_by_name(self.vessel, k2, v2)
            self.staging_done_for_current_stage = True

        if self.end_stage < current_stage:
            resources = self.vessel.resources_in_decouple_stage(current_stage - 1, cumulative=False)

            # check for interstages by checking if there is any fuel in the next decouple stage
            interstage_check = [True if resources.amount(fuel_type) == 0 else False for fuel_type in self.fuels]
            if all(interstage_check):
                time.sleep(1)
                self.vessel.control.activate_next_stage()
                self.staging_done_for_current_stage = False


            for fuel_type in self.fuels:
                if resources.amount(fuel_type) < 1 and resources.max(fuel_type) > 0:
                    # print('Decoupling stage %d to stage %d to empty %s' % (current_stage, current_stage - 1, fuel_type))
                    self.vessel.control.activate_next_stage()
                    self.staging_done_for_current_stage = False

            
    def gravity_turn(self):
        # quadratic gravity turn_start_altitude
        frac = self.flight_mean_altitude() / self.turn_end_altitude
        self.vessel.auto_pilot.target_pitch = 90 - (-90 * frac * (frac - 2))
        # linit max q
        self.vessel.control.throttle = self.thrust_controller.update(self.flight_dynamic_pressure())

    
    def ascent(self):
        # set ut auto_pilot
        self.vessel.auto_pilot.engage()
        self.vessel.auto_pilot.target_roll = self.roll

        # logic for desired inclination to compass heading
        if self.target_inclination >= 0:
            self.vessel.auto_pilot.target_heading = 90 - self.target_inclination
        elif self.target_inclination < 0:
            self.vessel.auto_pilot.target_heading = -(self.target_inclination - 90) + 360


        # schedule 
        scheduler = BackgroundScheduler()
        scheduler.add_job(id='Autostaging', func=self.staging, trigger='interval', seconds=1)
        scheduler.add_job(id='Gravity turn', func=self.gravity_turn, trigger='interval', seconds=1)
        scheduler.start()


        # ascent loop  
        while self.apoapsis() < self.target_altitude * .98:
            pass


        # reschedule for more granular control
        scheduler.remove_job('Gravity turn')
        scheduler.add_job(id='Gravity turn', func=self.gravity_turn, trigger='interval', seconds=0.1)


        scheduler.remove_job('Gravity turn')

        self.vessel.control.throttle = 0.05

        # fine tune apoapsis
        # ToDo: implement fine tuning apoapsis function
        while self.apoapsis() < self.target_altitude:
            pass

        scheduler.remove_job('Autostaging')
        self.vessel.control.throttle = 0
       

        # while self.flight_mean_altitude() < self.vessel.orbit.body.atmosphere_depth:
            # pass
        # print('Leaving atmosphere the atmosphere ...')
        

        # stage until final stage
        # while self.vessel.control.current_stage > self.end_stage:
            # self.vessel.control.activate_next_stage()

        # node creation burn vector targeting
        self.node, burn_time = self.create_circularization_burn()
        reference_frame = self.vessel.orbit.body.reference_frame
        
        self.vessel.auto_pilot.reference_frame = reference_frame
        self.vessel.auto_pilot.engage()
        self.vessel.auto_pilot.target_direction = self.node.remaining_burn_vector(reference_frame)
        self.vessel.auto_pilot.wait()


        # warp 
        self.conn.space_center.warp_to(self.node.ut - (burn_time / 2.0) - 5)
        while self.node.time_to > (burn_time / 2.0):
            pass
        # self.vessel.auto_pilot.wait()

        
        # circularization burn
        while self.node.remaining_delta_v > self.precision:

            self.vessel.control.throttle = self.orbit_thrust_controller(self.node.remaining_delta_v)
            self.vessel.auto_pilot.target_direction = self.node.remaining_burn_vector(self.vessel.orbit.body.reference_frame)


        # cleanup
        self.vessel.auto_pilot.disengage()
        self.vessel.control.throttle = 0
        self.node.remove()


    def orbit_thrust_controller(self, remaining_delta_v):
        twr = self.vessel.max_thrust / self.vessel.mass
        if remaining_delta_v < twr / 3:
            return 0.05
        elif remaining_delta_v < twr / 2:
            return 0.1
        elif remaining_delta_v < twr:
            return 0.25
        else:
            return 1


    def create_circularization_burn(self):
        # Plan circularization burn (using vis-viva equation)
        print('Planning circularization burn')
        mu = self.vessel.orbit.body.gravitational_parameter
        r = self.vessel.orbit.apoapsis
        a1 = self.vessel.orbit.semi_major_axis
        a2 = r
        v1 = math.sqrt(mu*((2./r)-(1./a1)))
        v2 = math.sqrt(mu*((2./r)-(1./a2)))
        delta_v = v2 - v1
        self.node = self.vessel.control.add_node(
            self.ut() + self.vessel.orbit.time_to_apoapsis, prograde=delta_v)

        # Calculate burn time (using rocket equation)
        F = self.vessel.available_thrust
        Isp = self.vessel.specific_impulse * self.vessel.orbit.body.surface_gravity
        m0 = self.vessel.mass
        m1 = m0 / math.exp(delta_v/Isp)
        flow_rate = F / Isp
        burn_time = (m0 - m1) / flow_rate

        return self.node, burn_time

# launch parameters
target_altitude = 120000
turn_start_altitude = 2500
turn_end_altitude = 80000
inclination = 0
roll = 90
max_q = 20000
end_stage = 6
staging_options = None
# staging_options = {
                   # 5: {'cryoengine-erebus-1': {'active': True, 'gimbal_limit': 0.2, 'thrust_limit': .5}},

                   # 6: {'cryoengine-erebus-1': {'active': True, 'gimbal_limit': 0.4, 'thrust_limit': 1.0}},
 
                   # }
# staging_options = {8: {'cryoengine-erebus-1': {'active': True, 'gimbal_limit': 0.2, 'thrust_limit': .6},
                       # 'cryoengine-vesuvius-1': {'active': True, 'gimbal_limit': 0.2, 'thrust_limit': 1.0}},

                   # 7: {'cryoengine-erebus-1': {'active': True, 'gimbal_limit': 0.3, 'thrust_limit': 1.0}},
                 # }
print(staging_options)
# Go for launch!
launch = LaunchIntoOrbit(target_altitude,
                        turn_start_altitude,
                        turn_end_altitude,
                        end_stage,
                        inclination,
                        roll,
                        max_q,
                        staging_options)

try:
    launch.ascent()
finally:
    launch.conn.close()
    print("Connection closed")







# fps sucking monstes below
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




