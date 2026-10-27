"""Batch audit of original marker-search callback handoffs; static decoding only."""
import hashlib
import json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder

CONTEXTS = ((0x608A, 0x609A, 0x60A0, 0x60A6, 5),
            (0x6118, 0x611A, 0x6120, 0x6174, 5),
            (0x6126, 0x614C, 0x6152, 0x6164, 11),
            (0x6126, 0x6158, 0x615E, 0x6174, 5))

def catalogue(project):
    rom = (project / 'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest() != ROM_HASH:
        raise ValueError('Pinned ROM differs')
    inventory = json.loads((project / 'docs/stage9/inventory.json').read_text())
    accepted = {address for routine in inventory['routines'] for address in routine['blocks']}
    def instruction(address):
        if address not in accepted:
            raise ValueError(f'Unaccepted instruction boundary {address:04X}')
        return Decoder(rom, address).decode()
    rows = []
    direct_calls = {call['address'] for call in inventory['calls'] if call.get('target') == 0x3E2C}
    expected_calls = {context[2] for context in CONTEXTS}
    transfers = [edge for edge in inventory['inter_entry_transfers'] if edge.get('destination') == 0x3E2C]
    if direct_calls != expected_calls or transfers:
        raise ValueError('Accepted incoming search paths changed; expand caller audit')
    for entry, producer, call, target, marker_class in CONTEXTS:
        selector = instruction(producer - 2)
        pointer = instruction(producer)
        invocation = instruction(call)
        if (selector['mnemonic'], selector['operands']) != ('MOVEQ', f'#{marker_class},D0'):
            raise ValueError('Marker class producer differs')
        if pointer['mnemonic'] != 'LEA' or pointer['references'] != [target] or pointer['size'] != call - producer:
            raise ValueError('A4 handoff is not adjacent to search call')
        if invocation['mnemonic'] != 'BSR' or invocation.get('target') != 0x3E2C:
            raise ValueError('Search call differs')
        instruction(target)
        rows.append(dict(caller=f'{entry:04X}', producer=f'{producer:04X}', call=f'{call:04X}',
                         target=f'{target:04X}', marker_class=marker_class,
                         instruction_evidence=[selector, pointer, invocation]))
    expected = {0x3E66: '48e7fffe', 0x3E7E: '4e94', 0x3E80: '4a40',
                0x3E82: '4cdf7fff', 0x3E86: '67d0'}
    preservation = []
    for address, raw in expected.items():
        decoded = instruction(address)
        if rom[address:address + decoded['size']].hex() != raw:
            raise ValueError('Callback preservation/return protocol differs')
        preservation.append(decoded)
    return dict(rom_sha256=ROM_HASH, dispatch='3E7E', contexts=rows,
                distinct_targets=['60A6', '6164', '6174'], preservation_evidence=preservation,
                incoming_edge_coverage=dict(accepted_direct_calls=len(direct_calls), audited_direct_calls=len(rows),
                                            accepted_noncall_transfers=len(transfers),
                                            scope='Current accepted graph only; computed/hidden entries are not excluded.'),
                conclusion='All four recorded immediate handoffs are adjacent and bounded. MOVEM restores A4 after every callback, including allocator callbacks that overwrite A4. TST.W D0 precedes restoration; restored registers do not replace the tested CCR, so zero resumes scanning and nonzero stops.',
                remaining=['All other incoming search contexts and aliases must be audited.',
                           'Callback return assumes balanced stack and ordinary RTS; service lifetime/failure behavior remains separately scoped.',
                           'MAP row offsets, zero height and record extents remain unclosed.'],
                global_resolved=False, new_native_greens=0)

if __name__ == '__main__':
    project = Path(__file__).resolve().parents[1]
    report = catalogue(project)
    (project / 'docs/stage9/marker-search-caller-audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Four marker callback handoffs and shared preservation protocol audited; no global closure claimed.')
