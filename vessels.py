import time

import krpc
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tabulate

from orbits import Orbit
from nodes import Node
# from nodes import NodeManager

from utils.handle_orientation import orientate_vessel
from utils.handle_vessels import (
    decouple_by_name,
    manipulate_engines_by_name,
    select_vessel_and_duplicates_by_name,
    switch_vessel,
)
class VesselManager():
    def __init__(self, name=None, vessel_list=None, orbit_flag=False, node_flag=False, exact_name=False, instance_name='VesselManager'):
        self.conn = krpc.connect(name="VesselManager")
        self.sc = self.conn.space_center

        self.orbit_flag = orbit_flag
        self.node_flag = node_flag

        self.exact_name = exact_name

        if vessel_list is None and name is None:
            self.vessel_list = self.sc.vessels
        elif vessel_list is not None:
            self.vessel_list = vessel_list
        else:
            self.vessel_list = self.search_by_name(name=name)

        self.df = self.setup_df()

    def setup_df(self):
        ''' Returns a dataframe of Vessel objects '''
        self.df = pd.concat([Vessel(v, orbit_flag=self.orbit_flag, node_flag=self.node_flag, conn=self.conn).df for v in self.vessel_list])
        return self.df

    def search_by_name(self, name='*'):
        if self.exact_name:
            self.vessel_list = [v for v in self.sc.vessels if name == v.name]
        else:
            self.vessel_list = [v for v in self.sc.vessels if name in v.name]

        # self.df = self.setup_df()
        return self.vessel_list

    def filter_df_by_attr(self, df, attr, value):
        """ Returns a dataframe of vessels with a given name"""
        return df[df[attr].str.contains(value)]




class Vessel():
    def __init__(self, vessel=None, orbit_flag=False, node_flag=False, conn=None):
        if conn is None:
            self.conn = krpc.connect(name="Vessel")
        else:
            self.conn = conn
        # Vessel attributes
        self.vessel = vessel
        # Dataframe
        self.df = self.setup_df()

        #ToDO: fix this shit
        if orbit_flag:
            self.orbit = Orbit(self.vessel, conn=self.conn)
            self.df = pd.merge(self.df, self.orbit.df, how='inner', left_index=True, right_index=True)
        if node_flag:
            self.node = Node(self.vessel)
            self.df = pd.merge(self.df, self.node.df, how='inner', left_index=True, right_index=True)

    def setup_df(self):
        """ Returns a dataframe of vessel attributes """
        df = pd.DataFrame([{
                'vessel': self.vessel,
                'name': self.vessel.name,
            }])
        df = df.set_index('vessel')
        return df 


