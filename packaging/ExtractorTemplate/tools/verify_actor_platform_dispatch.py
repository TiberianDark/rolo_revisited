"""Shared actor state leaves, phase waits and explicit literal no-op entries."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/actor-platform-dispatch-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,carry_cases=1048576,dispatch_cases=8192)
import re
sources=['src/core/actor_platform_dispatch.hpp','tests/actor_platform_dispatch_verification_tests.cpp'];pending=list(sources)
while pending:
 source=pending.pop()
 for include in re.findall(r'#include "(core/[^"\n]+)"',(p/source).read_text(encoding='utf-8')):
  child='src/'+include
  if child not in sources:sources.append(child);pending.append(child)
dependencies=['platform-contact','actor-wave-motion','actor-platform-family','actor-rider-platforms','actor-triggered-platforms','actor-bounce-chain-platforms','actor-common-state']
for name in dependencies:sources.append('docs/stage9/'+name+'-verification.json')
exe=root/'work/actor_platform_dispatch_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources if not s.endswith('.json'))
expected_targets=[0xbee0,0xbf54,0xc022,0xc08a,0xc0ec,0xc160,0xc18e,0xc1bc,0xc1f8,0xc244,0xc2b4,0xc322,0xc3ee,0xc4ba,0xc51e,0xc582,0xc61a,0xc6aa,0xc730,0xc7b8,0xc7fc,0xc844,0xc850]+list(range(0xc85a,0xc86c,2))
assert len(expected_targets)==32
for i,target in enumerate(expected_targets):
 instruction=Decoder(rom,0xbe60+4*i).decode();assert instruction['mnemonic']=='BRA' and instruction['target']==target

inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
specs=[(0x8a0c,[(0x8a0c,0x8a68)],'Snapshotintegerdisplacement58/62,copyto60/64. VisitbaseC4E4thenthreeliveslots; ifrider98equalsplatform and124bit5set addintegerXY. Aliasesvisitagain. Finallyclear58/62highWORDonly,leavingcopieddisplacementsin60/64.'),(0xbe4e,[(0xbe4e,0xbe60)],'Run90A0contactroster, thenreadliveWORD54 andselectoneof32translatedtargets usingaligned0..124offset, then8A0Cridertransfer. Contacts canchange54andtypedretainedD1/D3context beforeselection. All23statefultargetsand9literalnoopsdispatchtonativefunctions.')]
for start,ranges,contract in specs:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi,(hex(start),hex(at),hex(hi))
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),code_ranges=ranges,instruction_evidence=items,original_bytes=rom[start:max(b for a,b in ranges)].hex(),verification_status='verified',status=('verified green: literal no-op entry' if contract.startswith('Literal BRA') else 'verified green: local actor platform dispatch contract'),native_sources=[sources[0]],checked_cases=1048576 if start==0x8a0c else 8192,contract=contract,proof='One focused composition batch:1048576WORDdisplacement/alias/flagcases compareall48actorrecords;8192all32selectorintegrations comparemanualoriginalslotmap withcertifiedchildfunctions andindependentridertransferoracle. Contactrestorechangesoldselector124toeachactualselector, retainedcontext andsupportflags; servicelog/flags/fullpoolcompared. Original32BRA-targettable pinned; directordered90A0and8A0Cchildcalls reviewed.',scope='Local typedplatformcaller composition for validactors,alignedselector0..124 andallchildproofdomains. Fixedsixlinkchain,gridphase,explicitincomingD1context/D3highWORD andmutablecontact/direction/allocation boundaries retained. ActualCPUregisterancestry,liveSDLworldadapter andrestore8A68service remainexternal. This doesnotcertifywholeplatformgameplay.'))

report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/actor-platform-dispatch-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Platform dispatcher and rider-transfer local contracts verified.')
