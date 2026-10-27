"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "native_event_boundary",\n  "title": "reviewed native platform return and palette callback entry substitution",\n  "sources": [\n    "src/core/native_event_boundary.hpp",\n    "tests/native_event_boundary_verification_tests.cpp"\n  ],\n  "results": {\n    "passed": true,\n    "cases": 327682\n  },\n  "cases": 327682,\n  "specs": [\n    {\n      "address": 4212,\n      "ranges": [\n        [\n          4212,\n          4214\n        ]\n      ],\n      "contract": "Original1074 RTE restores interrupted context and returns with no game payload. Native structured event scope restores the host callback ownership/depth/kind and resumes normal C++ control flow. No CPU frame/register interpretation or game state write."\n    },\n    {\n      "address": 5278,\n      "ranges": [\n        [\n          5278,\n          5384\n        ]\n      ],\n      "contract": "Original149E saves15registers, TRAP0 dispatches taggedvector12001074 to1074 RTE, then14A4 updates latch/frame,input,audio and palette/publication before restoring and returning. Native synchronous palette callback encloses empty trap-return scope and actual verified14A4nativebody within caller ownership scope; shared payload mutations persist while host ownership restores."\n    }\n  ],\n  "data_pins": [\n    [\n      128,\n      "12001074"\n    ],\n    [\n      4212,\n      "4e73"\n    ],\n    [\n      5278,\n      "48e7fffe4e40"\n    ],\n    [\n      5378,\n      "4cdf7fff4e73"\n    ]\n  ],\n  "proof": "Reviewed original1074,149E/TRAP0/vector80/14A4fallthrough/1502restore+1506RTE boundaries.327682nativecases:all65536 frameWORDs across4 live input/audio/palette/abort partitions plus nested host ownership restoration, normal return and native unwinding, unchanged caller value records, exact callback order and frame/latch/palette payload, initial nesting overflow and failed nested entry rollback. Existing certified native palette body composed directly; no dummy no-op-only tests or ROM execution.",\n  "scope": "Verified explicit native platform substitution for these entry/return roles, not instruction-for-instruction CPU equivalence. Host C++ calling convention replaces register/exception-stack preservation; scoped context is host ownership metadata, not a68k register file. Original physical CPU SR/PC/stack and asynchronous interrupt timing are not emulated or runtime-certified. Admitted synchronous native callback domain; native fault-unwinding checks are robustness only, not original exception-behaviour equivalence. SDL main-loop adoption and complete scene timing remain outside this local proof."\n}')
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
slug=CONFIG['name'].replace('_','-');result=root/('work/'+slug+'-results.json');r=json.loads(result.read_text(encoding='utf-8-sig'));assert r==CONFIG['results']
sources=list(CONFIG['sources']);pending=list(sources)
while pending:
 source=pending.pop()
 for include in re.findall(r'#include "(core/[^"\n]+)"',(p/source).read_text(encoding='utf-8')):
  child='src/'+include
  if child not in sources:sources.append(child);pending.append(child)
exe=root/('work/'+CONFIG['name']+'_verification_tests.exe');assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
sources+=CONFIG.get('dependencies',[])
for at,expected in CONFIG.get('data_pins',[]):assert rom[at:at+len(bytes.fromhex(expected))].hex()==expected
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
for lo,hi in CONFIG.get('boundary_extensions',[]):
 assert CONFIG.get('boundary_basis') and CONFIG.get('boundary_producers')
 for source,encoded in CONFIG['boundary_producers']:assert rom[source:source+len(bytes.fromhex(encoded))].hex()==encoded
 cursor=lo
 while cursor<hi:
  accepted.add(cursor);cursor+=Decoder(rom,cursor).decode()['size']
 assert cursor==hi
for spec in CONFIG['specs']:
 start=spec['address'];ranges=spec['ranges'];items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi
 end=max(b for a,b in ranges)
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),code_ranges=ranges,instruction_evidence=items,verification_status='verified',status='verified green: '+CONFIG['title'],native_sources=spec.get('native_sources',[CONFIG['sources'][0]]),checked_cases=spec.get('cases',CONFIG['cases']),contract=spec['contract'],proof=CONFIG['proof'],scope=spec.get('scope',CONFIG['scope'])))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(result.read_bytes()).hexdigest())
(p/('docs/stage9/'+slug+'-verification.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(str(len(records))+' local contracts registered: '+slug)
