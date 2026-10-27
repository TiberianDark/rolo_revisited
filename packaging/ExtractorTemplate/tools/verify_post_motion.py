"""Controlled type8 post-motion mutation and two ordered display-row writes."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/post-motion-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r=={'passed':True,'8D4E':65536,'8C88':262144}
sources=['src/core/player_post_motion.hpp','src/core/terrain_display.hpp','src/core/actor_state.hpp','tests/post_motion_verification_tests.cpp'];exe=root/'work/post_motion_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for item in inv['routines'] for a in item['blocks']};records=[]
specs=[(0x8c88,0x8d4e,'Post-motion terrain mutation','Type8/actor53nonzeroonly; clear53BEFOREsound12. Reloadlivebank/facing aftersound; table8D8ErelativeWORDnegative returns. X=((X±8)&3F0)>>3,Y=((Y-8)&3F0)<<3. Lookupcount+1eightBYTEentries bytilelow9, firstmatchonly. Replacecurrentcell andpreviousringrow via8D4E retainingoldFE00flags; readsignedmetadataatsecondcell+8192 andwriteentryfinalWORDtoF32C+offset. Sound/latchconsumed evenmiss.'),(0x8d4e,0x8d8e,'Post-motion quad publication','Lookupunmodified4quadpatternWORDs. Firstnamerowoffset=((x+y)*2)&F7C,secondOR128; publishtworowsinorder. OnlyAFTERpublicationwritebackingtile=replacement|oldflags atx+y. Do NOTORoldflagsintodisplayedquadpatterns; rawVDPbase40000003replacedbytypedrownameservice.')]
for start,end,name,contract in specs:
 at=start;items=[]
 while at<end:
  assert at in accepted;i=Decoder(rom,at).decode();items.append(i);at+=i['size']
 assert at==end
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=end,original_bytes=rom[start:end].hex(),instruction_evidence=items,verification_status='verified',status='verified green: local '+name,native_sources=[sources[0]],checked_cases=r[f'{start:X}'],contract=contract,proof='Independent2Dcoordinate/tablematch andorderedservice/stateoracle.65536quad/flag/ringcoordinatecases;262144WORDXY/tile/type/latch/bank/facingpartitions. Eventorderincludesactor53atSound; soundmutatesbank/facingtoverifylatereads. Negativetablepointer,no-match,lastentrymatch,count0..2,all16bitmetadataoffsets(even),current+precedingrowwrap,flagsandquadpublication. Compare130actorbytes,all16KBbacking,64KBMAPimage,bankandservicetrace. Originalboundariesreviewed.',scope='Local type8/typedbounded8D8E-relativetable/count0..2fixture,validquads<512andfinitebacking/MAPrange. Actualperbanktableproducer/descriptoradmission, F32Cbasealias/VDPqueue/CPUABI andfullstreamingintegrationremainexternal. RawmetadataWORDsignextendmodel; actualROMMAPmetadataalignment remainscallerconstraint. Notwholeterrainbreak/gameplayclaim.'))
report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
(p/'docs/stage9/post-motion-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Two post-motion terrain mutation local contracts verified.')
