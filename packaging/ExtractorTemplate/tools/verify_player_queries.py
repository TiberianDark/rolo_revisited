"""Generate collision fixtures by querying sparse records directly from the ROM."""
import sys,random,json,argparse
from pathlib import Path
from rolo_maps import word
from rolo_codec import decode_backward_lz
from rolo_extract import font_evidence
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('rom');parser.add_argument('--out',required=True)
args=parser.parse_args()
rom=Path(args.rom).read_bytes();font_evidence(rom);data,_=decode_backward_lz(rom,0x4bc56)
def tile_at(x,y):
    result=0
    for row in range(y//16+1):
        for p in range(word(data,8+row*2),word(data,10+row*2),4):
            kind,origin=word(data,p),word(data,p+2)
            if kind>=1024:continue
            macro=0x70128+word(rom,0x7012e+(kind&127)*2);w,h=rom[macro:macro+2]
            dx=(x-origin)//16;dy=y//16-row
            if not 0<=dx<w or not 0<=dy<h:continue
            if kind&0xff00:dy=h-1-dy
            value=word(rom,macro+2+(dy*w+dx)*2)
            if value:result=value^(4096 if kind&0xff00 else 0)
    return result
def query(x,y,direction):
    tile=tile_at(x,y)
    if not tile&16384:return None
    flip=bool(tile&4096)
    side=([2,0] if flip else [0,2])[direction] if direction<2 else [6,4][direction-2]
    start=0x74876+(tile&511)*8+side;offset,shape=rom[start:start+2]
    coordinate=x if direction<2 else y
    mirror=bool(shape&64)
    if direction>=2:mirror^=flip
    if mirror:coordinate=~coordinate
    height=rom[0x4a71a+(shape&63)*16+(coordinate&15)]
    if height>=128:return None
    if direction==0:boundary=(y&~15)+(31-offset-height if flip else 15-offset+height)
    elif direction==1:boundary=(y&~15)+(offset-height if flip else -16+offset+height)
    elif direction==2:boundary=(x&~15)-16+offset+height
    else:boundary=(x&~15)+15-offset+height
    return boundary,shape^(64 if flip else 0),tile
cases=[]
random.seed(7)
candidates=[(x+random.randrange(16),y+random.randrange(16)) for y in range(0,1440,16) for x in range(0,1984,16) if tile_at(x,y)&16384]
random.shuffle(candidates)
for x,y in [(184,768),(184,752),(920,784),(1050,780)]+candidates[:64]+[(random.randrange(1984),random.randrange(680,850)) for _ in range(16)]:
 for direction in range(4):cases.append((x,y,direction,query(x,y,direction)))
lines=['#pragma once','struct PlayerQueryFixture {int x,y,direction,position,slope,tile;bool valid;};',f'inline constexpr PlayerQueryFixture player_query_fixtures[{len(cases)}]={{']
for x,y,d,result in cases:lines.append(f' {{{x},{y},{d},{result[0] if result else 0},{result[1] if result else 0},{result[2] if result else 0},{str(result is not None).lower()}}},')
lines.append('};')
Path(args.out).write_text('\n'.join(lines)+'\n')
print(len(cases),'independent ROM queries,',sum(c[3] is not None for c in cases),'hits')
