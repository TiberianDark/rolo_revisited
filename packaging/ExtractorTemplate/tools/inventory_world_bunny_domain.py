"""Canonical E836 world-rabbit direction domain; no ROM execution."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
from rolo_sprites import sequence_frames

RANGES=((0x28b0,0x29ee),(0x6384,0x63a6),(0x9f72,0x9fee),(0xe7be,0xe912),(0x716e,0x719a))
TARGETS=(0xe84c,0xe872,0xe878,0xe888,0xe894,0xe8a4,0xe8aa,0xe8ba,0xe8c6)

def catalogue(project):
 rom=(project/'local/rolo.md').read_bytes()
 if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM revision mismatch')
 inventory=json.loads((project/'docs/stage9/inventory.json').read_text())
 accepted={a for routine in inventory['routines'] for a in routine['blocks']}
 evidence=[]
 for start,end in RANGES:
  at=start
  while at<end:
   item=Decoder(rom,at).decode()
   if at not in accepted:raise ValueError(f'Unaccepted boundary{at:06X}')
   evidence.append(item);at+=item['size']
  if at!=end:raise ValueError('Range crosses instruction')
 slots=[]
 for selector,target in enumerate(TARGETS):
  slot=0xe83a+selector*2;item=Decoder(rom,slot).decode()
  if item['mnemonic']!='BRA' or item['target']!=target or item['size']!=2 or target not in accepted:raise ValueError('Dispatch slot mismatch')
  slots.append(dict(selector=selector,slot=slot,target=target,bytes=rom[slot:slot+2].hex()))
 frames,controls=sequence_frames(rom,0x13050)
 if controls!=[dict(address=0x13070,command=0,parameter=0)]:raise ValueError('Unexpected animation mutation')
 definition_references=[];other_direction_writes=[]
 for at in sorted(accepted):
  item=Decoder(rom,at).decode();operands=item['operands']
  if '#$00014EDE' in operands:definition_references.append(item)
  if '(+46,A' in operands:
   destination=operands.rsplit(',',1)[-1]
   # Displacement itself contains a comma; use suffix as conservative alias list.
   if operands.endswith(('(+46,A0)','(+46,A1)','(+46,A3)','(+46,A4)','(+46,A5)')) and item['mnemonic'].split('.')[0] not in ('CMP','CMPI','TST','BTST'):
    other_direction_writes.append(item)
 canonical_writers=[0x291a,0xe7e4,0xe80a,0xe82a,0xe858]
 return dict(rom_sha256=ROM_HASH,dispatch=0xe836,canonical_domain=list(range(9)),canonical_targets=slots,instruction_evidence=evidence,
  canonical_writers=[item for item in evidence if item['address'] in canonical_writers],definition_references=definition_references,
  animation=dict(table=0x1304c,selector=0,frames=frames,controls=controls,mutation='Eight frame publications and unconditional loop only; no command56 WriteByte or selector change'),
  proof=['Successful28B0 allocation uses D5=0 and clears LONG46 at291A.','Canonical14EDE callback E7BE clears direction to0 at clamp or expired timer; sole nonzero assignment is716E result[1,9).','Paused branch does not write46; coordinate integration and acceleration helpers do not write46.','Selector0 animation cannot mutate46. Definition linked pointer is0, so allocator has no definition-chain child for this actor.','MOVEQ0D7 then BYTE46 and ADD.WD7,D7 bounds canonical offset0..16 exactly covering9 accepted two-byte slots.'],
  alias_caveats=['29A4 lifetime gateC5A8[type>>2] can replace definition callback withA8BC;14EDE type0 requiresC5A8[0]=0 for canonical E7BE path.6384 clearsindex0, but all entry ancestry and persistent mutations need separate caller proof.','Accepted-instruction field46 alias list includes other actor callbacks and menu/cursor mutations. Numeric offset equality alone does not prove14EDE alias; no global all-caller closure is claimed.','C5BA external writes, arbitrary direct E7BE calls, callback42 mutations, interrupt aliases and actor reuse after failed allocation remain unclosed.','Allocation failure does not initialize a rabbit;9F72 publishes return0 without a separate failure branch.'],
  all_accepted_direction_destination_candidates=other_direction_writes,
  globally_resolved=False,status='Canonical original world actor domain proven conditional on successful allocation and original callback identity; all-caller alias closure pending')

if __name__=='__main__':
 project=Path(__file__).resolve().parents[1];report=catalogue(project)
 (project/'docs/stage9/world-bunny-domain-contract.json').write_text(json.dumps(report,indent=2)+'\n')
 print('Verified canonical9-slot E836 dispatch; global alias closure explicitly pending')
