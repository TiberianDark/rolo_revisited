import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
p=Path(__file__).resolve().parents[1];root=p.parents[1]
rp=root/'work/census-startup-integration-results.json';r=json.loads(rp.read_text());assert r=={'passed':True,'cases':512}
files=['src/core/level1_enemy_slice.hpp','src/core/companion_census.hpp','tests/census_startup_integration_tests.cpp'];exe=root/'work/census_startup_integration_tests.exe';assert exe.stat().st_mtime>=max((p/f).stat().st_mtime for f in files)
proof=json.loads((p/'docs/stage9/companion-census-verification-evidence.json').read_text());assert proof['rom_sha256']==ROM_HASH
report=dict(rom_sha256=ROM_HASH,source_sha256={f:hashlib.sha256((p/f).read_bytes()).hexdigest() for f in files},test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),result_sha256=hashlib.sha256(rp.read_bytes()).hexdigest(),checked_cases=r['cases'],scope='All256currentflagBYTEs acrossLevel1/2 constructors; preservesC552/C553 sampled before census, flagsotherthanstartupbit2 and originalMAPcount. Doesnotcertify all523Eresetfields oractorallocation/startupservice ordering.',census_proof_sha256=hashlib.sha256((p/'docs/stage9/companion-census-verification-evidence.json').read_bytes()).hexdigest())
(p/'docs/stage9/census-startup-integration-evidence.json').write_text(json.dumps(report,indent=2)+'\n');print('512 startup integration cases pinned')
