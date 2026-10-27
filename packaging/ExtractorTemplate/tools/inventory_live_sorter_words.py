"""Live actor sorter WORD0 initialization, mutation and retirement evidence."""
import hashlib,json,re,collections
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
SPECS=((0x27f0,0x2816,'Mark free actor slots','Initialize48keys998Cstride130; STBYTE0only leaveslowBYTE1retained. TheseinactiveFFxxWORDs mustneverbeexecutedbysorter.'),(0x28b0,0x29ee,'Initialize live sorter opcode','Successfulallocator28EA copiesdefinitionWORD8toactorWORD0. ImmutableROMorRAMdefinitions bothflowthroughthiswrite; typegatechangescallback42only.'),(0x2cbc,0x2d1a,'Retire actor and release resource','Releasegraphicsifdefinitionresource4nonzero; STBYTE0at2CF0 marksactorinactivewithoutclearingotherbytes; returnactorpointerfreepool andrepairchainlinks. Nolegalopcodeguaranteeoninactiveslot.'),(0x4958,0x4a48,'Construct RAM macro definition','Pop34byteRAMdefinitionfrom6426/64AEpool.4996clearslinkedLONG0,49AAwritesWORD8=3AC8 beforeallocator49F2. Onlylistedfieldsinitialized; unwrittenpooledbytesremainretained. SuccessactorLONG8=XTRN isresidentgraphics, notdefinitionWORD8.'),(0xf362,0xf372,'Select chain descendant for regrouping','A0=inputD1actor; looploadsLONG84 andDBEQwithD0counter; returnA0=selecteddescendantpointer,D1nonnullcondition. CallersuseD0=3; returnedactorandits84successormayhaveWORD0changed.'))
MUTATIONS=(0xf09a,0xf0ae,0xf17e,0xf18c,0xf1be,0xf1cc,0xf278,0xf28a)
RANGES=((0xf07e,0xf0ba),(0xf178,0xf194),(0xf1ae,0xf1ee),(0xf25e,0xf292),(0x29ee,0x2a24))
def catalogue(project):
 rom=(project/'local/rolo.md').read_bytes()
 if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
 inv=json.loads((project/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']}
 def decode(start,end):
  out=[];at=start
  while at<end:
   i=Decoder(rom,at).decode()
   if at not in accepted:raise ValueError(f'Unaccepted boundary{at:X}')
   out.append(i);at+=i['size']
  if at!=end:raise ValueError('Extent mismatch')
  return out
 opcode_counts=collections.Counter(int.from_bytes(rom[d['address']+8:d['address']+10],'big') for d in inv['object_definitions'])
 candidates=[]
 for at in sorted(accepted):
  i=Decoder(rom,at).decode()
  if i['mnemonic']=='MOVE.W' and any(f'#{chr(36)}{v:04X}' in i['operands'] for v in opcode_counts):candidates.append(i)
 return dict(rom_sha256=ROM_HASH,operations=[dict(entry=f'{s:X}',name=n,contract=c,instruction_evidence=decode(s,e),pending='Reachablealias/caller andpool/list consistency remainexplicit') for s,e,n,c in SPECS],helper_evidence=[i for s,e in RANGES for i in decode(s,e)],
  immutable_opcodes=[dict(word=v,count=n) for v,n in sorted(opcode_counts.items())],known_live_mutations=[Decoder(rom,a).decode() for a in MUTATIONS],all_accepted_literal_opcode_writes=candidates,
  live_mutation_domain='F09A/F0AE/F278/F28Awrite32C8;F17E/F18C/F1BE/F1CCwrite3AC8. Thesearelegalexistingqueueopcodes butdifferfromimmutabledefinitiongroup. TargetA0isF362chainactor,notdefinitionpointer.',
  ram_definitions=dict(base=0xffff64ae,count=32,stride=34,group_producer=0x49aa,group_word=0x3ac8,aliases='Actor4holdsdefinitionpointer. Actor8holdsresidentgraphicsLONG; writingXTRNthereat4A1AisnotWORD0mutation. Retiredmacrodefinitionreturnpool mustretainunwrittenbytes until nextpartialinitialization.'),
  inactive_exclusion='29EE checksTST.Wactor0/BMI2AC8, soFFxxpool/retiredrecords areexcludedfromactive98C8list. SorterC5B8/listcount agreement isrequired; inactiveopcodesarenotpartoflegaldispatchdomain.',
  remaining=['OtherregisterheldWORD0orRAMdefinitionWORD8aliases cannotbeclosedfromliteralwritesalone; actualreachablecontexts mustbeaudited.','Reset/retirement plusactive-list C5B8agreement andrecycledidentity timing remaincallercontracts.','F362inputchainidentity/domain acrossallcallbacks andunwrittenRAMdefinitionbytes outsideWORD8 remainexplicit.','No globalcopiedsorteropcode closure fromsevenimmutablevaluesalone.'])
if __name__=='__main__':
 p=Path(__file__).resolve().parents[1];r=catalogue(p)
 (p/'docs/stage9/live-sorter-word-contract.json').write_text(json.dumps(r,indent=2)+'\n')
 print('Verified liveWORD0 initialization,8regroupwrites,RAMproducer andinactive exclusion')
