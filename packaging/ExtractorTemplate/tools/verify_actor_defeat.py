import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from verify_leaf_routines import PIN
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==PIN
rp=root/'work/actor-defeat-results.json';r=json.loads(rp.read_text());assert r['passed'] and r['97AC']==1048576
sources=['src/core/actor_defeat.hpp','src/core/actor_state.hpp','tests/actor_defeat_verification_tests.cpp'];exe=root/'work/actor_defeat_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
c=0x97ac;ins=[]
while c<0x97fe:
 i=Decoder(rom,c).decode();ins.append(i);c+=i['size']
assert c==0x97fe
record=dict(address=0x97ac,hex='0097AC',end_exclusive=0x97fe,original_bytes=rom[0x97ac:0x97fe].hex(),status='verified green: local defeat state and secondary-spawn request contract',verification_status='verified',native_sources=['src/core/actor_defeat.hpp'],instruction_evidence=ins,checked_cases=r['97AC'],contract='Read definitionWORD32;zero noactorwrites/noallocationrequest, native nullreplacesoriginaldefinitionA0. Otherwise actor70=selector,callback42=A84C;nonzero definitionLONG28 requests28B0secondaryatfullactorX/Y,originalD4/D7zero. Parent76nonzero returnsactorwithoutlinkscan;otherwisepropagateselector/callbacktofinite84chainandreturntail. Definitionreadonce;spawnrequestbeforelinkpropagation.',proof='Reviewed complete original instruction boundaries including earlydefinitionA0 return and parent gate. EveryWORDselector across16parent/secondary/chain-lengthpartitions; allfour130BYTErecords, returnedidentity andserviceeventcounts/ordercompared toindependent selected-record oracle.',scope='Complete local actor state and explicit spawn-request API boundary, validstablefinitechain, immutabledefinition; allocation28B0result/global/poolsideeffects remain a separate unverified service contract. Spawnservice must preserve existingchain/definition in declared domain. CPUtemporaryregister/CCRABI and scheduler excluded; this is not a complete enemy-defeat lifecycle certificate.')
report=dict(rom_sha256=PIN,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=[record],test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest());(p/'docs/stage9/actor-defeat-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Defeat local state/spawn-request contract verified; allocation service remains separate.')
