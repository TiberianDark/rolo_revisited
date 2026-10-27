"""Pin local injury branches and valid original phase tables; no ROM execution."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
result=root/'work/actor-orbit-leap-results.json';r=json.loads(result.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,state_cases=2097152,boundary_cases=11968)
sources=['src/core/actor_orbit_leap.hpp','tests/actor_orbit_leap_verification_tests.cpp'];pending=list(sources)
while pending:
 source=pending.pop()
 for include in re.findall(r'#include "(core/[^"\n]+)"',(p/source).read_text(encoding='utf-8')):
  child='src/'+include
  if child not in sources:sources.append(child);pending.append(child)
exe=root/'work/actor_orbit_leap_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)

inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
specs=[(0xd960,[(0xd960,0xda22)],'Contacts; zero46BYTE captures fullXY anchors and clears50highWORDonly. Positive46 proximity uses signedwrapped200pixel directional window. Negative46 reads old50WORD phase; zero phase resets48=580 andtoggles121bit0. Signed48WORD shifted8 adds/subtracts50LONGby121nonzero. SUB.W32borrow sets46=1 andfacing. CertifiedCCF8wave uses oldphase100/divisor1 plus full anchors.'),(0xe620,[(0xe620,0xe6d8)],'117gate,object/playercontactdirecthurt. Unless124bit4set,clear58LONG/selector,choosefacingby wrappedXdelta. SignedabsoluteX<=100 includes8000. Ydelta[-16,150]arms124bit4,122FF; clamped arithmeticYdelta/4 to4..10writes62highWORDpreservingfraction,58LONG60000,selector4. Gravity/integrate/landalwaysafteractivepath.')]
for start,ranges,contract in specs:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),original_bytes=rom[start:max(b for a,b in ranges)].hex(),code_ranges=ranges,instruction_evidence=items,verification_status='verified',status='verified green: local orbit and leap contract',native_sources=[sources[0]],checked_cases=1048576,contract=contract,proof='One focused related family test;2097152statecasescompareallthreeactorrecords,liveA5andallmutablecontact/motionentrysnapshots. Independentwaveintegerformula,rawsignedmodulararithmeticandoldphaseoracle. Added11968explicitcrossproductleapthreshold/signed8000/fractionfixtures beforeadmission,thenreranonlythischangednewbatch. AllWORDspeedvalues,zero/positive/negativephasepaths,borrowandphasezeroreset represented.',scope='Localvalidactors andexplicitcontact/damage/hurt/controlled/gravity/integration/landingservices. ExistingCCF8nativewave withinamplitude100/divisor1domain. Callerdataancestry,liveSDLbindingandcompleteenemyoriginal-referencefidelityremainexternal.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(result.read_bytes()).hexdigest())
(p/'docs/stage9/actor-orbit-leap-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Two orbit/leap contracts verified.')
