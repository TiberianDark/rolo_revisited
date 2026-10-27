"""Development-only migration; never include source headers or packs in release media."""
import argparse, hashlib, json, re, shutil, struct
from pathlib import Path

FORMATS = {'uint8_t':'B','int8_t':'b','uint16_t':'H','int16_t':'h','uint32_t':'I','int32_t':'i'}
def declaration(text, name):
    pattern = r'inline\s+constexpr\s+std::array<([^,]+),\s*(\d+)>\s*'+re.escape(name)+r'\s*\{\{(.*?)\}\};'
    match = re.search(pattern, text, re.S)
    if not match:
        # Runtime-loaded scalar tables use mutable single-brace declarations.
        pattern = r'(?:inline\s+)?(?:constexpr\s+)?std::array<([^,]+),\s*(\d+)>\s*'+re.escape(name)+r'\s*\{([^{}]*)\};'
        match = re.search(pattern, text, re.S)
    if not match: raise ValueError('Unsupported declaration: '+name)
    return match

def items(text):
    result=[];start=0;brace=paren=0
    for i,ch in enumerate(text):
        if ch=='{':brace+=1
        elif ch=='}':brace-=1
        elif ch=='(':paren+=1
        elif ch==')':paren-=1
        elif ch==',' and brace==0 and paren==0:
            if text[start:i].strip():result.append(text[start:i].strip())
            start=i+1
    if text[start:].strip():result.append(text[start:].strip())
    return result

def parseint(v): return int(v.strip().rstrip('uUlL'),0)

