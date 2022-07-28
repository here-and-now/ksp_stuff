import krpc

conn = krpc.connect(name="Launch into orbit")
mj = conn.mech_jeb
sc = conn.space_center
vessels = sc.vessels


def select_vessel(vessel_name):
    for v in vessels:
        if v.name == vessel_name:
            return v
    return None

def select_vessel_by_id(vessel_id):
    for v in vessels:
        if v.id == vessel_id:
            return v
    return None

def switch_vessel_if_needed(vessel):
    if vessel != sc.active_vessel:
        backup_vessel = sc.active_vessel
        sc.active_vessel = vessel
        print("Switched to vessel: " + vessel.name + "from " + backup_vessel.name)
        return True
    else:
        print("Vessel is already active: " + vessel.name)
    return False

vessel_name = 'Kerbin_Goresat/VS-3/Magneto/MSIP'

vessel = select_vessel(vessel_name)
switch_vessel_if_needed(vessel)


# Set up streams for telemetry
ut = conn.add_stream(getattr, conn.space_center, 'ut')
altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')

# control stuff
control = vessel.control
print(control)
control.throttle = 1.0

# ut = 500
# control.add_node(ut, prograde=1.0)
# print(control.throttle)

#change apoapsis to desired value
# vessel.
# planner = mj.maneuver_planner
# apo = planner.operation_apoapsis
# apo.new_apoapsis = 1000000000
# apo.make_nodes()
# conn.close()
