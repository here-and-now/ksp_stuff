import math
import time

import krpc
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tabulate

from orbits import Orbit
# from nodes import NodeManager

from utils.handle_orientation import orientate_vessel
from utils.handle_vessels import (
    decouple_by_name,
    manipulate_engines_by_name,
    select_vessel_and_duplicates_by_name,
    switch_vessel,
)
class VesselManager():
    def __init__(self, name=None, instance_name='VesselManager'):
        self.conn = krpc.connect(name="VesselManager")
        self.sc = self.conn.space_center
        self.name = name
        print('VesselManager connected ...')
        if name == None:
            self.vessel_list = [self.sc.active_vessel]
            self.name = self.sc.active_vessel.name
        else:
            self.vessel_list = [v for v in self.sc.vessels if self.name in v.name]
        self.df = self.setup_vessels_df()
    
    def setup_vessels_df(self):
        ''' Returns a dataframe of Vessel objects '''
        df = pd.concat([Vessel(v, orbit_bool=True).df for v in self.vessel_list])
        return df

    def filter_df_by_attr(self, df, attr, value):
        """ Returns a dataframe of vessels with a given name"""
        return df[df[attr].str.contains(value)]




class Vessel():
    def __init__(self, vessel=None,orbit_bool=False):
        if vessel == None:
            vessel = krpc.connect('Vessel').space_center.active_vessel
            print(f'Vessel: No vessel selected. Defaulting to active vessel {vessel.name}')
        # Vessel attributes
        self.vessel = vessel
        self.vessel_name = vessel.name
        # Dataframe
        self.df = self.setup_df()

        #ToDO: fix this shit
        if orbit_bool:
            self.orbit = Orbit(self.vessel)
            self.df = pd.merge(self.df, self.orbit.df, how='inner', left_index=True, right_index=True)

    def setup_df(self):
        """ Returns a dataframe of vessel attributes """
        df = pd.DataFrame([{
                'vessel': self.vessel,
                'name': self.vessel.name,
            }])
        df = df.set_index('vessel')
        return df 


