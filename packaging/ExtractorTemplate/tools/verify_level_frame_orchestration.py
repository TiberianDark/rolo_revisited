"""Shared actor state leaves, phase waits and explicit literal no-op entries."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/level-frame-orchestration-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,orchestration_cases=524288,failure_cuts=56)
sources=['src/core/level_frame_orchestration.hpp','tests/level_frame_orchestration_verification_tests.cpp'];exe=root/'work/level_frame_orchestration_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
expected_calls={0x1c6c:[0x5c58,0x260a,0x25a8,0x2f3c,0x6960,0x6aa6,0x7748,0x8c88,0x29ee,0xa808,0x785c,0x6796,0x881c,0x9196,0x8838,0x925c,0x4d54,0x948a,0xfcd4,0xfaa0,0x5060,0x5348,0x31d6,0x2c4c,0x7292,0x72a2,0x5ce6,0x9534],0x1d94:[0x63fa,0x2674,0x2684,0x523e,0x36ba,0x3e8a,0x3bf6,0x27da,0x3478,0x3784,0x766a,0x3f34,0x7730,0x4cb8,0x684e,0x6864,0x7292,0x72a2,0x6960,0x6aa6,0x6750,0x29ee,0xfcd4,0x5324,0x54a0,0x66de]}
import re
header=(p/sources[0]).read_text(encoding='utf-8')
for name,count in [('LevelFrameService',28),('LevelRestartService',26)]:
 labels=[v.strip() for v in re.search(r'enum class '+name+r'\s*\{(.*?)\}',header,re.S).group(1).split(',')];assert len(labels)==count and len(set(labels))==count

inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
specs=[(0x1c6c,[(0x1c6c,0x1cee)],'Publish C466=1C6C before all28normal native services in original order. Services remain live and continue even if they request a state change; no invented earlyreturn.'),(0x1d94,[(0x1d94,0x1e20)],'Fadeblack first, clear C432bit6 and publish liveWORD, invoke25remaining rebuild services in original order, set live C432bit6 and publishagain. No retained displaycontrol snapshot across mutable services.')]
for start,ranges,contract in specs:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi,(hex(start),hex(at),hex(hi))
 assert [i['target'] for i in items if i['flow']=='call']==expected_calls[start]
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),code_ranges=ranges,instruction_evidence=items,original_bytes=rom[start:max(b for a,b in ranges)].hex(),verification_status='verified',status=('verified green: literal no-op entry' if contract.startswith('Literal BRA') else 'verified green: local level frame orchestration contract'),native_sources=[sources[0]],checked_cases=262144,contract=contract,proof='One focused pair: all65536displayWORDs across4mutable service partitions, complete serviceorder/entrysnapshots/finalstate checked. Every service mutates control andmarker;56failurecuts ensure immediate native exception propagation without extra calls. Original decoded calltargetorder pinned to28/26native service ordinals; exact typed enum/source reviewed.',scope='Local frame/restart orchestration contract only. Each childservice and its state/persistence domain still needs live world binding; automatic playable death/restart remains partial and is not enabled by this helper. HardwareVDPpublication, fade timing and CPU scratch/stack ABI external. Not whole-frame or whole-restart fidelity.'))

report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/level-frame-orchestration-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Two local frame/restart orchestration contracts verified; playable restart remains unbound.')
