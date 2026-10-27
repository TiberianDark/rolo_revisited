"""Collect overlapping global accesses; never infer absence of indirect writers."""
import argparse
import json
from pathlib import Path
from inventory_rom import inventory, ROM_HASH
from inventory_ram_schema import accesses
from inventory_ram_aliases import hints

TARGETS = [(0xffc50f, 1, 'actor switch selector'), (0xffc556, 2, 'remaining marker count'),
           (0xffc542, 2, 'menu selector'), (0xffc510, 1, 'controlled actor selection gate'),
           (0xffc558, 80, 'world progress byte array'), (0xffc5a8, 16, 'actor type gates'),
           (0xfff2f6, 2, 'current level selector'), (0xfff2f0, 2, 'saved level selector'),
           (0xfff26f, 1, 'descriptor background flag byte'),
           (0xffc5e4, 2, 'shared vector phase'), (0xffc5e6, 1, 'shared amplitude index'),
           (0xffc5e7, 1, 'shared tick latch'), (0xffc5e8, 1, 'shared update gate')]


def overlap(start, width, target, length):
    return width is not None and start < target+length and target < start+width


def catalogue(rom, project):
    inv, trace = inventory(rom, project / 'docs')
    direct = [row for instruction in trace['instructions'] for row in accesses(instruction)]
    aliases = hints(trace['instructions'], [row['address'] for row in inv['routines']])
    from inventory_bulk_writes import catalogue as bulk_catalogue
    bulk = [dict(address=row['address'], width=row['length_bytes'], element_width=row['width'],
                 iterations=row['iterations'], site=row['site'], access='write',
                 local_entry=row['entry'], contract=row['contract'])
            for row in bulk_catalogue(rom, project)['spans']]
    fields = []
    for address, length, name in TARGETS:
        evidence = [dict(row, evidence_kind=kind) for kind, rows in [('absolute', direct), ('constant alias hint', aliases), ('inspected constant bulk span', bulk)]
                    for row in rows if overlap(row['address'], row['width'], address, length)]
        fields.append(dict(address=f'{address:06X}', length_bytes=length, name=name,
            accesses=evidence, writer_sites=sorted({row['site'] for row in evidence if row['access'] in ('write', 'read_modify_write')}),
            complete_writer_domain=False))
    return dict(rom_sha256=ROM_HASH, fields=fields,
        scope='Accepted explicit operands, bounded constant alias hints and seven inspected constant bulk spans with byte overlap. Indexed, pointer-derived, other bulk and unresolved code writers remain outside this evidence; absence is not domain closure.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rom', type=Path)
    parser.add_argument('--project', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    result = catalogue(args.rom.read_bytes(), args.project)
    (args.project / 'docs/stage9/global-domain-evidence.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print({row['address']: len(row['writer_sites']) for row in result['fields']})


if __name__ == '__main__':
    main()
