import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from verify_leaf_routines import PIN
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==PIN
rp=root/'work/companion-history-target-results.json';r=json.loads(rp.read_text());assert r['passed'] and r['B114']==2621440
sources=['src/core/level1_companions.hpp','src/core/player_frame_history.hpp','src/core/actor_state.hpp','tests/companion_history_target_verification_tests.cpp'];exe=root/'work/companion_history_target_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
c=0xb114;ins=[]
while c<0xb1a8:
 i=Decoder(rom,c).decode();ins.append(i);c+=i['size']
assert c==0xb1a8
record=dict(address=0xb114,hex='00B114',end_exclusive=0xb1a8,original_bytes=rom[0xb114:0xb1a8].hex(),status='verified green: local companion history target in bounded slot domain',verification_status='verified',native_sources=['src/core/level1_companions.hpp'],instruction_evidence=ins,checked_cases=r['B114'],contract='Historyoffset=(cursor-(BYTE47<<4))AND1023. Base124bit5choosesbaseX/YelsehistoryX/Y. Sumpriornonnullcompanionsheight38minus4for slot>=2;targetY=chosenY-baseheight+4-stack WORDwrapped. Facingfromhistory12;selectorhistory4retains24/8/12else28. Returnnativevalueobject; no statewrites.',proof='Reviewedoriginalcompleteboundaries, SUBQ.W/BMI andDBF count slot-1; certificateboundsBYTE47to0..4, atmostthreepriorentries. EveryWORD fixture acrossfive slots and8nullpatterns checksmodularheightstack, all64alignedhistorypositions, bit5 override andselectorpartitions. Sourceconstinput/read-onlypooluse reviewed; arithmeticlinearandzero/nonzerointerpretation matchesoriginal.',scope='LocalAPI withslot0..4, aligned16historycursor, valid three slot identities andimmutable history/base/actors. OriginalwiderBYTE47domain, producerpublication, exactlevelreachability, CPUregister/CCRABI excluded.')
report=dict(rom_sha256=PIN,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=[record],test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest());(p/'docs/stage9/companion-history-target-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Companion history target local contract verified in bounded slot domain.')
