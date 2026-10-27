from pathlib import Path
import re,struct,sys
p=Path(__file__).resolve().parents[1];sys.path.insert(0,str(p/'tools'))
from export_preview import MAGIC
import hashlib
assert hashlib.sha256((p/'local/rolo.md').read_bytes()).hexdigest()=='9478d47cc1883df42f3714ea485aedd71b541274eb45a3aa7c49f4a3518305e9'
s=(p/'src/core/level1_terrain_data.hpp').read_text()
def arr(name):return list(map(int,re.findall(r'\d+',re.search(name+r'\{\{(.*?)\}\}',s,re.S).group(1))))
quads=arr('quad_words');patterns=arr('bank_patterns');pal=arr('palette_words');ms=re.findall(r'\{(\d+),(\d+),std::span<const std::uint16_t>\(macro_tiles\).subspan\((\d+),(\d+)\)\}',s);w,h,start,count=map(int,ms[84]);tiles=arr('macro_tiles')[start:start+count];records=[]
for bank in range(4):
 pixels=bytearray()
 for y in range(32):
  for x in range(64):
   q=tiles[(y//16)*4+x//16]&511;tile=quads[q*4+(y%16//8)*2+x%16//8]&2047;v=patterns[tile*32+(y%8)*4+(x%8)//2];n=(v>>(0 if x%2 else 4))&15;c=pal[bank*16+n];pixels.extend([((c>>b)&7)*255//7 for b in (1,5,9)]+[255 if n else 0])
 records.append(struct.pack('<6I',3,0x5854524c,bank,64,32,len(pixels))+pixels)
(p/'bin/forest-log-assets.rla').write_bytes(MAGIC+struct.pack('<I',len(records))+b''.join(records))
print('Original forest log asset pack exported')
