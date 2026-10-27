"""Reproduce immutable CA0A direction-vector tables from the pinned ROM."""
import hashlib,struct
from pathlib import Path
from inventory_rom import ROM_HASH
def export(p):
 rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
 pointers=struct.unpack_from('>8I',rom,0xca28);assert pointers==tuple(0xcab8+i*72 for i in range(8))
 values=[struct.unpack_from('>18I',rom,at) for at in pointers]
 lines=['#pragma once','#include <array>','#include <cstdint>','namespace rolo::direction_vector_data {','inline constexpr std::array<std::array<std::uint32_t,18>,8> tables{{']
 lines += ['{{'+','.join(f'0x{x:08x}u' for x in row)+'}},' for row in values];lines+=['}};','}']
 (p/'src/core/direction_vector_data.hpp').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 # Independent complete output fixture: quadrant sign/permutation matrices, not native switch.
 outputs=[]
 for bank,row in enumerate(values):
  for angle in range(64):
   octant,within=divmod(angle,8);index=8-within if octant%2 else within;a,b=row[index*2:index*2+2]
   xy=(a,b) if octant in (0,3,4,7) else (b,a)
   x=xy[0] if octant<4 else -xy[0];y=-xy[1] if octant in (0,1,6,7) else xy[1];outputs.append((x&0xffffffff,y&0xffffffff))
 lines=['#pragma once','#include <array>','#include <cstdint>','inline constexpr std::array<std::array<std::uint32_t,2>,512> expected_vectors{{']
 lines+=['{{'+','.join(f'0x{x:08x}u' for x in xy)+'}},' for xy in outputs];lines+=['}};']
 (p/'tests/direction_vector_expected.hpp').write_text('\n'.join(lines)+'\n',encoding='utf-8')
if __name__=='__main__':export(Path(__file__).resolve().parents[1])
