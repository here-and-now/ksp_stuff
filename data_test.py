import krpc

conn = krpc.connect(name="Launch into orbit")
vessels = conn.space_center.vessels

def select_vessel(vessel_name):
    for v in vessels:
        if v.name == vessel_name:
            return v
    return None

vessel_name = 'OsNet_1.0_Ring_1'
vessel = select_vessel(vessel_name)

# Set up streams for telemetry
ut = conn.add_stream(getattr, conn.space_center, 'ut')
altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
stage_2_resources = vessel.resources_in_decouple_stage(stage=2, cumulative=False)
srb_fuel = conn.add_stream(stage_2_resources.amount, 'SolidFuel')
conn.close()
