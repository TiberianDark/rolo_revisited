"""CA0A fixed-point vector lookup and eight octant contracts."""
import hashlib,json,re,struct
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/direction-vector-results.json';r={k.upper():v for k,v in json.loads(rp.read_text(encoding='utf-8-sig')).items()};assert r==dict(PASSED=True,CA0A=512,**{f'{0xca48+i*2:04X}':64 for i in range(8)})
header=(p/'src/core/direction_vector_data.hpp').read_text(encoding='utf-8');data=[int(x,16) for x in re.findall(r'0x([0-9a-f]{8})u',header)];pointers=struct.unpack_from('>8I',rom,0xca28);assert data==[v for ptr in pointers for v in struct.unpack_from('>18I',rom,ptr)]
expected=[]
for bank in range(8):
 for angle in range(64):
  octant,within=divmod(angle,8);index=8-within if octant%2 else within;a,b=data[bank*18+index*2:bank*18+index*2+2];xy=(a,b) if octant in (0,3,4,7) else (b,a);expected.extend((xy[0] if octant<4 else -xy[0],-xy[1] if octant in (0,1,6,7) else xy[1]))
fixture=(p/'tests/direction_vector_expected.hpp').read_text(encoding='utf-8');assert [int(x,16) for x in re.findall(r'0x([0-9a-f]{8})u',fixture)]==[x&0xffffffff for x in expected]
sources=['src/core/actor_direction_vector.hpp','src/core/direction_vector_data.hpp','tests/direction_vector_expected.hpp','tests/direction_vector_verification_tests.cpp','tools/export_direction_vectors.py'];exe=root/'work/direction_vector_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
ends=[0xca58,0xca62,0xca70,0xca78,0xca84,0xca8e,0xca9c,0xcaa8,0xcab8]
for entry in [0xca0a]+[0xca48+i*2 for i in range(8)]:
 if entry==0xca0a:ranges=[(0xca0a,0xca28),(0xca48,0xcab8)]
 else:
  i=(entry-0xca48)//2;ranges=[(entry,entry+2),(ends[i],ends[i+1])]
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted;i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi
 records.append(dict(address=entry,hex=f'{entry:06X}',end_exclusive=max(b for a,b in ranges),code_ranges=ranges,original_bytes=rom[entry:max(b for a,b in ranges)].hex(),instruction_evidence=items,verification_status='verified',status='verified green: local direction-vector lookup',native_sources=[sources[0]],checked_cases=r[f'{entry:04X}'],contract='Magnitude1..8 selects original pointer table; angle0..63 splits low3bits and signed-shift octant. Odd octants use8-step table pair, even use step. Eight exact LONG swaps/negations yield fixed-point XY without trigonometric approximation.',proof='Entire finite admitted input domain:512 vectors plus64 cases per octant entry. Independent quadrant sign/permutation fixture generated directly from original big-endian pairs; fixture and compiled table separately byte/value-checked against pinned ROM. Every native output compared exactly. Branch-slot target bodies reviewed, not merely BRA opcodes.',scope='Local immutable original magnitude tables1..8, angles0..63 and lowstep0..7. CPU register/condition-code ABI represented by typed XY. Utility available for caller translations; not yet substituted into a playable actor callback and does not certify those callers or scene fidelity.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest(),original_table_sha256=hashlib.sha256(rom[0xcab8:0xccf8]).hexdigest())
(p/'docs/stage9/direction-vector-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('CA0A and eight full octant targets verified.')
