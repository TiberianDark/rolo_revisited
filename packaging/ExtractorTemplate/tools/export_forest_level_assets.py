"""Reuse pinned forest bank1; bind every world-linked forest MAP as native data."""
from pathlib import Path
import hashlib,json,struct
p=Path(__file__).resolve().parents[1]
rom=(p/'local/rolo.md').read_bytes()
expected='9478d47cc1883df42f3714ea485aedd71b541274eb45a3aa7c49f4a3518305e9'
assert hashlib.sha256(rom).hexdigest()==expected
root=p/'assets/extracted/all-levels';manifest=json.loads((root/'manifest.json').read_text())
entries=[e for e in manifest['selectors'] if e['world_referenced'] and e['layers']['foreground']['bank']==1]
assert [e['selector'] for e in entries]==list(range(1,14))
lines=['#pragma once','#include <array>','namespace rolo::forest_level_data {'];rows=[]
def array(name,ctype,values):
    lines.append(f'inline constexpr std::array<{ctype},{len(values)}> {name}{{{{')
    for at in range(0,len(values),24):lines.append('  '+','.join(map(str,values[at:at+24]))+',')
    lines.append('}};')
for e in entries:
    n=e['selector']
    if n in (1,2,3,4,8):continue
    for layer in ('foreground','background'):
        source=root/f'selector-{n:02}'/f'{layer}.map';data=source.read_bytes()
        assert hashlib.sha256(data).hexdigest()==e['layers'][layer]['binary']['sha256']
        assert data[:3]==b'MAP' and data[3]==1
        array(f'level{n}_{layer}','std::uint8_t',list(data))
    palette=(root/f'selector-{n:02}/palette.cram').read_bytes();assert len(palette)==128
    array(f'level{n}_palette','std::uint16_t',list(struct.unpack('>64H',palette)))
    reward=rom[0x4ab1a+n*8+4]
    rows.append(dict(selector=n,width=e['layers']['foreground']['width'],height=e['layers']['foreground']['height'],reward=reward))
lines.append('}')
target=p/'src/core/forest_level_data.hpp';target.write_text('\n'.join(lines)+'\n',encoding='utf-8')
(p/'docs/stage9/forest-level-assets.json').write_text(json.dumps(dict(rom_sha256=expected,added=rows,header_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),scope='Immutable forest bank1 MAP/palette bindings; gameplay helpers and object completeness separate.'),indent=2)+'\n',encoding='utf-8')
print(rows)
