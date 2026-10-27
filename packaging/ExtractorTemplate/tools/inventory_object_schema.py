"""Record allocator writes and syntactic field uses without assuming register aliases."""
import argparse
import json
import re
from pathlib import Path
from inventory_rom import inventory

DESTINATION=re.compile(r'^(.*),\(\+([0-9]+),A3\)$')
WIDTHS={'B':1,'W':2,'L':4}

def allocator_write(instruction):
    mnemonic=instruction['mnemonic']
    if mnemonic not in ('MOVE.B','MOVE.W','MOVE.L'):return None
    match=DESTINATION.fullmatch(instruction['operands'])
    if not match:return None
    source,offset=match.groups();size=WIDTHS[mnemonic[-1]]
    return dict(address=instruction['address'],offset=int(offset),size=size,source=source,
        scope='Syntactic A3 destination inside allocator; source semantics and conditional execution kept separate')

def catalogue(rom,project):
    inv,trace=inventory(rom,project/'docs')
    writes=[row for i in trace['instructions'] if 0x28d8<=i['address']<=0x29bc
            and (row:=allocator_write(i)) is not None]
    covered={byte for row in writes for byte in range(row['offset'],row['offset']+row['size'])}
    if covered and max(covered)>=130:raise ValueError('Allocator writes exceed observed pool stride')
    refs=inv['object_field_references'];offsets=sorted({r['offset'] for r in refs}|{r['offset'] for r in writes})
    fields=[dict(offset=offset,allocator_writes=[r for r in writes if r['offset']==offset],
        a5_reference_sites=[r['address'] for r in refs if r['offset']==offset],
        scope='Offset grouping only. Different widths can overlap; A5 identity and field meanings require consuming-code evidence.') for offset in offsets]
    pools=[dict(name='active objects',base=0xff998c,free_stack=0xff9804,stack_pointer_field=0xffc46e,
                count=48,stride=130,evidence=['27F0','27F6','27FC','2802','2804','2808','280A','280E','2812']),
           dict(name='RAM definitions',base=0xff64ae,free_stack=0xff642a,stack_pointer_field=0xff6426,
                count=32,stride=34,evidence=['2816','281C','2822','2828','282A','282C','2830','2834']),
           dict(name='observed terrain-list resources',base=0xff6936,free_stack=0xff68f2,stack_pointer_field=0xff68ee,
                count=16,stride=16,evidence=['2838','283E','2844','284A','284C','284E','2852','2856']),
           dict(name='observed deferred-marker restoration records',base=0xff6aa2,free_stack=0xff6a3e,stack_pointer_field=0xff6a3a,
                count=24,stride=10,evidence=['2860','2866','286C','2872','2874','2876','287A','287E']),
           dict(name='observed contact-list nodes',base=0xff6bbc,free_stack=0xff6b98,stack_pointer_field=0xff6b94,
                count=8,stride=4,evidence=['2888','288E','2894','289A','289C','289E','28A2','28A6'])]
    return dict(rom_sha256=inv['rom_sha256'],pools=pools,allocator_writes=writes,fields=fields,
        bytes_without_direct_allocator_write=[offset for offset in range(130) if offset not in covered],
        counts=dict(pools=len(pools),allocator_writes=len(writes),syntactic_offset_groups=len(fields),
            bytes_with_direct_allocator_writes=len(covered)),
        scope='Static storage/initialization contract only. Unwritten bytes can be set by later paths; allocation failure, partial rollback, linked definitions, runtime aliases and semantic field names still require tracing.')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('rom')
    p.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
    report=catalogue(Path(a.rom).read_bytes(),a.project)
    (a.project/'docs/stage9/object-schema.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report['counts']))

if __name__=='__main__':main()
