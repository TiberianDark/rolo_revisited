"""Definition-pointer alias candidates and original RAM-definition allocation handoff."""
import hashlib
import json
import re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder

def catalogue(project):
    rom = (project / 'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest() != ROM_HASH:
        raise ValueError('Pinned ROM differs')
    inv = json.loads((project / 'docs/stage9/inventory.json').read_text())
    accepted = {a for r in inv['routines'] for a in r['blocks']}
    def decode(address):
        if address not in accepted:
            raise ValueError(f'Unaccepted boundary {address:04X}')
        return Decoder(rom, address).decode()
    writes = []
    for address in sorted(accepted):
        instruction = decode(address)
        if instruction['mnemonic'].split('.')[0] not in ('MOVE', 'CLR', 'ADD', 'ADDI', 'ADDQ', 'SUB', 'SUBI', 'SUBQ', 'AND', 'ANDI', 'OR', 'ORI', 'EOR', 'EORI', 'NEG', 'NOT', 'BSET', 'BCLR', 'BCHG', 'ST', 'SF'):
            continue
        if not re.search(r'\(\+4,A[0-7]\)$', instruction['operands']):
            continue
        writes.append(dict(instruction=instruction,
                           actor_definition_binding=address == 0x28F6,
                           scope='Displacement match only. A6 often denotes a device port; other registers can denote resource or map records. Requires identity evidence before calling this an actor definition mutation.'))
    evidence = []
    at = 0x4996
    while at < 0x49FA:
        instruction = decode(at)
        evidence.append(instruction)
        at += instruction['size']
    if at != 0x49FA:
        raise ValueError('RAM definition handoff extent differs')
    expected = {0x28F6: ('MOVE.L', 'A2,(+4,A3)'),
                0x49B6: ('MOVE.L', '#$0000BE4E,(+12,A0)'),
                0x49EE: ('MOVE.L', 'A0,D0')}
    for address, operation in expected.items():
        decoded = decode(address)
        if (decoded['mnemonic'], decoded['operands']) != operation:
            raise ValueError('Definition pointer/handler producer differs')
    call = decode(0x49F2)
    if call.get('target') != 0x28B0:
        raise ValueError('RAM definition allocator handoff differs')
    decode(0xBE4E)
    lifecycle = []
    for start, end, name, contract in (
        (0x2816, 0x2838, 'Initialize definition pool',
         '6426 points to free-list642A; 32 pointers enumerate64AE+n*34, n0..31, followed by zero sentinel. Definitions are not cleared here.'),
        (0x4958, 0x4972, 'Reserve definition',
         'Pop pointer through6426. Zero returns4A44 without advancing6426. Nonzero advances free-list pointer by4 then uses popped pointer asA0.'),
        (0x49EA, 0x4A48, 'Allocate or return definition',
         'Preserve A0/A1/D4/D5 across28B0. MOVEM restore retains allocator CCR; BEQ4A34 tests it. Failure discards saved WORD and pushes the sameA0 definition back through6426; returnsD0=-1. Success binds dimensions/resource metadata toA4, calls4B2E and returnsD0=0. Allocation-failure resource/marker side effects remain28B0 dependencies.'),
        (0x2B24, 0x2B8C, 'Retirement return ordering',
         'After retirement eligibility, definition typeWORD10==24 pushes definitionA4 back through6426 before later2CBC disposal. Actor126bit3 bypasses return and setsbit2. Remaining definition flags can skip marker restoration2BCE; normaldisposal2CBC follows. This is conditional ownership transfer, not everyframe/free-on-every-call.'),
        (0x2CD8, 0x2D1A, 'Disposal after pool return',
         '2CBC resolvesactor+4 again, readsdefinitionresourceWORD4 andconditionallycalls34F0 beforefreeingactor andsplicinglinks. No allocator call occurs in the reviewed return-to-disposal interval; helper reentry/clobber and alias concurrency still require closure.'),
    ):
        instructions = []
        at = start
        while at < end:
            decoded = decode(at)
            instructions.append(decoded)
            at += decoded['size']
        if at != end:
            raise ValueError('Lifecycle boundary differs')
        lifecycle.append(dict(start=f'{start:04X}', end_exclusive=f'{end:04X}', name=name,
                              contract=contract, instruction_evidence=instructions))
    return dict(rom_sha256=ROM_HASH, displacement4_write_candidates=writes,
                counts=dict(candidates=len(writes), a6_candidates=sum(r['instruction']['operands'].endswith('A6)') for r in writes)),
                allocator_binding=dict(site='28F6', meaning='Allocator stores incoming definition A2 in actor A3+4; this is the reviewed actor definition binding.'),
                ram_definition_path=dict(handler='BE4E', handler_write='49B6', allocation_call='49F2',
                                         evidence=evidence,
                                         meaning='A0 is populated as a mutable RAM definition, then passed as D0 to 28B0. Handler+12 is BE4E. Therefore callback restores cannot assume every definition pointer addresses the immutable ROM table.'),
                lifecycle=lifecycle,
                ram_definition_pool=dict(base='FFFF64AE', record_bytes=34, records=32, end_exclusive='FFFF68EE',
                                         free_list_base='FFFF642A', free_list_cursor='FFFF6426'),
                immutable_definition_domain=dict(records=len(inv['object_definitions']), handlers=len({d['handler'] for d in inv['object_definitions']})),
                remaining=['Close pool reset/admission/retirement caller ownership, exhaustion and duplicate-return invariants.',
                           'Review bulk initialization/copy and indexed aliases, not only +4 displacements.',
                           'Prove each restore caller uses a live definition and cannot select a recursive/stale callback.'],
                scope='Static definition identity evidence and broad alias candidates; no whole-program mutation closure or new native green.')

if __name__ == '__main__':
    project = Path(__file__).resolve().parents[1]
    report = catalogue(project)
    (project / 'docs/stage9/definition-identity-audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report['counts']))
