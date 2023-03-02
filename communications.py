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

        self.vessel_list = []

        self.mj = self.conn.mech_jeb
        self.auto_pilot = self.vessel.auto_pilot

        if self.vessel_list:
            self.setup_df()

    def get_antennas(self):
        self.antenna_list = []
        for antennas in self.vessel.control.nodes:
            self.antenna_list.append(antennas)

        return self.antenna_list

    def update_df(self):
        # self.antenna_list = self.get_antennas()
        self.antennas = self.return_antennas()

        self.df = pd.DataFrame([{
            'vessel': self.vessel,
            # 'name': self.vessel.name,
            'antennas': self.antennas,
        }])
        self.df = self.df.set_index('vessel')
        # print(df)
        return self.df


    def return_antennas(self, vessel):
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
