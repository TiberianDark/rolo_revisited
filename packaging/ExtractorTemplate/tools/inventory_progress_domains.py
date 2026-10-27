"""Join progress selectors to immutable sources and checked local producers."""
import argparse
import json
from pathlib import Path
from inventory_rom import inventory, ROM_HASH
from inventory_spawns import catalogue as spawn_catalogue
from inventory_world_progression import catalogue as world_catalogue


def catalogue(rom,project):
    inv,trace=inventory(rom,project/'docs')
    accepted={i['address']:i for i in trace['instructions']}
    world=world_catalogue(rom,project)
    assets=json.loads((project/'assets/extracted/catalog/manifest.json').read_text(encoding='utf-8'))
    spawns=spawn_catalogue(rom,assets)
    markers=[m for m in spawns['markers'] if m['category']==11]
    rows=[]
    ranges=[(0x3e66,0x3e88),(0x60f4,0x6174),(0x9a1a,0x9a5e),(0xd374,0xd39e),(0xd3fe,0xd452)]
    for start,end in ranges:
        cursor=start;evidence=[]
        while cursor<end:
            instruction=accepted[cursor];evidence.append(instruction);cursor+=instruction['size']
        if cursor!=end:raise ValueError('Progress producer end is not an instruction boundary')
        rows.append(dict(start=f'{start:06X}',end_exclusive=f'{end:06X}',instructions=evidence))
    absolute_byte_cases=[]
    for byte in range(256):
        signed=byte if byte<128 else byte-256
        index=abs(signed)
        absolute_byte_cases.append(dict(input_byte=byte,index=index,within_80_bytes=index<80))
    byte_overwrite_examples=[]
    for prior in (0,1,79,80,255,256,32767,32768,65531,65535):
        for byte in (0,1,79,80,128,255):
            word=(prior&0xff00)|byte
            signed=word if word<32768 else word-65536
            byte_overwrite_examples.append(dict(prior_word=prior,new_byte=byte,
                effective_signed_index=signed,within_80_bytes=0<=signed<80))
    world_ids=sorted({cell['level_selector'] for cell in world['cells']})
    neighbour_ids=sorted({n['selector'] for cell in world['cells'] for n in cell['neighbours'] if n['completion_flag_read_possible']})
    parameters=sorted({m['parameter'] for m in markers})
    return dict(rom_sha256=ROM_HASH,array_address='FFC558',initialized_bytes=80,
        bit_roles=dict(bit0='availability/reveal gate',bit1='completion gate',bit2='visited snapshot producer',bit3='exit/progression override gate'),
        bit_role_scope='Observed local consumers; semantic names do not imply all writers/uses mapped.',
        world_cell_selector_domain=world_ids,conditional_neighbour_selector_domain=neighbour_ids,
        immutable_class0B_markers=markers,class0B_parameter_domain=parameters,
        immutable_domains_inside_initialized_array=all(0<=value<80 for value in world_ids+neighbour_ids+parameters),
        callback_6164_source='Checked3E66 callback preparation MOVEQ0 then MOVE.B marker parameter intoD0. Canonical path provides unsigned byte0..255; observed41 class0B records are within0..79. Mutations/alternate callback callers remain pending.',
        callback_6164_unsigned_byte_domain=dict(inside=80,outside=176),
        d3fe_signed_byte_absolute_cases=absolute_byte_cases,
        d3fe_cases_inside=sum(case['within_80_bytes'] for case in absolute_byte_cases),
        byte_overwrite_examples=byte_overwrite_examples,
        byte_overwrite_rule='9A3A,610C,613E,D392 replace only D0 lowbyte after F2F6word load. Effective index is signed16((F2F6&FF00)|newByte). Do not zero-extend implicitly. Full domain depends on both producers.',
        evidence_ranges=rows,
        base_producers=[i for i in trace['instructions'] if i['mnemonic']=='LEA' and '($FFFFC558).L' in i['operands']],
        label_caution='A50A legacy contract name says complete, but its instruction sets bit0; preserve the actual bit operation and distinguish bit1 completion consumers.',
        complete_runtime_selector_domain=False,
        pending='All F2F6/F26F and actor50 producers, marker mutations and alternate callback entries, indexed writes with other base producers, world XY bounds, array lifetime/initialization ordering and original-reference progression cases.')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('rom',type=Path)
    parser.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1]);args=parser.parse_args()
    report=catalogue(args.rom.read_bytes(),args.project)
    (args.project/'docs/stage9/progress-selector-domains.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(dict(class0B_records=len(report['immutable_class0B_markers']),base_producers=len(report['base_producers']),
        immutable_domains_inside=report['immutable_domains_inside_initialized_array'],d3fe_cases_inside=report['d3fe_cases_inside']))


if __name__=='__main__':main()
