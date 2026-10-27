import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from verify_leaf_routines import PIN
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==PIN
rp=root/'work/checkpoint-results.json';r=json.loads(rp.read_text());assert r['passed'] and r['7730']==524288;sources=['src/core/level1_startup.hpp','src/core/actor_state.hpp','tests/checkpoint_verification_tests.cpp'];exe=root/'work/checkpoint_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
c=0x7730;ins=[]
while c<0x7748:
 i=Decoder(rom,c).decode();ins.append(i);c+=i['size']
assert c==0x7748 and [i['mnemonic'] for i in ins]==['MOVEA.L','MOVE.W','MOVE.W','RTS']
record=dict(address=0x7730,hex='007730',end_exclusive=0x7748,original_bytes=rom[0x7730:0x7748].hex(),status='verified green: local checkpoint integer-position restore contract',verification_status='verified',native_sources=['src/core/level1_startup.hpp'],instruction_evidence=ins,checked_cases=524288,contract='Resolve controlledC4E0; copycheckpointWORDC4FEtoX12 andWORDC500toY16; preservefraction14/18 andeveryotheractorbyte. Nativeactor/checkpoint parameters replaceglobalpointer/dataAPI.',proof='Originalfourinstructionsreviewed with no branches/calls. All65536X andall65536Yvalues across8offsetsweeps, independentexpectedfieldwrites andall130bytecomparison; checkpointsourceunchanged. Assignments areindependentdirectWORDcopies, so crossproduct hasnoadditionalbranches.',scope='Complete local native game-state contract with validcontrolledactor andcheckpointdata supplied. Globalproducer/publication, callerrestart flow,scheduler andCPUtemporaryregister/CCR/ABI notcertified.')
report=dict(rom_sha256=PIN,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=[record],test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest());(p/'docs/stage9/checkpoint-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Checkpointintegerrestoreverified.')
