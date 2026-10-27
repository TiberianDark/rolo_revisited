import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from verify_leaf_routines import PIN
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==PIN
rp=root/'work/player-history-results.json';r=json.loads(rp.read_text());assert r['passed'] and r['881C']==1572864 and r['6796']==131072
sources=['src/core/player_frame_history.hpp','src/core/actor_state.hpp','tests/player_history_verification_tests.cpp'];exe=root/'work/player_history_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
records=[]
for a,e,name,contract in [(0x881c,0x8838,'Airborne frame counter','C524nonzero or124bit0set preservesactor;elseincrement68WORDwrapped. EveryWORDcount across8flagpartitions and3zero/nonzerogates;all130bytescompared.'),(0x6796,0x6814,'Player frame history publication','Requiremainstate1C6C;advancecursor16AND03FF;recordbaseintegerX/Y,selectorWORDfrom6814serviceatlogicalselector70>>1, directions121/122,speed58/62WORD,facing118,shape120,flags124withbit0clearedifbit5set. Preservebyte15andotherrecords. All65536selectorvalues acrossactive/inactivestate,all64alignedcursorpositions andall256flags viafixtures;compareall1024historybytes,cursor,baseactorandserviceoffset.')]:
 c=a;ins=[]
 while c<e:
  i=Decoder(rom,c).decode();ins.append(i);c+=i['size']
 assert c==e
 records.append(dict(address=a,hex=f'{a:06X}',end_exclusive=e,original_bytes=rom[a:e].hex(),status='verified green: local '+name,verification_status='verified',native_sources=['src/core/player_frame_history.hpp'],instruction_evidence=ins,checked_cases=r[f'{a:X}'],contract=contract,proof='Completeoriginalboundariesandbranch/writeorderreviewed. Independentliteralfieldlayout/modularcounteroracle; exactpreservationincludinghistorybyte15. SelectorLSRproduces0..32767so native signedoffset doesnotreinterpretnegative. Immutableactualselectortableextent/callerselectorsremainseparate.',scope='Canonical local native API; history cursoraligned16within1024, disjointbase/history, suppliedreadonlyselectorservice. Validtablepublication,callerselectordomain,frameschedulerandCPUregister/CCRABIexcluded.'))
report=dict(rom_sha256=PIN,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest());(p/'docs/stage9/player-history-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Two player history/counter local contracts verified.')
