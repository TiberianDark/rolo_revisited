"""Pinned data-only definitions for terrain macros used as dynamic platforms."""
import hashlib,json,struct
from pathlib import Path
from inventory_rom import ROM_HASH
from rolo_maps import parse_map
P=Path(__file__).resolve().parents[1]
def export(p=P):
 r=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(r).hexdigest()==ROM_HASH
 manifest=json.loads((p/'assets/extracted/all-levels/manifest.json').read_text());pairs=set();fixtures={}
 for level in manifest['selectors']:
  if not level['world_referenced'] and level['selector'] not in (35,53,70,71):continue
  layer=level['layers']['foreground'];data=(p/layer['binary']['path']).read_bytes();assert hashlib.sha256(data).hexdigest()==layer['binary']['sha256']
  for record in parse_map(data)['records']:
   if 0x2000<=record['type']<0x4000:
    pairs.add((layer['bank'],record['type']&255))
    mode=(record['type']>>8)-32
    if 0<=mode<=22:
     # record coordinates supplied by parse_map are original decoded MAP data.
     fixtures.setdefault((layer['bank'],mode),(level['selector'],record))
 (p/'docs/stage9/dynamic-platform-fixtures.txt').write_text('\n'.join(f"{selector} {record['offset']} {record['type']} {record['x']} {record['y']}" for selector,record in fixtures.values())+'\n')
 lines=['#pragma once','#include "core/actor_definition.hpp"','namespace rolo::dynamic_platform_data {',f'inline constexpr std::array<ActorDefinition,{len(pairs)}> definitions{{{{']
 report=[]
 for bank,index in sorted(pairs):
  table=struct.unpack_from('>I',r,0x4afb2+bank*4)[0];at=table+struct.unpack_from('>H',r,table+6+index*2)[0];width,height=r[at]*16,r[at+1]*16;units=width*height//2;assert 0<units<32768
  key=0xffff6000 if (bank,index)==(1,84) else 0xffff6100+bank*256+index
  d=bytearray(34);struct.pack_into('>H',d,4,units);d[7]=2;struct.pack_into('>HHI',d,8,0x3ac8,24,0xbe4e);d[27]=255
  lines.append('ActorDefinition{0x%x,{%s}},'%(key,','.join(map(str,d))));report.append(dict(bank=bank,macro=index,source=at,width=width,height=height,units=units,key=key))
 lines+=['}};','inline constexpr std::uint32_t definition_key(unsigned bank,unsigned macro){return bank==1&&macro==84?0xffff6000u:0xffff6100u+bank*256+macro;}','inline constexpr bool is_definition(std::uint32_t key){for(const auto&d:definitions)if(d.key==key)return true;return false;}','}']
 (p/'src/core/dynamic_platform_data.hpp').write_text('\n'.join(lines)+'\n');(p/'docs/stage9/dynamic-platform-export.json').write_text(json.dumps(dict(rom_sha256=ROM_HASH,records=report),indent=2)+'\n');return len(pairs)
if __name__=='__main__':print(export())
