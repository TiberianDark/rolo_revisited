"""Batch native BMP companions for existing immutable all-level PNG extracts."""
from pathlib import Path
import hashlib,json
from PIL import Image
p=Path(__file__).resolve().parents[1]
root=p/'assets/extracted/all-levels'
manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
rows=[]
for entry in manifest['selectors']:
    selector=entry['selector']
    for layer in ('foreground','background'):
        source=root/f'selector-{selector:02}'/f'{layer}.png'
        target=source.with_suffix('.bmp')
        with Image.open(source) as im:
            rgb=im.convert('RGB')
            rgb.save(target)
            with Image.open(target) as check:
                assert check.size==rgb.size and check.convert('RGB').tobytes()==rgb.tobytes()
        rows.append(dict(selector=selector,layer=layer,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),bmp_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),size=target.stat().st_size))
(root/'demo-preview-manifest.json').write_text(json.dumps(dict(rom_sha256=manifest['rom_sha256'],scope='Lossless format conversion of existing static extracts only; no new gameplay.',layers=rows),indent=2)+'\n',encoding='utf-8')
print(f'{len(rows)} preview layers prepared and pixel-checked in one batch')
