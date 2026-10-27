"""Offline selector arithmetic and supplied-layout domains; never execute ROM code."""
import argparse
import json
from collections import Counter
from pathlib import Path
from inventory_rom import ROM_HASH, inventory
from inventory_spawns import TABLES, catalogue as spawn_catalogue
from m68k_static import Decoder


def selector(type_word):
    """Derive only the checked normal 446C -> 463C selector path."""
    word = type_word & 0xffff
    if word < 0x400:
        return dict(path='visual descriptor')
    high = word & 0xff00
    signed_high = high if high < 0x8000 else high - 0x10000
    if signed_high >= 0x2000:
        return dict(path='macro factory', initial_mode_offset=(high >> 6) - 0x80)
    offset = ((high - 0x400) & 0xffff) >> 6
    return dict(path='spawn branch', branch_offset=offset,
                within_catalogued_slots=offset in range(0, 80, 4))


def definition_index(category, parameter):
    if category not in TABLES:
        return None
    _, count, shape = TABLES[category]
    # 4796/48D8 double the byte before 4A48 clears bit0 and doubles again.
    # Thus their "direct" input uses parameter*4, not paired floor(parameter/2).
    index = parameter // 2 if shape == 'paired' else parameter
    if shape == 'progress_gate':
        index = 0
    return dict(index=index, count=count, within_table=index < count)


def terrain_selector(category, parameter):
    if category not in (7, 8, 9, 10):
        return None
    offset = 64 if category == 7 else 68 if category in (8, 9) else (parameter & 255) * 4
    return dict(offset=offset, within_catalogued_slots=offset in range(0, 72, 4))


def catalogue(rom, project):
    inv, trace = inventory(rom, project / 'docs')
    accepted = {i['address'] for i in trace['instructions']}
    for address, base, count in ((0x4662, 0x466c, 20), (0x92dc, 0x92f2, 18)):
        table = next(t for t in inv['dispatch_tables'] if t['dispatch'] == address)
        if table['base'] != base or [s['address'] - base for s in table['slots']] != list(range(0, count * 4, 4)):
            raise ValueError('Spawn/trigger slot extent differs')
    evidence = {}
    for address, mnemonic, operands in [
        (0x446e, 'CMPI.W', '#$0400,D0'), (0x4472, 'BCC', '$00463C'),
        (0x4648, 'ANDI.W', '#$FF00,D2'), (0x464c, 'CMPI.W', '#$2000,D2'),
        (0x4650, 'BLT', '$004658'), (0x4658, 'SUBI.W', '#$0400,D2'),
        (0x465c, 'LSR.W', '#6,D2'), (0x4662, 'JSR', '(+8,PC,D2.W)'),
        (0x92d8, 'MOVE.W', '(+8,A0),D0'), (0x92dc, 'JSR', '(+20,PC,D0.W)'),
        (0x4a48, 'BCLR', '#0,D0'), (0x4a4e, 'ADD.W', 'D0,D0'),
        (0x47b2, 'ADD.W', 'D0,D0'), (0x48f4, 'ADD.W', 'D0,D0'),
        (0x490e, 'ADD.W', 'D0,D0'), (0x4910, 'ADD.W', 'D0,D0')]:
        decoded = Decoder(rom, address).decode()
        if address not in accepted or (decoded['mnemonic'], decoded['operands']) != (mnemonic, operands):
            raise ValueError('Spawn selector evidence differs')
        evidence[f'{address:06X}'] = {key: decoded[key] for key in ('bytes', 'mnemonic', 'operands')}
    assets = json.loads((project / 'assets/extracted/catalog/manifest.json').read_text(encoding='utf-8'))
    spawns = spawn_catalogue(rom, assets)
    groups = []
    for category in sorted({m['category'] for m in spawns['markers']}):
        markers = [m for m in spawns['markers'] if m['category'] == category]
        parameters = sorted({m['parameter'] for m in markers})
        row = dict(category=category, records=len(markers), parameters=parameters,
                   normal_spawn_path=selector(category << 8))
        indices = [definition_index(category, p) for p in parameters]
        if any(i is not None for i in indices):
            row['definition_index_domain'] = sorted({i['index'] for i in indices})
            row['observed_definition_indices_in_table'] = all(i['within_table'] for i in indices)
        terrain = [terrain_selector(category, p) for p in parameters]
        if terrain[0] is not None:
            row['initial_terrain_offset_domain'] = sorted({i['offset'] for i in terrain})
            row['observed_terrain_offsets_in_slots'] = all(i['within_catalogued_slots'] for i in terrain)
        groups.append(row)
    class12 = Counter(m['layout_source'] for m in spawns['markers'] if m['category'] == 0x12)
    marker_counts = dict(scope='Immutable spawn ledger class12 records by layout; not runtime C556 after consumption or distinct playable level count',
        total=sum(class12.values()), layouts=[dict(layout_source=a, class12_records=class12[a])
            for a in sorted({m['layout_source'] for m in spawns['markers']})])
    inputs = Counter(selector(word)['path'] for word in range(65536))
    escaped = [category for category in range(4, 256)
               if selector(category << 8).get('within_catalogued_slots') is False]
    macro_escaped = [category for category in range(32, 128)
                     if selector(category << 8)['initial_mode_offset'] not in range(0, 128, 4)]
    return dict(rom_sha256=ROM_HASH, instruction_evidence=evidence, groups=groups, marker_class12_counts=marker_counts,
        exhaustive_word_arithmetic=dict(input_counts=dict(inputs),
            categories_outside_spawn_slots=escaped,
            macro_categories_outside_initial_BE56_slots=macro_escaped),
        counts=dict(marker_records=len(spawns['markers']), observed_classes=len(groups),
            observed_spawn_branch_escapes=sum(g['records'] for g in groups if g['normal_spawn_path'].get('within_catalogued_slots') is False),
            observed_definition_index_escapes=sum(g['records'] for g in groups if g.get('observed_definition_indices_in_table') is False),
            observed_terrain_selector_escapes=sum(g['records'] for g in groups if g.get('observed_terrain_offsets_in_slots') is False)),
        scope='Finite arithmetic of one checked producer path and immutable extracted layout records. Class17 has a separate startup consumer. No claim all runtime/computed entries or mutated markers retain this domain; no ROM execution.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rom'); parser.add_argument('--project', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    result = catalogue(Path(args.rom).read_bytes(), args.project)
    (args.project / 'docs/stage9/spawn-selector-domains.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    (args.project / 'docs/stage9/marker-class12-counts.json').write_text(json.dumps(result['marker_class12_counts'], indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result['counts']))


if __name__ == '__main__':
    main()
