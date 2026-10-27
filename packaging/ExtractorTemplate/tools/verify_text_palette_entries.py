"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "text_palette_entries",\n  "title": "text-control palette fade and clear contracts",\n  "sources": [\n    "src/core/text_palette_entries.hpp",\n    "tests/text_palette_entries_verification_tests.cpp"\n  ],\n  "results": {\n    "passed": true,\n    "cases": 131072\n  },\n  "cases": 131072,\n  "specs": [\n    {\n      "address": 28156,\n      "ranges": [\n        [\n          28156,\n          28160\n        ],\n        [\n          28242,\n          28364\n        ]\n      ],\n      "contract": "Command2setsWORDoffset0A00/count03FF;savecursor,chooseoneof4palettejobsfromattributes6000ROL6,16colours,target32360,rate4;releasegate/waitactive/reinhibit;zero-fillplane+offset,resettext/restorepalette,restorecursor/continueparser."\n    },\n    {\n      "address": 28180,\n      "ranges": [\n        [\n          28180,\n          28184\n        ],\n        [\n          28224,\n          28242\n        ],\n        [\n          28258,\n          28364\n        ]\n      ],\n      "contract": "Command8setsWORDoffset0/count0FFFthenidenticalsharedpalette/clear/resumecontract."\n    }\n  ],\n  "data_pins": [\n    [\n      205664,\n      "0000000000000000000000000000000000000000000000000000000000000000"\n    ],\n    [\n      28364,\n      "ffffc66cffffc5ecffffc740ffffc60cffffc814ffffc62cffffc8e8ffffc64c"\n    ]\n  ],\n  "proof": "Fulloriginalboundaries/tablebankmapping/WORDwrappingandsavedcursorrestorationreviewed. Focused131072nativecases:all65536attributeWORDs x2commands,actualnative2FF6/3060effectclock36ticks(rate4),correctbank16colours,untouchedbanks,perchannelcurrent/delta,clearaddress/count/control/order,andchildservicesmutatingcursorbeforeoriginalrestore.",\n  "scope": "Localpalette/state/finitejobclockandtypedclear/reset/restore/parsercontinuationservices. AllattributeWORDpartitions,butnotoriginalinterruptcadence/VDPcompletion,globalRAMalias/callerCPUregister/ABIorwholetextscreenfidelity. NotSDLadoption."\n}')
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
