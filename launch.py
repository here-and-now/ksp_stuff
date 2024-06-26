import math
import time
import krpc
from pkg_resources import get_importer
import utils.pid
import pandas as pd

from orbits import OrbitManager
from nodes import NodeManager

from apscheduler.schedulers.background import BackgroundScheduler

from utils.handle_vessels import (
    manipulate_engines_by_name,
)

# from utils.debug import print_parts
from utils.pid import PID


class LaunchManager():
    def __init__(self,
             target_altitude=150000,
             turn_start_altitude=2500,
             turn_end_altitude=120000,
             end_stage=8,
             inclination=0,
             roll=90,
             max_q=20000,
             staging_options=None):

        # initilize vessel
        self.conn = krpc.connect(name='LaunchManager')

        self.mj = self.conn.mech_jeb
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

        self.solar_deployed = False
        self.fairings_jettisoned = False
        self.launch_finished = False

        # set up PID controllers
        self.thrust_controller = PID(P=.001, I=0.0001, D=0.01)
        self.thrust_controller.ClampI = self.max_q
        self.thrust_controller.setpoint(self.max_q)

        # telemetry
        self.ut = self.conn.add_stream(getattr, self.conn.space_center, 'ut')
        self.met = self.conn.add_stream(getattr, self.vessel, 'met')

        self.flight_mean_altitude = self.conn.add_stream(getattr, self.vessel.flight(
            self.vessel.orbit.body.non_rotating_reference_frame), 'mean_altitude')
        self.flight_dynamic_pressure = self.conn.add_stream(getattr, self.vessel.flight(
            self.vessel.orbit.body.non_rotating_reference_frame), 'dynamic_pressure')
        # self.vessel = self.conn.add_stream(getattr, self.conn.space_center, 'active_vessel')

        # self.altitude = self.conn.add_stream(
            # getattr, self.vessel.flight(), 'mean_altitude')
        self.apoapsis = self.conn.add_stream(
            getattr, self.vessel.orbit, 'apoapsis_altitude')
        self.periapsis = self.conn.add_stream(
            getattr, self.vessel.orbit, 'periapsis_altitude')
        self.eccentricity = self.conn.add_stream(
            getattr, self.vessel.orbit, 'eccentricity')
        self.inclination = self. conn.add_stream(
            getattr, self.vessel.orbit, 'inclination')


        self.scheduler = BackgroundScheduler()
        self.df = self.setup_launch_df()


    def setup_launch_df(self):
        df = pd.DataFrame([{
            'met': self.met(),
            'flight_mean_altitude': self.flight_mean_altitude(),
        }])
        return df

    def concat_launch_data(self):
        ''' concat launch data to a pandas dataframe '''
        self.df = pd.concat([self.df, pd.DataFrame([{
            'met': self.met(),
            'flight_mean_altitude': self.flight_mean_altitude(),
            'flight_dynamic_pressure': self.flight_dynamic_pressure(),
        }])])



    def staging(self):
        current_stage = self.vessel.control.current_stage
        go_to_next_stage = False

        # staging special needs
        if not self.staging_done_for_current_stage and self.staging_options != None:
            for k, v in self.staging_options.items():
                if current_stage == k:
                    for k2, v2 in v.items():
                        manipulate_engines_by_name(self.vessel, k2, v2)
            self.staging_done_for_current_stage = True

        if self.end_stage < current_stage:
            resources = self.vessel.resources_in_decouple_stage(
                current_stage - 1, cumulative=False)

            # check for interstages by checking if there is any fuel in the next decouple stage
            interstage_check = [True if resources.amount(
                fuel_type) == 0 else False for fuel_type in self.fuels]

            if all(interstage_check):
                print('Interstage detected')
                go_to_next_stage = True

            for fuel_type in self.fuels:
                if resources.amount(fuel_type) < 1 and resources.max(fuel_type) > 0:
                    print(f'Stage {current_stage} fuel type {fuel_type} empty')
                    go_to_next_stage = True

            if go_to_next_stage:
                self.vessel.control.activate_next_stage()
                print(f'Staging done - current stage: {current_stage}')
                self.staging_done_for_current_stage = False

        # Fairings and solar panel deployment
        if not self.solar_deployed and not self.fairings_jettisoned and self.flight_mean_altitude() > self.vessel.orbit.body.atmosphere_depth:
            self.fairing_deployment()
            time.sleep(2)
            self.solar_deployment()

    def solar_deployment(self):
        for s in self.vessel.parts.solar_panels:
            s.deployed = True
        self.solar_deployed = True
        print(f'Solar panels deployed at t+{self.met():.1f}')

    def fairing_deployment(self):
        event_name = 'Jettison Fairing'
        for f in self.vessel.parts.fairings:
            for m in f.part.modules:
                if m.has_event(event_name):
                    m.trigger_event(event_name)
        self.fairings_jettisoned = True
        print(f'Fairings jettisoned')

    def gravity_turn(self):
        # quadratic gravity turn_start_altitude
        print('Mean Altitude', self.flight_mean_altitude())
        frac = self.flight_mean_altitude() / self.turn_end_altitude
        self.vessel.auto_pilot.target_pitch = 90 - (-90 * frac * (frac - 2))
        # linit max q
        self.vessel.control.throttle = self.thrust_controller.update(
            self.flight_dynamic_pressure())

    def ascent(self):
        try:
            # set up auto_pilot
            self.vessel.auto_pilot.engage()
            self.vessel.auto_pilot.target_roll = self.roll

            # logic for desired inclination to compass heading
            if self.target_inclination >= 0:
                self.vessel.auto_pilot.target_heading = 90 - self.target_inclination
            elif self.target_inclination < 0:
                self.vessel.auto_pilot.target_heading = - \
                    (self.target_inclination - 90) + 360

            # schedule
            self.scheduler.add_job(id='autostaging', func=self.staging,
                              trigger='interval', seconds=2)
            self.scheduler.add_job(
                id='gravity_turn', func=self.gravity_turn, trigger='interval', seconds=1)
            self.scheduler.start()


            # while self.flight_mean_altitude() < self.turn_end_altitude:
            #     pass
            #
            # self.turn_end_reached()

            # call_target_apoapsis = self.conn.get_call(getattr, self.vessel.flight(), 'mean_altitude')
            call_target_apoapsis = self.conn.get_call(getattr, self.vessel.orbit, 'apoapsis_altitude')
            # expression test
            expr_apo = self.conn.krpc.Expression.greater_than(
                    self.conn.krpc.Expression.call(call_target_apoapsis),
                    self.conn.krpc.Expression.constant_double(self.target_altitude))

            event = self.conn.krpc.add_event(expr_apo)
            event.add_callback(self.turn_end_reached)
            event.start()

            while self.launch_finished == False:
                pass


        except KeyboardInterrupt:
            print('Ascent interrupted')
            self.vessel.control.throttle = 0
            self.vessel.auto_pilot.disengage()
            self.scheduler.shutdown()
        # except krpc.error.RPCError:
        #     print('Fjucked up')
        #     self.vessel.control.throttle = 0
        #     self.vessel.auto_pilot.disengage()
        #     self.scheduler.shutdown()


    def turn_end_reached(self):
        print(f'Turn end altitude of {self.turn_end_altitude} m reached')
        self.vessel.control.throttle = 0
        self.vessel.auto_pilot.disengage()
        self.scheduler.remove_job('gravity_turn')

        print('Gravity turn finished')
        # print(
        #     f'Planning circularization burn at apoapsis of {self.apoapsis()} m')
        #
        # time.sleep(3)
        circularization_burn = self.mj.maneuver_planner.operation_circularize
        circularization_burn.make_node()
        NodeManager().execute_node()

        self.scheduler.remove_job('autostaging')
        self.launch_finished = True
        print('Launch finished')

    def thrust_throttle_adjustments(self, remaining_delta_v):
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

