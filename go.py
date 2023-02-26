from comsat_network import ComSatNetwork
from orbits import OrbitManager
from communications import Communication
coms = ComSatNetwork()
# coms.release_sats_triangle_orbit()

# coms.init_existing_network('OsCom_0.1 Probe')



tel = Communication()
tel.init_existing_network('OsCom_0.1 Probe')

tel.setup_communications()

print(coms.vessel_list)

# orbs = OrbitManager(df=coms.df)
# orbs.vessel_list = coms.vessel_list

# orbs.fine_tune_orbital_period()

