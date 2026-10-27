"""Extract menu selector evidence and finite arithmetic; no ROM execution."""
import argparse
import hashlib
import json
from pathlib import Path
from inventory_rom import inventory, ROM_HASH


def catalogue(rom, project):
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:
        raise ValueError('ROM revision differs')
    inv, trace=inventory(rom, project/'docs')
    ranges=[(0x1eac,0x1ef2), (0x1f12,0x1f38), (0x784c,0x785c), (0x3a68,0x3a88)]
    evidence=[]
    for start,end in ranges:
        instructions=[i for i in trace['instructions'] if start<=i['address']<end]
        cursor=start
        for instruction in instructions:
            if instruction['address']!=cursor:
                raise ValueError('Noncontiguous menu evidence')
            cursor+=instruction['size']
        if cursor!=end:
            raise ValueError('Menu evidence boundary differs')
        evidence.append(dict(start=f'{start:06X}',end_exclusive=f'{end:06X}',instructions=instructions))
    raw=rom[0x2224:0x223c]
    rows=[list(raw[index:index+4]) for index in range(0,24,4)]
    transitions=[]
    for selector,row in enumerate(rows):
        for direction,value in enumerate(row):
            transitions.append(dict(selector=selector,direction=direction,raw=value,
                next_selector=selector if value&128 else value))
    reachable={3}
    while True:
        expanded=reachable|{t['next_selector'] for t in transitions if t['selector'] in reachable}
        if expanded==reachable:
            break
        reachable=expanded
    safe_words=[]
    for value in range(65536):
        offset=(value*4)&65535
        if value!=5 and offset<=20:
            safe_words.append(dict(input_word=value,slot_offset=offset))
    death_cases=[dict(c50f=value,output_word=(3+value)&255) for value in range(256)]
    return dict(rom_sha256=ROM_HASH,table_address='002224',table_bytes=raw.hex(),
        table_sha256=hashlib.sha256(raw).hexdigest(),rows=rows,transitions=transitions,
        conditional_reachable_from_initial_3=sorted(reachable),
        transition_domain_closed_for_inputs_0_through_5=all(0<=t['next_selector']<=5 for t in transitions),
        arithmetic_word_cases_checked=65536,dispatch_guard_word=5,
        words_addressing_catalogued_slots=safe_words,
        words_outside_slots=65536-1-len(safe_words),death_selector_byte_cases=death_cases,
        evidence_ranges=evidence,
        contracts=[
            '1EAC..1EBA supplies direction D1=0..3. If C4D2 is zero return. Otherwise D0=C542 word multiplied by4 with wrap; add into D1 word, read table byte into only D1 lowbyte, BMI on that byte leaves selection unchanged. Nonnegative byte stores the whole D1 word into C542. For inputs0..5, D1 highbyte is zero and the table closes the same six-state domain. Larger inputs may retain nonzero D1 highbyte or read outside table; no local clamp exists.',
            '1F12 calls223C and effect000F preserving D0word around sound. Load C542word, exact5 returns; otherwise multiply by4 with word wrap and JSR indexed branch slots1F6C..1F80. Subsequent BMI consumes returned N, not an independently normalized boolean.',
            '784C MOVEQ3 zeroes D0 upper bits, then ADD.B C50F wraps only lowbyte; store D0word toC542. Known explicit C50F producers write0/1 so this producer conditionally yields3/4; exhaustive byte cases include other menu values and values outside0..5.',
            '3A68 reads C542word, ASL.W5 then signed ADDA.W into ROM3B06; copies four8B records while replacing sprite link bytes from D7. It has no local menu selector bound guard.'
        ],complete_writer_domain=False,
        pending='All indexed/pointer/bulk C542/C50F writers, computed entry/reaching paths, menu rendering and action callbacks, state initialization order and original-reference input cases. Conditional closure does not resolve the global dispatch domain.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rom',type=Path)
    parser.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1])
    args=parser.parse_args()
    report=catalogue(args.rom.read_bytes(),args.project)
    (args.project/'docs/stage9/menu-selector-domain.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print({key:report[key] for key in ('conditional_reachable_from_initial_3','transition_domain_closed_for_inputs_0_through_5','words_outside_slots')})


if __name__=='__main__':main()
