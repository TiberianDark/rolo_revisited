"""Pin reviewed complete local state contracts and their native verification.

Static ROM decoding only. No instruction interpreter or ROM execution.
"""
import hashlib,json
from pathlib import Path
from m68k_static import Decoder
PIN='9478d47cc1883df42f3714ea485aedd71b541274eb45a3aa7c49f4a3518305e9'
SPECS=(
 (0xcd7a,0xcd8e,'Actor deceleration','src/core/level2_actor_updates.hpp',4096,
  'Subtract12288 modulo32 fromspeed58. If signed wrapped resultnegative, clearspeed58 anddirection121; otherwise retain result and direction. Allother actorbytesunchanged.',
  'Two sign partitions after modular subtraction; source is one SUBI.L/BPL and two conditional clears. Native signed test uses same wrapped result. Samples straddle every sign/wrap threshold; every direction byte checked.'),
 (0xcd8e,0xcde4,'Actor gravity','src/core/actor_motion.hpp',1048576,
  'Status117&14 inhibits all writes. Negative direction122 subtracts24576 modulo32, negatesnegative result andsetsdirection1. Other directions set1, skip speedalready>=983040 signed, otherwise add24576 modulo32 andclamp signed resultsabove983040. Allother bytesunchanged.',
  'Complete mask/sign/threshold branch partitions reviewed against20decodedinstructions. Every status/direction byte pair checked; speed cases cover zero, subtraction boundary, terminal clamp and both signed overflow endpoints. Constant modular transforms prove interior intervals.'),
 (0xcfce,0xcffc,'Actor position integration','src/core/actor_motion.hpp',1048576,
  'X12/Y16 advance modulo32 byvelocity58/62 according to signed byte121/122: zero retainsposition, positive adds, negative subtracts. Both velocities andallother fields retained.',
  'All65536 direction pairs checked across16boundary/value combinations. Direct signed64bit arithmetic oracle then32bit wrapping. Two identical axis branches with no dependencies; linear modular addition/subtraction establishes every interior value.'),
 (0xd042,0xd05a,'Actor integer X step','src/core/actor_motion.hpp',786432,
  'Cleardirection121;copyinputWORDtospeed58highword; addinput orwrappednegationtoX12highword accordingtofacing118bit3. Retainfraction14 andspeedfraction60 andeveryother byte.',
  'Every65536inputWORDs tested forbothbit3states at6position boundaries; all130bytescompared. Modular WORD addition is linear, so remaining positions share the same proof. Source conditional NEG.W affects onlydirection of integer add.'),
 (0x9a04,0x9a1a,'Add player lives','src/core/score_award.hpp',65536,
  'AddincomingBYTEtoC51D modulo256; clamp signed BYTE results>99 to99; retainwrappednegative byte results. WriteonlyC51D.',
  'All256x256inputs exhaustively compared to an independent integer arithmetic oracle. Original ADD.B and signed BLE are preserved, including overflow/negative BYTE cases; no callees.'),
)
def generate(project,results_path):
    rom=(project/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==PIN
    results=json.loads(results_path.read_text());assert results['passed'] and results['all_fields_checked']==130
    executable=project/'build-next/rolo_leaf_routine_verification_tests.exe';assert executable.exists()
    test_source=project/'tests/leaf_routine_verification_tests.cpp'
    assert '#undef NDEBUG' in test_source.read_text()
    pins={str(p.relative_to(project)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in (test_source,project/'src/core/actor_state.hpp',*(project/s[3] for s in SPECS))}
    records=[]
    for start,end,name,native,cases,contract,proof in SPECS:
        assert results[f'{start:04X}']==cases
        assert executable.stat().st_mtime>=max((project/p).stat().st_mtime for p in pins),'Native evidence predates audited sources'
        cursor=start;instructions=[]
        while cursor<end:
            instruction=Decoder(rom,cursor).decode();instructions.append(instruction);cursor+=instruction['size']
        assert cursor==end and instructions[-1]['mnemonic']=='RTS'
        assert not any(i['flow']=='call' for i in instructions)
        assert all(i.get('target') is None or start<=i['target']<end for i in instructions)
        records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,name=name,status='verified green: complete local native state contract',verification_status='verified',
            native_sources=[native],original_bytes=rom[start:end].hex(),instruction_evidence=instructions,contract=contract,proof=proof,checked_cases=cases,
            scope='Complete declared gameplay-state contract for this leaf routine. CPU temporary registers/CCR/call ABI are replaced by the native API; caller scheduling, integration and device timing are not certified.'))
    return dict(rom_sha256=PIN,source_sha256=pins,test_executable_sha256=hashlib.sha256(executable.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(results_path.read_bytes()).hexdigest(),records=records)
if __name__=='__main__':
    project=Path(__file__).resolve().parents[1];result=generate(project,project.parents[1]/'work/leaf-routine-results.json')
    (project/'docs/stage9/leaf-routine-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Verified local native state contracts: '+', '.join('$'+r['hex'] for r in result['records']))
