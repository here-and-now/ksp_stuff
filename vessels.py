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
    def __init__(self, name='active_vessel', instance_name='VesselManager'):
        self.conn = krpc.connect(name="VesselManager")
        self.sc = self.conn.space_center
        self.vessel = self.sc.active_vessel
        print('VesselManager connected ...')

        if name == 'active_vessel':
            vessel_list = [self.sc.active_vessel]
            name = self.sc.active_vessel.name
        else:
            vessel_list = self.sc.vessels

        self.df = pd.DataFrame([{
                'vessel': v,
                'name': v.name,
            }
            for v in vessel_list])

        self.df.set_index('vessel', inplace=True)
        self.df = self.df[self.df['name'].str.contains(name)]

 



