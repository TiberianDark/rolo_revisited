"""Build related-batch evidence from current pinned static catalogues; no ROM execution."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from inventory_campaign_statistics import catalogue as campaign
from inventory_entry_marker_callback import catalogue as markers
from inventory_level1_transport import catalogue as transport

def build(p):
    c,m,t=campaign(p),markers(p),transport(p)
    inv=json.loads((p/'docs/stage9/inventory.json').read_text(encoding='utf-8'))
    groups=[('campaign-progress',['6236'],c['operations'],['C558[node] bit1','4BAAA descriptor records'],['Prove the native statistic against all 71 possible completion counts and flag-bit independence.','Trace every completion-bit producer and reset owner before claiming campaign fidelity.']),('entry-marker-relocation',['3E2C','608A','60A6','4CB8'],m['operations'],['F26E','C4E0','C494','F30A+34 foreground MAP'],['Preserve callback D0 across scan termination decisions and allocator/camera service ordering.','Cover variants 14/15, rejected variants, allocation failure and incoming D2 upper word.']),('transporter-destination',['3EE4','937A'],[],['Class 11 hexadecimal destination records','C4E0 integer/fraction positions','121/122 directions and 58/62 speeds'],t['remaining'])]
    rows=[]
    for name,entries,ops,state,gaps in groups:
        addresses={int(v,16) for v in entries}
        calls=[v for v in inv['calls'] if v.get('target') in addresses]
        evidence=[i for i in t['instruction_evidence'] if 0x3ee4<=i['address']<0x3f34] if name=='transporter-destination' else []
        rows.append(dict(group=name,entries=entries,shared_state=state,operations=[o for o in ops if o['entry'] in entries],additional_instruction_evidence=evidence,incoming_call_records=calls,verification_gaps=gaps,status='partial; grouping does not confer verification'))
    files=['src/core/trigger_destination.hpp','src/core/terrain_record_search.hpp','src/core/transporter_continuation.hpp','tests/trigger_destination_tests.cpp']
    return dict(rom_sha256=ROM_HASH,scope='Shared batch dependencies and proof gaps; original instruction evidence, not gameplay certificates',groups=rows,native_evidence=[dict(path=f,sha256=hashlib.sha256((p/f).read_bytes()).hexdigest()) for f in files],campaign_nodes=c['nodes'],campaign_percent_cases=c['percentage_cases'],transporter_links=t['links'],remaining='HUD and terrain streaming remain separate publication batches. No new green status is awarded by this catalogue.')
if __name__=='__main__':
    p=Path(__file__).resolve().parents[1]
    result=build(p)
    (p/'docs/stage9/related-batch-dependencies.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('Related batch dependencies: 3 groups, 7 routine entries, original boundaries and native source hashes pinned')
