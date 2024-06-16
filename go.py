from numpy import true_divide
from comsat_network import ComSatNetwork
from orbits import OrbitManager, Orbit
from communications import Communication
from launch import LaunchManager
from vessels import VesselManager
from nodes import NodeManager
import time
import krpc

conn = krpc.connect()
sc = conn.space_center
vessel = sc.active_vessel
#
# launch = LaunchManager(inclination=90, max_q=20000, roll=90)
# launch.ascent()
# while not launch.launch_finished:
    # pass
#
antenna_parts = vessel.parts.with_name('RTLongAntenna2')
for ap in antenna_parts:
    for module in ap.modules:
        if module.name == 'ModuleRTAntenna':
            module.set_action('Activate')

# orb = Orbit()
# orb.set_altitude_and_circularize(0,40000000)


coms = ComSatNetwork()
# coms.resonant_orbit()
# time.sleep(30)
# coms.release_all_satellites(nr_sats=5)
# coms.init_existing_network('OsCom_0.6 Probe')
# coms.fine_tune_orbital_period()
#
coms.recircularize_multiple_sats()
coms.fine_tune_orbital_period()
coms.setup_communications()
coms.update_df()



# tel.init_existing_network('OsCom_0.2 Probe')

# tel.setup_communications()

# orbs = OrbitManager(df=tel.df)
# orbs.vessel_list = tel.vessel_list

# orbs.fine_tune_orbital_period()

