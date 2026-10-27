import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from verify_leaf_routines import PIN
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==PIN
sources=['src/core/level1_progress.hpp','src/core/level1_enemy_slice.hpp','src/core/actor_contact.hpp','src/core/actor_state.hpp','tests/exit_contact_verification_tests.cpp','tests/level_exit_verification_tests.cpp']
dep='docs/stage9/player-contact-verification.json';assert json.loads((p/dep).read_text())['records'][0]['address']==0x9012
specs=[(0x8ff2,0x9012,'exit-contact',2097152,'Exit reduced-dimension contact wrapper','SubtractsuppliedWORDshrinkfrom36/38,call9012,restorebothWORDdimensionsbyoriginalADDback,TST123suppliesresult. Preserve9012latch123/129writesandallotheractorbytes. Nativeoriginal-widthrestoreequivalentbecausecertified9012preservesdimensions.'),(0xe528,0xe5a4,'level-exit',2621440,'Level exit readiness and transition request','ClearF2BD;null84returnswithoutotherwrites. Setlinked125bit1. ReadyifC552nonzeroorC556zeroorselectorflagbit3;otherwise return. ReadyF2BDFF;C490bit5clearslinked125bit1. C510nonzeroblockscontact;else8FF2shrink20/28;hitrequestsC4441A6Ethenmusiccommand23argument0. Otherstatepreserved.')]
for a,e,name,cases,title,contract in specs:
 rp=root/('work/'+name+'-results.json');r=json.loads(rp.read_text());assert r['passed'] and r[f'{a:X}']==cases
 exe=root/('work/'+name.replace('-','_')+'_verification_tests.exe');relevant=[s for s in sources if not s.startswith('tests/') or name.replace('-','_') in s];assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in relevant)
 c=a;ins=[]
 while c<e:
  i=Decoder(rom,c).decode();ins.append(i);c+=i['size']
 assert c==e
 deps=[dep]+(['docs/stage9/exit-contact-verification.json'] if a==0xe528 else [])
 if a==0xe528:assert json.loads((p/deps[1]).read_text())['records'][0]['address']==0x8ff2
 proof=('EveryWORDwidth with16signed/wrappedshrink/positionfixtures inbothnativeworlds. Certified9012composition checksall130actorbytesandreturnedbool. Sourcearithmetic/restore reviewed againstoriginalstacksequence.' if a==0x8ff2 else 'All80validflagselectors,256flagbytesand64link/readiness/action/contact/blinkpartitionsinbothLevel1/2worlds. Independentstate/eventoraclecomparesall130exit/graphicbytes,flagarrayandallprogressfields,transition/musicrequestfields. Contactcomposesverified8FF2/9012ratherthanre-provinggeometry. Null/blockedpathsverifyrequestfieldsremainunchanged.')
 record=dict(address=a,hex=f'{a:06X}',end_exclusive=e,original_bytes=rom[a:e].hex(),status='verified green: local '+title,verification_status='verified',native_sources=['src/core/level1_enemy_slice.hpp'] if a==0x8ff2 else ['src/core/level1_progress.hpp'],instruction_evidence=ins,checked_cases=cases,contract=contract,proof='Completeoriginalinstructionboundariesandbranchorderreviewed. '+proof,scope='Local native actor/progress/request API; valid0..79selector, distinctstableexit/graphic/controlledrecords. Musicdevice, subsequent1A6Esceneexecution, publication/frame timing andCPUtemporaryregister/CCRABIexcluded. This does not certify complete end-to-overworld transition fidelity.')
 report=dict(rom_sha256=PIN,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in relevant+deps},records=[record],test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest());(p/('docs/stage9/'+name+'-verification.json')).write_text(json.dumps(report,indent=2)+'\n')
print('Exit contact and level-completion request local contracts verified.')
