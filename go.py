from numpy import true_divide
from comsat_network import ComSatNetwork
from orbits import OrbitManager, Orbit
from communications import Communication
from launch import LaunchManager
from vessels import VesselManager
import time
import krpc

# conn = krpc.connect()
# sc = conn.space_center
# vessel = sc.active_vessel

# launch = LaunchManager(max_q=30000)
# orbs = OrbitManager(df=VesselManager().df)

# launch.ascent()

# while not launch.launch_finished:
    # pass

# antenna_parts = vessel.parts.with_name('RTLongAntenna2')


# for ap in antenna_parts:
    # for module in ap.modules:
        # if module.name == 'ModuleRTAntenna':
            # module.set_action('Activate')

# orb = Orbit()
# orb.set_altitude_and_circularize(0,2500000)

# orb_m = OrbitManager()
coms = ComSatNetwork()
coms.release_all_satellites(nr_sats=5)
    # print(vessel)
    # print(vessel.name)
    # coms.conn.space_center.active_vessel = vessel
    # time.sleep(3)
    # vessel.control.rcs = True
    # coms.mj.smart_ass.autopilot_mode = coms.mj.SmartASSAutopilotMode.retrograde
    
    # coms.mj.smart_ass.update(True)
    # time.sleep(3)

    # vessel.control.throttle = 0.05


# time.sleep(20)

coms.fine_tune_orbital_period()
# print(coms.vessel_list)


# coms.release_sats_triangle_orbit()

# coms.init_existing_network('OsCom_0.2 Probe')



# tel = Communication()
# tel.init_existing_network('OsCom_0.2 Probe')

# tel.setup_communications()

# orbs = OrbitManager(df=tel.df)
# orbs.vessel_list = tel.vessel_list

# orbs.fine_tune_orbital_period()

