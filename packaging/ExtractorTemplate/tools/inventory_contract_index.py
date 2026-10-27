"""Index existing static contracts without promoting their fidelity status."""
import argparse
import hashlib
import html
import json
from pathlib import Path


def catalogue(directory):
    sources = []
    for path in sorted(directory.glob('*contract.json')):
        raw = path.read_bytes()
        document = json.loads(raw.decode('utf-8-sig'))
        sections, obligations = [], []

        def visit(value, location):
            if isinstance(value, dict):
                if 'entry' in value or 'contract' in value:
                    sections.append(dict(location=location, entry=value.get('entry'),
                        end_exclusive=value.get('end_exclusive'), name=value.get('name', location),
                        contract=value.get('contract'), pending=value.get('pending'),
                        evidence_count=len(value.get('instruction_evidence', value.get('evidence', [])))))
                for key, child in value.items():
                    if 'pending' in key.lower() or key.lower() == 'remaining':
                        obligations.append(dict(location=location+'/'+key, text=child))
                    if key not in ('instruction_evidence', 'evidence'):
                        visit(child, location+'/'+key)
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    visit(child, location+'/'+str(index))

        visit(document, '')
        sources.append(dict(path=path.name, sha256=hashlib.sha256(raw).hexdigest(),
            scope=document.get('scope'), status='partial_static_contract',
            sections=sections, explicit_pending=obligations))
    return dict(scope='Search index of authored static evidence. A section is not a completed routine; missing pending text does not prove completeness.',
        fully_mapped_claimed=0, full_native_gameplay_ported=False,
        counts=dict(sources=len(sources), sections=sum(len(s['sections']) for s in sources),
            explicit_pending=sum(len(s['explicit_pending']) for s in sources)), sources=sources)


def render(report):
    cards = []
    for source in report['sources']:
        text = json.dumps(source, ensure_ascii=False)
        details = []
        for section in source['sections']:
            title = str(section['name'])+' — '+str(section['entry'] or 'section')
            details.append('<p><b>'+html.escape(title)+'</b><br>'+html.escape(str(section['contract'] or 'See source contract.'))+'</p>')
        pending = ''.join('<li>'+html.escape(str(item['text']))+'</li>' for item in source['explicit_pending'])
        cards.append('<article data-search="'+html.escape(text, quote=True)+'"><h2><a href="'+source['path']+'">'+source['path']+'</a></h2><p>Amber: partial static evidence</p>'+''.join(details)+'<h3>Explicit outstanding obligations</h3><ul>'+pending+'</ul></article>')
    return '<!doctype html><meta charset="utf-8"><title>Rolo static contract index</title><style>body{background:#101820;color:#eee;font:16px system-ui;max-width:1100px;margin:30px auto;padding:20px}a{color:#85caff}article{border-left:5px solid #e9ae36;background:#1c2833;padding:18px;margin:20px 0}input{width:95%;padding:12px}p,li{line-height:1.5}</style><h1>Rolo static contract index</h1><p>'+html.escape(report['scope'])+'</p><p>'+str(report['counts']['sources'])+' source files. No complete mapping or new native gameplay claimed.</p><input id="search" placeholder="Search address, field, behavior or outstanding obligation" aria-label="Search contracts">'+''.join(cards)+'<script>document.getElementById("search").addEventListener("input",event=>{const query=event.target.value.toLowerCase();document.querySelectorAll("article").forEach(card=>card.hidden=!card.dataset.search.toLowerCase().includes(query));});</script>'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=Path(__file__).resolve().parents[1])
    directory = parser.parse_args().project/'docs/stage9'
    report = catalogue(directory)
    (directory/'contract-index.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    (directory/'contract-index.html').write_text(render(report), encoding='utf-8')
    print(json.dumps(report['counts']))


if __name__ == '__main__':
    main()
