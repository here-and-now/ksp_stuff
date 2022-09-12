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

class Vessel():
    def __init__(self, vessel=None):

        if vessel == None:
            vessel = krpc.connect('Vessel').space_center.active_vessel
        # Vessel attributes
        self.vessel = vessel
        self.vessel_name = vessel.name



        # Dataframe
        self.df = self.get_dataframe()

    def get_dataframe(self):
        df = pd.DataFrame({
                'vessel': self.vessel,
                'name': self.vessel.name,
            },
            index=['vessel'])
        return df 


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
    
        self.df = self.get_dataframe()
    
    def get_dataframe(self):
        """ Returns a dataframe of all vessels """
        df = pd.concat([Vessel(vessel).df for vessel in self.vessel_list])
        df = df.set_index('vessel')
        df = df[df['name'].str.contains(self.name)]
        return df





        # self.df.set_index('vessel', inplace=True)
        # self.df = self.df[self.df['name'].str.contains(name)]





# a = VesselManager(name='Com')
a = VesselManager()
print(a.df)


