import krpc

conn = krpc.connect(name='Debugger')
vessel = conn.space_center.active_vessel

def print_parts(part_type='all'):
    if part_type == 'all':
        for part in vessel.parts.all:
            print(part.name)

    if part_type == 'engines':
        for engine in vessel.parts.engines:
            for engine in  vessel.parts.engines:
                print(engine.part.name)

    if part_type == 'resources':
        for resources in vessel.resources.all:
            print(resources.name)


