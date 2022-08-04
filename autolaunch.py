import krpc
import time
import sys
import time
import os
import subprocess

conn = krpc.connect(name="Launch into orbit")

sc = conn.space_center
mj = conn.mech_jeb
ascent = mj.ascent_autopilot

# use AscentClassic as path
ascent.ascent_path_index = 0
path = ascent.ascent_path_classic

path.turn_shape_exponent = 0.5 #set the turn shape to 50%
path.auto_path = False #don't use autopath
path.turn_start_altitude = 3000
path.turn_start_velocity = 120
path.turn_end_altitude = 65000

ascent.desired_orbit_altitude = 100000
ascent.desired_inclination = 6

ascent.autostage = False


    

ascent.enabled = True
sc.active_vessel.control.activate_next_stage() #launch the vessel

with conn.stream(getattr, ascent, "enabled") as enabled:
    enabled.rate = 1 #we don't need a high throughput rate, 1 second is more than enough
    with enabled.condition:
        while enabled():
            enabled.wait()

print("Launch complete!")
conn.close()
