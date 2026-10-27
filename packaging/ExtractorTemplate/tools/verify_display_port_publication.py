"""Shared actor state leaves, phase waits and explicit literal no-op entries."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/display-port-publication-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,drain_cases=524288,fill_cases=524288)
sources=['src/core/display_port_publication.hpp','src/core/display_setup.hpp','src/core/plane_scroll.hpp','src/core/actor_state.hpp','tests/display_port_publication_verification_tests.cpp'];exe=root/'work/display_port_publication_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)

inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
specs=[(0x25a8,[(0x25a8,0x260a)],'SetliveC432bit4,publishcontrol and8F02. Read14BYTEpackets fromEB56 untilzero firstLONG:twoLONGcontrolwrites,threeWORDcontrolwrites,statusbit1waitperpacket. ClearliveC432bit4/publish,clearfirstLONG/resetcursorEB56.'),(0x260a,[(0x260a,0x2674)],'Same queueprotocol fromE448with8F01; clearfirstLONG/resetcursorE448andE444WORD128afterlastpublish.'),(0x26c8,[(0x26c8,0x2746)],'SetliveC432bit4,publish8F01,length9300|lowcount/9400|highcount,9780. C462command=(destinationlow14<<16)|(destinationbits14..15)|80|fullcontrol; publishlivehighthenlowWORD,writefullD0WORD,statusbit1wait,clearliveC432bit4/publish. Zero count still submitted.')]
for start,ranges,contract in specs:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi,(hex(start),hex(at),hex(hi))
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),code_ranges=ranges,instruction_evidence=items,original_bytes=rom[start:max(b for a,b in ranges)].hex(),verification_status='verified',status=('verified green: literal no-op entry' if contract.startswith('Literal BRA') else 'verified green: local display port publication contract'),native_sources=[sources[0]],checked_cases=524288 if start==0x26c8 else 262144,contract=contract,proof='One focused publicationfamily:524288queuedrains and524288fills acrossallWORDcontrols/counts/values with8packet/queue partitions,0..4packets,0..3busyreads. Independentserializedeventoracle compares everyLONG/WORD/data/status event, fullqueuebytes/cursors/counter andstate. Portcallbacks deliberatelymutatecontrolandcommandlatch, provingliveC432andsecondcommandWORDreads. Fixedcommandconstants andoriginalboundariesreviewed.',scope='Local originalrequestprotocol andstateeffects withvalidboundedterminated14BYTEqueues andfinitebusycompletion. Displayportfunctions aretypednativebackendboundaries, notemulatedCPU/VDPimplementation. DMAdevicememoryeffects, SDLuploadequivalence, concurrency anddevice/fade timing remainexternal. No actualgraphicsfidelityclaimfromthesealone.'))

report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/display-port-publication-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Three display queue/fill publication contracts verified.')
