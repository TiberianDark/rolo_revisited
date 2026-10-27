"""Reproduce the inspected Rolo startup and frame-path listings, with evidence notes."""
import argparse
import json
from pathlib import Path
from romtool import read_rom
from rolo_extract import font_evidence
from m68k_static import walk

NOTES = {
    0x200:'Reset entry, vector 1. Hardware control-port check.',
    0x210:'A5 points to startup constants at $28E; data, not instructions.',
    0x218:'A0=$A00000 A1=$A11100 A2=$A11200 A3=$C00000 A4=$C00004.',
    0x226:'TMSS SEGA write at $A14000 if version low nibble is nonzero.',
    0x238:'Write 24 VDP register values from table $2A8.',
    0x250:'Copy 38 bytes of startup Z80 code from $2C4 to $A00000.',
    0x25c:'Clear 64 KiB work RAM by descending longword writes.',
    0x28c:'Skip startup constants $28E..$2FA.',
    0x300:'ROM integrity routine: second checksum; not graphics/game code.',
    0x31e:'Cold-path startup visual initialization.',
    0x32c:'Poll VDP status bit 3; wait for VBlank edge.',
    0x34c:'Cold-start visual update; meaning of all graphics not reconstructed.',
    0x358:'Mark startup complete and enter main initialization.',
    0x8e0:'Cold startup visuals: RAM clear, VDP configuration and generated tiles.',
    0x93a:'VDP reg 12=$81: H40 (320 pixels); reg 1=$34 has 224-line mode.',
    0x1052:'Main program init: disable interrupts, reset stack, set VDP data pointer.',
    0x13b8:'VDP register baseline; screen remains disabled.',
    0x1414:'Pop return address before clearing all 64 KiB RAM; JMP (A0) is manual return.',
    0x146c:'Main display layout: plane/sprite/scroll table addresses and H40 mode.',
    0x1356:'Main subsystem initialization.',
    0x1388:'Initial main-dispatch pointer $FFC444=$165E.',
    0x139e:'SR=$2500 allows level-6 VBlank, masks lower interrupt levels.',
    0x13a2:'Enable display through VDP register-1 shadow $FFC432.',
    0x149e:'Level-6 autovector handler (ROM vector 30 at $78). Save registers.',
    0x14a2:'TRAP #0 goes to vector 32 at $80, whose bus address is $1074 (RTE).',
    0x14a4:'Manual continuation seed after verified returning TRAP #0.',
    0x14aa:'Increment word at $FFC490 once per handler invocation.',
    0x14b6:'Poll controller through $2314.',
    0x14ce:'Busy flag gates later queued work in interrupt handler.',
    0x1502:'Restore registers before interrupt return.',
    0x1508:'Main loop: wait for VBlank signal, call RAM-held dispatcher, repeat.',
    0x1518:'Unresolved by automatic walk; initial pointer is manually traced to $165E.',
    0x165e:'Initial dispatched state; exact screen/state name still unassigned.',
    0x166a:'One-time state initialization when $FFC466 differs from $165E.',
    0x1688:'State transition writes next main pointer $19BA.',
    0x16c2:'Cache current state pointer at $FFC466.',
    0x2314:'Controller polling and button-state storage; semantics need further tracing.',
    0x2468:'Immediate 68000-to-VDP DMA loader; D0 source, D1 destination, D2 words, D3 command.',
    0x2480:'DMA word count split into VDP registers 19 and 20.',
    0x249a:'Source byte address shifted to word address for DMA registers 21/22.',
    0x24b6:'Source high bits and mode in DMA register 23.',
    0x24c8:'Pack destination and DMA command.',
    0x24f2:'Wait for VDP DMA-busy bit to clear.',
    0x2694:'VDP word-fill helper used for VRAM/CRAM/VSRAM clearing.',
    0x313e:'Copy 102-byte native 68000 routine from $3152 into RAM $FFC3CC.',
    0x31b8:'Verified font DMA arguments: source=$27040, VRAM=$F680, words=$480.',
    0x31d0:'Call DMA loader $2468; raw font/symbol bank is 2304 bytes (72 tiles).',
    0x31d6:'Call copied RAM routine $FFC3CC; automatic ROM walk cannot resolve RAM code.',
    0x3152:'Source of 102-byte RAM routine; actual execution address is $FFC3CC.',
    0x317e:'A7 points at in-routine code slot: source $3192, relocated RAM $FFC40C.',
    0x3192:'Initial NOP placeholder; overwritten by $319A, so static decode is incomplete.',
    0x319a:'Self-modifying write into code slot (A7), using word from referenced object.',
    0x319c:'Next iteration branches to the modified code slot, not necessarily NOP.',
    0x28ea:'Copy object-definition group word at offset +8 into allocated object header.',
    0x29fa:'Scan 48 object records, stride $82, to build active list at $FF98C8.',
    0x2aba:'Append active object pointer in scan order; increment active count at $FFC5B8.',
    0x652c:'Packed initial-scene tile bank at $28A80.',
    0x6538:'Decode backwards LZ into work RAM; returned byte length drives DMA.',
    0x6564:'40x6 title-logo tilemap at $4592C, palette 3 and priority set by D0.',
    0x6582:'Packed title-logo tile bank at $44F1C, loaded after first bank.',
    0x65b2:'40x14 scene-background map at $2B680, written to VRAM $E300.',
    0x65c8:'40x14 scene-frame map at $2BAE0, written to VRAM $C300.',
    0x6670:'Mask source tilemap word to 11-bit index; add caller attribute base.',
    0x66de:'Initial-state target palettes: signed selector -1 selects table row $4B07A.',
    0x702c:'Font character mapping: subtract $20, add $7B4, OR text attributes.',
    0xa75a:'Backwards LZ decoder wrapper; preserves registers and returns decoded byte count.',
    0xa768:'A0 advances by packed block size; A4 points to four distance-width bytes.',
    0xa77a:'Read footer: decoded size in high 24 bits, padding count in low byte.',
    0xa78c:'Read literal-vs-match flag.',
    0xa792:'Literal length accumulated from 2-bit groups; 3 continues.',
    0xa7ac:'LSB-first backwards word reader with sentinel refill.',
    0xa7ba:'Read D0+1 bits into D1, in most-significant-result-bit order.',
    0xa7ce:'Read match selector and distance width.',
    0xa7e2:'Extended-match short-distance form uses 7 bits after helper subtracts one.',
    0xa7e8:'Extended match length accumulated from 3-bit groups; 7 continues.',
    0xa7fa:'Copy overlapping decoded suffix bytes toward beginning of destination.',
    0x713e:'Clear VBlank signal byte $FFC48C and spin until interrupt sets it.',
    0x7ffb0:'Second ROM checksum entry.',
    0x7ffb4:'$1FFEC iterations; each advances source by four bytes.',
    0x7ffba:'Exclude longword at $18C (product-tail and standard header checksum).',
    0x7ffca:'Compare accumulated 32-bit sum to $32EA75C6.',
    0x7ffd2:'Matching sum: return to reset caller.',
    0x7ffd4:'Failure path: VDP/palette writes then permanent loop.',
}


