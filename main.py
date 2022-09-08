from comsat_network import ComSatNetwork
from orbit_manager import OrbitManager


if __name__ == '__main__':

    network = ComSatNetwork()
    orbit_manager = OrbitManager()

    orbit_manager.set_altitude_and_circularize(90, 2000000)

    network.release_sats_triangle_orbit()



    # network.preexisting_network(constellation_name='Comsat_0.4_RingZero')
    # network.fine_tune_orbital_period()
    # network.setup_communications()
    network.get_antennas()
    network.get_comm_status()
