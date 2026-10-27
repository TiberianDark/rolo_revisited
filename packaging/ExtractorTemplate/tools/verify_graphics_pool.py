"""Graphics free-span pool initializer and release/coalescing contracts."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/graphics-pool-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r=={'passed':True,'3478':65536,'34F0':1048576}
sources=['src/core/graphics_pool.hpp','src/core/actor_allocation.hpp','src/core/actor_state.hpp','tests/graphics_pool_verification_tests.cpp'];exe=root/'work/graphics_pool_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for item in inv['routines'] for a in item['blocks']};records=[]
for start,end,name,contract in [(0x3478,0x34c2,'Graphics free pool initialization','ReservedWORDshiftleft5wraps before LONGzeroextension. Seedsize=A800-reserved andstart=reserved. Reset sentinelnextnull/startFFFFFFFF/remaining0;25free-nodekeys inascendingorder,cursor0; invoke34F0toinsertinitialspan. Nativeoutcome consumesnode1/cursor1;unusednodesremainstale.'),(0x34f0,0x355a,'Graphics span release and merge','Traverse finite linkednodes while signedstart>=next.start; preserve lastpredecessor/next. Mergeleft iffstart==previous.start+previous.remainingLONGwrapped; elsepopfree-node andinsertbetween. Mergeright compares original releasedstart+size againstnext.start (notmutatedresidentextent); addrightremaining,unlinkright,pushitsnodekey. Publish updatedfreecursor; untouchednodes/stackslotspreserved.')]:
 at=start;items=[]
 while at<end:
  assert at in accepted;i=Decoder(rom,at).decode();items.append(i);at+=i['size']
 assert at==end
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),instruction_evidence=items,verification_status='verified',status='verified green: local '+name,native_sources=[sources[0]],checked_cases=r[f'{start:X}'],contract=contract,proof='All65536reservedWORDs withstale-node/stackguards. Release all65536baseWORDs x16before/between/left/right/bothadjacent/end/zero/wrapped-size/signed-boundary partitions. Independent ordered-node/interval oracle comparesall26nodes,25freestackslotsandcursor; originalcompleteboundaries/WORDvsLONGwrappingreviewed.',scope='Local typed finite linked-node andadequatefree-stack domain; noalias/cycle/exhaustion. Memory/rawpointerABI andgraphicsreservation producer/actualVRAM budget/caller ownership remainexternal. SomeWORDreservevalues yieldwrapped sizesasoriginal; testsdo notauthorize DMA ofthose sizes. No wholegraphics/frameclaim.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/graphics-pool-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Two graphics free-pool local contracts verified.')