def pack_record(entry, body, source):
    kind=entry['type'];schema=entry.get('schema',{}).get('id','')
    data=bytearray()
    if kind=='TerrainMacroDefinition':
        refs=set()
        rows=re.findall(r'\{(\d+),(\d+),std::span<const std::uint16_t>\((\w+)\).subspan\((\d+),(\d+)\)\}',body)
        for w,h,target,offset,count in rows:
            w,h,offset,count=map(int,(w,h,offset,count));tile=next(r for r in entry['_resources'] if r['header']==entry['header'] and r['name']==target)
            if w*h!=count or offset+count>tile['count']:raise ValueError('Invalid terrain macro')
            refs.add(target);data+=struct.pack('<BBII',w,h,offset,count)
        if len(refs)!=1:raise ValueError('Terrain macro tile resource is ambiguous')
        desc={'id':'terrain-macro-v1','fields':['width:u8','height:u8','tile_offset:u32','tile_count:u32'],'tile_resource':next(iter(refs)),'record_bytes':10}
    else:
        rows=items(body)
        if kind=='Frame' and (schema=='animation-frame-v1' or entry['header']!='actor_pattern_data.hpp'):
            for row in rows:
                values=items(row[len('Frame'):].strip()[1:-1]);data+=struct.pack('<IIIhhHHH',*map(parseint,values))
            desc={'id':'animation-frame-v1','fields':['descriptor:u32','left_graphics:u32','right_graphics:u32','offset_x:i16','offset_y:i16','width:u16','height:u16','bytes:u16'],'record_bytes':22}
        elif kind=='Frame':
            for row in re.findall(r'Frame\{([0-9, ]+)\}',body):data+=struct.pack('<IIIII',*map(int,row.split(',')))
            desc={'id':'frame-v1','fields':['source:u32','width:u32','height:u32','offset:u32','size:u32'],'record_bytes':20}
        elif kind=='Sprite':
            for row in rows:
                values=items(row[len('Sprite'):].strip()[1:-1]);data+=struct.pack('<IIII',*map(parseint,values))
            desc={'id':'sprite-v1','fields':['source:u32','width:u32','height:u32','offset:u32'],'record_bytes':16}
        elif kind=='AnimationNode':
            enumtext=(source/'animation.hpp').read_text();block=re.search(r'enum class AnimationOp\s*\{(.*?)\};',enumtext,re.S)[1]
            enums={n.strip():i for i,n in enumerate(block.replace('\n',' ').split(',')) if n.strip()}
            for row in rows:
                values=items(row[len('AnimationNode'):].strip()[1:-1]);op=values[0].split('::')[-1]
                data+=struct.pack('<IHiiiI',enums[op],parseint(values[1]),*map(parseint,values[2:]))
            desc={'id':'animation-node-v1','fields':['op:i32','parameter:u16','frame:i32','next:i32','target:i32','evidence_address:u32'],'record_bytes':22}
        elif kind=='AnimationProgram':
            for row in rows:data+=struct.pack('<IHBi',*map(parseint,items(row[len(kind):].strip()[1:-1])))
            desc={'id':'animation-program-v1','fields':['definition:u32','selector:u16','delay:u8','start:i32'],'record_bytes':11}
        elif kind=='Track':
            for row in rows:data+=struct.pack('<IIIIII',*map(parseint,items(row[1:-1])))
            desc={'id':'tile-track-v1','fields':['cache_byte_offset:u32','delay:u32','first:u32','bytes:u32','sequence_first:u32','sequence_count:u32'],'record_bytes':24}
        elif kind=='ActorDefinition':
            for row in rows:
                m=re.fullmatch(r'ActorDefinition\s*\{\s*([^,]+),\s*\{(.*?)\}\s*\}',row,re.S)
                values=[parseint(x) for x in m[2].split(',') if x.strip()]
                if len(values)!=34:raise ValueError('ActorDefinition requires 34 bytes')
                data+=struct.pack('<I34B',parseint(m[1]),*values)
            desc={'id':'actor-definition-v1','fields':['key:u32','data:u8[34]'],'record_bytes':38}
        elif kind=='EnemyBurstRecord':
            for row in rows:
                vals=items(row[1:-1]);data+=struct.pack('<I4B',parseint(vals[0]),*map(parseint,items(vals[1][1:-1])))
            desc={'id':'enemy-burst-v1','fields':['definition:u32','bytes:u8[4]'],'record_bytes':8}
        elif kind=='Graphic':
            for row in rows:
                value=row[len(kind):].strip() if row.startswith(kind) else row
                data+=struct.pack('<IIIII',*map(parseint,items(value[1:-1])))
            desc={'id':'graphic-v1','fields':['width:u32','height:u32','frame_size:u32','first:u32','palette:u32'],'record_bytes':20}
        elif kind=='Piece':
            for row in rows:
                vals=items(row[len(kind):].strip()[1:-1]);data+=struct.pack('<7B4B',*map(parseint,vals[:7]),*map(parseint,items(vals[7][1:-1])))
            desc={'id':'map-piece-v1','fields':['selector:u8','group:u8','row:u8','column:u8','stride:u8','xbase:u8','edges:u8','neighbors:u8[4]'],'record_bytes':11}
        elif kind=='Descriptor':
            for row in rows:data+=struct.pack('<IBB',*map(parseint,items(row[len(kind):].strip()[1:-1])))
            desc={'id':'route-descriptor-v1','fields':['pointer:u32','negate_x:u8','negate_y:u8'],'record_bytes':6}
        elif kind=='Stream':
            for row in rows:data+=struct.pack('<IIH',*map(parseint,items(row[len(kind):].strip()[1:-1])))
            desc={'id':'route-stream-v1','fields':['pointer:u32','terminator:u32','pairs:u16'],'record_bytes':10}
        else:raise ValueError('Unsupported structured type: '+kind)
    if len(data)!=entry['count']*desc['record_bytes']:raise ValueError('Structured record size mismatch: '+entry['name'])
    return bytes(data),desc

