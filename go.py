from numpy import true_divide
from comsat_network import ComSatNetwork
from orbits import OrbitManager, Orbit
from communications import Communication
from launch import LaunchManager
from vessels import VesselManager
from nodes import NodeManager
import time
import krpc
from communications import Communication

conn = krpc.connect()
sc = conn.space_center
# vessel = sc.active_vessel
#
# launch = LaunchManager(inclination=90, max_q=20000, roll=90)
# launch.ascent()
# while not launch.launch_finished:
    # pass
#
# antenna_parts = vessel.parts.with_name('RTLongAntenna2')
# for ap in antenna_parts:
#     for module in ap.modules:
#         if module.name == 'ModuleRTAntenna':
#             module.set_action('Activate')

# orb = Orbit()
# orb.set_altitude_and_circularize(0,40000000)


# coms = ComSatNetwork()
# coms.resonant_orbit()
# time.sleep(15)
# coms.release_all_satellites(nr_sats=3)
# coms.recircularize_multiple_sats()

com = Communication()
com.init_existing_network('ComSat_AdAstra_0.3 Probe')
antenna_targets = {
    'HighGainAntenna': 'setup_network',
    # 'nfex-antenna-relay-tdrs-2': ['active_vessel', 'ScanSat_0.2']
    'RTShortDish2': ['active_vessel', 'ScanSat_0.2']
}
com.setup_communications(antenna_targets)
com.display_network_info()
# coms.setup_communications()
# coms.update_df()
# coms.init_existing_network('ComSat_AdAstra_0.13 Relay')
# coms.fine_tune_orbital_period()


# coms.fine_tune_orbital_period()
# coms.setup_communications(connection_list=['ScanSat_0.2'])
# coms.update_df()



# tel.init_existing_network('OsCom_0.2 Probe')

# tel.setup_communications()

# orbs = OrbitManager(df=tel.df)
# orbs.vessel_list = tel.vessel_list

# orbs.fine_tune_orbital_period()

