"""Pin local injury branches and valid original phase tables; no ROM execution."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
result=root/'work/actor-facing-emitter-results.json';r=json.loads(result.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,state_cases=2097152,boundary_cases=180)
sources=['src/core/actor_facing_emitter.hpp','tests/actor_facing_emitter_verification_tests.cpp'];pending=list(sources)
while pending:
 source=pending.pop()
 for include in re.findall(r'#include "(core/[^"\n]+)"',(p/source).read_text(encoding='utf-8')):
  child='src/'+include
  if child not in sources:sources.append(child);pending.append(child)
exe=root/'work/actor_facing_emitter_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)

inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
specs=[(0xdc2c,[(0xdc2c,0xdcda)],'117gate,object/playercontact/damage. Live48requestclearsbefore149B0allocation;integerX/Y-16becomehighWORDs withliveincomingD2/D3highWORDfractionsretainedafterSWAP. D1resourcecontextlive,118facing,marker0. A5allocationresultnotrestored,failuredoesnotrollbackrequest. Otherpathselector0required;integerwalk1,gravity/integrate/land,direction. Nonzero46decrements;elsefrontsignedX0..160 andsignedabsoluteY<=16setsselector4,timer100.')]
for start,ranges,contract in specs:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),original_bytes=rom[start:max(b for a,b in ranges)].hex(),code_ranges=ranges,instruction_evidence=items,verification_status='verified',status='verified green: local facing emitter contract',native_sources=[sources[0]],checked_cases=2097152,contract=contract,proof='One focused emitter batch2097152statefixtures compareallthreefullactors,liveA5,allocationdefinition/context/fullfractionXY/facing andallserviceentrysnapshots.180explicitfront-range/Y/signed8000boundaryfixtures. TestwasextendedoncebeforeadmissiontorouteD1/D2/D3retainedcontextaslive reference mutatedbycontactservices;onlychangedbatchrerun. AllocationfailureclearsrequestandretainschangedA5.',scope='Localvalidactors andexplicitmutablecontact/physics/direction/allocationservices. RetainedD1resourceandD2/D3highWORDsrepresentedbylivereferencecontext; actualoriginalregisterproducerancestryremainsunproven. Nativecaller/worldbinding andfullenemyfidelityremainexternal.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(result.read_bytes()).hexdigest())
(p/'docs/stage9/actor-facing-emitter-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Facing emitter local contract verified.')
