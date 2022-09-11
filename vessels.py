import math
import time

import krpc
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tabulate

# from orbits import OrbitManager
# from nodes import NodeManager

from utils.handle_orientation import orientate_vessel
from utils.handle_vessels import (
    decouple_by_name,
    manipulate_engines_by_name,
    select_vessel_and_duplicates_by_name,
    switch_vessel,
)

class VesselManager():
    def __init__(self):
        self.conn = krpc.connect(name="VesselManager")
        print('VesselManager connected ...')

        self.sc = self.conn.space_center
        self.vessel = self.sc.active_vessel
        self.vessel_name = self.vessel.name

        self.mj = self.conn.mech_jeb
        self.auto_pilot = self.vessel.auto_pilot



        # Telemetry
        self.ut = self.conn.add_stream(getattr, self.conn.space_center, 'ut')
        self.altitude = self.conn.add_stream(
            getattr, self.vessel.flight(), 'mean_altitude')
        self.apoapsis = self.conn.add_stream(
            getattr, self.vessel.orbit, 'apoapsis_altitude')
        self.periapsis = self.conn.add_stream(
            getattr, self.vessel.orbit, 'periapsis_altitude')
        self.eccentricity = self.conn.add_stream(
            getattr, self.vessel.orbit, 'eccentricity')
        self.inclination = self. conn.add_stream(
            getattr, self.vessel.orbit, 'inclination')

    def init_vessel_dataframe(self, name='active_vessel'):
        """Setup pandas dataframe for telemetry"""
        
        if name == 'active_vessel':
            vessel_list = [self.sc.active_vessel]
            name = self.sc.active_vessel.name
        else:
            vessel_list = self.sc.vessels

        data = [[v, v.name] for v in vessel_list]

        df = pd.DataFrame(data, columns=['vessel', 'name'])
        df.set_index('vessel', inplace=True)
        
        df = df[df['name'].str.contains(name)]

        return df
 



