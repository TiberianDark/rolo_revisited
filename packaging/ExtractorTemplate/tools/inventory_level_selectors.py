"""Pin level descriptor flag domains and byte-overlap selector writers."""
import argparse
import hashlib
import json
from pathlib import Path
from inventory_rom import inventory, ROM_HASH
from inventory_ram_schema import accesses


def catalogue(rom,project):
    inv,trace=inventory(rom,project/'docs')
    fields=[]
    for address,length,name in ((0xfff2f6,2,'current level selector'),(0xfff2f0,2,'saved level selector'),(0xfff26f,1,'background descriptor flag')):
        rows=[row for i in trace['instructions'] for row in accesses(i)
            if row['width'] is not None and row['address']<address+length and address<row['address']+row['width']]
        fields.append(dict(address=f'{address:06X}',length=length,name=name,explicit_accesses=rows,
            writer_sites=sorted({r['site'] for r in rows if r['access'] in ('write','read_modify_write')}),complete_writer_domain=False))
    descriptors=[]
    raw=rom[0x4ab1a:0x4ad9a]
    for selector in range(80):
        address=0x4ab1a+selector*8
        flag=rom[address+4];signed=flag if flag<128 else flag-256
        descriptors.append(dict(selector=selector,address=f'{address:06X}',bytes=rom[address:address+8].hex(),
            background_flag=flag,signed_background_flag=signed,absolute_signed_flag=abs(signed),
            raw_flag_inside_progress_array=flag<80,absolute_signed_flag_inside_progress_array=abs(signed)<80))
    accepted={i['address']:i for i in trace['instructions']}
    evidence=[]
    for start,end in ((0x933a,0x936a),(0xf2ce,0xf2f4),(0x37ea,0x37f2),(0x4eaa,0x4ef4),(0x4cb8,0x4d54),(0x1c6c,0x1cee)):
        cursor=start;instructions=[]
        while cursor<end:
            instruction=accepted[cursor];instructions.append(instruction);cursor+=instruction['size']
        if cursor!=end:raise ValueError('Selector producer end differs')
        evidence.append(dict(start=f'{start:06X}',end_exclusive=f'{end:06X}',instructions=instructions))
    cases=[dict(input_byte=value,selector=value&127,within_80_descriptors=(value&127)<80) for value in range(256)]
    dispatch=next(t for t in inv['dispatch_tables'] if t['dispatch']==0x4ed6)
    slot_addresses={slot['address'] for slot in dispatch['slots']}
    if slot_addresses!=set(range(0x4ef4,0x4f1c,4)):
        raise ValueError('Parallax branch slot extent differs')
    parallax=[];dispatch_inside=0
    for word in range(65536):
        signed=word if word<32768 else word-65536
        mode=rom[0x4aeda+signed]
        offset=(((word&0xff00)|mode)*4)&65535
        signed_offset=offset if offset<32768 else offset-65536
        target=0x4ef4+signed_offset
        within=target in slot_addresses
        dispatch_inside+=within
        if word<80 or word>=65531:
            parallax.append(dict(selector_word=word,selector_signed=signed,mode_byte=mode,
                retained_word=(word&0xff00)|mode,dispatch_offset_signed=signed_offset,
                target=target,within_catalogued_slots=within))
    return dict(rom_sha256=ROM_HASH,descriptor_table_address='04AB1A',descriptor_table_bytes=len(raw),
        descriptor_table_sha256=hashlib.sha256(raw).hexdigest(),descriptors=descriptors,
        raw_background_flag_domain=sorted({d['background_flag'] for d in descriptors}),
        descriptors_with_raw_flag_outside_80=sum(not d['raw_flag_inside_progress_array'] for d in descriptors),
        all_absolute_signed_flags_inside_80=all(d['absolute_signed_flag_inside_progress_array'] for d in descriptors),
        fields=fields,evidence_ranges=evidence,trigger_selector_byte_cases=cases,
        trigger_cases_within_descriptors=sum(c['within_80_descriptors'] for c in cases),
        parallax_modes_table_address='04AEDA',parallax_modes80=rom[0x4aeda:0x4aeda+80].hex(),
        parallax_checked_word_cases=65536,parallax_word_cases_addressing_slots=dispatch_inside,
        parallax_normal80_and_negative_screen_cases=parallax,
        normal80_parallax_cases_inside=all(c['within_catalogued_slots'] for c in parallax if c['selector_word']<80),
        known_camera_calls=[c for c in inv['calls'] if c['target'] in (0x4cb8,0x4d54)],
        normal_frame_before_camera_calls=[c for c in inv['calls'] if 0x1c76<=c['address']<0x1cb8],
        camera_domain_obligation='4CB8 resets camera from controlled actor and calls4D54 at4D04 without a local F2F6sign/bound guard. Normal frame1C6C calls actor updates A808 and trigger/contact helpers before4D54 at1CB8; main transition handler9534 comes after camera at1CE8. Therefore end-of-frame transition alone is not proof that preceding actor/trigger callbacks preserve the0..79domain.',
        contracts=[
            '933A checks C4E8word equals4. MOVEQ127 D0 then AND.B actor/trigger byte10 produces unsigned0..127, stores wholewordF2F6. No80-descriptor bound guard. Separately extracts original byte10 bit7 toF26C via MOVEQ-128/AND.B/ROL.B1; setsF26D andC522.',
            'F2CE tests A5.positionYlong negative; if negative clearYlong, setF26D/F26E, copy rawF26Fbyte intoF2F7only and setC522. HighbyteF2F6retained. This overlaps the current level selector; a search for literalF2F6alone misses it.',
            '37EA copies descriptor byte4 toF26F. Across80 immutable descriptors,23rawflags are outside0..79, but all signed-byte absolute values are inside0..79. This supports only the D3FE signed-absolute producer; raw byte-overwrite producers require their caller gates and reaching domains.',
            '4EAA loads F2F6word intoD2, uses signed wordindex at ROM4AEDA, then replaces only D2lowbyte with mode and doubles D2word twice. Normal0..79selectors choose modes1..9 and catalogued slots. Negative screen selectors retain highbyteFF and do not address those slots. No claim this path is invoked by those screen states; caller reachability must establish the nonnegative level domain. Returned D0/D1/D2/D3 populateF348/F34A/C546/F286.'
        ],negative_immediate_selectors=sorted({int(i['operands'].split(',')[0][2:],16)-65536
            for i in trace['instructions'] if i['mnemonic']=='MOVE.W' and i['operands'].startswith('#$FF') and i['operands'].endswith(',($FFFFF2F6).L')}),
        complete_runtime_selector_domain=False,
        pending='F2F0 producers, aliases/bulk/indexed writes, trigger byte10 immutable data join, negative-screen-state reachability, raw flag paths and their gates, initialization order and original-reference transitions.')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('rom',type=Path)
    parser.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1]);args=parser.parse_args()
    report=catalogue(args.rom.read_bytes(),args.project)
    (args.project/'docs/stage9/level-selector-domains.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(dict(raw_flags_outside=report['descriptors_with_raw_flag_outside_80'],absolute_flags_inside=report['all_absolute_signed_flags_inside_80'],trigger_cases_inside=report['trigger_cases_within_descriptors']))


if __name__=='__main__':main()
