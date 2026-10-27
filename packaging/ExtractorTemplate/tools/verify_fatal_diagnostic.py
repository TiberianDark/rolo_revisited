"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "fatal_diagnostic",\n  "title": "selector-zero fatal diagnostic payload and explicit halt outcome",\n  "boundary_extensions": [\n    [\n      4412,\n      4414\n    ]\n  ],\n  "boundary_basis": "TRAP0 at113A has a sequential return continuation113C; encoded60FC at113C branches back to113A. Existing CFG stops atTRAP and omitted this legitimate continuation. Statically decoded and modeled as explicit fatal halt outcome, not executed.",\n  "boundary_producers": [\n    [\n      4410,\n      "4e4060fc"\n    ]\n  ],\n  "sources": [\n    "src/core/fatal_diagnostic.hpp",\n    "tests/fatal_diagnostic_verification_tests.cpp"\n  ],\n  "results": {\n    "passed": true,\n    "cases": 65536\n  },\n  "cases": 65536,\n  "specs": [\n    {\n      "address": 4214,\n      "ranges": [\n        [\n          4214,\n          4414\n        ]\n      ],\n      "contract": "Original1076 entry sets A0zero, selecting first116A message. Preserve message across five ordered initialization services, setselectorFFFF and palette, OR live display40, publish original heading/message/address label and native eight-digit hexadecimal fault address; explicit halted state replaces endless TRAP wait."\n    }\n  ],\n  "data_pins": [\n    [\n      4414,\n      "554e455850454354454420455843455054494f4e204f43435552454400204154204144445245535320240000000011f2"\n    ]\n  ],\n  "proof": "All original38 boundaries and selector-zero entry dataflow reviewed.65536 nativecases cover every incoming displayWORD and varied32-bit fault addresses, child mutations, exact ordered publication commands/text tiles, original message pointer/coordinate prefix, final cursor, hexbuffer and fatal outcome against independent plain ASCII publication oracle.",\n  "scope": "Local1076 selector-zero diagnostic payload only. Shared1080 vector-tag selector domains, native platform exception capture, CPU stack/SR/register ABI and physicalTRAP cadence are outside contract. Initialization/palette are returning typed services; original text/hex nativehelpers composed directly. Caller must honor halted outcome; not connected to demo."\n}')
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
