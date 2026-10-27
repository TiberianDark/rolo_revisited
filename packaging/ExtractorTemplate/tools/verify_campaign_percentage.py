import hashlib,json,re
from pathlib import Path
from inventory_campaign_statistics import catalogue
p=Path(__file__).resolve().parents[1];root=p.parents[1];original=catalogue(p)
header=p/'src/core/campaign_percentage.hpp'
values=[int(v) for v in re.search(r'campaign_percentage_nodes\{([^}]+)\}',header.read_text()).group(1).split(',')]
assert values==original['nodes']
result=root/'work/campaign-percentage-results.json';r=json.loads(result.read_text(encoding='utf-8-sig'));assert r=={'passed':True,'cases':75008}
files=['src/core/campaign_percentage.hpp','tests/campaign_percentage_verification_tests.cpp'];exe=root/'work/campaign_percentage_verification_tests.exe'
assert exe.stat().st_mtime>=max((p/f).stat().st_mtime for f in files)
report=dict(rom_sha256=original['rom_sha256'],address=0x6236,end_exclusive=0x627e,instruction_evidence=original['operations'][0]['instruction_evidence'],tables=original['tables'],nodes=values,source_sha256={f:hashlib.sha256((p/f).read_bytes()).hexdigest() for f in files},test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(result.read_bytes()).hexdigest(),checked_cases=r['cases'],contract='For immutable pinned descriptors: count bit1 on70 distinct nonzero selector BYTEs, return floor(100*count/70); no state mutation. Original D1 cleared before BYTE loads; all selectors1..79. Denominator70 and numerator<=7000 avoid DIVU overflow. Zero entries excluded.',proof='All71 counts with256noiseBYTEs and3node rotations; all80selectors x256BYTEs; original tables independently hash pinned and native node order checked exactly.',scope='Pure local statistic using pinned table and80BYTEprogress array. Not bound to UI; completion-bit producers, persistence/reset ownership, generic mutable descriptors and CPU ABI remain outside proof.',status='native contract evidence passed; inventory registration/review pending')
rom=(p/'local/rolo.md').read_bytes()
report['records']=[dict(address=25142,hex='006236',end_exclusive=25214,original_bytes=rom[25142:25214].hex(),verification_status='verified',status='verified green: local bounded pinned campaign statistic',native_sources=['src/core/campaign_percentage.hpp'],instruction_evidence=report['instruction_evidence'],checked_cases=report['checked_cases'],contract=report.get('contract',report['proof']),proof=report['proof'],scope=report['scope'])]
report['status']='verified local API contract; wider caller and integration gaps remain explicit'
(p/'docs/stage9/campaign-percentage-verification-evidence.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('Campaign percentage: 75008 checks, original70node data and full6236 span pinned')
