"""Compare immutable map decodes to raw-copy extents without ROM execution."""
import argparse
import json
from pathlib import Path
from inventory_rom import ROM_HASH
from rolo_codec import decode_backward_lz


def catalogue(rom, project):
    manifest = json.loads((project / 'assets/extracted/catalog/manifest.json').read_text(encoding='utf-8'))
    rows = []
    for selector in manifest['selectors']:
        for plane, extent in [('foreground', 4096), ('background', 2048)]:
            if plane == 'background' and selector['selector'] == 0:
                continue
            source = selector[plane]
            raw = rom[source:source+3] == b'MAP'
            data = rom[source:source+extent] if raw else decode_backward_lz(rom, source)[0]
            rows.append(dict(selector=selector['selector'], plane=plane, source=source,
                raw=raw, decoded_size=len(data), raw_copy_size=extent,
                exceeds_raw_copy_extent=len(data) > extent))
    return dict(rom_sha256=ROM_HASH,
        scope='Immutable supplied selector sources compared to loader raw-copy extents; these extents are not independently proven buffer capacities',
        rows=rows, comparisons=len(rows),
        larger_than_raw_extent=sum(row['exceeds_raw_copy_extent'] for row in rows),
        max_foreground=max(row['decoded_size'] for row in rows if row['plane'] == 'foreground'),
        max_background=max(row['decoded_size'] for row in rows if row['plane'] == 'background'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rom', type=Path)
    parser.add_argument('--project', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    result = catalogue(args.rom.read_bytes(), args.project)
    (args.project / 'docs/stage9/level-plane-extents.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(result['comparisons'], 'plane sources;', result['larger_than_raw_extent'], 'larger than raw-copy extent')


if __name__ == '__main__':
    main()
