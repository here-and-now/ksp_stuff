import numpy as np
import time

def orientate_vessel(conn, vessel, new_orientation, accuracy_cutoff=1e-2, block=True):
    control = vessel.control
    control.sas = True
    if new_orientation == 'prograde':
        control.sas_mode = conn.space_center.SASMode.prograde
    elif new_orientation == 'retrograde':
        control.sas_mode = conn.space_center.SASMode.retrograde
    elif new_orientation == 'normal':
        control.sas_mode = conn.space_center.SASMode.normal
    elif new_orientation == 'anti-normal':
        control.sas_mode = conn.space_center.SASMode.anti_normal
    elif new_orientation == 'radial':
        control.sas_mode = conn.space_center.SASMode.radial
    elif new_orientation == 'anti-radial':
        control.sas_mode = conn.space_center.SASMode.anti_radial
    elif new_orientation == 'target':
        control.sas_mode = conn.space_center.SASMode.target
    elif new_orientation == 'maneuver':
        control.sas_mode = conn.space_center.SASMode.maneuver

    if block:
        print('Blocked: Orientating vessel...' +vessel.name + ' to ' + new_orientation)

        direction = conn.add_stream(getattr, vessel.flight(), 'direction')
        sas_direction = conn.add_stream(getattr, vessel.flight(), new_orientation)

        motion = True
        while motion:
            diff = np.abs(np.subtract(direction(), sas_direction()))
            diff_bool = diff < accuracy_cutoff
            motion = np.any(diff_bool==False)
            time.sleep(1)
    else:
        print('Non-blocked: Orientating vessel...' +vessel.name + ' to ' + new_orientation)
        

    return vessel
