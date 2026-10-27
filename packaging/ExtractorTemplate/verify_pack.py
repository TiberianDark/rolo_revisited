"""Strict development pack verification, including structured references."""
import hashlib,json,struct
from pathlib import Path

WIDTHS={'uint8_t':1,'int8_t':1,'uint16_t':2,'int16_t':2,'uint32_t':4,'int32_t':4}
def verify(root):
    root=Path(root).resolve()
    m=json.loads((root/'manifest.json').read_text())
    if (m.get('format'),m.get('version'),m.get('encoding'))!=('rolo-resources',1,'little-endian'): raise ValueError('Unsupported format/version/encoding')
    entries=m['resources'];seen=set();total=0;by_key={}
    for e in entries:
        path=Path(e['path'])
        if path.is_absolute() or path.drive or '..' in path.parts or not (root/path).resolve().is_relative_to(root):raise ValueError('Unsafe path')
        key=(e['header'],e['name'])
        if key in by_key or e['path'].casefold() in seen:raise ValueError('Duplicate resource')
        seen.add(e['path'].casefold());by_key[key]=e
        width=WIDTHS.get(e['type'],e.get('schema',{}).get('record_bytes'))
        if width is None or type(e['count']) is not int or e['count']<0 or e['bytes']!=e['count']*width: raise ValueError('Invalid size')
        data=(root/path).read_bytes()
        if len(data)!=e['bytes'] or hashlib.sha256(data).hexdigest()!=e['sha256']:raise ValueError('Size/hash mismatch')
        total+=len(data)
    for e in entries:
        if e['type']=='TerrainMacroDefinition':
            if e['schema']['id']!='terrain-macro-v1':raise ValueError('Unsupported terrain schema')
            tiles=by_key[e['header'],e['schema']['tile_resource']]
            if tiles['type']!='uint16_t':raise ValueError('Wrong tile type')
            for w,h,offset,count in struct.iter_unpack('<BBII',(root/e['path']).read_bytes()):
                if w*h!=count or offset+count>tiles['count']:raise ValueError('Invalid tile span')
        elif e['type'] not in WIDTHS:
            allowed={
                'Frame':{('frame-v1',20),('animation-frame-v1',22)},
                'Sprite':{('sprite-v1',16)},
                'AnimationNode':{('animation-node-v1',22)},
                'AnimationProgram':{('animation-program-v1',11)},
                'Track':{('tile-track-v1',24)},
                'ActorDefinition':{('actor-definition-v1',38)},
                'EnemyBurstRecord':{('enemy-burst-v1',8)},
                'Graphic':{('graphic-v1',20)},
                'Piece':{('map-piece-v1',11)},
                'Descriptor':{('route-descriptor-v1',6)},
                'Stream':{('route-stream-v1',10)},
            }
            schema=e.get('schema',{})
            if (schema.get('id'),schema.get('record_bytes')) not in allowed.get(e['type'],set()):raise ValueError('Unsupported record schema')
            if e['type']=='AnimationNode':
                for row in struct.iter_unpack('<IHiiiI',(root/e['path']).read_bytes()):
                    if row[0]>30:raise ValueError('Invalid animation opcode')
    if m['resource_count']!=len(entries) or m['total_binary_bytes']!=total or m['excluded_structured_arrays']:raise ValueError('Incomplete pack')
    return {'resources':len(entries),'bytes':total,'verified':True}

if __name__=='__main__':
    import sys
    print(json.dumps(verify(sys.argv[1])))
