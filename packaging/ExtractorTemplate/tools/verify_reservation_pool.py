import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from verify_leaf_routines import PIN
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==PIN
rp=root/'work/reservation-pool-results.json';r=json.loads(rp.read_text());assert r['passed'] and (r['2888'],r['8E3A'],r['8E6C'])==(256,110592,73728)
sources=['src/core/actor_reservations.hpp','src/core/actor_allocation.hpp','src/core/actor_state.hpp','tests/reservation_pool_verification_tests.cpp'];exe=root/'work/reservation_pool_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
records=[]
for a,e,name,contract in [(0x2888,0x28b0,'Reservation pool initialization','Initialize8freeLONGkeys6BBC+4*iandterminalnull;cursor0replaces6B94pointer;clearhead6BDC. Preserve8nodecontents.256priorstatepatterns.'),(0x8e3a,0x8e6c,'Actor reservation insertion','Actor126bit3setreturnsunchanged. Readcurrentfree-key;nullreturnsunchangedincludingcursor. Otherwisepoponekey;node.next=oldhead,node.actor=actorlowWORD;head=nodelowWORD;setactor126bit3. All256flags,9cursorpositionsand48actoridentities;completeactor/poolpreservation checked.'),(0x8e6c,0x8eaa,'Completed actor reservation release','Traversefiniteuniquechaininorder;clearactor126bit2everyvisit. Oldbit2setalsoclearsbit3,unlinksnodefrompredecessor,pushesfullsignextendednodekeyontofree-stack. Retainednodesbecomenextpredecessor;removednodecontentsnotcleared. Alllengths0..8,256removalmasks,4unrelatedflagpatternsand8rotatedorders;independent survivor-listoraclechecksallactorbytes,nodefields,head,free-stack/cursor.')]:
 c=a;ins=[]
 while c<e:
  i=Decoder(rom,c).decode();ins.append(i);c+=i['size']
 assert c==e
 records.append(dict(address=a,hex=f'{a:06X}',end_exclusive=e,original_bytes=rom[a:e].hex(),status='verified green: local '+name,verification_status='verified',native_sources=['src/core/actor_reservations.hpp'],instruction_evidence=ins,checked_cases=r[f'{a:X}'],contract=contract,proof='Originalcompleteboundaries, BYTEBCLRold-bitbranch, WORDpredecessorwrites andLONGfree-stackmovementreviewed. Typedpointer/indexreplacementpreservesordering. Independentconstant/whole-state/survivor-listoracles testdeclaredvalidfinitepooldomains; noROMexecution.',scope='Local typedpool/actorAPI, finiteunique8nodechain, validactoridentities, validfreecursorandadequatepushspace. Noaliasedactornodesorcycles. Caller/lifecycleordering, malformedrawpointerdomains andCPUregister/CCRABIexcluded.'))
report=dict(rom_sha256=PIN,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest());(p/'docs/stage9/reservation-pool-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Three actor reservation local contracts verified.')
