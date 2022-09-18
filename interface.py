from comsat_network import ComSatNetwork
from launch import LaunchManager
# from orbits import OrbitManager
from vessels import VesselManager

import bokeh
from bokeh.models.widgets import Tabs, Panel
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource, CustomJS, Slider, Button, Div, DataTable, TableColumn, NumberFormatter, FileInput, RangeSlider, Select, TextAreaInput, TextInput, ImageURL, ImageRGBA, DataTable
from bokeh.layouts import column, row
from bokeh.io import curdoc

import numpy as np
import glob
import time
import os
import io
import base64
import sys

from orbits import OrbitManager
from vessels import VesselManager, Vessel


class KSPBokehApp():
    def __init__(self):
        self.active_vessel = None

        self.vessel_manager = VesselManager(name='ComSat_0.33')
        self.vessel_source = ColumnDataSource(
            self.bokehfy_df(self.vessel_manager.df))

        self.vessel_table = DataTable(source=self.vessel_source, columns=[TableColumn(
            field=Ci, title=Ci) for Ci in self.vessel_manager.df.columns], width=800, height=280)

        # # layout
        self.vessel_table_layout = column(self.vessel_table)

        # # tabs
        self.vessel_tab = Panel(
            child=self.vessel_table_layout, title='Vessels')

        self.tabs = Tabs(tabs=[self.vessel_tab])

        # # show
        curdoc().add_root(self.tabs)

    def bokehfy_df(self, df):
        ''' Returns dataframe with bokeh compatible data types, currently only vessel objects'''
        df = df.apply(lambda x: x.apply(
            lambda y: y() if callable(y) else y))
        df = df.reset_index()
        df['vessel'] = df['vessel'].astype(str)
        df = df.set_index('vessel')
        return df


if __name__ == '__main__':
    KSPBokehApp()


# if __name__ == '__main__':

    # # launch parameters
    # target_altitude = 250000
    # turn_start_altitude = 2500
    # turn_end_altitude = 120000
    # inclination = 0
    # roll = 90
    # max_q = 20000
    # end_stage = 3

    # # Go for launch!
    # # launch = LaunchManager(target_altitude,
    # # turn_start_altitude,
    # # turn_end_altitude,
    # # end_stage,
    # # inclination,
    # # roll,
    # # max_q,
    # # staging_options=None)
    # # launch.ascent()
    # vessels = VesselManager(name='Com')

    # # a = orbit_manager.setup_df()
    # # print(a)
    # # orbit_manager.print_orbit_dataframe()


# # ####
    # # orbit_manager = OrbitManager()
    # # orbit_manager.print_telemetry()
    # # # orbit_manager.set_altitude_and_circularize(inclination, 20000000)

    # # network = ComSatNetwork()
    # # network.init_existing_network(constellation_name='Comsat_0.5_RingZero Relay')
    # # # network.release_sats_triangle_orbit()

    # # # orbit_manager.satellite_list = network.satellite_list
    # # # orbit_manager.fine_tune_orbital_period()

    # # # network.fine_tune_orbital_period()
    # # # network.setup_communications()
    # # network.manage_antennas()
# #     # network.get_antennas()
