import math
import time
import krpc

from utils.handle_vessels import (
    manipulate_engines_by_name,
    )

from utils.debug import print_parts
conn = krpc.connect('log')
sc = conn.space_center
vessel = sc.active_vessel

# Set up streams for telemetry
ut = conn.add_stream(getattr, conn.space_center, 'ut')
altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
thrust = conn.add_stream(getattr, vessel, 'thrust')
mass = conn.add_stream(getattr, vessel, 'mass')

start_time = time.time()
time_list = []
n = 10e5
# test nonsensicals
for _ in range(int(n)):
    a = ut()
    b = altitude()
    c = apoapsis()
    d = thrust()
    e = mass()
    print(c)

    r = b + c - e
    end_time = time.time()
    time_list.append(end_time - start_time)
    start_time = end_time

#calculae average of last 10e3 loops

average_time = sum(time_list)/n
average_time = (end_time - start_time) / n
print('Average time per loop: ' + str(average_time))


