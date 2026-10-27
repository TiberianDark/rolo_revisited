"""Pinned data-only fixtures for native backwards asset decoder verification."""
from pathlib import Path
import hashlib,json,struct
from inventory_rom import ROM_HASH
from rolo_codec import decode_backward_lz
p=Path(__file__).resolve().parents[1];root=p.parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
sources=set();empty_bank_aliases=[]
for i in range(17):
 source=struct.unpack_from('>I',rom,0x4af2a+i*4)[0]
 if struct.unpack_from('>I',rom,source)[0]==0:empty_bank_aliases.append(dict(bank=i,source=source))
 else:sources.add(source)
for f in (p/'assets/extracted/all-levels').glob('selector-*/manifest.json'):
 r=json.loads(f.read_text(encoding='utf-8'));assert r['rom_sha256']==ROM_HASH
 for layer in r['layers'].values():
  source=layer['source']
  if rom[source:source+3]!=b'MAP':sources.add(source)
for f in (p/'assets/extracted/maps').glob('map-*/manifest.json'):
 def visit(r):
  if isinstance(r,dict):
   if str(r.get('codec','')).startswith('rolo-backward-lz'):sources.add(r['source_start'])
   for v in r.values():visit(v)
  elif isinstance(r,list):
   for v in r:visit(v)
 visit(json.loads(f.read_text(encoding='utf-8')))
body=bytearray(struct.pack('>II',len(rom),len(sources)))+rom;records=[]
for source in sorted(sources):
 decoded,info=decode_backward_lz(rom,source);body+=struct.pack('>IIIIII',source,len(decoded),info['bits_read'],info['bitstream_lowest_read_offset'],info['literal_runs'],info['match_runs'])+decoded
 records.append(dict(source=source,decoded_size=len(decoded),sha256=hashlib.sha256(decoded).hexdigest(),**{k:v for k,v in info.items()if k not in ('source_start','decoded_size')}))
fixture=root/'work/backward-asset-fixtures.bin';fixture.write_bytes(body)
report=dict(rom_sha256=ROM_HASH,fixture_sha256=hashlib.sha256(body).hexdigest(),records=records,empty_bank_aliases=empty_bank_aliases,scope='All nonemptyterrain graphics bank sources and compressed layer sources from all80extractedselector manifests, plus existing map codec records. Ninezero-sizebankaliases reportedseparately. Data-only Python reference, not ROM execution.')
(root/'work/backward-asset-fixtures.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(compressed_blocks=len(records),decoded_bytes=sum(r['decoded_size']for r in records))))
