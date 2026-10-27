"""Visualise catalogued actor frames; scene-dependent colours remain explicit."""
import argparse
import hashlib
import html
import json
import struct
from pathlib import Path
from inventory_rom import ROM_HASH
from rolo_maps import long
from rolo_sprites import sprite_pixels
from rolo_stage2 import png_palette


def export(rom, catalog, out):
    report = json.loads((catalog/'manifest.json').read_text())
    if hashlib.sha256(rom).hexdigest() != ROM_HASH or report['rom_sha256'] != ROM_HASH:
        raise ValueError('Unexpected ROM revision')
    out.mkdir(parents=True, exist_ok=True)
    palette = b''.join(rom[long(rom, 0x4b09a+i*4):long(rom, 0x4b09a+i*4)+32] for i in range(4))
    colors = [tuple(((v >> s) & 7)*255//7 for s in (1, 5, 9)) for v in struct.unpack('>64H', palette)]
    frames = {f['descriptor']: f for f in report['frames']}
    programs = {(p['table'], p['selector']): p for p in report['candidate_programs']}
    actors = []
    rendered = set()
    for case in report['cases']:
        definition = case['definition']
        bank = (int.from_bytes(rom[definition+6:definition+8], 'big') >> 13) & 3
        selectors = [p for (table, _), p in programs.items() if table == case['table']]
        descriptors = sorted(set(case.get('descriptors', [])) | {d for p in selectors for d in p.get('descriptors', [])})
        images = []
        for descriptor in descriptors:
            frame = frames[descriptor]
            for variant in frame['variants']:
                raw = (catalog/variant['path']).read_bytes()
                if hashlib.sha256(raw).hexdigest() != variant['sha256']:
                    raise ValueError('Frame hash differs')
                name = f'{descriptor:06X}-{variant["source"]:06X}-palette{bank}.png'
                if name not in rendered:
                    pixels = sprite_pixels(raw, frame['width'], frame['height'])
                    (out/name).write_bytes(png_palette(frame['width'], frame['height'], pixels, colors[bank*16:bank*16+16], 4))
                    rendered.add(name)
                images.append({'image': name, 'descriptor': descriptor, 'source': variant['source']})
        actors.append({'definition': definition, 'handler': case['handler'], 'palette_bank': bank,
                       'candidate_selectors': len(selectors), 'images': images})
    result = {'rom_sha256': ROM_HASH, 'actors': actors, 'rendered_images': len(rendered),
        'scope': 'Actor definitions include enemies, player, objects and effects; species unclassified. Default plus bounded candidate animation selectors, not proven complete animation domains. Colours use Level 1 target palette; other scenes may differ.'}
    (out/'manifest.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    cards = []
    for actor in actors:
        images = ''.join(f'<a href="{v["image"]}"><img src="{v["image"]}" title="Descriptor ${v["descriptor"]:06X}; pixels ${v["source"]:06X}"></a>' for v in actor['images'])
        cards.append(f'<article id="definition-{actor["definition"]:06X}"><h2>Definition ${actor["definition"]:06X}</h2><p>Handler ${actor["handler"]:06X}; {actor["candidate_selectors"]} candidate selectors; {len(actor["images"])} frame variants</p>{images}</article>')
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Rolo actor atlas</title><style>body{background:#101820;color:#eee;font:16px system-ui;margin:24px}article{background:#283641;margin:16px 0;padding:16px}img{image-rendering:pixelated;min-width:48px;max-width:192px;margin:8px;background:#506070}a{color:#8cf}</style><h1>Rolo — original actor artwork</h1><p>'+html.escape(result['scope'])+'</p>'+''.join(cards), encoding='utf-8')
    print(f'{len(actors)} actor definitions; {len(rendered)} palette-specific images')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('rom', type=Path)
    p.add_argument('--catalog', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    export(a.rom.read_bytes(), a.catalog, a.out)
