"""Shared actor state leaves, phase waits and explicit literal no-op entries."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/actor-pursuit-family-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,actor_cases=2621440)
import re
sources=['src/core/actor_pursuit_family.hpp','tests/actor_pursuit_family_verification_tests.cpp'];pending=list(sources)
while pending:
 source=pending.pop()
 for include in re.findall(r'#include "(core/[^"\n]+)"',(p/source).read_text(encoding='utf-8')):
  child='src/'+include
  if child not in sources:sources.append(child);pending.append(child)
for dep in ['direction-vector','actor-wave-motion','acceleration-bunny']:sources.append('docs/stage9/'+dep+'-verification.json')
exe=root/'work/actor_pursuit_family_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources if not s.endswith('.json'))

inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
specs=[(0xe48c,[(0xe48c,0xe528)],'117gate/objectcontact/playercontact/damage. WrappedcontrolledX-actorX determinesfacing and4000/60000horizontalacceleration; wrappedactorY-controlledY+80 selects2000/20000verticalacceleration. SignedwrappedabsoluteXdistance<=50sets46BYTEFF. Integrateonly,nogravity/floor.'),(0xf7c4,[(0xf7c4,0xf856)],'Contact/direct976C;50WORD=(50+52)&63; CA0A(phase,1) addsfullLONGXY. Zero48gravity;else48decrement and4000/40000pursuitX/Y+16. Integrateaftereitherbranch.'),(0xe15e,[(0xe15e,0xe1bc)],'117gate/contact/direct976C; parent76resolvedbeforephase. Zero46 signextendsparent47to34;nonzeroparent46BYTEsetsup8pixelsandcachesY. Activephasegravity/integrationthen signedanchor<=YclampsY,clearsparent46BYTEandself46WORD inoriginalaliasorder.'),(0xd830,[(0xd830,0xd89e)],'117gate/contact/damage. Nonzero46BYTEclearsitandsetsupdirection/vertical4or8pixelsspeed basedsignedwrappedabsoluteXdistance<=128. Groundbit copiedto47FF/0; airborneintegerwalk1. Gravity,integration,floor,direction inoriginalorder.'),(0xd8be,[(0xd8be,0xd918)],'117gate; first47zero cachesintegerXYanchors. Contact/damage,facecontrolled,smallorbit. Signed46BYTE>10decrements;elsealternateYintegerstep3,nonzero46decrements,zero46callsD11Aandnonnegative resultreloads50BYTE.')]
for start,ranges,contract in specs:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi,(hex(start),hex(at),hex(hi))
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),code_ranges=ranges,instruction_evidence=items,original_bytes=rom[start:max(b for a,b in ranges)].hex(),verification_status='verified',status='verified green: local pursuit/parent/orbit actor contract',native_sources=[sources[0]],checked_cases=524288,contract=contract,proof='One focused fiveactorbatch2621440fullrecordcases:allWORDphase/positioninputs across8gate/contact/alias/timerpartitions. Independentmodularacceleration/branch/smallwaveoracle; CA0Achild reusedunderseparatepinnedproof. Mutatingcontact/gravity/integration/floor/directionservices withallentrysnapshots/callordercompared. Parent self/separatealias tested; fields47and46BYTE/WORDoverlapretained.',scope='Local validstableactor/parent identities andmutablechildservice contracts. Originalacceleration/vector/wavehelpers separatelyverified. Directcontact/gravity/integration/floor/verticaldirection remainexplicitorderedservices; liveSDLcallbackbinding andwholeenemy/referencefidelityexternal. No CPUinstructionexecution.'))

report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/actor-pursuit-family-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Five pursuit/parent/orbit actor contracts verified.')
