import krpc

conn = krpc.connect(name='Debugger')
sc = conn.space_center
av = sc.active_vessel
mj = conn.mech_jeb

def print_parts(part_type='all'):
    if part_type == 'all':
        for part in av.parts.all:
            print(part.name)

    if part_type == 'engines':
        for engine in av.parts.engines:
            for engine in  av.parts.engines:
                print(engine.part.name)

    if part_type == 'resources':
        for resources in av.resources.all:
            print(resources.name)


