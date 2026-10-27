"""Pinned destination lookup evidence. Does not certify transporter continuation."""
import hashlib,json
from pathlib import Path
from inventory_level1_transport import catalogue
p=Path(__file__).resolve().parents[1];root=p.parents[1]
rp=root/'work/destination-verification-results.json'
r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r=={'passed':True,'cases':139310}
e=catalogue(p)
files=['src/core/trigger_destination.hpp','src/core/terrain_record_search.hpp','src/core/terrain_descriptor.hpp','src/core/player_trigger_dispatch.hpp','tests/destination_verification_tests.cpp']
exe=root/'work/destination_verification_tests.exe'
assert exe.stat().st_mtime>=max((p/f).stat().st_mtime for f in files)
report=dict(rom_sha256=e['rom_sha256'],address=0x3ee4,end_exclusive=0x3f34,instruction_evidence=[i for i in e['instruction_evidence'] if 0x3ee4<=i['address']<0x3f34],source_sha256={f:hashlib.sha256((p/f).read_bytes()).hexdigest() for f in files},test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest(),checked_cases=r['cases'],proof='Reviewed complete original span: unsigned row comparison, sign-extended row offsets, class 0x11 then low parameter BYTE, first match, WORD X+8 and row<<4. Native tests cover all parameter/variant BYTE pairs, all X WORDs, every positive height row count, all heights 0..15 first-row paths, empty rows, duplicates, sentinel 0x17 rejection, missing destinations and immutable MAP bytes.',scope='MAPs with nonnegative monotone aligned row offsets and valid extents, including zero shifted height. Raw signed negative offsets remain outside native domain; missing-result coordinate registers and CPU ABI not certified.',status='focused native evidence passed; inventory promotion pending review of domain/caller closure')
rom=(p/'local/rolo.md').read_bytes()
report['records']=[dict(address=16100,hex='003EE4',end_exclusive=16180,original_bytes=rom[16100:16180].hex(),verification_status='verified',status='verified green: local bounded destination lookup',native_sources=['src/core/trigger_destination.hpp'],instruction_evidence=report['instruction_evidence'],checked_cases=report['checked_cases'],contract=report.get('contract',report['proof']),proof=report['proof'],scope=report['scope'])]
report['status']='verified local API contract; wider caller and integration gaps remain explicit'
(p/'docs/stage9/destination-verification-evidence.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('139310 destination cases passed; evidence saved without expanding inventory green scope')

