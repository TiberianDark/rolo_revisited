"""MAP quad scan, mapping/cache rules and pattern allocation publication order."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/quad-mapping-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,**{'3CD6':4096,'3E04':65536})
sources=['src/core/terrain_quad_mapping.hpp','src/core/terrain_record_search.hpp','src/core/actor_state.hpp','tests/quad_mapping_verification_tests.cpp'];exe=root/'work/quad_mapping_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
for start,end,contract in [(0x3cd6,0x3e04,'Read-before-terminal-check MAP scan: final record is read but not processed, even empty interval reads guard. Type<400 uses lowBYTE macro index; visited published before macro query. For each quad low9index, common0..27 uses packed LONG+05940594 with cross-word carry; others allocate negative cache entries in first-seen order and preserve sourceF800 attributes.'),(0x3e04,0x3e2c,'Publish cache[source]=nextPattern before upload service. Source index corresponds original doubled WORD shifted4 plusFFFF0000. Upload source pattern and WORD destination, return prior cursor, increment cursor modulo65536 after upload. No rollback.')]:
 at=start;items=[]
 while at<end:
  assert at in accepted;i=Decoder(rom,at).decode();items.append(i);at+=i['size']
 assert at==end
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),instruction_evidence=items,verification_status='verified',status='verified green: local terrain quad mapping',native_sources=[sources[0]],checked_cases=r[f'{start:04X}'],contract=contract,proof='4096 independent MAP/macro/cache mapping fixtures, counts0..32 incl terminal read, special/normal records, visited/nonvisited and signed cache values, varying valid macro dimensions, full quad/cache/visited/cursor arrays and ordered query/upload observations compared. Separate helper65536 WORD cursor inputs checks wrap and pre-upload cache/cursor observation exactly. Original packed LONG carry and allocation signed tests reviewed.',scope='Local immutable valid MAP offsets/guard record and macro indices0..127, nonempty macro dimensions1..8 by1..4, valid source quad records. Upload service observes publication and preserves caller registers/state; source data and DMA execution/capacity/timing external. Native helper extraction preserves existing host behaviour.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/quad-mapping-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('3CD6/3E04 verified.')
