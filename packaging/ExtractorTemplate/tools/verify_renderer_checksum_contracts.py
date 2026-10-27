"""Pinned local native contract evidence; static ROM decoding only."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
CONFIG=json.loads('{\n  "name": "renderer_checksum_contracts",\n  "title": "renderer list construction and ROM checksum",\n  "sources": [\n    "src/core/renderer_checksum_contracts.hpp",\n    "tests/renderer_checksum_contracts_verification_tests.cpp"\n  ],\n  "results": {\n    "passed": true,\n    "cases": 24844\n  },\n  "cases": 24844,\n  "specs": [\n    {\n      "address": 12606,\n      "ranges": [\n        [\n          12606,\n          12626\n        ]\n      ],\n      "contract": "Copyexact102originalrenderer-templateBYTEstoinertmetadata buffer, retainguards. Bytesneverexecutedorinvoked."\n    },\n    {\n      "address": 12626,\n      "ranges": [\n        [\n          12626,\n          12728\n        ]\n      ],\n      "contract": "Native6wayprioritylistbuilderreplaces6fixedoriginalself-modifyingappendwords; countWORD+1activehandles, orderedlowWORDkeysand6zeroterminators;statusscope2700/restored representedasdata."\n    },\n    {\n      "address": 524208,\n      "ranges": [\n        [\n          524208,\n          524288\n        ]\n      ],\n      "contract": "Sumoriginal0x1FFECbigendianLONGiterationsfromROM0,skipword018C;expected32EA75C6returns;failure5exactcontrolWORDs/64dataWORD14thenrequirednonreturnnativefault."\n    }\n  ],\n  "data_pins": [\n    [\n      12626,\n      "40e746fc27004e6743f9ffff6d7a45f9ffff6ddc47f9ffff6e3e49f9ffff6ea04bf9ffff6f024df9ffff6f644ffa001241f9ffff98c82c083e39ffffc5b860024e71cd8f205fcd8f3e9051cffff44251425242534254425542564df900c000004e6f46df4e75"\n    ]\n  ],\n  "proof": "ReviewedoriginalEXGstack/listappendtemplateand6validdatawords32C8..3CC8; nativecompiledswitchclassifiesonlythesefixedprioritytags,doesnotdecode/executeCPUinstructions. Focused24844cases:512priorityfixturesx48activeprefixlengthscompare6lists/terminators/fullpool/status;256metadatafillswith4guards;originalROMchecksumplus11bitcorruptionsincluding4excludedwordbytescomparefailurepackets/nonreturnfault.",\n  "scope": "Localnativeactivebucketprefixcontract,admitted1..48validactorhandlesand6fixedtags. NoCPU/USP/self-modifyingcodeexecutionoremulator;oldexecutabletemplatekeptasinertanalysismetadataonly. Unwrittenbucketstalescratchtails/CPUregisterABIoutsideoutputcontract. ChecksumROMextent>=7FFB0;failurevirtualhaltmustnotreturn(nativeexceptionused),notoriginalhardwareCPUlockup. DoesnotreplacepinnedSHA256ROMvalidationorclaimruntimeintegration."\n}')
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
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),code_ranges=ranges,instruction_evidence=items,verification_status='verified',status='verified green: '+CONFIG['title'],native_sources=[CONFIG['sources'][0]],checked_cases=spec.get('cases',CONFIG['cases']),contract=spec['contract'],proof=CONFIG['proof'],scope=spec.get('scope',CONFIG['scope'])))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(result.read_bytes()).hexdigest())
(p/('docs/stage9/'+slug+'-verification.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(str(len(records))+' local contracts registered: '+slug)
