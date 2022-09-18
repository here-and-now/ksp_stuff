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
            self.vessel_list = self.sc.vessels
    
        self.df = self.vessels_df()
        self.df = self.filter_df_by_name(self.df, self.name)
        self.df = self.add_orbit_data(self.df)
    
    def vessels_df(self):
        """ Returns a dataframe of all vessels """
        # df = pd.concat([Vessel(vessel).df for vessel in self.vessel_list])
        df = pd.concat([Vessel(vessel).df for vessel in self.vessel_list])
        return df
        # df = df.set_index('vessel')
    
    def add_orbit_data(self, df):
        """ Returns a dataframe with orbital data """
        # df = pd.concat([df, Orbit(vessel).df])
        df = pd.merge(df, Orbit(vessel).df, how='left', left_index=True)
        return df

    def filter_df_by_name(self, df, name):
        """ Returns a dataframe of vessels with a given name"""
        return df[df['name'].str.contains(name)]



class Vessel():
    def __init__(self, vessel=None):
        if vessel == None:
            vessel = krpc.connect('Vessel').space_center.active_vessel
            print(f'Vessel: No vessel selected. Defaulting to active vessel {vessel.name}')

        # Vessel attributes
        self.vessel = vessel
        self.vessel_name = vessel.name
        # Dataframe
        self.df = self.get_vessel_df()

    def get_vessel_df(self):
        df = pd.DataFrame([{
                'vessel': self.vessel,
                'name': self.vessel.name,
            }])
        df = df.set_index('vessel')
        return df 