def migrate(source, original, destination, generated):
    manifest = json.loads((original/'manifest.json').read_text())
    assert (manifest['format'],manifest['version'],manifest['encoding']) == ('rolo-resources',1,'little-endian')
    if destination.exists(): raise ValueError('Output must be a new directory')
    all_entries=manifest['resources']+manifest.get('excluded_structured_arrays',[])
    texts = {r['header']:(source/r['header']).read_text() for r in all_entries}
    resources = []
    bodies = []
    for entry in manifest['resources']:
        m = declaration(texts[entry['header']], entry['name'])
        if entry['type'] in FORMATS:
            values = [int(v.strip(),0) for v in m[3].split(',') if v.strip()]
            data = struct.pack('<'+FORMATS[entry['type']]*len(values), *values)
            assert len(values)==entry['count'] and len(data)==entry['bytes'], entry
        else:
            info=dict(entry);info['_resources']=manifest['resources']
            data,schema=pack_record(info,m[3],source);entry['schema']=schema
            assert len(data)==entry['bytes'], entry
        assert hashlib.sha256(data).hexdigest()==entry['sha256'], entry
        assert data==(original/entry['path']).read_bytes(), entry
        resources.append((dict(entry),data))
    for entry in manifest['excluded_structured_arrays']:
        m = declaration(texts[entry['header']], entry['name'])
        info=dict(entry);info['_resources']=manifest['resources']
        out,schema=pack_record(info,m[3],source)
        if 'bytes' in entry: assert len(out)==entry['bytes'],entry
        new = {k:entry[k] for k in ('header','name','type','count')}
        new.update(bytes=len(out),path=Path(entry['header']).stem+'/'+entry['name']+'.bin',sha256=hashlib.sha256(out).hexdigest(),schema=schema)
        resources.append((new,bytes(out)))
    destination.mkdir(parents=True)
    for entry,data in resources:
        path=destination/entry['path']; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)
    manifest.update(resources=[r for r,_ in resources], excluded_structured_arrays=[],resource_count=len(resources),total_binary_bytes=sum(len(d) for _,d in resources),structured_schema_version=1)
    (destination/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    generated.mkdir(parents=True,exist_ok=True)
    calls=[]
    for entry,data in resources:
        header=entry['header']; name=entry['name']; text=texts[header]
        m=declaration(text,name)
        namespace=re.search(r'namespace\s+([\w:]+)\s*\{',text)[1]
        target=namespace+'::'+name
        replacement=f'inline std::array<{m[1]},{m[2]}> {name}{{}};'
        texts[header]=text[:m.start()]+replacement+text[m.end():]
        args=f'root, "{entry["path"]}", "{entry["sha256"]}", {target}'
        if entry['type'] in FORMATS: calls.append('    load_numeric('+args+');')
        else:
            loader={'TerrainMacroDefinition':'load_macros','Frame':'load_animation_frames' if entry['schema']['id']=='animation-frame-v1' else 'load_frames','Sprite':'load_sprites','AnimationNode':'load_animation_nodes','AnimationProgram':'load_animation_programs','Track':'load_tracks','ActorDefinition':'load_actor_definitions','EnemyBurstRecord':'load_enemy_bursts','Graphic':'load_graphics','Piece':'load_pieces','Descriptor':'load_descriptors','Stream':'load_streams'}[entry['type']]
            extra=', '+namespace+'::'+entry['schema']['tile_resource'] if entry['type']=='TerrainMacroDefinition' else ''
            calls.append('    '+loader+'('+args+extra+');')
    for derived in manifest.get('derived_arrays_to_rebuild',[]):
        header=derived['header'];text=texts[header];name=derived['name']
        m=re.search(r'inline\s+constexpr\s+std::array<ActorChainDefinition,\s*(\d+)>\s*'+re.escape(name)+r'\s*\{\{.*?\}\};',text,re.S)
        if not m:raise ValueError('Missing derived array: '+name)
        count=int(m[1]);ns=re.search(r'namespace\s+([\w:]+)\s*\{',text)[1]
        texts[header]=text[:m.start()]+f'inline std::array<ActorChainDefinition,{count}> {name}{{}};'+text[m.end():]
        calls.append(f'    for(std::size_t i=0;i<{count};++i) {ns}::{name}[i]={ns}::definitions[i].allocation();')
    for header,text in texts.items(): (source/header).write_text(text)
    digest=hashlib.sha256((destination/'manifest.json').read_bytes()).hexdigest()
    code='#pragma once\n#include "resource_loader.hpp"\n'+''.join('#include "'+h+'"\n' for h in sorted(texts))
    code+='namespace rolo::resources {\ninline void initialize(const std::filesystem::path& root) {\n'
    code+=f'    checked_bytes(root, "manifest.json", "{digest}", {len((destination/"manifest.json").read_bytes())});\n'
    code+='\n'.join(calls)+'\n}\n}\n'
    (source/'resource_bindings.hpp').write_text(code)
    (generated/'catalog.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'numeric_resources':sum(1 for e,_ in resources if e['type'] in FORMATS),'structured_resources':sum(1 for e,_ in resources if e['type'] not in FORMATS),'resources':len(resources),'bytes':manifest['total_binary_bytes']}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('original',type=Path);p.add_argument('destination',type=Path);p.add_argument('generated',type=Path)
    a=p.parse_args();migrate(a.source,a.original,a.destination,a.generated)

