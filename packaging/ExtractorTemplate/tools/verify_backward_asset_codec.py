"""Shared actor state leaves, phase waits and explicit literal no-op entries."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
rp=root/'work/backward-asset-codec-results.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));assert r==dict(passed=True,bit_cases=66016,synthetic_cases=12,rom_blocks=95)
sources=['src/core/backward_asset_codec.hpp','tests/backward_asset_codec_verification_tests.cpp','tools/prepare_backward_asset_verification.py','tools/rolo_codec.py'];exe=root/'work/backward_asset_codec_verification_tests.exe';assert exe.stat().st_mtime>=max((p/s).stat().st_mtime for s in sources)
fixture=json.loads((root/'work/backward-asset-fixtures.json').read_text(encoding='utf-8'));assert fixture['rom_sha256']==ROM_HASH and len(fixture['records'])==95
assert hashlib.sha256((root/'work/backward-asset-fixtures.bin').read_bytes()).hexdigest()==fixture['fixture_sha256']
assert len(fixture['empty_bank_aliases'])==9

inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'));accepted={a for x in inv['routines'] for a in x['blocks']};records=[]
specs=[(0xa75a,[(0xa75a,0xa768),(0xa768,0xa7ac),(0xa7ce,0xa808)],'Register-preservingassetwrapper translatedtoimmutableinput/vectoroutput API; decodedsize=result.bytes.size. FullA768validformatbodyincluded; CPUregisterpreservation external totypedAPI.'),(0xa768,[(0xa768,0xa7ac),(0xa7ce,0xa808)],'ReverseLZdata decode:fourdistancewidths,traileroutputsize/skip,LSB-firstreverseLONGreader,literal2bitgroups3extend,matchselectors/optionalextendeddistance and3bitgroups7extend. Backrefsourceaddress evaluatedbeforepredecrement, overlappingcopyintentional.'),(0xa7ac,[(0xa7ac,0xa7b8)],'CanonicalD4=1/D5nonzerosentinel shift; ifstatebecomeszero refillsreversebigendianLONGandROXRwitholdcarry. Returnbit/updatedcursor/state.'),(0xa7b8,[(0xa7b8,0xa7ce)],'WidthentrySUB.W1thenA7BA; widthzero means65536iterations. Not a no-op orRTS. Unsigned32bitresultwrap forwidth>32.'),(0xa7ba,[(0xa7ba,0xa7ce)],'ClearresultD1; repeatcounterWORD+1times,shift/refillbits andappendcarryviaROXL; returnwrapped32bitvalue. CounterFFFFmeans65536bits.')]
for start,ranges,contract in specs:
 items=[]
 for lo,hi in ranges:
  at=lo
  while at<hi:
   assert at in accepted,(hex(start),hex(at));i=Decoder(rom,at).decode();items.append(i);at+=i['size']
  assert at==hi,(hex(start),hex(at),hex(hi))
 records.append(dict(address=start,hex=f'{start:06X}',end_exclusive=max(b for a,b in ranges),code_ranges=ranges,instruction_evidence=items,original_bytes=rom[start:max(b for a,b in ranges)].hex(),verification_status='verified',status=('verified green: literal no-op entry' if contract.startswith('Literal BRA') else 'verified green: local backward asset codec contract'),native_sources=[sources[0]],checked_cases=95 if start in (0xa75a,0xa768) else 66016,contract=contract,proof='One focused decoder batch:all95uniquecompressedblocks from80selectorlayer manifests/nonemptyterrainbanks/existingmapcodec records compareall221350decodedbytes, consumedbits,lowestread,literal/matchcounts toexistingPythondatareference. Independent syntheticbitstreambuilder tests literal/refill,allsmallselectors,extendedshort/longmatches,overlapdistance1,padding andmalformedbounds.66016bitreader/DBF/widthfixtures including32/33/65535/65536limits; formalshift/refillandDBFloopmapping reviewed. Ninezero-sizedbanktablealiasesreportedseparately.',scope='Local admittedwellformedbackwardLZblocks:nonoverlappingimmutableinput/newoutput, output1..65536,widths1..15,padding0..32andvalidbackrefs. Boundschecksrejectoutsideadmitteddata ratherthanemulatinginvalidmemorywrites. Standalonereaderadmitsfinitevalidstreamcount1..65536; CPUregister/stackABI andassetpublication/scheduler external. OriginalROMdataonly, neverinstructionexecution.'))

report=dict(rom_sha256=ROM_HASH,source_sha256={s:hashlib.sha256((p/s).read_bytes()).hexdigest() for s in sources},records=records,test_executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),results_sha256=hashlib.sha256(rp.read_bytes()).hexdigest(),fixture_sha256=fixture["fixture_sha256"],asset_records=fixture["records"],empty_bank_aliases=fixture["empty_bank_aliases"])
(p/'docs/stage9/backward-asset-codec-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Five native backward asset/bitreader contracts verified against95compressedblocks.')
