"""Terrain macro copy policies and normal descriptor setup contracts."""
import hashlib,json,struct
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/terrain-macro-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r=={'passed':True,'44C4':395264,'4536':395264,'45B4':395264,'446C':65536,'442A':65536}
manifest=json.loads((p/'assets/extracted/all-levels/manifest.json').read_text(encoding='utf-8'));dimensions=set()
for bank in manifest['banks']:
 artifact=bank['macros'];b=(p/artifact['path']).read_bytes();assert hashlib.sha256(b).hexdigest()==artifact['sha256']
 for i in range(struct.unpack_from('>H',b,4)[0]):
  off=struct.unpack_from('>H',b,6+i*2)[0];w,h=b[off:off+2];assert 1<=w<=16 and 1<=h<=8;dimensions.add((w,h))
sources=['src/core/terrain_macro_copy.hpp','src/core/terrain_descriptor.hpp','src/core/actor_state.hpp','tests/terrain_macro_verification_tests.cpp'];exe=root/'work/terrain_macro_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for item in inv['routines'] for a in item['blocks']};records=[]
specs=[(0x44c4,0x4536,'Replace nonzero macro tiles','Eachdestrowbottom-to-top, maskrowF2CA; columnAND7EWORDalignment. Unflaggedsourcepredecrements/reverseorder anddestinationright-to-left; flaggedsourceforward/left-to-right andXOR1000. Zero source alwaysskip. WriteWORDtile+parallelrecordoffsetmetadata; leaveallotherbackingbytes.'),(0x4536,0x45b4,'Fill only empty macro destinations','Sameoriginalorientation/row/column/source-zero policy; nonzerosourcewritesONLYiflive destinationWORDzero. Skippedmetadataunchanged. Ringaliaswritesobserveearlierwrites.'),(0x45b4,0x463c,'Macro record-priority overwrite','Sameorientation; nonzerosourcewritesiffunsignednewrecordoffset>=liveexistingmetadataWORD, equalitywrites. Zero sourcenowrite; preserveotherbackingbytes.'),(0x446c,0x44c4,'Normal terrain descriptor handoff','Unsignedtype>=400 specialservice; elsemacroindex=type&127, lookupdimension/tiles andbytecountB1EC. X>>3 setup,flag=(type&FF00)!=0; recordpointerrelativeMAPbase yieldsWORDmetadata; typedcopycontinuationmode supplied. Boundvalidcount/separationdomain.'),(0x442a,0x446c,'Initial terrain descriptor clipping','Specialtype>=400bypasseswidthclip. Normalmacro setup then signedWORD((windowright>>3)-(recordX>>3)-width*2); negative skipscopy. OtherwiseReplacecopy andmetadata. Originallookupcallsoccurbeforeclip; preserveorder.')]
for start,end,name,contract in specs:
 ranges=[(start,end)]+([(0x462c,0x463c)] if start in (0x44c4,0x4536) else [])+([(0x449a,0x44c4)] if start==0x442a else []);items=[];evidence=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted;i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi;evidence.append(dict(start=lo,end_exclusive=hi,original_bytes=rom[lo:hi].hex()))
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),instruction_evidence=items,code_ranges=evidence,verification_status='verified',status='verified green: local '+name,native_sources=[sources[1] if start in (0x442a,0x446c) else sources[0]],checked_cases=r[f'{start:X}'],contract=contract,proof='Independent2Dsource/destinationcoordinateoracle comparesall16384backingbytes. All65536sourceWORDs,metadataWORDs andbelow/equal/abovemetadata partitions,2flipstates,3copypolicies; allwidth1..16,height1..8 withringrow/columnwrap,zeroquads,smallrowmasks/livealias,guardbytes. All65536descriptorWORDs andinitialclipserviceordering.Allobserveddimensionpairsfrom8extractedbanksfalltestedrectangle. FailedindependentcheckercolumnalignmentwascorrectedtoAND7Eafterreview, thenbatchpassed; nativeimplementationunchanged.',scope='Local typedvalidmacrodata,positivewidth/height<=16/8, metadata_separation8192,validrowmask0380/1F80 andsignedpositivebytecount/separation. ActualITMS/B1EC produceradmission andspecialdescriptorservices, rawUSP/A4continuation/CPUABI andfullstreaming/camera integrationremainexternal. No wholemaprendering/gameclaim.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,observed_dimension_pairs=len(dimensions),test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/terrain-macro-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Five terrain macro/descriptor local contracts verified.')
