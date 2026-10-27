"""Independent byte comparison of generated forest artwork with the pinned ROM.

Does not import or call the exporter, execute ROM instructions, or certify the
animation player, hardware queue or final game composition.
"""
import hashlib,json,re,struct
from pathlib import Path
PIN='9478d47cc1883df42f3714ea485aedd71b541274eb45a3aa7c49f4a3518305e9'
def verify(project):
    rom=(project/'local/rolo.md').read_bytes()
    assert hashlib.sha256(rom).hexdigest()==PIN,'Wrong ROM revision'
    header=(project/'src/core/forest_tile_animation_data.hpp').read_text()
    def array(name):
        match=re.search(r'array<std::uint8_t,(\d+)> '+name+r'\{\{(.*?)\}\};',header,re.S)
        assert match,'Missing exported array'
        values=bytes(int(v) for v in re.findall(r'\d+',match[2]));assert len(values)==int(match[1]);return values
    patterns=array('patterns');sequences=array('sequences')
    rows=[tuple(map(int,m.groups())) for m in re.finditer(r'^\{(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)\},$',header,re.M)]
    table=struct.unpack_from('>I',rom,0xfb72+4)[0]
    frames=[];pattern_cursor=sequence_cursor=0
    for index,row in enumerate(rows):
        source,sequence_source,cache_offset,delay,_=struct.unpack_from('>IIHBB',rom,table+index*12)
        assert source,'Export extends past original table'
        sequence=[]
        for offset in range(256):
            value=rom[sequence_source+offset]
            if value>=128:break
            sequence.append(value)
        else:raise AssertionError('Missing original sequence terminator')
        assert sequence
        size=(max(sequence)+1)*128
        assert row==(cache_offset,delay,pattern_cursor,size,sequence_cursor,len(sequence)),'Exported track metadata differs'
        assert sequences[sequence_cursor:sequence_cursor+len(sequence)]==bytes(sequence),'Frame sequence differs'
        for frame in range(size//128):
            original=rom[source+frame*128:source+(frame+1)*128]
            exported=patterns[pattern_cursor+frame*128:pattern_cursor+(frame+1)*128]
            assert original==exported,f'Artwork differs in track{index} frame{frame}'
            frames.append(dict(track=index,frame=frame,source=source+frame*128,bytes=128,sha256=hashlib.sha256(original).hexdigest()))
        pattern_cursor+=size;sequence_cursor+=len(sequence)
    assert len(rows)==6 and struct.unpack_from('>I',rom,table+len(rows)*12)[0]==0,'Incomplete table coverage'
    assert pattern_cursor==len(patterns) and sequence_cursor==len(sequences),'Unverified trailing data'
    result=dict(component='Original forest animation artwork export',status='green',scope='All six bank1 tracks: exact artwork bytes, sequence bytes and immutable track metadata from the pinned supplied ROM.',
        excluded='Runtime animation timing, native rendering/composition, device queue/SAT behaviour and full gameplay fidelity.',rom_sha256=PIN,tracks=len(rows),frame_entries=len(frames),distinct_source_frames=len({f['source'] for f in frames}),artwork_bytes=len(patterns),sequence_bytes=len(sequences),different_bytes=0,
        header_sha256=hashlib.sha256(header.encode()).hexdigest(),verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),frames=frames)
    return result
if __name__=='__main__':
    project=Path(__file__).resolve().parents[1];result=verify(project)
    (project/'docs/stage9/forest-animation-artwork-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('component','status','tracks','frame_entries','distinct_source_frames','artwork_bytes','different_bytes')}))
