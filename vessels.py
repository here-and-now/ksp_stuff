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

        self.vessel_list = self.sc.vessels

    def setup_vessels_df(self, vessel_list):
        ''' Returns a dataframe of Vessel objects '''
        if vessel_list:
            self.vessel_list = vessel_list
        self.df = pd.concat([Vessel(v, orbit_bool=True).df for v in self.vessel_list])
        return self.df

    def search_by_name(self, name, exact=False):
        if exact:
            self.vessel_list = [v for v in self.sc.vessels if name == v.name]
        else:
            self.vessel_list = [v for v in self.sc.vessels if name in v.name]

        try:
            self.df = pd.concat([Vessel(v, orbit_bool=True).df for v in self.vessel_list])
            return self.df
        except:
            print(f"VesselManager: No vessels found with name {name}")
            # return empty complete empty dataframe
            return pd.DataFrame()


    def filter_df_by_attr(self, df, attr, value):
        """ Returns a dataframe of vessels with a given name"""
        return df[df[attr].str.contains(value)]




class Vessel():
    def __init__(self, vessel=None, orbit_bool=False):
        self.conn = krpc.connect(name="Vessel")
        # Vessel attributes
        self.vessel = vessel
        # Dataframe
        self.df = self.setup_df()

        #ToDO: fix this shit
        if orbit_bool:
            self.orbit = Orbit(self.conn, self.vessel)
            self.df = pd.merge(self.df, self.orbit.df, how='inner', left_index=True, right_index=True)
    def setup_df(self):
        """ Returns a dataframe of vessel attributes """
        df = pd.DataFrame([{
                'vessel': self.vessel,
                'name': self.vessel.name,
            }])
        df = df.set_index('vessel')
        return df 


