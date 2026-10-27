"""Independent data-only decoded bank references for a focused native caller test."""
from pathlib import Path
import hashlib,json,struct
from rolo_codec import decode_backward_lz
from inventory_rom import ROM_HASH
p=Path(__file__).resolve().parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
records=[];out=bytearray();cache={}
for bank in range(8):
    source=struct.unpack_from('>I',rom,0x4af2a+bank*4)[0]
    if source not in cache:cache[source]=decode_backward_lz(rom,source)[0]
    data=cache[source];out+=struct.pack('<II',bank,len(data))+data
    records.append(dict(bank=bank,source=source,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
target=p.parents[1]/'work/level-menu-bank-fixtures.bin';target.write_bytes(out)
(p/'docs/stage9/level-menu-bank-reference.json').write_text(json.dumps(dict(rom_sha256=ROM_HASH,fixture_sha256=hashlib.sha256(out).hexdigest(),banks=records),indent=2)+'\n',encoding='utf-8')
print(f'{len(records)} bank fixtures prepared from {len(cache)} unique compressed assets')

