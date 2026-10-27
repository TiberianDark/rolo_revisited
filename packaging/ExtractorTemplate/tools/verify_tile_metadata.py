import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from inventory_rom import ROM_HASH
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/tile-metadata-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r=={'passed':True,'cases':458752}
files=['src/core/tile_metadata_pair.hpp','tests/tile_metadata_verification_tests.cpp'];exe=root/'work/tile_metadata_verification_tests.exe';assert exe.stat().st_mtime>=max((p/f).stat().st_mtime for f in files)
inv=json.loads((p/'docs/stage9/inventory.json').read_text());accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
for a,e,cases,name in [(0x879a,0x87bc,196608,'Vertical metadata pair'),(0x87dc,0x87f6,131072,'First lateral metadata pair'),(0x87f6,0x8810,131072,'Second lateral metadata pair')]:
 at=a;ins=[]
 while at<e:
  assert at in accepted
  i=Decoder(rom,at).decode();ins.append(i);at+=i['size']
 assert at==e and ins[-1]['mnemonic']=='RTS'
 records.append(dict(address=a,hex=f'{a:06X}',end_exclusive=e,original_bytes=rom[a:e].hex(),verification_status='verified',status='verified green: local '+name,native_sources=['src/core/tile_metadata_pair.hpp'],instruction_evidence=ins,checked_cases=cases,contract='Index=(tileWORD&511)*8; verticaladds2ifbit12,firstlateraladds4,secondlateraladds6. ReadtwoBYTEs in order, advance metadata pointer2; native API returnsfirst/second BYTEandafter-pair offset. Allothertilebitsignored; no writes.',proof='Complete originalspansreviewed. All65536tileWORDsforeachhelper, plusall65536first/secondBYTEpairsineachusedpairslot. Comparevalues,after-pairindexandwhole4096BYTEimmutableinput. All512recordindicesandverticalflipbit covered.',scope='Complete local data lookup API forvalid4096BYTEtable andWORDtileinput. CPUupper-registerpreservation/CCR/rawpointerABI replacedbytypedAPI; F2FEtableproducer/aliases andlivefloor/wallcallerbindingremainexternal. Standalonehelper; notwholecollisionfidelity.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={f:hashlib.sha256((p/f).read_bytes()).hexdigest() for f in files},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/tile-metadata-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Three metadata lookup contracts verified.')
