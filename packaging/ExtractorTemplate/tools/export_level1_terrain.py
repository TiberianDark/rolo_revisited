"""Export immutable level-one MAP bytes and ITMS words; no CPU execution."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from rolo_maps import word,long,parse_map
from rolo_codec import decode_backward_lz

def generate(project,selector=1):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
    source=long(rom,0x4ab1a+selector*8)&0xffffff
    data=rom[source:source+4096] if rom[source:source+3]==b'MAP' else decode_backward_lz(rom,source)[0]
    layout=parse_map(data);bank=layout['bank'];macro_source=long(rom,0x4afb2+bank*4)
    background_source=long(rom,0x4ab1a+selector*8+4)&0xffffff
    background=rom[background_source:background_source+4096] if rom[background_source:background_source+3]==b'MAP' else decode_backward_lz(rom,background_source)[0]
    background_layout=parse_map(background)
    palette_sources=[long(rom,0x4b08a+selector*16+i*4) for i in range(4)]
    palette=[word(rom,p+n*2) for p in palette_sources for n in range(16)]
    slope_forward=[long(rom,0x7e58+n*4) for n in range(128)]
    slope_reverse=[long(rom,0x7ee0+n*4) for n in range(128)]
    slope_run_forward=[long(rom,0x7f68+n*4) for n in range(128)]
    slope_run_reverse=[long(rom,0x7ff0+n*4) for n in range(128)]
    if rom[macro_source:macro_source+4]!=b'ITMS':raise ValueError('Missing ITMS')
    count=word(rom,macro_source+4);macros=[];tiles=[]
    for i in range(count):
        relative=word(rom,macro_source+6+i*2)
        start=macro_source+relative;w,h=rom[start:start+2]
        if not w or not h or w*h*2>=0x8000:raise ValueError('Unproved macro dimensions')
        values=[word(rom,start+2+n*2) for n in range(w*h)]
        macros.append(dict(index=i,source=start,width=w,height=h,first=len(tiles),count=len(values)))
        tiles.extend(values)
    quad_source=long(rom,0x4af6e+bank*4)
    quad_count=max(t&511 for t in tiles)+1
    quads=[]
    for i in range(quad_count):
        start=0x6b452+i*8 if i<28 else quad_source+(i-28)*8
        quads.extend(word(rom,start+n*2) for n in range(4))
    graphics_source=long(rom,0x4af2a+bank*4)
    graphics=decode_backward_lz(rom,graphics_source)[0]
    if len(graphics)%32:raise ValueError('Incomplete decoded pattern')
    common=rom[0x53dc2:0x53dc2+0x6b0*2]
    if any((q&2047)*32+32>len(graphics) for q in quads[28*4:]):raise ValueError('Quad pattern outside decoded bank')
    visual=[r for r in layout['records'] if r['visual']]
    if any((r['type']&127)>=count for r in visual):raise ValueError('MAP macro index outside exported bank')
    if any((r['type']&127)>=count for r in background_layout['records'] if r['visual']):raise ValueError('Background macro outside shared bank')
    out=['#pragma once','#include "core/terrain_descriptor.hpp"','#include <array>',f'namespace rolo::level{selector}_terrain_data {{']
    out.append(f'inline constexpr std::uint8_t reward_selector={long(rom,0x4ab1a+selector*8+4)>>24}; // $37EA background pointer high byte, F26F.')
    def array(name,ctype,values):
        out.append(f'inline constexpr std::array<{ctype},{len(values)}> {name}{{{{')
        for n in range(0,len(values),24):out.append('  '+','.join(str(v) for v in values[n:n+24])+',')
        out.append('}};')
    array('map_bytes','std::uint8_t',data);array('macro_tiles','std::uint16_t',tiles)
    array('quad_words','std::uint16_t',quads)
    array('bank_patterns','std::uint8_t',graphics)
    array('common_patterns','std::uint8_t',common)
    array('background_map_bytes','std::uint8_t',background)
    array('palette_words','std::uint16_t',palette)
    array('history_selector_bytes','std::uint8_t',rom[0x6814:0x684e])
    # 17 offset pairs, followed by four literal count2 tables of three 8-byte records.
    mutation=rom[0x8d8e:0x8e3a]
    if len(mutation)!=172 or [word(mutation,p) for p in (68,94,120,146)]!=[2,2,2,2]:raise ValueError('Post-motion table shape differs')
    array('post_motion_table_bytes','std::uint8_t',mutation)
    array('rolo_slope_forward','std::uint32_t',slope_forward)
    array('rolo_slope_reverse','std::uint32_t',slope_reverse)
    array('rolo_slope_run_forward','std::uint32_t',slope_run_forward)
    array('rolo_slope_run_reverse','std::uint32_t',slope_run_reverse)
    out.append(f'inline constexpr std::array<TerrainMacroDefinition,{count}> macros{{{{')
    for m in macros:out.append(f"  {{{m['width']},{m['height']},std::span<const std::uint16_t>(macro_tiles).subspan({m['first']},{m['count']})}},")
    out.extend(['}};',f'inline constexpr std::uint16_t width={layout["width"]},height={layout["height"]};','}'])
    header='\n'.join(out)+'\n'
    report=dict(rom_sha256=ROM_HASH,map_source=f'{source:06X}',bank=bank,macro_source=f'{macro_source:06X}',macros=macros,
        map_bytes=len(data),map_sha256=hashlib.sha256(data).hexdigest(),map_records=len(layout['records']),
        visual_records=len(visual),special_records=len(layout['records'])-len(visual),macro_words=len(tiles),
        quad_source=f'{quad_source:06X}',quad_prefix_count=quad_count,
        graphics_source=f'{graphics_source:06X}',graphics_bytes=len(graphics),graphics_sha256=hashlib.sha256(graphics).hexdigest(),
        common_source='053DC2',common_bytes=len(common),common_destination_pattern=0x594,common_sha256=hashlib.sha256(common).hexdigest(),
        background_source=f'{background_source:06X}',background_bytes=len(background),background_sha256=hashlib.sha256(background).hexdigest(),
        background_width=background_layout['width'],background_height=background_layout['height'],background_header_bank=background_layout['bank'],
        palette_sources=[f'{p:06X}' for p in palette_sources],palette_words=palette,
        history_selector_window=dict(source='006814',end_exclusive='00684E',bytes=58,scope='Bounded candidate window ending at next accepted function; all reaching selector domains remain pending.'),
        post_motion_tables=dict(source='008D8E',end_exclusive='008E3A',bytes=172,relative_tables=[68,94,120,146],sha256=hashlib.sha256(mutation).hexdigest(),scope='17-pair literal prefix inferred from first relative table68; bank1/6 nonnegative pairs, othersFFFF. All reaching bank domains and adjacent reads remain unproven.'),
        rolo_slope_read_windows=dict(forward='007E58',reverse='007EE0',run_forward='007F68',run_reverse='007FF0',slots=64,scope='Literal reachable 6-bit read windows, not a claim of 64 semantic table definitions; windows overlap adjacent ROM data.'),
        header_sha256=hashlib.sha256(header.encode()).hexdigest(),
        scope='Immutable level1 foreground/background MAP decode, selected shared ITMS/quad/pattern bank and target palette. Not palette transition timing, mutation/spawn semantics, runtime streaming or reference fidelity proof.',world_integrated=False)
    return header,report

def verify(project):
    header,report=generate(project)
    if (project/'src/core/level1_terrain_data.hpp').read_text(encoding='utf-8')!=header:raise ValueError('Stale level1 terrain header')
    if json.loads((project/'docs/stage9/level1-terrain-assets.json').read_text(encoding='utf-8'))!=report:raise ValueError('Stale level1 terrain report')

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--selector',type=int,choices=(1,2,3,4,8),default=1);args=parser.parse_args()
    project=Path(__file__).resolve().parents[1];header,report=generate(project,args.selector)
    report['scope']=report['scope'].replace('level1',f'level{args.selector}')
    (project/f'src/core/level{args.selector}_terrain_data.hpp').write_text(header,encoding='utf-8')
    (project/f'docs/stage9/level{args.selector}-terrain-assets.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print({key:report[key] for key in ('map_bytes','map_records','visual_records','special_records','macro_words')})


