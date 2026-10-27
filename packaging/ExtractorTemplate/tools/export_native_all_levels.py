"""Generate immutable native bindings for all70world-linked levels; no ROM execution."""
import hashlib,json,struct
from pathlib import Path
from rolo_maps import word,long,parse_map
from rolo_codec import decode_backward_lz
P=Path(__file__).resolve().parents[1];rom=(P/"local/rolo.md").read_bytes();expected="9478d47cc1883df42f3714ea485aedd71b541274eb45a3aa7c49f4a3518305e9";assert hashlib.sha256(rom).hexdigest()==expected
manifest=json.loads((P/"assets/extracted/all-levels/manifest.json").read_text());entries=[r for r in manifest["selectors"]if r["world_referenced"] or r["selector"] in (35,53,70,71)];assert len(entries)==74
lines=['#pragma once','#include "core/terrain_descriptor.hpp"','#include <array>','namespace rolo::all_native_level_data {'];banks={};report=[]
def array(name,typ,values):
 lines.append(f'inline constexpr std::array<{typ},{len(values)}> {name}{{{{')
 for at in range(0,len(values),24):lines.append(','.join(map(str,values[at:at+24]))+',')
 lines.append('}};')
for bank in sorted({r["layers"]["foreground"]["bank"]for r in entries}):
 ptr=long(rom,0x4afb2+bank*4);assert rom[ptr:ptr+4]==b'ITMS';tiles=[];macros=[]
 for i in range(word(rom,ptr+4)):
  start=ptr+word(rom,ptr+6+i*2);w,h=rom[start:start+2];assert w and h;values=[word(rom,start+2+n*2)for n in range(w*h)];macros.append((w,h,len(tiles),len(values)));tiles.extend(values)
 qptr=long(rom,0x4af6e+bank*4);quads=[]
 for q in range(max(v&511 for v in tiles)+1):
  at=0x6b452+q*8 if q<28 else qptr+(q-28)*8;quads.extend(word(rom,at+n*2)for n in range(4))
 graphics=decode_backward_lz(rom,long(rom,0x4af2a+bank*4))[0];assert len(graphics)%32==0
 collision=rom[long(rom,0x4aff6+bank*4):][:4096];assert len(collision)==4096
 assert all((v&2047)*32+32<=len(graphics)for v in quads[28*4:])
 for name,typ,values in [('tiles','std::uint16_t',tiles),('quads','std::uint16_t',quads),('patterns','std::uint8_t',list(graphics)),('collision','std::uint8_t',list(collision))]:array(f'bank{bank}_{name}',typ,values)
 lines.append(f'inline constexpr std::array<TerrainMacroDefinition,{len(macros)}> bank{bank}_macros{{{{')
 for w,h,first,count in macros:lines.append(f'{{{w},{h},std::span<const std::uint16_t>(bank{bank}_tiles).subspan({first},{count})}},')
 lines.append('}};');banks[bank]=len(macros)
lines.extend(['struct TerrainBank {std::span<const TerrainMacroDefinition> macros;std::span<const std::uint16_t> quads;std::span<const std::uint8_t> patterns,collision;};','inline const TerrainBank& bank(unsigned n){switch(n){'])
for bank in banks:lines.append(f'case {bank}:{{static const TerrainBank data{{bank{bank}_macros,bank{bank}_quads,bank{bank}_patterns,bank{bank}_collision}};return data;}}')
lines.extend(['default:throw std::out_of_range("Native terrain bank not exported");}}'])
for r in entries:
 n=r['selector'];b=r['layers']['foreground']['bank'];assert r['layers']['background']['bank']==b
 for layer in ('foreground','background'):
  data=(P/r['layers'][layer]['binary']['path']).read_bytes();assert hashlib.sha256(data).hexdigest()==r['layers'][layer]['binary']['sha256'];layout=parse_map(data)
  assert all((v['type']&127)<banks[b]for v in layout['records']if v['visual']);array(f'level{n}_{layer}','std::uint8_t',list(data))
 pal=(P/r['palette']['path']).read_bytes();assert hashlib.sha256(pal).hexdigest()==r['palette']['sha256'];array(f'level{n}_palette','std::uint16_t',list(struct.unpack('>64H',pal)))
 report.append(dict(selector=n,bank=b,width=r['layers']['foreground']['width'],height=r['layers']['foreground']['height'],reward=rom[0x4ab1a+n*8+4]))
lines.extend(['struct Level {std::span<const std::uint8_t> foreground,background;std::span<const std::uint16_t,64> palette;std::uint16_t selector,width,height;std::uint8_t reward,bank;};',f'inline constexpr std::array<std::uint16_t,{len(entries)}> selectors{{{{'+','.join(str(r['selector'])for r in entries)+'}};','inline bool connected(unsigned n){for(auto id:selectors)if(id==n)return true;return false;}','inline Level level(unsigned n){switch(n){'])
for r in report:
 n=r['selector'];lines.append(f'case {n}:return {{level{n}_foreground,level{n}_background,level{n}_palette,{n},{r["width"]},{r["height"]},{r["reward"]},{r["bank"]}}};')
lines.extend(['default:throw std::out_of_range("Not a world-linked native level");}}','}'])
out=P/'src/core/all_native_level_data.hpp';out.write_text('\n'.join(lines)+'\n',encoding='utf-8');(P/'docs/stage9/all-native-level-data.json').write_text(json.dumps(dict(rom_sha256=expected,levels=report,banks=banks,header_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),scope='Immutable70world-linked plus4interior MAP/bank/collision/palettebindings. Originalactorcompletenessandfidelitynotcertified.'),indent=2)+'\n');print('Generated70world-linkedlevelsplus4interiorsand7terrainbanks')

fixtures=[]
for level in entries:
 for marker in level['markers']:
  if marker['category']==7:fixtures.append((level['selector'],marker['record_offset'],marker['type'],marker['x'],marker['y']))
(P/'docs/stage9/interior-transition-fixtures.txt').write_text('\n'.join(' '.join(map(str,row))for row in fixtures)+'\n')
