"""Export Level1 collectible immutable definitions, animation and original graphics."""
import hashlib,json,re,struct
from pathlib import Path
import export_entrance
from inventory_rom import ROM_HASH
from rolo_sprites import sprite_pixels
from export_preview import rgba,MAGIC

def export(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
    programs=tuple((0x14130+34*i,(0,4)) for i in range(24))+(
        # $144C6 is the immediately active B314 variant of $144A4. Its other
        # 30 definition bytes and animation table are identical in the pinned ROM.
        (0x144a4,(0,4,0x30,0x34)),(0x144c6,(0,4,0x30,0x34)),(0x13f54,(0,4,8,12,16,20,24,28,32,36)),(0x144e8,(0,)),
        (0x14482,(0,4)),(0x14e78,(0,)),(0x14e9a,(0,)),(0x15808,(0,)),(0x157e6,(0,)),(0x1410e,(0,)),
        (0x13f10,(0,4,8,12,16,20,24,28,32,36,52)),(0x13f76,(0,4,8,12,16,20,24,28,32,36,52)),
        (0x13fdc,(0,4,8,48)),(0x14020,(0,4)),(0x13f32,tuple(range(0,60,4))),(0x13ffe,(0,)),
        (0x14042,(0,4)),(0x140ca,(0,4)),
        (0x1487e,(0,4)),(0x14c14,(0,)),
        (0x14818,(0,4)),(0x1483a,(0,4)),(0x1485c,(0,4)),(0x148a0,(0,4)),
        (0x1494a,(0,4,8)),(0x1496c,(0,4)),(0x14bd0,(0,)),(0x14e12,(0,4)),(0x14e56,(0,4,8)),
        (0x14c9c,(0,4)),(0x14cbe,(0,4)),(0x14ce0,(0,4,8)),(0x14064,(0,4)),
        (0x14dac,(0,4)),(0x14dce,(0,4)),(0x14df0,(0,4)),(0x14c58,(0,4)),(0x14c7a,(0,4)),(0x14c36,(0,)),(0x14d8a,(0,)),(0x14906,(0,)),(0x148c2,(0,)),(0x14e34,(0,4)),(0x14a5a,(0,4,8)),(0x157c4,(0,)),(0x14d02,(0,4)),(0x14d24,(0,4)),(0x14d46,(0,4,8)),(0x14d68,(0,)),
        (0x14faa,(0,4,8)),(0x14fcc,(0,4,8)),(0x14fee,(0,4,8)),(0x15010,(0,4,8)),(0x15032,(0,4,8)),(0x15054,(0,4,8)),(0x15076,(0,4,8)),(0x15098,(0,4,8)),(0x150ba,(0,4,8)),(0x150dc,(0,4,8)),(0x150fe,(0,4,8)),(0x15120,(0,4,8)),(0x15142,(0,4,8)),(0x15164,(0,)),(0x15186,(0,)),(0x151a8,(0,)),(0x151ca,(0,)),(0x15296,(0,)),(0x14928,(0,)),(0x1472a,(0,)),(0x1474c,(0,4)),(0x157a2,(0,4)),(0x14086,(0,)),(0x140a8,(0,)), (0x145f8,(0,4)),(0x1461a,(0,4)),(0x1463c,(0,4)),(0x1465e,(0,4)),(0x14680,(0,4)),(0x146a2,(0,4)),(0x146c4,(0,4)),(0x146e6,(0,4)),(0x14708,(0,4)),(0x14460,(0,4)),(0x14ebc,(0,4,8)),(0x14790,(0,4)),(0x147b2,(0,4,8,12)),(0x147d4,(0,4,8,12)),(0x147f6,(0,4)), (0x1450a,(0,)),(0x1452c,(0,)),(0x1454e,(0,)),(0x14570,(0,)),(0x14592,(0,)),(0x145b4,(0,)),(0x145d6,(0,)),(0x151ec,(0,)),(0x1498e,(0,4,8)),(0x149b0,(0,)),(0x149d2,(0,)),(0x149f4,(0,)),(0x14a16,(0,)),(0x14a38,(0,)))
    programs += tuple((key,(0,)) for key in range(0x152b8,0x153c8,34))
    programs += tuple((key,(0,)) for key in range(0x1540c,0x1571a,34))
    programs += ((0x14b26,(0,)),(0x14b48,(0,4)),(0x14b6a,(0,4)),(0x14b8c,(0,)),(0x14bae,(0,)),
                 (0x1520e,(0,4,8,12,16,20)),(0x15230,(0,4,8,12,16,20)),(0x15252,(0,4,8,12,16,20)),(0x15274,(0,4,8)),
                 (0x153c8,(0,4,8,12,16)),(0x153ea,(0,4,8,12,16)),(0x1571a,(0,4,8)),(0x1573c,(0,)))
    programs += ((0x148e4,(0,)),(0x14a7c,(0,)),(0x14a9e,(0,4)),(0x14ac0,(0,4)),(0x14ae2,(0,)),(0x14b04,(0,)))
    programs += ((0x14bf2,(0,)),)
    keys=tuple(key for key,_ in programs)
    target=project/'src/core/level1_object_data.hpp'
    lines=['#pragma once','#include "core/actor_definition.hpp"','namespace rolo::level1_object_data {',f'inline constexpr std::array<ActorDefinition,{len(keys)}> definitions{{{{']
    for key in keys:lines.append('ActorDefinition{0x%x,{%s}},'%(key,','.join(map(str,rom[key:key+34]))))
    lines+=['}};','inline constexpr std::array<std::uint32_t,24> collectible_spawn_table{{',
        ','.join('0x%x'%struct.unpack_from('>I',rom,0x47ba+i*4)[0] for i in range(24)),'}};',
        'inline constexpr std::array<std::uint32_t,37> enemy_spawn_table{{',
        ','.join('0x%x'%struct.unpack_from('>I',rom,0x46c6+i*4)[0] for i in range(37)),'}};',
        'inline constexpr std::array<std::uint32_t,2> special_spawn_table{{', ','.join('0x%x'%v for v in struct.unpack_from('>2I',rom,0x48fc)),'}};',
        'inline constexpr std::array<std::uint32_t,13> generic_spawn_table{{',
        ','.join('0x%x'%struct.unpack_from('>I',rom,0x4762+i*4)[0] for i in range(13)),'}};',
        'inline constexpr std::array<std::uint32_t,4> companion_spawn_table{{',
        ','.join('0x%x'%struct.unpack_from('>I',rom,0x4948+i*4)[0] for i in range(4)),'}};',
        'inline constexpr std::array<std::uint32_t,128> ride_slope_forward{{', ','.join('0x%x'%v for v in struct.unpack_from('>128I',rom,0x8078)),'}};',
        'inline constexpr std::array<std::uint32_t,128> ride_slope_reverse{{', ','.join('0x%x'%v for v in struct.unpack_from('>128I',rom,0x7ff0)),'}};',
        'inline constexpr std::array<std::uint32_t,8> phase_boss_offsets{{', ','.join('0x%x'%v for v in struct.unpack_from('>8I',rom,0xd7c6)),'}};',
        'inline constexpr std::array<std::uint32_t,9> choreography_spawn{{', ','.join('0x%x'%v for v in struct.unpack_from('>9I',rom,0xbe1a)),'}};',
        'inline constexpr std::array<std::uint32_t,18> choreography_permutations{{', ','.join('0x%x'%v for v in struct.unpack_from('>18I',rom,0xbbea)),'}};',
        'inline constexpr std::array<std::uint8_t,9> choreography_groups{{', ','.join(map(str,rom[0xbb84:0xbb8d])),'}};',
        'inline constexpr std::array<std::uint16_t,8> choreography_tiles{{', ','.join(map(str,struct.unpack_from('>8H',rom,0xbe3e))),'}};',
        'inline constexpr std::array<std::uint32_t,17> spawner_rewards{{', ','.join('0x%x'%v for v in struct.unpack_from('>17I',rom,0xb9cc)),'}};',
        'inline constexpr std::array<std::uint8_t,6> spawner_directions{{', ','.join(map(str,rom[0xba5e:0xba64])),'}};',
        'inline constexpr std::array<std::uint8_t,48> boss29_part_offsets{{', ','.join(map(str,rom[0xec94:0xecc4])),'}};',
        'inline constexpr std::array<std::uint16_t,15> common_flash_palette{{', ','.join(map(str,struct.unpack_from('>15H',rom,0x4b7ca))),'}};',
        'inline constexpr std::array<std::uint8_t,24> companion_menu_navigation{{',
        ','.join(map(str,rom[0x2224:0x223c])),'}};','}'];target.write_text('\n'.join(lines)+'\n')
    animation=project/'src/core/level1_object_animation_data.hpp'
    old=export_entrance.PROGRAMS
    try:
        export_entrance.PROGRAMS=programs
        report=export_entrance.export(rom,animation)
    finally:export_entrance.PROGRAMS=old
    animation.write_text(animation.read_text().replace('rolo::entrance_data','rolo::level1_object_animation_data'))
    palette_sources=json.loads((project/'docs/stage9/first-level-roster.json').read_text())['selector']['palette_sources']
    palettes=[]
    for source in palette_sources:
        palettes.append([tuple(((v>>s)&7)*255//7 for s in (1,5,9)) for v in struct.unpack_from('>16H',rom,source)])
    records=[];seen=set()
    for match in re.finditer(r'Frame\{(0x[0-9a-f]+),(0x[0-9a-f]+),(0x[0-9a-f]+),(-?\d+),(-?\d+),(\d+),(\d+),(\d+)\}',animation.read_text()):
        descriptor,left,right,ox,oy,w,h,size=[int(v,0) for v in match.groups()]
        for graphics in (left,right):
            if not graphics or (graphics,w,h) in seen:continue
            seen.add((graphics,w,h))
            for bank,colors in enumerate(palettes):
                pixels=rgba(sprite_pixels(rom[graphics:graphics+size],w,h),colors,True)
                records.append(struct.pack('<6I',3,graphics,bank,w,h,len(pixels))+pixels)
    (project/'bin/level1-object-assets.rla').write_bytes(MAGIC+struct.pack('<I',len(records))+b''.join(records))
    report.update(definitions=[f'{key:06X}' for key in keys],scope='Shared immutable actor definitions and reached animation selectors for connected native callbacks; original art, not complete level fidelity',graphics_records=len(records),rom_sha256=ROM_HASH)
    (project/'docs/stage9/level1-object-export.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':print(export(Path(__file__).resolve().parents[1]))







