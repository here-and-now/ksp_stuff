from comsat_network import ComSatNetwork
from orbit_manager import OrbitManager


if __name__ == '__main__':
    network = ComSatNetwork()
    orbit_manager = OrbitManager()

    # Add satellites to the network

    orbit_manager.get_telemetry()
    orbit_manager.desired_orbit(90, 10e5)


    # network.preexisting_network(constellation_name='Comsat_0.4_RingZero')
    # network.fine_tune_orbital_period()
    # network.setup_communications()
    network.get_antennas()
    network.get_comm_status()
