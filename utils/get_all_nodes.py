import time
import krpc

# init
conn = krpc.connect(name="Satellites Triangle Orbit")
print("Connected to kRPC")

sc = conn.space_center
vessels = sc.vessels
mj = conn.mech_jeb

nodes_list = []
for vessel in vessels:
    sc.active_vessel = vessel
    time.sleep(2)
    for node in vessel.control.nodes:
        nodes_list.append(node)

print(nodes_list)

