import hashlib,json
from pathlib import Path
from m68k_static import Decoder
from inventory_rom import ROM_HASH
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
inv=json.loads((p/'docs/stage9/inventory.json').read_text());accepted={a for r in inv['routines'] for a in r['blocks']};at=0x3e8a;instructions=[]
while at<0x3ee4:
 assert at in accepted
 i=Decoder(rom,at).decode();instructions.append(i);at+=i['size']
assert at==0x3ee4
rp=root/'work/companion-census-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r=={'passed':True,'cases':90109}
files=['src/core/companion_census.hpp','src/core/terrain_record_search.hpp','src/core/terrain_descriptor.hpp','tests/companion_census_verification_tests.cpp'];exe=root/'work/companion_census_verification_tests.exe';assert exe.stat().st_mtime>=max((p/f).stat().st_mtime for f in files)
report=dict(rom_sha256=ROM_HASH,address=0x3e8a,end_exclusive=0x3ee4,instruction_evidence=instructions,source_sha256={f:hashlib.sha256((p/f).read_bytes()).hexdigest() for f in files},test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest(),checked_cases=r['cases'],contract='Count class0x12 marker bytes; write WORDC556. Only zero count indexes signedWORDF2F6 intoC558 and setsbit1. Does not modify C552 rescue latch; zeroheight stillvisitsfirstrow.',scope='Bounded nonnegative aligned row offsets and validMAP extents; zero-count selectors0..79. Nonzero counts never index flags, including arbitraryselector values. Rawaddress aliases, signednegativeoffsets and live startup/spawn ordering unproved.',remaining=['Bind live startup census and preserve523E C552 sample-before-census order.','Certify all indexed/overlapping progressflag producers and reset owners.'])
report['records']=[dict(address=0x3e8a,hex='003E8A',end_exclusive=0x3ee4,original_bytes=rom[0x3e8a:0x3ee4].hex(),verification_status='verified',status='verified green: local bounded companion census',native_sources=['src/core/companion_census.hpp'],instruction_evidence=instructions,checked_cases=r['cases'],contract=report['contract'],proof='Allcounts0..8188; sparse four-row mixing with every class/parameter BYTE pair; all flag BYTEs and heights0..31; preserves input and high flag bits. Complete original span reviewed.',scope=report['scope'])]
(p/'docs/stage9/companion-census-verification-evidence.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Census evidence saved; multirow composition remains before promotion')

