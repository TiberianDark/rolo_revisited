"""Original RAM-macro selector arithmetic, caller separation and observed target domain."""
import hashlib
import json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder

def catalogue(project):
    rom = (project / 'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest() != ROM_HASH:
        raise ValueError('ROM mismatch')
    docs = project / 'docs/stage9'
    inv = json.loads((docs / 'inventory.json').read_text())
    spawns = json.loads((docs / 'spawn-inventory.json').read_text())
    accepted = {a for r in inv['routines'] for a in r['blocks']}
    expected = {0x4646: ('MOVE.W', 'D0,D2'), 0x4648: ('ANDI.W', '#$FF00,D2'),
                0x464C: ('CMPI.W', '#$2000,D2'), 0x4650: ('BLT', '$004658'),
                0x48A6: ('MOVE.L', '#$0000B80A,(+42,A0)'),
                0x48AE: ('MOVE.B', '(A2)+,(+54,A0)'), 0x48B2: ('MOVE.B', '(A2)+,(+55,A0)'),
                0x498E: ('LSR.W', '#6,D2'),
                0x4990: ('SUBI.W', '#$0080,D2'), 0x4A26: ('MOVE.W', '(A7)+,(+54,A4)'),
                0xBE52: ('MOVE.W', '(+54,A5),D0')}
    evidence = []
    for address, operation in expected.items():
        instruction = Decoder(rom, address).decode()
        if address not in accepted or (instruction['mnemonic'], instruction['operands']) != operation:
            raise ValueError(f'Selector producer differs {address:04X}')
        evidence.append(instruction)
    table = next(t for t in inv['dispatch_tables'] if t['dispatch'] == 0xBE56)
    slots = {s['address'] - table['base']: s['target'] for s in table['slots']}
    records = []
    for marker in spawns['markers']:
        if 'mode' not in marker:
            continue
        offset = ((marker['type'] & 0xFF00) >> 6) - 0x80
        if offset != marker['dispatch_offset'] or offset not in slots:
            raise ValueError('Observed macro selector escapes original slots')
        records.append(dict(marker, target=f'{slots[offset]:04X}'))
    admitted = [((word & 0xFF00) >> 6) - 0x80 for word in range(65536)
                if 0x2000 <= (word & 0xFF00) < 0x8000]
    unsafe = sorted(set(admitted) - set(slots))
    return dict(rom_sha256=ROM_HASH, dispatch='BE56', instruction_evidence=evidence,
                observed_markers=records, observed_offsets=sorted({r['dispatch_offset'] for r in records}),
                counts=dict(markers=len(records), observed_targets=len({r['target'] for r in records}),
                            branch_slots=len(slots), signed_gate_offsets=len(set(admitted)),
                            signed_gate_offsets_outside_slots=len(unsafe)),
                gate_only_outside_offsets=unsafe,
                conclusion='The signed 464C/4650 gate admits categories32..127, producing96 distinct offsets. The32-slot table alone therefore does not bound arbitrary incoming marker words. All recorded89 canonical macro markers fit18 offsets. Initial map-domain evidence cannot close later actor54 mutations.',
                alternate_caller='489E calls4958 but48A6 replaces the returned callback withB80A and48AE/48B2 overwrite54/55 bytes; its domain must remain separate from BE4E.',
                remaining=['Prove complete map admission and corrupted/external marker policy.',
                           'Audit WORD/BYTE/LONG/bulk/indexed mutations overlapping actor54/55.',
                           'Close RAM-definition actor identity/lifetime and callback replacement paths.'],
                global_resolved=False, new_native_greens=0)

if __name__ == '__main__':
    project = Path(__file__).resolve().parents[1]
    report = catalogue(project)
    (project / 'docs/stage9/ram-macro-selector-audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report['counts']))
