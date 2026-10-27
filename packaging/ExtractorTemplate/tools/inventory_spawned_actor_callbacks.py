"""Bounded spawned actor/breakable callback entries and literal tables."""
import hashlib,json,struct
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
SPECS=((0xb714,((0xb714,0xb726),),'Initialize thrown actor then original handler','B782randomvelocity;definitionA4=actor4; callback42=definitionLONG12; JMPsamecallback immediately. NotordinaryRTSafterinitialization.'),(0xb726,((0xb726,0xb782),),'Thrown actor until landing','117bit1set skips.46BYTEzero→setFFandB782. CD8E,CFCE,CF46; signedclampX32..F330-32. If124bit0grounded clear46 andrestoredefinitioncallback12; fractions/speedsnotexplicitlyreset.'),(0xb7b8,((0xb7b8,0xb804),),'Offscreen retirement and free debris motion','TST117/SNE116 thenfallthroughB7C0. Once46zero setFF/B7D8randomvelocity, thenCD8E/CFCE; nofloorcollision. B7D8 horizontaldirectionRNG[0,3)-1, speedLONG3<<16; upwardspeedRNG[3,9)<<16;122FF.'),(0xb804,((0xb804,0xb80a),),'Contact-only resting macro wrapper','Call90A0thenRTS; noexplicitfieldwrites orgatedsuccessreturn.'),(0xb80a,((0xb80a,0xb8ee),),'Breakable macro activation and rest','WORD56nonzero skipsactivation.9132contact; controlledC4E0attachment98mustbeA5,controlled122negative,Y>=macroY. SaveinitialYto56,updirectionFF,copycontrolled62speedandclearcontrolledverticalmotion. RepeatedlyspawndefinitionLONG50 atactorX/Y-height withD4/D7zero; failureskipstoverticalupdate. SuccesscallbackB726orB714dependingchilddefinitionBYTE7bit3;decrementBYTE55andloopwhilenonzero. AfterCD8E/CFCE,landatstoredY,clearfraction/verticalspeed/direction/56,setB804,markerBYTE92=0. NonnegativeBYTE54publishesreplacement93andqueuesmacrographics4B2E.'),(0xb8ee,((0xb8ee,0xb956),),'Spawn limited rising reward actors','BYTE50zero initializesFF,C5CE=0,BYTE53/52=100. While signedC5CE<3,decrementBYTE52; onlyborrow reloadsdelaymax(old53,41)-2 andspawns1474CatfullXY. Noallocationfailurebranch. AtC5CE>=3,decrementYintegerWORDtoward0.'),(0xb956,((0xb956,0xb9cc),(0xba14,0xba5e)),'Rising collectible contact and completion','46zero initializesdirectionfrom6BYTEtable,speedRNG[1,5)<<16thenLONG>>1,122FF,vertical8<<16. AirborneCD8E/CFCE/CF46;newgroundincrementsC5CE.9012contact;123nonzero setscallbackB7C0,selector70=4,46=0; RNG[0,17)selectsliteralspawn table,allocationatfullXY,successsetsB726. AlreadygroundedC5CE>=3setsB7C0/46zero. Literal17LONGtableexcludedfromcode.'))
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
 for s,ranges,n,c in SPECS:
  items=[i for a,b in ranges for i in decode(a,b)]
  defs=[dict(address=d['address'],bytes=rom[d['address']:d['address']+34].hex(),linked=d['linked'],handler=d['handler']) for d in inv['object_definitions'] if d['handler']==s]
  operations.append(dict(entry=f'{s:X}',name=n,contract=c,instruction_evidence=items,immutable_definitions=defs,calls=[i for i in items if i['mnemonic'] in('BSR','JSR')],return_clause='LiteralreturnCCR/registers orB714tailcallback; nostableD0successguaranteeasserted.',pending='ActualA5/controlled/definition/markeridentities, helpercontact/terrain effects, count/timerdomains/native/reference integration remainpending.'))
 producers=[]
 for a in sorted(accepted):
  i=Decoder(rom,a).decode()
  if i['mnemonic']=='MOVE.L' and '(+42,' in i['operands'] and any(f'#{chr(36)}{t:08X}' in i['operands'] for t in entries):producers.append(i)
 return dict(rom_sha256=ROM_HASH,operations=operations,helper_evidence=decode(0xb782,0xb7b2)+decode(0x4878,0x48c8),accepted_immediate_callback_producers=producers,
  immutable_data=[dict(start=0xb7b2,end_exclusive=0xb7b8,bytes=rom[0xb7b2:0xb7b8].hex(),use='6directionBYTEweightedtableB782'),dict(start=0xb9cc,end_exclusive=0xba14,words=list(struct.unpack_from('>17I',rom,0xb9cc)),use='17LONGspawnweightedtableB956'),dict(start=0xba5e,end_exclusive=0xba64,bytes=rom[0xba5e:0xba64].hex(),use='6directionBYTEtableBA38'),dict(start=0x48c8,end_exclusive=0x48d8,bytes=rom[0x48c8:0x48d8].hex(),use='Class0C? actualdispatch4878macroparameter8byte descriptors; BYTE0macro,BYTE1replacement54,BYTE2count55,LONG4spawn50. Onlyboundedtablebytes,fullparameterextentunproved.')],
  register_identity='B80Asaves/restoresA5acrossallocator,thenusesA4allocatedhead. B8EE/B956allocationpathsdo notrestoreA5:28B0 mayleaveA4head/A5tail. D0/CCRallocationreturns determine explicitBEQsites only; no wrapperpreservation invented.',
  failure_domains=['B80A56=0sentinelaliasesactivationatworldY0;noadditionalbooleaninvented.','B80A55count0underflowsFFandcanspawnup to256times untilallocationfailure;canonicalcountneedsdescriptorproof.','B714definitionoriginalcallbackmustnotrecurseB714;validityrequiresactualproducer/definitiondomain.','B8EE1474Callocationfailureisnotretriedwithinframeandtimerstilladvances.','B956tableweights/duplicatepointersmustremainliteral; dontsubstituteuniformuniquedefinitionchoice.'],
  scope='Sevenboundedentrycontracts joinedtolocalspawn/motion states; nofullactorlifecycle orspeciescompletionclaim.')
if __name__=='__main__':
 p=Path(__file__).resolve().parents[1];r=catalogue(p)
 (p/'docs/stage9/spawned-actor-callback-contract.json').write_text(json.dumps(r,indent=2)+'\n')
 print('Verified7spawnedactorentrycontracts; literal tables separated')
