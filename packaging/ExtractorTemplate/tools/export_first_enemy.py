"""Export proven first-body/link selectors as native animation data, never code."""
import argparse
import hashlib
import json
import tempfile
from pathlib import Path
import export_entrance
from inventory_rom import ROM_HASH

PROGRAMS=((0x13f98,(0,4,0x30)),(0x13fba,(0,4,0x2c,0x30)),(0x140ec,(0,)))

def export(rom,project):
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('Unexpected ROM revision')
    old=export_entrance.PROGRAMS
    target=project/'src/core/first_enemy_animation_data.hpp'
    try:
        export_entrance.PROGRAMS=PROGRAMS
        report=export_entrance.export(rom,target)
    finally:
        export_entrance.PROGRAMS=old
    target.write_text(target.read_text(encoding='utf-8').replace('rolo::entrance_data','rolo::first_enemy_animation_data'),encoding='utf-8')
    definitions=[]
    lines=['// Generated immutable actor definitions and score wave; no machine code.','#pragma once',
           '#include "core/actor_definition.hpp"','namespace rolo::first_enemy_definition_data {',
           'inline constexpr std::array<ActorDefinition,3> definitions{{']
    for key in [0x13f98,0x13fba,0x140ec]:
        raw=rom[key:key+34]
        if len(raw)!=34:raise ValueError('Definition extent')
        lines.append('  ActorDefinition{0x%x,{%s}},'%(key,','.join(str(x) for x in raw)))
        definitions.append(dict(key=f'{key:06X}',raw=raw.hex(),sha256=hashlib.sha256(raw).hexdigest()))
    lines+=['}};','inline constexpr std::array<ActorChainDefinition,3> allocations{{',
            '  definitions[0].allocation(), definitions[1].allocation(), definitions[2].allocation()',
            '}};','inline constexpr std::array<std::int8_t,16> score_wave{{']
    wave=rom[0xe468:0xe478]
    lines+=['  '+','.join(str(x if x<128 else x-256) for x in wave),' }};','}']
    (project/'src/core/first_enemy_definition_data.hpp').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    report.update(selector_scope='Body initialization0, normal4, attack0, defeat30; linked initialization0, copied4, attack2C, defeat30; generated score object140EC default0. World mutation/caller closure remains pending.',
        sources=[dict(definition=f'{d:06X}',selectors=list(s)) for d,s in PROGRAMS],
        definitions=definitions,score_wave_source='00E468',score_wave_raw=wave.hex(),
        controls_scope='Frame, Jump, Repeat, Hold, SetReturn, Return, Sound116 and Retire8; original timing comparison pending.',
        playable=False,original_reference_verified=False)
    (project/'docs/stage9/first-enemy-animation-export.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report

def verify_export(rom,project):
    scratch=(project/'build-core').resolve()
    scratch.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='rolo-enemy-export-',dir=scratch) as directory:
        fresh=Path(directory)
        (fresh/'src/core').mkdir(parents=True)
        (fresh/'docs/stage9').mkdir(parents=True)
        report=export(rom,fresh)
        for relative in ['src/core/first_enemy_animation_data.hpp','src/core/first_enemy_definition_data.hpp','docs/stage9/first-enemy-animation-export.json']:
            if (fresh/relative).read_bytes()!=(project/relative).read_bytes():
                raise ValueError('First enemy animation export differs: '+relative)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('rom',type=Path)
    p.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
    print(export(a.rom.read_bytes(),a.project))
