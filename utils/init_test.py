import krpc

conn = krpc.connect()
sc = conn.space_center
av = sc.active_vessel

mj = conn.mech_jeb



