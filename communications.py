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
            if constellation_name in vessel.name:
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

    def setup_communications(self, connection_list):
        '''
        Based on distance between satellites, sets up
        communication links between them in a triangular orbit.
        One antenna will always target Kerbin.
        connection_list is a list of specific vessel names to connect to.
        '''

        # Get the vessel objects for the names in connection_list with exact name match
        vessel_name_to_object = {v.name: v for v in self.conn.space_center.vessels}
        connection_vessels = []
        for name in connection_list:
            if name in vessel_name_to_object:
                connection_vessels.append(vessel_name_to_object[name])
            else:
                print(f"Warning: Vessel named '{name}' not found.")

        distance_dict = {}
        for vessel in self.vessel_list:
            distance_dict[vessel] = {}
            for target_vessel in self.vessel_list:
                if vessel is not target_vessel:
                    self.sc.target_vessel = target_vessel
                    time.sleep(0.2)
                    distance = vessel.orbit.distance_at_closest_approach(target_vessel.orbit)
                    distance_dict[vessel].update({target_vessel: distance})

        for vessel, distance_to_vessel_dict in distance_dict.items():
            self.switch_to_vessel(vessel)
            antenna_parts = vessel.parts.with_name('RelayAntenna5')

            sorted_distance_to_vessel_dict = sorted(distance_to_vessel_dict.items(), key=lambda x: x[1])

            # Connect to the two nearest satellites to form a triangular communication link
            nearest_vessels = [sorted_distance_to_vessel_dict[0][0], sorted_distance_to_vessel_dict[1][0]]

            # Add vessels from connection_list if they are not already in nearest_vessels
            for conn_vessel in connection_vessels:
                if conn_vessel not in nearest_vessels:
                    nearest_vessels.append(conn_vessel)

            for i, antenna_part in enumerate(antenna_parts):
                antenna = self.conn.remote_tech.antenna(antenna_part)
                for module in antenna_part.modules:
                    if module.name == 'ModuleRTAntenna':
                        module.set_action('Activate')
                    if module.name == 'ModuleDeployableAntenna':
                        module.set_action('Extend Antenna')

                if i == 0:
                    # The first antenna targets Kerbin
                    antenna.target_body = self.conn.space_center.bodies['Kerbin']
                elif i == 1:
                    # The second antenna targets the active vessel
                    antenna.target = self.conn.remote_tech.Target.active_vessel
                elif i < len(nearest_vessels) + 2:
                    # Subsequent antennas target the nearest satellites or specified vessels
                    antenna.target_vessel = nearest_vessels[i - 2]

            # Log errors if any antennas are not set properly
            if not antenna_parts or len(antenna_parts) < 3:
                print(f"Warning: Not enough antennas on vessel {vessel.name}.")
            if i >= len(antenna_parts):
                print(f"Warning: Antenna part {i} is not available for vessel {vessel.name}.")
            if nearest_vessels[0] is None or nearest_vessels[1] is None:
                print(f"Warning: Nearest vessels not properly identified for vessel {vessel.name}.")

# Example usage
if __name__ == "__main__":
    com = Communication()
    com.init_existing_network('ComSat_AdAstra_0.13 Relay')
    
    com.setup_communications(['ScanSat_0.2'])  # Add appropriate vessel names here
    com.display_network_info()
