"""Bounded connected actor entry contracts, not complete actor lifecycles."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
SPECS=((0xb2d2,0xb2e6,'Visible actor vertical update','A5actor. NonzeroBYTE117 returns unchanged; elseCD8E,CFCE,CF46 in order. Noexplicitcallbackwrite, allocation, sound ordefinedD0result.'),(0xb3c4,0xb3f2,'Visible moving contact actor update','A5actor;117nonzero skips.8EAAenrolcontact,9012contacttest; nonzeroresultcalls96C6injury/contactservice. ThenD1CA,CD7A,CD8E,CFCE,CF46,CE14 in order. Calleeeffects/returns notcollapsedtoonesuccessflag.'),(0xb3f2,0xb440,'Visible actor minimum horizontal speed update','117nonzero skips.8EAA,9012 andconditional96C6. SignedWORD58<=1 setsWORD58=1 retainingfractionWORD60;D168setsfacingfromterrain/bounds,thenBYTE121set+1orFFfrom118bit3. ThenD1CA,CD7A,CD8E,CFCE,CF46. NoCE14callhere.'),(0xb440,0xb47c,'Attach presentation actor to base actor head','ResolveC4E4baseA0, itsLONG84headA1. A5Xinteger=baseX plus(headWORD32+12)negatedwhenbase118bit3; A5Yinteger=baseY+headWORD34-3; copybaseBYTE118. FractionWORDS14/18remainuntouched. No117gate ornullchaincheck.'),(0xb47c,0xb498,'Integrate actor and mark offscreen retirement','AlwaysCFCEfirst. If117zero return; otherwisetest126bit3, setBYTE116=FFwhenbitclear/0whenset, thenBSET126bit2. Contactlistlatecleanup/disposal mustpreserveoriginalflagorder.'),(0xb498,0xb51e,'Visible reflected actor resting transition','117nonzero returns. DefinitionA4=actor4. IfdefinitionBYTE26bit7clear,setactor119bit4. SignedclampXto8..F330-8; clamping skipsphysicsandnegatesBYTE121. InboundsCD7A,CD8E,CFCE,CF46,CE14 then124mask6nonzero also negates121. Nonzero121returns; zero sets126bit2. Definitionbit7set restorescallbackfromdefinitionLONG12; otherwisecallbackB51EandWORD46=250.'),(0xb51e,0xb566,'Timed actor reset and upward terminal motion','No117gate. D1CA,CD7A,CFCE,CD8E,CF46; decrementWORD46. Exactlyzero restoresdefinitioncallbackLONG12 andclears119bit4. Nonzero signedWORD46<=50 with124bit0set setsBYTE122FF andWORD62=2 retainingfractionWORD64. Otherwisereturn.'))
def catalogue(project):
 rom=(project/'local/rolo.md').read_bytes()
 if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
 inv=json.loads((project/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']}
 def decode(start,end):
  at=start;out=[]
  while at<end:
   i=Decoder(rom,at).decode()
   if at not in accepted:raise ValueError(f'Unaccepted boundary{at:X}')
   out.append(i);at+=i['size']
  if at!=end:raise ValueError('Extent mismatch')
  return out
 targets={s for s,e,n,c in SPECS};operations=[]
 for s,e,n,c in SPECS:
  items=decode(s,e)
  definitions=[dict(address=d['address'],bytes=rom[d['address']:d['address']+34].hex(),callback=d['handler'],type_word=int.from_bytes(rom[d['address']+10:d['address']+12],'big'),flags_byte26=rom[d['address']+26],linked=d['linked']) for d in inv['object_definitions'] if d['handler']==s]
  operations.append(dict(entry=f'{s:X}',name=n,contract=c,instruction_evidence=items,immutable_definitions=definitions,calls=[i for i in items if i['mnemonic'] in('BSR','JSR')],return_clause='RTSwithliteralfieldchangesandlastcallee/compareCCR; no stableallocation/successD0contract asserted.',pending='A5liveidentity, immutableversusRAMdefinitionaliases, helpercontact/terrain/state effects andnative/refverification remainincomplete.'))
 producers=[]
 for a in sorted(accepted):
  i=Decoder(rom,a).decode()
  if i['mnemonic']=='MOVE.L' and '(+42,' in i['operands'] and any(f'#{chr(36)}{t:08X}' in i['operands'] for t in targets):producers.append(i)
 return dict(rom_sha256=ROM_HASH,operations=operations,accepted_immediate_callback_producers=producers,helper_evidence=decode(0xd168,0xd1ca),
  callback_restore_sites=[0xb516,0xb558],restore_domain='ActorLONG4 suppliesdefinitionLONG12; RAMdefinitionmutation canchange restoredcallback. Noimmutable-only assumption.',
  arithmetic='WORDcoordinate/speed/timer writes retainadjacentfractionWORDS. SignedBGT/BGE inB3F2/B498/B51E mustnotbeconvertedunsigned. Timer0underflowsFFFFthenfollowsnonzero<=50path, notimmediaterestore.',
  failure_domains=['B440 requiresnon-nullC4E4/head84; nooriginalnullcheck.','Contactnodeallocation8EAA mayexhaust; callbackwrappersdo notintroducefailurebranch.','B498mapwidthbelow16orwrappedcoords preserveliteralclamporder; noextentvalidationinROM.','B51Ecallbackdefinitionpointer andtimerinitialization requiresactualB498orothercallerprovenance.'],
  scope='Seven bounded entries with definition/producers and exactlocalcallorder; notfullactorspecies/lifecycle completion orbranch-slot relabeling.')
if __name__=='__main__':
 p=Path(__file__).resolve().parents[1];r=catalogue(p)
 (p/'docs/stage9/connected-actor-callback-contract.json').write_text(json.dumps(r,indent=2)+'\n')
 print('Verified7boundedactorcallbackentries andimmutable/producer sources')
