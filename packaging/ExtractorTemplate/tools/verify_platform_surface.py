"""Shared actor state leaves, phase waits and explicit literal no-op entries."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/platform-surface-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,coordinate_cases=523989,surface_cases=524288,restore_cases=524288)
sources=['src/core/platform_surface.hpp','src/core/actor_platform_contact.hpp','src/core/actor_contact.hpp','src/core/actor_allocation.hpp','src/core/actor_state.hpp','tests/platform_surface_verification_tests.cpp'];exe=root/'work/platform_surface_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)

inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
specs=[(0x8c06,[(0x8c06,0x8c24)],'ArithmeticWORDX/Y>>4; unsignedrowWORD*widthBYTE, wrappedWORDcolumn+product then doubledWORD signedEAoffset. ReadoneoriginaltileWORD; retaincallerD5abstractedaway.'),(0x8bac,[(0x8bac,0x8c06),(0x879a,0x87bc)],'Coordinate tile lookup; bit14solidgate. Originaldescriptor(tile&511)*8+invertedbit12offset2 yieldsheightoffset/shapeBYTE. Shape64flipsX; low6shape selects16BYTEprofile. NegativeprofileBYTEfails. YFFF0 +16-offset+profile, orinverted+31-offset-profile; returnrawtileandoriginalshapeBYTE.'),(0x8a68,[(0x8a68,0x8bac)],'Rider98platform. Clear124bits5/6 and120; wrappedreach=58+62+absplatform64+absplatform60+1. Risingrider rejectsnonnegativeplatform64. WrappedlocalXYnegativegatebeforeC494/C498cachewrite. ThreeorderedY-32/Y-16/Ysurfaceprobes withsignedheight/reach andunsignedfinalsurface<=riderY. OnacceptclampY/clearfraction,120shapeXORinversion64,ground/supportflags,old62WORDto66,cleardirection/verticalvelocity;nonzero68clearsandsets124bit6.')]
for start,ranges,contract in specs:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi,(hex(start),hex(at),hex(hi))
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),code_ranges=ranges,instruction_evidence=items,original_bytes=rom[start:max(b for a,b in ranges)].hex(),verification_status='verified',status=('verified green: literal no-op entry' if contract.startswith('Literal BRA') else 'verified green: local platform surface contract'),native_sources=[sources[0]],checked_cases=523989 if start==0x8c06 else 524288,contract=contract,proof='One focused threeentry batch:523989admittedcoordinate cases fromall65536WORDinputs x16width/phasepartitions,524288surfacequeries acrossalltileWORDs/profiles/flip/inversionflags,524288restores withfull48recordandcachecomparison. Independent signedfloor/modularindex/profileoracle; allWORDreach/wrap/signedvelocity gates andstatepreservation checked. Originalcompleteboundaries anddescriptor879A reviewed.',scope='Local immutable validtile/collision/profiledata spans, nonnegativeadmittedsignedEAread anddistinctstablerider/platformrecords. Actualplatform46map-pointeradmission, generatedmapbounds andliveworldrestoreadapter remainexternal. CPU scratchregisterABI replacedbytyped tile/surface results; D7lowBYTEshape retained explicitly. Not fullplatform/game fidelity.'))

report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/platform-surface-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Three platform surface/restore contracts verified.')
