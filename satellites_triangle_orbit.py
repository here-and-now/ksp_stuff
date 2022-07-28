import krpc

conn = krpc.connect(name="Launch into orbit")
print("Connected to kRPC")

mj = conn.mech_jeb
sc = conn.space_center
vessels = sc.vessels

def select_vessel_and_duplicates_by_name(vessel_name):
    vessel_list = []
    for v in vessels:
        if v.name == vessel_name:
            vessel_list.append(v)

    if len(vessel_list) == 0:
        print("No vessel found with name: " + vessel_name)
        return False
    if len(vessel_list) == 1:
        print("Vessel found: " + vessel_list[0].name)
        return vessel_list[0]
    else:
        #sort vessel list by attribute met
        vessel_list.sort(key=lambda v: v.met)

        #ask for input which vessel to use, default 0
        print("Multiple vessels found:")
        import tabulate
        #print vessel list names and met in tabulated format with index
        print(tabulate.tabulate([[i, v.name, v.met] for i, v in enumerate(vessel_list)], headers=['Index', 'Name', 'MET']))

        vessel_index = int(input("Select vessel by index: "))
        print("Vessel selected: " + vessel_list[vessel_index].name)
        return vessel_list[vessel_index]


        
        
        for i in range(len(vessel_list)):
            print(str(i) + ": " + vessel_list[i].name + " (" + str(vessel_list[i].met) + ")")
        vessel_index = input("Select vessel by index (default 0): ")
        if vessel_index == "":
            vessel_index = 0
        else:
            vessel_index = int(vessel_index)
        if vessel_index < 0 or vessel_index >= len(vessel_list):
            print("Invalid index: " + str(vessel_index))
            return False
        print("Vessel found: " + vessel_list[vessel_index].name)
        return vessel_list[vessel_index]

        return vessel_list

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

# vessel_name = 'Kerbin_Goresat/VS-3/Magneto/MSIP'
vessel_name = 'OsNet_1.0_Ring_1'

vessel = select_vessel_and_duplicates_by_name(vessel_name)
# switch_vessel_if_needed(vessel)


# Set up streams for telemetry
# ut = conn.add_stream(getattr, conn.space_center, 'ut')
# altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
# apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')

# control stuff
# control = vessel.control
# print(control)
# control.throttle = 1.0

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
