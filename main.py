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
    # launch = LaunchManager(target_altitude,
                            # turn_start_altitude,
                            # turn_end_altitude,
                            # end_stage,
                            # inclination,
                            # roll,
                            # max_q,
                            # staging_options=None)
    # launch.ascent()


    orbit_manager = OrbitManager()
    orbit_manager.print_telemetry()
    # orbit_manager.set_altitude_and_circularize(inclination, 20000000)

    network = ComSatNetwork()
    network.init_existing_network(constellation_name='Comsat_0.5_RingZero Relay')
    # network.release_sats_triangle_orbit()
    orbit_manager.satellite_list = network.satellite_list
    orbit_manager.fine_tune_orbital_period()




    # network.fine_tune_orbital_period()
    # network.setup_communications()
    network.manage_antennas()
    # network.get_antennas()
