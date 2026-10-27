"""Join all accepted object+42 mutation candidates with target/provenance evidence."""
import csv
import hashlib
import json
import re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder

def catalogue(project):
    rom = (project / 'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest() != ROM_HASH:
        raise ValueError('ROM revision differs')
    inv = json.loads((project / 'docs/stage9/inventory.json').read_text())
    accepted = {a for r in inv['routines'] for a in r['blocks']}
    sources = {}
    for source in inv['callback_sources']:
        sources.setdefault(int(source['write'], 16), []).append(source)
    owners = {}
    for routine in inv['routines']:
        for a in routine['blocks']:
            owners.setdefault(a, []).append(routine['address'])
    rows = []
    for write in inv['callback_writes']:
        address = write['address']
        instruction = Decoder(rom, address).decode()
        if address not in accepted or instruction['mnemonic'] != 'MOVE.L' or instruction['operands'] != write['operands']:
            raise ValueError('Mutation boundary differs')
        literal = re.match(r'^#\$([0-9A-F]+),', instruction['operands'])
        targets = [int(literal[1], 16)] if literal else []
        producer_evidence = []
        for source in sources.get(address, []):
            producer = int(source['producer'], 16)
            decoded = Decoder(rom, producer).decode()
            target = int(source['target'], 16)
            if producer not in accepted or f'#{chr(36)}{target:08X}' not in decoded['operands']:
                raise ValueError('Declared callback producer differs')
            targets.append(target)
            producer_evidence.append(dict(context=source, instruction=decoded))
        targets = sorted(set(targets))
        missing = [target for target in targets if target not in accepted]
        definition = '(+12,' in instruction['operands'].split(',(+42,')[0]
        kind = 'literal target' if literal else 'declared bounded producer' if targets else 'definition field restore' if definition else 'register provenance pending'
        field_provenance = []
        if address in (0x29B0, 0xB720):
            specifications = ((0x2994, 'MOVE.L', '(+12,A2),D0'),
                              (0x29AA, 'MOVE.L', '#$0000A8BC,D0')) if address == 0x29B0 else (
                              (0xB718, 'MOVEA.L', '(+4,A5),A4'),
                              (0xB71C, 'MOVEA.L', '(+12,A4),A0'))
            for site, mnemonic, operands in specifications:
                decoded = Decoder(rom, site).decode()
                if site not in accepted or (decoded['mnemonic'], decoded['operands']) != (mnemonic, operands):
                    raise ValueError('Definition-held register provenance differs')
                field_provenance.append(decoded)
            kind = 'definition with conditional allocator override' if address == 0x29B0 else 'definition field restore via register'
            if address == 0x29B0:
                targets = [0xA8BC]
                missing = [target for target in targets if target not in accepted]
        rows.append(dict(address=address, hex=f'{address:04X}', operands=instruction['operands'], kind=kind,
                         targets=[f'{target:04X}' for target in targets], unaccepted_targets=[f'{target:04X}' for target in missing],
                         owners=[f'{owner:04X}' for owner in sorted(set(owners[address]))],
                         instruction_evidence=instruction, producer_evidence=producer_evidence,
                         field_provenance_evidence=field_provenance,
                         remaining='Actor/definition identity, alias writes, producer-to-write path and lifetime closure remain required; this row is not a green contract.'))
    return dict(rom_sha256=ROM_HASH, writes=rows,
                counts=dict(total=len(rows), literal=sum(r['kind']=='literal target' for r in rows),
                            declared=sum(r['kind']=='declared bounded producer' for r in rows),
                            definition_restore=sum(r['kind']=='definition field restore' for r in rows),
                            definition_via_register=sum(r['kind'] in ('definition with conditional allocator override', 'definition field restore via register') for r in rows),
                            provenance_pending=sum(r['kind']=='register provenance pending' for r in rows)),
                scope='Every accepted MOVE.L to +42 is catalogued as a candidate. Other-sized/bulk/indexed writes and field aliases are not excluded; no global callback closure claimed.')

if __name__ == '__main__':
    project = Path(__file__).resolve().parents[1]
    report = catalogue(project)
    docs = project / 'docs/stage9'
    (docs / 'callback-write-audit.json').write_text(json.dumps(report, indent=2) + '\n')
    fields = ['hex', 'operands', 'kind', 'targets', 'owners', 'unaccepted_targets', 'remaining']
    with (docs / 'callback-write-audit.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in report['writes']:
            writer.writerow({key: '; '.join(row[key]) if isinstance(row[key], list) else row[key] for key in fields})
    print(json.dumps(report['counts']))
