from comsat_network import ComSatNetwork
from orbits import OrbitManager
from communications import Communication
from launch import LaunchManager
import time

launch = LaunchManager()
launch.ascent()

while not launch.launch_finished:
    pass

# coms = ComSatNetwork()
# coms.release_sats_triangle_orbit()

# coms.init_existing_network('OsCom_0.1 Probe')



# tel = Communication()
# tel.init_existing_network('OsCom_0.1_Polar Probe')

# tel.setup_communications()

# orbs = OrbitManager(df=tel.df)
# orbs.vessel_list = tel.vessel_list

# orbs.fine_tune_orbital_period()

