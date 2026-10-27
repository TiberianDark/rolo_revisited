"""Extract the first selected level's immutable roster; no runtime reachability claim."""
import argparse
import hashlib
import json
from pathlib import Path
from inventory_rom import ROM_HASH
from inventory_spawns import catalogue as spawn_catalogue


def catalogue(rom, project):
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:
        raise ValueError('ROM revision differs')
    manifest=json.loads((project/'assets/extracted/catalog/manifest.json').read_text(encoding='utf-8'))
    selector=next(row for row in manifest['selectors'] if row['selector']==1)
    address=0x4ab1a+8
    foreground=int.from_bytes(rom[address:address+4],'big')
    background=int.from_bytes(rom[address+4:address+8],'big')
    expected=dict(foreground=foreground&0xffffff,background=background&0xffffff,
                  spawn_selector=foreground>>24,background_parameter=background>>24,
                  camera_mode=rom[0x4aeda+1])
    if any(selector[key]!=value for key,value in expected.items()):
        raise ValueError('First-level manifest differs from ROM descriptor')
    markers=[row for row in spawn_catalogue(rom,manifest)['markers'] if row['layout_source']==selector['foreground']]
    groups=[]
    for category in sorted({m['category'] for m in markers}):
        selected=[m for m in markers if m['category']==category]
        groups.append(dict(category=category,category_hex=f'{category:02X}',records=len(selected),
            parameters=sorted({m['parameter'] for m in selected}),
            definitions=sorted({m['definition'] for m in selected if m.get('definition')}),
            initial_handlers=sorted({m['handler'] for m in selected if m.get('handler')})))
    return dict(rom_sha256=ROM_HASH,descriptor_address=f'{address:06X}',
        descriptor_bytes=rom[address:address+8].hex(),selector=selector,markers=markers,groups=groups,
        counts=dict(markers=len(markers),classes=len(groups),
            definitions=len({m['definition'] for m in markers if m.get('definition')}),
            initial_handlers=len({m['handler'] for m in markers if m.get('handler')})),
        scope='Immutable first-level spawn ledger only. Marker counts are not enemy counts. Linked definitions, startup overrides, callbacks, animation spawns, macro/terrain activation, player allocation and dynamic objects require separate dependency closure.',
        complete_first_level_mapping=False)


def markdown(report):
    lines=['# First-level immutable object roster','',
        'Regenerate with `tools/inventory_first_level.py local/rolo.md` from the project directory.',
        '',report['scope'],'',
        '| Marker class | Records | Parameter bytes | Definition addresses | Initial handler addresses |',
        '|---|---:|---|---|---|']
    for row in report['groups']:
        fmt=lambda values: ', '.join(f'${value:06X}' for value in values) or 'Separate path / unresolved'
        lines.append('| $'+row['category_hex']+' | '+str(row['records'])+' | '+', '.join(f'${v:02X}' for v in row['parameters'])+' | '+fmt(row['definitions'])+' | '+fmt(row['initial_handlers'])+' |')
    lines+=['','Detailed marker positions and raw classes are in [first-level-roster.json](first-level-roster.json).',
        'Each record must be accounted for, including failure, offscreen disposal and re-entry. An initial handler is not a complete object lifecycle.',
        '', 'See [FIRST-LEVEL-CHECKLIST.md](FIRST-LEVEL-CHECKLIST.md) for the playable-level requirements.','']
    return '\n'.join(lines)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('rom',type=Path)
    parser.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1]);args=parser.parse_args()
    report=catalogue(args.rom.read_bytes(),args.project);directory=args.project/'docs/stage9'
    (directory/'first-level-roster.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    (directory/'FIRST-LEVEL-ROSTER.md').write_text(markdown(report),encoding='utf-8')
    print(json.dumps(report['counts']))


if __name__=='__main__':main()
