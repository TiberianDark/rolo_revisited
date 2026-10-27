"""Pin original vector words and direct caller evidence without executing ROM code."""
import argparse
import hashlib
import json
from pathlib import Path
from inventory_rom import inventory, ROM_HASH


def catalogue(rom, project):
    inv, trace = inventory(rom, project / 'docs')
    blob = rom[0x1582a:0x15c2a]
    words = [int.from_bytes(blob[i:i+2], 'big', signed=True) for i in range(0, 1024, 2)]
    instructions = trace['instructions']
    indices = {row['address']: i for i, row in enumerate(instructions)}
    contexts = []
    for call in inv['calls']:
        if call['target'] != 0xccf8:
            continue
        index = indices[call['address']]
        starts = {0xc3a6: 0xc372, 0xc472: 0xc43e, 0xd9c6: 0xd978, 0xd51e: 0xd4f6}
        start_index = indices[starts[call['address']]] if call['address'] in starts else max(0, index-10)
        prefix = instructions[start_index:index+1]
        producer = next(row for row in reversed(prefix[:-1]) if row['operands'].endswith(',D2'))
        if producer['mnemonic'] != 'MOVEQ' or producer['operands'] not in ('#1,D2', '#8,D2'):
            raise ValueError('Vector divisor producer differs')
        divisor = int(producer['operands'].split(',')[0][1:])
        contexts.append(dict(call=call,
            local_divisor_producer=dict(address=f"{producer['address']:06X}", bytes=producer['bytes'],
                incoming_word=divisor, divisor_after_subtract=divisor-1,
                path='no division' if divisor == 1 else 'two-stage division'),
            divisor_scope='Checked preceding immediate producer; computed entry bypass and all reaching paths remain pending',
            prefix_scope='Accepted address-order context; selected branch-dependent angle paths expanded to their load. Computed entry bypass and full reaching domains pending',
            angle_timing=('Load old word50 before ADD/SUB.L changes packed fields50/52; helper receives old phase' if call['address'] in (0xc3a6, 0xc472, 0xd9c6) else 'See producer instructions; full argument domains pending'),
            instruction_evidence=[dict(address=f"{i['address']:06X}", bytes=i['bytes'],
                mnemonic=i['mnemonic'], operands=i['operands']) for i in prefix]))
    return dict(rom_sha256=ROM_HASH,
        scope='Immutable table words and exact direct-call locations; semantic sine labeling and full caller domains pending',
        amplitude_lookup=dict(address='D554', bytes=rom[0xd554:0xd558].hex(), unsigned_values=list(rom[0xd554:0xd558]), scope='Four immutable bytes; D4CC retains unmasked index on non-wrap phase, global domain audit pending'),
        address='1582A', length_bytes=1024, sha256=hashlib.sha256(blob).hexdigest(),
        signed_words=words, minimum=min(words), maximum=max(words),
        half_cycle_negation=all(words[(i+256)%512] == -words[i] for i in range(512)),
        quarter_samples=[words[i] for i in (0, 128, 256, 384)], caller_contexts=contexts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rom', type=Path)
    parser.add_argument('--project', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    report = catalogue(args.rom.read_bytes(), args.project)
    output = args.project / 'docs/stage9/vector-table-evidence.json'
    output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print('512 original words and', len(report['caller_contexts']), 'direct caller contexts')


if __name__ == '__main__':
    main()
