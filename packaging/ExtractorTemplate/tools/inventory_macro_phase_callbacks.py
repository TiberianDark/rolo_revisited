"""Bounded macro/phase actor callbacks with dispatch and literal exclusions."""
import hashlib,json,struct
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
SPECS=((0xba64,((0xba64,0xba9e),),'Dispatch actor BYTE50 mode','ZeroextendBYTE50,multiplyWORD4,JMPBA72indexed. ElevenacceptedBRAslots shown; selector0..10callerproof remainsrequired. Notcompleteimplementations ofbranchhandlers.'),(0xba9e,((0xba9e,0xbb84),),'Activate macro and update linked group','WORD56gate;9132contact; controlled98==A5,updirectionnegative,Y>=macroY andLONG46!=BE46required. Transferupmotion, saveY56,spawnLONG50childrenB726withBYTE55loop; allocationfailurefallstoupdate. CD8E/CFCE; clampatstoredYandclearfraction/verticalspeed/56. BYTElookupBB84indexedWORD20selectsF28Cgroup; settledpathsetsthreeactors70=4. EveryactivepathsetsthreeactorsLONG46=BE46. LookupMOVE.B retainsD0upperBYTE, soWORD20domainmatters.'),(0xbe4e,((0xbe4e,0xbe60),(0xbe60,0xbee0)),'Dispatch macro motion WORD54','90A0contact; WORD54indexesBE60JSRtable; then8A0Cpublication/helper;RTS. Thirtytwoaccepted4bytebranchslots; noselectoralignment/rangecheck. RAMmacroproducer4A26 suppliesoriginalmodeWORD54.'),(0xd452,((0xd452,0xd49e),),'Animate counter vertical wave','WORD46byteoffsetintoD4A0WORDwave. Nonnegativewavevalue optionallynegatedbyBYTE49, addsignextendedBYTE48to46andwavevalueYinteger. Negativewave entersD478; ADDQincrementsoriginalindexD0, notwaveD1. Negativewrapped(index46+1) marks116FFandclearsC4D8; otherwisedecrementBYTE50andonzero46-=2/set48FE/49FF. Offset/timer domainscallerconditioned.'),(0xd57e,((0xd57e,0xd624),),'Phase actor completion gate','D4CCsharedphasefirst. WORD46zero cachesXandD558resetsphaseglobals. OtherwiseX=46-F268. F2B5orC5EAzero gatescontactstage.8EAAconditionflagsmaysetF2B5/F2B8=8 andclearF2BA. Selector70==4setsC5E8FF,callsD3FE,spawns14E78at560,513,thenF2B5..F2B8=1/F2BA0 regardlessallocationresult.'),(0xd624,((0xd624,0xd6c6),),'Phase actor conditional selector and spawn','D4CC; zero46cachesXandD558reset. ElseX=46-F268. WhenF2B5zero:8EAAflagsmaysettimers;selector70==12setsC5E9FF/returns. Elseorafterthat,48nonzero→D77Cspawn. IfC5E6!=3 and(C490&127)==63, comparecontrolledtop againstactorY+34 andset70=4or8signedcomparison.'),(0xd6c6,((0xd6c6,0xd77a),),'Phase actor followup selector and spawn','D4CC; initialcache/resetasabove. F2B5zero andC5E9set enables8EAA;selector70==12setsC5EAFF/returns.48nonzero→D77Cspawn. OtherwiseC5E6!=3 and(C490&127)==0 chooses70=4or8fromsignedactorY+34-height versuscontrolledY. Phase3onlyreevaluateswhen(F268&FFF8)==0130.'))
HELPER_RANGES=((0xd4cc,0xd554),(0xd558,0xd57e),(0xd77c,0xd7c6))
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
 entries={s for s,rs,n,c in SPECS};operations=[]
 for s,rs,n,c in SPECS:
  items=[i for a,b in rs for i in decode(a,b)]
  defs=[dict(address=d['address'],bytes=rom[d['address']:d['address']+34].hex(),linked=d['linked']) for d in inv['object_definitions'] if d['handler']==s]
  operations.append(dict(entry=f'{s:X}',name=n,contract=c,instruction_evidence=items,immutable_definitions=defs,calls=[i for i in items if i['mnemonic'] in('BSR','JSR')],return_clause='LiteralCCR/registereffects; no stableD0successflag asserted.',pending='Liveactor/definition/selector/group identities, helperphysics/contact effects andnative/reference integration remainpending.'))
 producers=[]
 for a in sorted(accepted):
  i=Decoder(rom,a).decode()
  if i['mnemonic']=='MOVE.L' and '(+42,' in i['operands'] and any(f'#{chr(36)}{t:08X}' in i['operands'] for t in entries):producers.append(i)
 branch_tables=[]
 for start,end in((0xba72,0xba9e),(0xbe60,0xbee0)):
  slots=decode(start,end)
  if any(i['mnemonic']!='BRA'or i['size']!=4 for i in slots):raise ValueError('Branch table mismatch')
  branch_tables.append(dict(start=start,end_exclusive=end,slots=[dict(offset=i['address']-start,target=i['target']) for i in slots]))
 return dict(rom_sha256=ROM_HASH,operations=operations,helper_evidence=[i for a,b in HELPER_RANGES for i in decode(a,b)],accepted_immediate_callback_producers=producers,branch_tables=branch_tables,
  literal_data=[dict(start=a,end_exclusive=b,bytes=rom[a:b].hex()) for a,b in((0xbb84,0xbb8e),(0xd49e,0xd4cc),(0xd554,0xd558),(0xd7c6,0xd7de))],wave_words=list(struct.unpack_from('>22h',rom,0xd4a0)),
  helpers=dict(phase='D4CConceperC491BYTEchangeusingC5E7; setwidthF330=640;C5E8gatesprogress. C5E4+=2&511,wrapadvancesC5E6mod4;4BYTEtableD554selectsCCF8parameter; resultsetsF268. Framephasegatesound3D.',reset='D558clearsC5E4/C5E6/C5E7/C5E8/C5E9/C5EA only.',spawn='D77CBYTE48minus1zeroextendedthenmultiply8selectsD7C6signedLONGXYoffsetpair. Spawn147F6atfullfixedXYplusoffsets,save/restoreA5; successcopies48tochild/clearsparent48/sound2C. Failureleavesparent48forlaterretry. FulloffsettableextentrequiresBYTE48domain.'),
  failure_domains=['BA64/BE4Edispatcherentries are notcompletebranchactors; selectoroutsidecanonicalslots unproved.','BA9Egroup lookupWORD20/highBYTEretention/non-nullthreeF28Cactors requiresproducerproof.','D452waveindex/arbitrarynegativeword domains remainunclosed.','D57Eupdatesglobaltimers evenallocationfailure; no inventedrollback.','D77Cinvalid48 canreadoutsideknownoffsetpairs; failurepreservesretryrequest.'],scope='Sevenboundedcallbackentries andconnectedsharedhelpers, notfullscene oractorfamilycompletion.')
if __name__=='__main__':
 p=Path(__file__).resolve().parents[1];r=catalogue(p)
 (p/'docs/stage9/macro-phase-callback-contract.json').write_text(json.dumps(r,indent=2)+'\n')
 print('Reviewed7macro-phaseentries,dispatchtables andliteralexclusions')


