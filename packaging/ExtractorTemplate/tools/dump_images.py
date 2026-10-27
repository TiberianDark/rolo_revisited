"""Installer entry point: regenerate original image catalogues from a user ROM."""
import argparse
import hashlib
import json
from pathlib import Path
from inventory_rom import ROM_HASH
from inventory_animations import catalogue
from export_map_atlas import export as export_maps
from export_actor_atlas import export as export_actors
from export_marker_atlas import export as export_markers
from export_visual_index import export as export_visual_index


def tool_provenance():
    directory=Path(__file__).resolve().parent
    return [{'path':'tools/'+p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
            for p in sorted(directory.glob('*.py'))]


def dump(rom_path, out):
    rom = rom_path.read_bytes()
    if len(rom) != 524288 or hashlib.sha256(rom).hexdigest() != ROM_HASH:
        raise ValueError('Unsupported ROM: expected the pinned 524288-byte USA/Europe revision')
    out.mkdir(parents=True, exist_ok=True)
    completion = out/'image-dump-complete.json'
    # Never retain a success marker if a repeated installer run fails midway.
    completion.unlink(missing_ok=True)
    print('1/4: Extracting actor animation records and original pixel data', flush=True)
    animations = catalogue(rom, out/'catalog'/'animations')
    print('2/4: Rendering maps and oversized map sections', flush=True)
    maps = export_maps(rom, out/'map-atlas')
    print('3/4: Rendering actor gallery with labelled Level 1 palette', flush=True)
    export_actors(rom, out/'catalog'/'animations', out/'actor-atlas')
    print('4/4: Generating recorded marker overlays and checking artifacts', flush=True)
    export_markers(out/'map-atlas')
    visual = export_visual_index(rom, out)
    for row in maps['selectors']:
        for layer in row['layers']:
            for item in [layer]+layer.get('sections', []):
                if hashlib.sha256((out/'map-atlas'/item['image']).read_bytes()).hexdigest() != item['sha256']:
                    raise ValueError('Map image verification failed')
    actors = json.loads((out/'actor-atlas'/'manifest.json').read_text())
    for actor in actors['actors']:
        for item in actor['images']:
            if not (out/'actor-atlas'/item['image']).is_file():
                raise ValueError('Missing actor image')
    artifacts = [{'path': str(p.relative_to(out)).replace('\\','/'),
                  'size': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                 for root in (out/'map-atlas', out/'actor-atlas', out/'catalog'/'animations')
                 for p in sorted(root.rglob('*')) if p.is_file()]
    for name in ('visual-index.html','visual-inventory.json','visual-marker-relations.csv'):
        p=out/name
        artifacts.append({'path':name,'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    result = {'schema':1, 'rom_sha256':ROM_HASH, 'map_counts':maps['counts'],
              'extraction_tool_bundle':tool_provenance(),
              'animation_counts':animations['counts'], 'actor_images':actors['rendered_images'],
              'visual_counts':visual['counts'],
              'artifacts':artifacts, 'known_gaps':[{ 'selector':r['selector'], 'errors':r['errors']}
                                               for r in maps['selectors'] if r['errors']],
              'scope':'Static image extraction, no ROM instruction execution. Not gameplay completion. Actor colours use Level 1 palette; generated world background remains pending.'}
    completion.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('Image dump complete:', completion, flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rom',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    dump(args.rom,args.out)
