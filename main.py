from comsat_network import ComSatNetwork
from launch_manager import LaunchManager
from orbit_manager import OrbitManager


if __name__ == '__main__':

    # launch parameters
    target_altitude = 250000
    turn_start_altitude = 2500
    turn_end_altitude = 120000
    inclination = 0
    roll = 90
    max_q = 20000
    end_stage = 3

    # Go for launch!
    launch = LaunchManager(target_altitude,
                            turn_start_altitude,
                            turn_end_altitude,
                            end_stage,
                            inclination,
                            roll,
                            max_q,
                            staging_options=None)
    launch.ascent()


    orbit_manager = OrbitManager()
    orbit_manager.set_altitude_and_circularize(inclination, 2000000)

    network = ComSatNetwork()
    network.release_sats_triangle_orbit()



    # network.preexisting_network(constellation_name='Comsat_0.4_RingZero')
    # network.fine_tune_orbital_period()
    # network.setup_communications()
    network.get_antennas()
    network.get_comm_status()
