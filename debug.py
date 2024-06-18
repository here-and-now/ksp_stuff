import math
import time
import krpc
import pandas as pd
from tabulate import tabulate

from orbits import OrbitManager
from vessels import VesselManager

class Communication:
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

    def setup_df(self):
        """Initialize the dataframe to store vessel and antenna information"""
        self.df = pd.DataFrame(columns=['vessel', 'name', 'body', 'inclination', 'apoapsis', 'periapsis', 'period', 'antennas', 'period_diff'])

    def get_antennas(self):
        self.antenna_list = []
        for antennas in self.vessel.control.nodes:
            self.antenna_list.append(antennas)
        return self.antenna_list

    def update_df(self):
        ves = VesselManager(orbit_flag=True, node_flag=False, vessel_list=self.vessel_list)
        self.df = ves.df.apply(lambda x: x.apply(lambda y: y() if callable(y) else y))

        self.df['antennas'] = self.df.index.map(lambda v: self.return_antennas(v))
        self.df['period_diff'] = self.df['period'] - self.df['period'].mean()

        return self.df

    def return_antennas(self, vessel):
        return self.conn.remote_tech.comms(vessel).antennas

    def manage_antennas(self):
        '''
        Manage antennas of all vessels in constellation.
        Currently only activates RT antenna part modules.
        WIP: Targeting
        '''
        self.df['antennas'].apply(lambda antennas: self.activate_antennas(antennas))

    def activate_antennas(self, antennas):
        '''
        Activates all RT antennas in list
        '''
        for antenna in antennas:
            for module in antenna.part.modules:
                if module.name == 'ModuleRTAntenna':
                    module.set_action('Activate')
                    print('Antenna activated on', antenna.part.vessel.name)

    def init_existing_network(self, constellation_name):
        self.constellation_name = constellation_name
        self.vessel_list = []

        for vessel in self.conn.space_center.vessels:
            if vessel.name == constellation_name:
                self.vessel_list.append(vessel)

        print(f'{len(self.vessel_list)} preexisting satellites found with name {constellation_name}')

        self.setup_df()
        self.update_df()

    def get_antenna_target(self, antenna):
        """Helper function to get the target of an antenna"""
        try:
            target = antenna.target
            if target == self.conn.remote_tech.Target.none:
                return 'No target'
            elif target == self.conn.remote_tech.Target.celestial_body:
                return antenna.target_body.name
            elif target == self.conn.remote_tech.Target.vessel:
                return antenna.target_vessel.name
            elif target == self.conn.remote_tech.Target.ground_station:
                return antenna.target_ground_station
            elif target == self.conn.remote_tech.Target.active_vessel:
                return 'Active vessel'
        except Exception:
            return 'Error retrieving target'
        return 'No target'

    def get_antenna_state(self, antenna_module):
        """Helper function to get the state of an antenna"""
        if 'Status' in antenna_module.fields:
            state = antenna_module.fields['Status']
            if state in ['Connected', 'Operational']:
                return 'Activated'
            else:
                return 'Inactive'
        else:
            return 'N/A'

    def display_antenna_info(self, vessel):
        """Collect and return information about the antennas of a given vessel"""
        antenna_parts = [part for part in vessel.parts.all if 'Antenna' in part.name]
        info = []
        for antenna_part in antenna_parts:
            antenna = self.conn.remote_tech.antenna(antenna_part)
            for module in antenna_part.modules:
                if module.name in ['ModuleRTAntenna', 'ModuleDeployableAntenna']:
                    target = self.get_antenna_target(antenna)
                    state = self.get_antenna_state(module)
                    info.append([antenna_part.name, module.name, target, state])
        return info

    def switch_to_vessel(self, vessel):
        """Switch to the given vessel"""
        self.sc.active_vessel = vessel
        time.sleep(2)  # Allow some time for the switch to complete

    def display_network_info(self):
        """Display information about all satellites in the network in a nested tabulated format"""
        nested_info = []
        for vessel in self.vessel_list:
            self.switch_to_vessel(vessel)
            vessel_info = [
                vessel.name,
                vessel.orbit.body.name,
                vessel.orbit.inclination,
                vessel.orbit.apoapsis_altitude,
                vessel.orbit.periapsis_altitude,
                vessel.orbit.period
            ]
            nested_info.append(vessel_info)

            antenna_info = self.display_antenna_info(vessel)
            for antenna in antenna_info:
                nested_info.append([''] * 6 + antenna)

        headers = ["Vessel Name", "Body", "Inclination", "Apoapsis", "Periapsis", "Period", "Antenna Part Name", "Module Name", "Target", "State"]
        print(tabulate(nested_info, headers=headers, tablefmt="fancy_grid"))

# Example usage
if __name__ == "__main__":
    com = Communication()
    com.init_existing_network('ComSat_AdAstra_0.13 Relay')
    com.display_network_info()
