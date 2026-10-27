"""Reviewed marker entry request and relocation contracts; no ROM execution."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/entry-marker-results.json';results=json.loads(rp.read_text(encoding='utf-8-sig'));assert results=={'passed':True,'cases':74240}
sources=['src/core/entry_marker_relocation.hpp','src/core/actor_state.hpp','src/core/actor_allocation.hpp','tests/entry_marker_verification_tests.cpp'];exe=root/'work/entry_marker_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
inv=json.loads((p/'docs/stage9/inventory.json').read_text());accepted={a for routine in inv['routines'] for a in routine['blocks']};records=[]
for a,e,cases,name,contract in [(0x608a,0x60a6,512,'Conditional class5 entry scan request','ZeroF26Ereturnswithoutrequest. Nonzero clearsF26Ebefore scanner request class5/callback60A6. Preserve scanner service mutations; scanner implementation and CPU return registers are separate.'),(0x60a6,0x60f4,73728,'Entry marker relocation and camera request','Acceptonly variants0x14/0x15(decimal20/21). SaveD7WORDC494,controlledXWORD12=D6,clearLONG16andretainXfraction14. Allocate152B8 withX=(D6<<16)|incomingD2upperWORD,Y0,D4context0,markerA2. NonzeroD0success usesreturnedA4,sets42F046and54currentC494includingallocator mutation. Failedallocationstillcalls4CB8; returncameraWORDresult. Rejectreturnszero withnoactor/global/service mutation.')]:
 cursor=a;instructions=[]
 while cursor<e:
  assert cursor in accepted
  instruction=Decoder(rom,cursor).decode();instructions.append(instruction);cursor+=instruction['size']
 assert cursor==e and instructions[-1]['mnemonic']=='RTS'
 if a==0x608a:assert any(i['mnemonic']=='LEA' and i['references']==[0x60a6] for i in instructions)
 else:assert any(i['address']==0x60aa and '#$14' in i['operands'] for i in instructions)
 records.append(dict(address=a,hex=f'{a:06X}',end_exclusive=e,original_bytes=rom[a:e].hex(),verification_status='verified',status='verified green: local '+name,native_sources=['src/core/entry_marker_relocation.hpp'],instruction_evidence=instructions,checked_cases=cases,contract=contract,proof='Reviewed complete original spans and instruction boundaries. All256pending flag values and service-mutation partitions; all256variants,4D2upperWORDpartitions,allocation success/failure,controlled/newactoralias and scratch mutations. Compare complete130BYTEactor records; every65536cameraWORDreturn checked. Requests and ordering asserted.',scope='Typed local actor/state/request contract with validcontrolledactor, validnonnullallocatorA4onsuccess and explicit stable identities. Scanner3E2C,allocator28B0,camera4CB8,F046callbacklifetime, rawaliases, caller provenance, CPUABI and devicepublication are external. Standalone helper; this is not full entry/transport gameplay fidelity.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/entry-marker-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('608A/60A6 local API contracts verified; external services remain explicit gaps.')
