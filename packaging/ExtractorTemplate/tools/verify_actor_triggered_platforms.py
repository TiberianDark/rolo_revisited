"""Shared actor state leaves, phase waits and explicit literal no-op entries."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/actor-triggered-platforms-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,actor_cases=4194304)
sources=['src/core/actor_triggered_platforms.hpp','src/core/actor_platform_family.hpp','src/core/actor_wave_motion.hpp','src/core/actor_displacement.hpp','src/core/actor_common_state.hpp','src/core/actor_state.hpp','tests/actor_triggered_platforms_verification_tests.cpp'];exe=root/'work/actor_triggered_platforms_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
import struct
assert list(struct.unpack_from('>8h',rom,0xc60a))==[0,-2,2,0,0,2,-2,0]

inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
specs=[(0xbe9c,[(0xbe9c,0xbea0),(0xc582,0xc60a)],'Rider-gated grid platform: cooldown52zerodisplacement, initialphase4/cooldown20, fourphaseWORDpairs. FirstC95Astep then temporaryextraLONGXY beforeD168, subtractsameextraafterservice. Nonzero121 useslive50&15+4/cooldown20.'),(0xbea0,[(0xbea0,0xbea4),(0xc61a,0xc6aa)],'F281zero requiresrider, initialY+16anchor/rate0. Unsignedanchor<=YsetsF281FF/zero displacement; else signedclampedrate+64max128drivesY. F281nonzero uses wrappedY-origin-224signed<=32; BYTE50zero givesone16pixelstepthenlatches.'),(0xbea4,[(0xbea4,0xbea8),(0xc6aa,0xc730)],'F282zero: zeroanchor invokesobjectcontact andrequires125bit6, cachesX-16/rate0. Unsignedanchor>=XsetsF282FF/zerodisplacement;else signedclampedrate+64max512negativeXdrive. Latchedgate usesorigin-Xsigned<=32 andone16pixelleftstep.'),(0xbea8,[(0xbea8,0xbeac),(0xc730,0xc7b8)],'Rightvariant: cachesX+16, unsignedanchor<=Xlatch, positiveXdrive. Latchedgate usesX-origin-320signed<=32 andone16pixelrightstep.')]
for start,ranges,contract in specs:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi,(hex(start),hex(at),hex(hi))
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),code_ranges=ranges,instruction_evidence=items,original_bytes=rom[start:max(b for a,b in ranges)].hex(),verification_status='verified',status=('verified green: literal no-op entry' if contract.startswith('Literal BRA') else 'verified green: local actor triggered platforms contract'),native_sources=[sources[0]],checked_cases=1048576,contract=contract,proof='One focused fourplatform batch4194304fullrecord cases acrossallWORDinputs and16cooldown/support/alias/anchor/gatepartitions. Independent64bitpositionoracle, snapshotsofcontact/directionentry andmutableglobalgates checked. Directionservicechangespositions andphase, verifying temporaryprobe restoration preserveslivechanges. Fixedgridtable pinned toROM. Initialtablegate caughtrotated nativegrid order beforegreenregistration; correctednativeandoraclethenreranfocusedbatchonce. Zero-displacement calls distinguishedfromearlyreturn.',scope='Local slot plusfulltarget state contract with validactoridentities. Gridphase4/8/12/16, orzero initialization, explicitlyadmitted. Object/direction services explicitmutableboundaries; D168preservesD2/D3asoriginalreviewed. Selector54admission andlivegameplaybinding remain external.'))

report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/actor-triggered-platforms-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Four grid/triggered platform slot contracts verified.')
