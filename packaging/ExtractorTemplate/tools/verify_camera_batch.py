"""Original level camera geometry and ten background modes, typed state API."""
import hashlib,json,re,struct
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/camera-batch-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r=={'passed':True,'layers':2621440,'initialize':172,'tracking':1028}
sources=['src/core/camera.hpp','src/core/camera_data.hpp','tests/camera_reference.hpp','tools/export_camera.py','tests/camera_batch_verification_tests.cpp'];exe=root/'work/camera_batch_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
text=(p/'src/core/camera_data.hpp').read_text(encoding='utf-8');sine=[int(v) for v in re.search(r'sine\{(.*?)\}',text).group(1).split(',')];modes=[int(v) for v in re.search(r'modes\{(.*?)\}',text).group(1).split(',')];assert struct.pack('>512h',*sine)==rom[0x1582a:0x15c2a] and bytes(modes)==rom[0x4aeda:0x4af2a]
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));entries={x['address'] for x in inv['routines']};accepted={a for item in inv['routines'] for a in item['blocks']};records=[]
specs=[(0x4ef4,0x4f1c,0x4f26,'Mode0 half XY'),(0x4ef8,0x4f26,0x4f30,'Mode1 half XY with flag'),(0x4efc,0x4f30,0x4f36,'Mode2 unchanged XY'),(0x4f00,0x4f36,0x4f40,'Mode3 half X zero Y'),(0x4f04,0x4f40,0x4f46,'Mode4 unchanged XY with flag'),(0x4f08,0x4f46,0x4f70,'Mode5 circular phase'),(0x4f0c,0x4f70,0x4f82,'Mode6 foreground shift'),(0x4f10,0x4f82,0x4fc8,'Mode7 four row bands'),(0x4f14,0x4fc8,0x5028,'Mode8 moving water rows'),(0x4f18,0x5028,0x5060,'Mode9 two row bands')]
for slot,start,end,name in specs:
 records.append(dict(address=slot,hex=f'{slot:06X}',end_exclusive=slot+4,original_bytes=rom[slot:slot+4].hex(),ranges=[(slot,slot+4),(start,end)],checked_cases=262144,contract=name+': foregroundXYcopiedbeforetransform; backgroundflag/scrollmodeWORDlowBYTEoutputs; signedASRrowsvslogicalhalfWORD. Preserveunusedrowstorage/fractions/trackingbands. CircularD2=1CCF8domain usespinnedsignedsinetable*400/highWORD andphaseWORDwrap.',scope='Local mode transform withcanonical inputmode0..9; includesmappedforeground/background output androwarray, notscreen/render publication orcomplete tracking/callerABI. Circular CCF8 onlyD1=200/D2=1 domain; other vector callersremainexternal.'))
for start,end,key,name,contract in [(0x4cb8,0x4d54,'initialize','Level camera geometry initialization','WORDplayerX-176 signedfloor0, signedmapwidth-320clamp; Y-160 signedfloor0andheight-224clamp. Calltracking BEFOREinitializebands. Then left=maxSigned0(playerX-cameraX-60),right=left+120,top134,bottom154. TypedAPI preservesfractionwords; originalF320/F34CFFFFdirtysentinelsareexternalpublicationdomain.'),(0x4d54,0x4ef4,'tracking','Level camera tracking and layer handoff','C519/C51Anonzero skiptrackingbutlayerupdatecontinues. HorizontalWORDdisplacement doubled/clampedunsigned15; directionuseswrappedN, bandsmove/clamporiginalunsignedbranches, stepmovesneartargetwithwrappedcomparisons. Signedverticaldeadzone immediatefollowandheightclamp. 4EAAselector-mode dispatch writesforeground/background/flags.')]:
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),ranges=[(start,end)],checked_cases=r[key],contract=contract,scope='Local geometry typedCameraState withvalidmodeandmapdimensions inexistingROM-derivedfixtureadmission (320..16000 width,224..16000height,validplayer/initialcamera positions). Fulloriginalboundaries/branchesreviewed; independentofflinearithmeticfixtures. RAMdirtysentinel/publication, rawpointerABI, interruptclock/aliasandactualcallerhistory remainexternal. Notwholecamera/gameplaycertification.'))
for record in records:
 assert record['address'] in entries
 items=[];ranges=[]
 for lo,hi in record.pop('ranges'):
  at=lo
  while at<hi:
   assert at in accepted;i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi;ranges.append(dict(start=lo,end_exclusive=hi,original_bytes=rom[lo:hi].hex()))
 record.update(instruction_evidence=items,code_ranges=ranges,verification_status='verified',status='verified green: local '+record['contract'].split(':')[0],native_sources=['src/core/camera.hpp'],proof='Singlefocusedbatch:262144layercasespermode (all65536X/phaseWORDs x4Y/shift/vblankpartitions), independent rowindex/arithmetic model comparesentireCameraState.172initialization+1028trackingofflinefixtureswithsigned/unsigneddeadzone/freeze/mapboundpartitions, fractionsguarded. Original512sinewordsand80modeselectorbytesmatchedROM; code/referenceproducerpinned.')
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/camera-batch-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('12 camera geometry/background local contracts verified.')
