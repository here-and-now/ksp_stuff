from abc import update_abstractmethods
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

from apscheduler.schedulers.background import BackgroundScheduler


class KSPBokehApp():
    def __init__(self):
        self.active_vessel = None

        # self.vessel_manager = VesselManager(name='ComSat_0.33')
        self.vessel_manager = VesselManager(name=None)
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

        # Vessels
        # reset index as TableColumns does not support index
        columns = [TableColumn(field=Ci, title=Ci, formatter=formatter_dict.get(
            Ci, None)) for Ci in self.vessel_manager.df.reset_index().columns]
        self.vessel_table = DataTable(
            source=self.vessel_source, columns=columns, autosize_mode='fit_viewport')
        # width=800, height=280)

        self.search_vessel_input = TextInput(value="", title="Search Vessel:")
        self.search_vessel_input.on_change('value', self.search_vessel)

        self.update_button = Button(label="Update", button_type="success")
        self.update_button.on_click(self.update_vessel_source)

        # test stuff
        self.test_btn = Button(label="Test", button_type="success")
        self.test_btn.on_click(self.teeeest)
        self.text_test = TextInput(value="0", title="Search Vessel:")
        # end vessels

        # Communication network

        # Launch
        self.slider_target_altitude = Slider(
            start=100000, end=1000000, value=250000, step=1000, title="Target Altitude")
        self.slider_turn_start_altitude = Slider(
            start=1000, end=100000, value=2500, step=100, title="Turn Start Altitude")
        self.slider_turn_end_altitude = Slider(
            start=1000, end=100000, value=120000, step=100, title="Turn End Altitude")
        self.slider_inclination = Slider(
            start=-90, end=90, value=0, step=1, title="Inclination")
        self.slider_roll = Slider(
            start=0, end=360, value=90, step=1, title="Roll")
        self.slider_max_q = Slider(
            start=10000, end=100000, value=20000, step=1000, title="Max Q")
        self.slider_end_stage = Slider(
            start=1, end=10, value=3, step=1, title="End Stage")

        self.launch_button = Button(label="Launch", button_type="success")
        self.launch_button.on_click(self.go_for_launch)

        self.fig_launch_telemetry = figure(plot_width=800, plot_height=400)

        # self.communication_network_tab = Panel(child=column(
            # self.vessel_table, self.update_button, self.test_btn, self.text_test, self.search_vessel_input), title='Communication Network')
        self.launch_slider_column = column(self.slider_target_altitude, self.slider_turn_start_altitude, self.slider_turn_end_altitude, self.slider_inclination, self.slider_roll, self.slider_max_q, self.slider_end_stage, self.launch_button)
        self.launch_telemetry_column = column(self.fig_launch_telemetry)
        self.launch_tab = Panel(child=row(self.launch_slider_column, self.launch_telemetry_column), title='Launch')

        self.vessels_tab=Panel(child = column(self.search_vessel_input, self.vessel_table,
                                 self.update_button, self.text_test, self.test_btn), title = 'Vessels')

        self.tabs=Tabs(tabs = [self.vessels_tab, self.launch_tab])
        self.curdoc = curdoc()
        self.curdoc.add_periodic_callback(self.select_active_vessel_index_on_vessel_source, 1000)
        self.curdoc.add_root(self.tabs)

    def go_for_launch(self):
        ''' Launches the vessel '''
        self.launch=LaunchManager(self.slider_target_altitude.value,
                               self.slider_turn_start_altitude.value,
                               self.slider_turn_end_altitude.value,
                               self.slider_end_stage.value,
                               self.slider_inclination.value,
                               self.slider_roll.value,
                               self.slider_max_q.value,
                               staging_options = None)

        # plotting stuff
        launch_data = {'met' : [],
                       'flight_mean_altitude' : []}
        self.launch_source = ColumnDataSource(data=launch_data)
        self.fig_launch_telemetry.line(x='met', y='flight_mean_altitude', source=self.launch_source)
        # periodic callback for live plotting of launch data
        self.curdoc.add_periodic_callback(self.stream_launch_source, 1000)

        # Gooooooooo 
        self.launch.ascent()

    def stream_launch_source(self):
        ''' Streams the launch telemetry plot '''
        print(self.launch.flight_mean_altitude())
        launch_data = {'met' : [self.launch.met()],
                       'flight_mean_altitude' : [self.launch.flight_mean_altitude()]}

        self.launch_source.stream(launch_data)
        
        

    def teeeest(self):
        selected_vessel=self.vessel_source.selected.indices[0]
        vname=self.vessel_source.data['vessel'][selected_vessel]
        self.text_test.value=vname

    def select_active_vessel_index_on_vessel_source(self):
        ''' Selects the active vessel on the vessel_source '''
        df=self.bokehfy_df(self.vessel_manager.df)
        active_vessel=self.vessel_manager.active_vessel()
        try:
            active_vessel_index=df.index[df['vessel'] == str(active_vessel)].tolist()[
                0]
            self.vessel_source.selected.indices = [active_vessel_index]
        except IndexError:
            pass

    def update_on_search_vessel(self, attr, old, new):
        self.vessel_manager.name = new
        self.vessel_manager.df = self.vessel_manager.setup_vessels_df()
        self.update_vessel_source()

    # def select_data_table_row(self, attr, old, new):
    def select_data_table_row(self):
        ''' Selects a row in the data table '''
        # self.vessel_table.selected.indices = [new]
        self.vessel_source.selected.indices = [0]

    def search_vessel(self, attr, old, new):
        ''' Searches for vessels containing the search string '''

        df = self.vessel_manager.search_vessels_by_name(new)
        self.vessel_source.data = self.bokehfy_df(df)

    def update_vessel_source(self):
        ''' Updates the source of the vessel table '''
        self.vessel_source.data = self.bokehfy_df(self.vessel_manager.df)

    def bokehfy_df(self, df):
        ''' Returns dataframe with bokeh compatible data types, currently only vessel objects. Also calls streams if necessary '''
        df = df.apply(lambda x: x.apply(
            lambda y: y() if callable(y) else y))

        df = df.reset_index()
        if 'vessel' in df.columns:
            df['vessel'] = df['vessel'].apply(lambda x: str(x))
            # df['vessel'] = df['vessel'].apply(lambda x: str(x).split('#')[1])
        if 'body' in df.columns:
            df['body'] = df['body'].apply(lambda x: str(x))

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
