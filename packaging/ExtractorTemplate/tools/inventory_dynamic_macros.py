"""Connect observed macro markers to their original collision matrices and spawn geometry."""
import argparse
import hashlib
import json
import struct
from pathlib import Path
from inventory_rom import ROM_HASH

def geometry(marker,width,height):
    width_pixels=(width<<4)&65535;height_pixels=(height<<4)&65535
    product_low=(width_pixels*height_pixels)&65535
    signed_product=product_low if product_low<32768 else product_low-65536
    return dict(width_pixels=width_pixels,height_pixels=height_pixels,
        canonical_x_word=(marker['x']+(width_pixels>>1))&65535,
        canonical_y_word=(marker['y']+height_pixels)&65535,
        definition_size_word=(signed_product>>1)&65535,
        size_scope='Literal MULU low word then ASR.W1 and MOVE.W; full resource lifetime/graphics meaning requires consuming-code evidence')

def catalogue(rom,assets,spawns):
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH or assets['rom_sha256']!=ROM_HASH or spawns['rom_sha256']!=ROM_HASH:
        raise ValueError('Unexpected ROM revision')
    layouts={r['source']:r for r in assets['layouts']}
    banks={r['bank']:r for r in assets['graphics_banks'] if 'macro_records' in r}
    records=[];matrices={}
    for marker in spawns['markers']:
        if not 32<=marker['category']<128:continue
        bank_id=layouts[marker['layout_source']]['bank'];bank=banks[bank_id]
        macro=next(r for r in bank['macro_records'] if r['slot']==marker['macro'])
        source=bank['macros']+macro['relative'];width=macro['width'];height=macro['height']
        if rom[source:source+2]!=bytes([width,height]):raise ValueError('Macro matrix dimensions differ')
        payload=rom[source+2:source+2+width*height*2]
        if len(payload)!=width*height*2:raise ValueError('Macro matrix truncated')
        key=(bank_id,marker['macro'])
        if key not in matrices:
            words=list(struct.unpack('>'+str(width*height)+'H',payload))
            matrices[key]=dict(bank=bank_id,macro=marker['macro'],header_source=source,matrix_source=source+2,
                width=width,height=height,word_count=len(words),matrix_sha256=hashlib.sha256(payload).hexdigest(),
                tile_words=words,solid_cell_count=sum(bool(word&0x4000) for word in words),
                bank_macro_artifact=bank['macro_artifact'],
                scope='Original ITMS matrix cells; runtime mutation and support-query validity still require tracing')
        records.append(dict(marker,bank=bank_id,matrix_source=source+2,
            initial_geometry=geometry(marker,width,height),
            scope='Canonical 4958 row-loader spawn path; selector aliases and runtime execution are not inferred'))
    return dict(rom_sha256=ROM_HASH,markers=records,matrices=list(matrices.values()),
        evidence_sites=['497C','4984','498A','498C','499A','49D4','49D8','49DA','49E0','49E2','49E4','4A04','4A08','4A22','4A26','8BAC','8C12','8C16','8C1C'],
        counts=dict(observed_macro_markers=len(records),distinct_bank_macro_matrices=len(matrices),
            referenced_banks=len({m['bank'] for m in matrices.values()}),matrix_cells=sum(m['word_count'] for m in matrices.values())),
        scope='Cross-reference of inspected macro markers only, not a count of platforms, encounters or supported dynamic gameplay. Matrix word flags use the selected bank collision records and shared shape profiles. No new runtime behavior.')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('rom')
    p.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
    assets=json.loads((a.project/'assets/extracted/catalog/manifest.json').read_text(encoding='utf-8'))
    spawns=json.loads((a.project/'docs/stage9/spawn-inventory.json').read_text(encoding='utf-8'))
    report=catalogue(Path(a.rom).read_bytes(),assets,spawns)
    (a.project/'docs/stage9/dynamic-macro-inventory.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report['counts']))

if __name__=='__main__':main()
