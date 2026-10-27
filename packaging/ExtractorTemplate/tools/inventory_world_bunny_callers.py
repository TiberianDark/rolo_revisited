"""Actual original-world allocation/list callback identity dependencies."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder

RANGES=((0x1bf2,0x1c46),(0x6384,0x63a6),(0x2994,0x29de),(0x29ee,0x2b8c),(0xc9ae,0xca0a),(0xa808,0xa84c),(0x9fcc,0x9fee))
def catalogue(project):
 rom=(project/'local/rolo.md').read_bytes()
 if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
 inventory=json.loads((project/'docs/stage9/inventory.json').read_text());accepted={a for r in inventory['routines'] for a in r['blocks']}
 evidence=[]
 for start,end in RANGES:
  at=start
  while at<end:
   i=Decoder(rom,at).decode()
   if at not in accepted:raise ValueError(f'Unaccepted boundary{at:X}')
   evidence.append(i);at+=i['size']
  if at!=end:raise ValueError('Instruction extent mismatch')
 absolute=[]
 for at in sorted(accepted):
  i=Decoder(rom,at).decode()
  if any(s in i['operands'] for s in ('C5A8','C5BA','C5A9','C5AA','C5AB','C5AC','C5AD','C5AE','C5AF')):absolute.append(i)
 return dict(rom_sha256=ROM_HASH,scope='Successful original world-entry lifecycle and canonical callback identity; not arbitrary direct-call closure',instruction_evidence=evidence,accepted_absolute_alias_references=absolute,
  lifetime_gate=dict(initializer=0x6384,caller=0x1c06,writes='Clear16bytesC5A8..C5B7; set offsets2,3,4,5 only. Index0 remains0.',consumers=[0x299e,0x2b4e],canonical_effect='14EDE typeWORD0 selectsindex0 atallocator29A4, so callback isE7BE, notA8BC.',actual_other_writes='Accepted absolute C5B6 writes belong to index14 and do not affectindex0. No other accepted absolute references toindex0..7.',pending='Register aliases outside these bounded reachable world services require separate evidence if discovered; numeric field46 candidates are not a blocking actor alias by themselves.'),
  pointer=dict(address='C5BA',writers=[0x9fde],readers=[0x9e98],effect='Sole accepted absolute writer stores second allocation return. Paused camera reads pointer; neither camera norE7BE replaces it.'),
  callback_path=dict(order=['29EE lifetime/list rebuild','A808 callback dispatch','9E98 camera','FCD4 animation','FAA0 publication'],list='29EE enumerates48pool entries at998C with130byte stride, skipping inactiveWORD0; lifetime survivor appends98C8 list and clears126bit6.14EDE definitionbyte26bit3 exempts offscreen top/bottom path from retirement.',dispatch='A808 firstC9AE builds640E list from cursor/companion attachments. Then each640E and98C8 actor uses BSET126bit6 and invokesLONG42 exactly once unless bit alreadyset. Successful original rabbit is in98C8 survivor list, not controlledcursor/companion list.',callback42='Allocator29B0 setsLONG42 to definitionE7BE when lifetimeindex0clear.29EE/AD8 lifetime path/A808/C9AE/E7BE do not overwrite42 for this actor.',mutations='Existing callbackmutation inventory controlledactor and threecompanion-list setters targetC4E0/6402, which9F72 publishes cursor/clears respectively. They do not targetC5BA on original world path.'),
  canonical_dependency_status='Known C5A8[0], C5BA absolute writes and actualA808 callback path established for original successful allocation following1BF2 initialization; no all-caller/globaldispatch closure claim',
  remaining=['Initial entry1BF2 must have run to establish lifetime defaults; synthetic direct1AFE entry witharbitrary retainedstate is not covered.','Allocator exhaustion and actor retirement/reuse remain exceptional caller domains.','Register-held alias writes not reachable through bounded original world services should not be invented as demonstrated mutations.'])
if __name__=='__main__':
 project=Path(__file__).resolve().parents[1];report=catalogue(project)
 (project/'docs/stage9/world-bunny-caller-contract.json').write_text(json.dumps(report,indent=2)+'\n')
 print('Verified original world rabbit initializer, lifetime/list and callback dispatch dependencies')
