"""Read immutable world route descriptors and byte pairs, never execute ROM code."""
import argparse
import hashlib
import json
from pathlib import Path
from inventory_rom import ROM_HASH


def route_pairs(data, start, end):
    cursor = start
    pairs = []
    while cursor < end:
        first = data[cursor]
        if first >= 128:
            return dict(source=start, end_exclusive=cursor+1, terminator=first,
                        pairs=pairs, unsigned_totals=[sum(p[axis] for p in pairs) for axis in (0, 1)])
        if cursor+1 >= end:
            raise ValueError('Route pair crosses data boundary')
        pairs.append([first, data[cursor+1]])
        cursor += 2
    raise ValueError('Route has no negative first-byte terminator within data boundary')


def catalogue(rom):
    if hashlib.sha256(rom).hexdigest() != ROM_HASH:
        raise ValueError('ROM revision differs')
    records = []
    for group in range(8):
        for direction in range(4):
            address = 0xa22c+group*24+direction*6
            records.append(dict(address=f'{address:06X}', group=group, direction_offset=direction*6,
                pointer=int.from_bytes(rom[address:address+4], 'big'),
                negate_x=rom[address+4], negate_y=rom[address+5]))
    starts = sorted({record['pointer'] for record in records if record['pointer']})
    if any(not 0xa2ec <= start < 0xa368 for start in starts):
        raise ValueError('Route pointer outside inspected immutable data')
    routes = [route_pairs(rom, start, 0xa368) for start in starts]
    for route in routes:
        route['later_starts_before_terminator'] = [start for start in starts if route['source'] < start < route['end_exclusive']]
        route['runtime_length_proven'] = False
    cases = []
    for tile in range(512):
        valid = 28 <= tile <= 123
        cases.append(dict(tile_id=tile, accepted=valid,
            descriptor_offset=((tile-28) % 8)*24 if valid else None))
    return dict(rom_sha256=ROM_HASH, descriptor_bytes=rom[0xa22c:0xa2ec].hex(),
        reverse_direction_words=[int.from_bytes(rom[a:a+2], 'big') for a in range(0xa092, 0xa09a, 2)],
        records=records, routes=routes, tile_selector_cases=cases,
        counts=dict(descriptors=len(records), nonzero_descriptors=sum(bool(r['pointer']) for r in records),
                    unique_route_starts=len(starts)),
        scope='Immutable byte-pair parsing. Odd starts and overlapping streams retained; unsigned totals are linear data scans before orientation and may cross other starts. Runtime changes routes at cell boundaries, so these are not path lengths. Finite tile selector arithmetic is not global caller/bounds proof. No CPU execution.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rom', type=Path)
    parser.add_argument('--project', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    report = catalogue(args.rom.read_bytes())
    (args.project / 'docs/stage9/world-route-data.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(report['counts'])


if __name__ == '__main__':
    main()
