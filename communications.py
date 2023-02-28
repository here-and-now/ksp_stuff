import math
import time
import krpc
import pandas as pd
import tabulate

from orbits import OrbitManager

class Communication():
    def __init__(self):
        self.conn = krpc.connect(name="ComSat_Network")
        print("ComSatNetwork connected ...")

        self.sc = self.conn.space_center

        self.vessel = self.sc.active_vessel
        self.vessel_name = self.vessel.name
        self.constellation_name = self.vessel_name

        self.vessel_list = []

        self.mj = self.conn.mech_jeb
        self.auto_pilot = self.vessel.auto_pilot

        if self.vessel_list:
            self.setup_df()

        # Telemetry
        self.ut = self.conn.add_stream(getattr, self.conn.space_center, 'ut')
        self.altitude = self.conn.add_stream(
            getattr, self.vessel.flight(), 'mean_altitude')
        self.apoapsis = self.conn.add_stream(
            getattr, self.vessel.orbit, 'apoapsis_altitude')
        self.periapsis = self.conn.add_stream(
            getattr, self.vessel.orbit, 'periapsis_altitude')
        self.eccentricity = self.conn.add_stream(
            getattr, self.vessel.orbit, 'eccentricity')
        self.inclination = self. conn.add_stream(
            getattr, self.vessel.orbit, 'inclination')

    def setup_df(self):
        '''
        Creates a pandas dataframe to store
        telemetry data and antennas
        '''
        self.period_mean = sum(
            vessel.orbit.period for vessel in self.vessel_list) / len(self.vessel_list)

        data = [[v, v.name, v.orbit.body.name, v.orbit.apoapsis_altitude, v.orbit.periapsis_altitude,
                 v.orbit.inclination, v.orbit.period, (
                     v.orbit.period - self.period_mean),
                 self.return_antennas(v)] for v in self.vessel_list]

        self.df = pd.DataFrame(data, columns=['Vessel', 'Name', 'Body', 'Apoapsis', 'Periapsis',
                                              'Inclination', 'Period', 'Period diff', 'Antennas'])
        self.df.set_index('Vessel', inplace=True)

        print(tabulate.tabulate(self.df.drop('Antennas', axis=1),
              headers='keys', tablefmt='fancy_grid'))

        return self.df

    def return_antennas(self, vessel):
        '''
        Switches to vessel and returns all
        remote tech antennas
        '''
        self.sc.active_vessel = vessel
        return self.conn.remote_tech.comms(vessel).antennas


    def manage_antennas(self):
        '''
        Manage antennas of all vessels in constellation.
        Currrently only activates RT antenna part modules.
        WIP: Targeting
        '''

        self.df['Antennas'].to_frame().apply(lambda x: self.activate_antennas(x.index, x.values))


    def activate_antennas(self, vessel, antennas):
        '''
        Activates all RT antennas in list
        '''
        print(vessel[0])
        # print(antennas.values)
        self.sc.active_vessel = vessel[0]
        for antenna in antennas[0]:
            print(antenna)
            # self.sc.active_vessel = antenna.part.vessel
            for module in antenna.part.modules:
                if module.name == 'ModuleRTAntenna':
                    module.set_action('Activate')
                    print('Antenna activated on ')


    def setup_communications(self):
        '''
        Outdated, use manage_antennas instead.
        Based on distance between satellites, sets up
        communication links between them
        '''

        distance_dict = {}
        print(self.vessel_list)
        for vessel in self.vessel_list:
            distance_dict[vessel] = {}
            for target_vessel in self.vessel_list:

                print('tarvessel', target_vessel)
                if vessel is not target_vessel:
                    self.sc.target_vessel = target_vessel
                    print('Target', self.sc.target_vessel)
                    distance = self.sc.target_vessel.orbit.distance_at_closest_approach(
                        vessel.orbit)
                    distance_dict[vessel].update({target_vessel: distance})

        for vessel, distance_to_vessel_dict in distance_dict.items():
            self.sc.active_vessel = vessel
            antenna_parts = vessel.parts.with_name('nfex-antenna-relay-tdrs-1')

            sorted_distance_to_vessel_dict = sorted(
                distance_to_vessel_dict.items(), key=lambda x: x[1])

            for i, antenna_part in enumerate(antenna_parts):
                antenna = self.conn.remote_tech.antenna(antenna_part)

                #if antenna is from RT itself?
                for module in antenna_part.modules:
                    if module.name == 'ModuleRTAntenna':
                        module.set_action('Activate')
                #if not, extend antenna normally
                for module in antenna_part.modules:
                    if module.name == 'ModuleDeployableAntenna':
                        module.set_action('Extend Antenna')

                # even target nearest satellite
                if i % 2 == 0:
                    antenna.target_vessel = sorted_distance_to_vessel_dict[0][0]
                # uneven target 2nd nearest satellite
                else:
                    antenna.target_vessel = sorted_distance_to_vessel_dict[1][0]

    def init_existing_network(self, constellation_name):
        self.constellation_name = constellation_name
        self.vessel_list = []

        for vessel in self.conn.space_center.vessels:
            if vessel.name == constellation_name:
                self.vessel_list.append(vessel)

        print(
            f'{len(self.vessel_list)} preexisting satellites found with name {constellation_name}')

        # print("Fucking up satellite list for testing purposes ... ")
        # self.satellite_list = [self.sc.active_vessel]

        self.setup_df()