def annotated(result):
    lines = ['; Generated by tools/trace_rolo.py. Offline decoding only.',
             '; Possible direct paths; unknown/indirect flow stops are in companion JSON.',
             '; ROM SHA256 '+result['rom_sha256']]
    for i in result['instructions']:
        if i['address'] in NOTES: lines.append('; '+NOTES[i['address']])
        lines.append(f"{i['address']:06X}  {i['bytes'].upper():<24} {i['mnemonic']:<9} {i['operands']}")
    return '\n'.join(lines)+'\n'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rom'); parser.add_argument('--out',required=True)
    args=parser.parse_args()
    data=read_rom(args.rom); font_evidence(data) # Verify inspected revision and callsite.
    output=Path(args.out); output.mkdir(parents=True,exist_ok=True)
    groups = {
        'startup':([0x200],[(0x28e,0x2fa)],['Reset vector']),
        'frame-paths':([0x165e,0x2468,0x149e,0x14a4,0x1074],[],
                       ['Initial RAM dispatcher value $FFC444=$165E at $1388',
                        'Font DMA loader identified at $31D0',
                        'Level-6 autovector at ROM $78',
                        'Manual TRAP #0 continuation; target $1074 immediately RTE',
                        'TRAP #0 handler from vector 32']),
        'ram-copy-source':([0x3152],[(0x200,0x3152),(0x31b8,len(data))],
                           ['102-byte code copy at $313E and RAM call at $31D6; listing uses source addresses']),
        'backward-lz':([0xa75a],[(0x200,0xa75a),(0xa808,len(data))],
                       ['Called by graphics initialization at $6538 and $658E']),
    }
    for name,(seeds,excluded,reasons) in groups.items():
        result=walk(data,seeds,15000,excluded)
        result['seed_evidence']=reasons
        if name == 'ram-copy-source':
            result['relocation']={'source_start':0x3152,'destination_start':0xffc3cc,'size':102}
            result['dynamic_code_sites']=[{'source_address':0x3192,'ram_address':0xffc40c,
                                          'writer_source_address':0x319a,
                                          'note':'List append MOVE.W A0,(A1..A6)+ words; terminal sentinel patches FFFF but does not execute it; see STAGE2.md'}]
        result['annotations']={f'0x{key:06X}':value for key,value in NOTES.items()
                               if any(i['address']==key for i in result['instructions'])}
        (output/(name+'.json')).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        (output/(name+'.asm')).write_text(annotated(result),encoding='utf-8')
        print(f"{name}: {len(result['instructions'])} decoded instructions, {len(result['stops'])} recorded stops")


if __name__ == '__main__': main()
