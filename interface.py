import bokeh
from bokeh.models.widgets import Tabs, Panel
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource, CustomJS, Slider, Button, Div, DataTable, TableColumn, NumberFormatter, StringFormatter, RangeSlider, Select, TextInput, DataTable
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
from comsat_network import ComSatNetwork
from launch import LaunchManager


class KSPBokehApp():
    def __init__(self):
        self.active_vessel = None

        # self.vessel_manager = VesselManager(name='ComSat_0.33')
        self.vessel_manager = VesselManager(name='')
        self.vessel_source = ColumnDataSource(
            self.bokehfy_df(self.vessel_manager.df))

        formatter_dict = {
            'vessel': StringFormatter(),
            'name': StringFormatter(),
            'body': StringFormatter(),
            'eccentricity': NumberFormatter(format='0.00000'),
            'inclination': NumberFormatter(format='0.00000'),
            'semi_major_axis': NumberFormatter(format='0.00'),
            'longitude_of_ascending_node': NumberFormatter(format='0.00000'),
            'argument_of_periapsis': NumberFormatter(format='0.00000'),
            'true_anomaly': NumberFormatter(format='0.00000'),
        }

        # reset index as TableColumns does not support index
        columns = [TableColumn(field=Ci, title=Ci, formatter=formatter_dict.get(
            Ci, None)) for Ci in self.vessel_manager.df.reset_index().columns]
        self.vessel_table = DataTable(source=self.vessel_source, columns=columns,
                                      width=800, height=280)


        self.update_button = Button(label="Update", button_type="success")
        self.update_button.on_click(lambda: self.update_source())

        # self.search_vessel_input = TextInput(value="", title="Search Vessel:")
        # sealf.search_vessel_input.on_change('value', lambda attr, old, new: self.search_vessel(new))

        tabs = Tabs(tabs=[
            Panel(child=column(self.update_button,
                  self.vessel_table), title="Vessels"),
        ])

        curdoc().add_root(tabs)

    def update_source(self):
        ''' Updates the source of the vessel table '''
        self.vessel_source.data = self.bokehfy_df(self.vessel_manager.df)

    def bokehfy_df(self, df):
        ''' Returns dataframe with bokeh compatible data types, currently only vessel objects. Also calls streams if necessary '''
        df = df.apply(lambda x: x.apply(
            lambda y: y() if callable(y) else y))

        df = df.reset_index()
        df['vessel'] = df['vessel'].apply(lambda x: str(x))

        return df


if __name__ == '__main__':
    KSPBokehApp()



# ooooold

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
