"""Add inspectable raw MAP markers without inventing object identities."""
import argparse
import html
import json
from pathlib import Path


def export(atlas):
    report = json.loads((atlas/'manifest.json').read_text())
    pages = []
    for row in report['selectors']:
        for layer in row['layers']:
            if layer['layer'] != 'foreground':
                continue
            sections = layer.get('sections', [{'image':layer['image'],'x':0,'y':0,
                                               'width':layer['width'],'height':layer['height']}])
            pictures = []
            for section in sections:
                ox,oy,w,h = (section[k] for k in ('x','y','width','height'))
                circles = []
                for marker in layer['markers']:
                    x,y = marker['x']-ox,marker['y']-oy
                    if 0<=x<w and 0<=y<h:
                        circles.append(f'<g><circle cx="{x}" cy="{y}" r="8" fill="#ffdf40" stroke="#000" stroke-width="2"/><title>Raw type ${marker["type"]:04X}; ({marker["x"]}, {marker["y"]}); MAP offset ${marker["offset"]:04X}</title></g>')
                pictures.append(f'<p>Section origin ({ox}, {oy})</p><svg viewBox="0 0 {w} {h}" style="width:100%;background:#000"><image href="{section["image"]}" width="{w}" height="{h}"/>'+''.join(circles)+'</svg>')
            records = ''.join(f'<tr><td>${m["type"]:04X}</td><td>{m["x"]}</td><td>{m["y"]}</td><td>${m["offset"]:04X}</td></tr>' for m in layer['markers'])
            page = f'selector-{row["selector"]:02d}-markers.html'
            (atlas/page).write_text('<!doctype html><meta charset="utf-8"><style>body{background:#101820;color:#eee;font:16px system-ui;margin:24px}svg image{image-rendering:pixelated}td,th{padding:8px;text-align:left}</style><h1>Selector '+str(row['selector'])+' — recorded markers</h1><p>Yellow dots show raw special MAP records, not confirmed enemy identities or final actor positions. Hover for type, coordinate and source offset. All special records are listed below, including any outside the image bounds.</p>'+''.join(pictures)+'<table><tr><th>Raw type</th><th>X</th><th>Y</th><th>MAP offset</th></tr>'+records+'</table>',encoding='utf-8')
            pages.append(f'<li><a href="{page}">Selector {row["selector"]:02d}: {len(layer["markers"])} recorded markers</a></li>')
    (atlas/'markers.html').write_text('<!doctype html><meta charset="utf-8"><h1>Rolo marker atlas</h1><p>Raw MAP records; meanings and runtime changes remain subject to tracing.</p><ul>'+''.join(pages)+'</ul>',encoding='utf-8')
    print(f'{len(pages)} foreground placement pages')


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('atlas',type=Path)
    export(p.parse_args().atlas)
