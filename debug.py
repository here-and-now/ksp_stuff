import krpc
import time
from tabulate import tabulate

def get_antenna_target(antenna):
    """Helper function to get the target of an antenna"""
    try:
        target = antenna.target
        if target == conn.remote_tech.Target.none:
            return 'No target'
        elif target == conn.remote_tech.Target.celestial_body:
            return antenna.target_body.name
        elif target == conn.remote_tech.Target.vessel:
            return antenna.target_vessel.name
        elif target == conn.remote_tech.Target.ground_station:
            return antenna.target_ground_station
        elif target == conn.remote_tech.Target.active_vessel:
            return 'Active vessel'
    except Exception as e:
        return f'Error retrieving target: {str(e)}'
    return 'No target'

def get_antenna_state(antenna_module):
    """Helper function to get the state of an antenna"""
    if 'Status' in antenna_module.fields:
        state = antenna_module.fields['Status']
        if state in ['Connected', 'Operational']:
            return 'Activated'
        else:
            return 'Inactive'
    else:
        return 'N/A'

def print_antenna_info(antenna_parts, conn):
    info = []
    for antenna_part in antenna_parts:
        antenna = conn.remote_tech.antenna(antenna_part)
        for module in antenna_part.modules:
            if module.name in ['ModuleRTAntenna', 'ModuleDeployableAntenna']:
                target = get_antenna_target(antenna)
                state = get_antenna_state(module)
                info.append([antenna_part.name, module.name, target, state])
    return info

# Connect to kRPC
conn = krpc.connect(name='Antenna Info Script')

# Get the active vessel
vessel = conn.space_center.active_vessel

# Add a sleep to ensure the vessel is properly selected
time.sleep(2)

# Find all antennas on the active vessel
antenna_parts = [part for part in vessel.parts.all if 'Antenna' in part.name]

# Collect information from the antennas
antenna_info = print_antenna_info(antenna_parts, conn)

# Print the collected antenna information in a table format
headers = ["Antenna Part Name", "Module Name", "Target", "State"]
print(tabulate(antenna_info, headers=headers, tablefmt="grid"))
