"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "cold_boot_initialization",\n  "title": "cold initialization data requests and native boot admission",\n  "sources": [\n    "src/core/cold_boot_initialization.hpp",\n    "tests/cold_boot_initialization_verification_tests.cpp",\n    "tests/boot_coordinator_tests.cpp"\n  ],\n  "dependencies": [\n    "../../work/boot-coordinator-results.json"\n  ],\n  "results": {\n    "passed": true,\n    "cases": 4096\n  },\n  "cases": 4096,\n  "specs": [\n    {\n      "address": 512,\n      "ranges": [\n        [\n          512,\n          654\n        ],\n        [\n          762,\n          866\n        ]\n      ],\n      "contract": "First expansion-port gate selects cold initialization; version low-nibble controls TMSS request. Publish24original register words, clear display entry, stage38opaque sound bytes across exact bus/reset requests, clear all65536workRAMbytes, palette/scroll zeros and4PSGmute bytes. After checksum re-read live expansion gates; reset and enable startup, advance finite display edges/native animation to completionBYTE, admit native main."\n    }\n  ],\n  "data_pins": [\n    [\n      654,\n      "80003fff010000a0000000a1110000a1120000c0000000c000040414303c076c00000000ff0081370001010000ffff00008040000080af01d91f112700212600f977edb0dde1fde1ed47ed4fd1e1f108d9c1d1e1f1f9f3ed5636e9e981048f02c0000000400000109fbfdfff"\n    ]\n  ],\n  "proof": "Original executable regions exclude inline28E..2FAinitialization DATA; all87original instruction boundaries reviewed with word/long/device order and DBF counts.4096 complete cold-start compositions cover all256versionBYTEs x16RAM/sound seeds; independently enumerated full request stream, all65536RAM bytes and8192sound staging bytes compared. Prior2048 boot-coordinator cases cover both gates, live post-checksum changes, finite1..256frame completions and admission. Fixture constant corrected against ROM2C0=40000080 after failed check, then focusedfamily passed.",\n  "scope": "Local typed boot payload with finite returning sound-grant/display-edge/checksum/startup/main services and pinned original init table. Sound bootstrap bytes are opaque staging DATA, never executed. Physical MMIO/CPU USP/SR/register restoration is replaced by host runtime ownership and remains outside payload proof; native services are not SDL-bound. No claim of complete hardware timing or whole startup fidelity."\n}')
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
