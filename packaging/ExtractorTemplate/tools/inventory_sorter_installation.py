"""Relocated sorter installation and explicit address references; static only."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder

def catalogue(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH: raise ValueError('ROM revision')
    inventory=json.loads((project/'docs/stage9/inventory.json').read_text())
    accepted=sorted({a for r in inventory['routines'] for a in r['blocks']})
    decoded=[Decoder(rom,a).decode() for a in accepted]
    refs=[i for i in decoded if any(0xffc3cc <= (v&0xffffff) < 0xffc432 for v in i.get('references',[]))]
    calls=[i for i in decoded if i.get('target')==0x313e]
    startup=[i for i in decoded if 0x1364<=i['address']<0x13b2]
    if [i['address'] for i in refs]!=[0x3142,0x31d6]: raise ValueError('Explicit sorter reference domain changed')
    if [i['address'] for i in calls]!=[0x1374]: raise ValueError('Installer caller domain changed')
    return dict(rom_sha256=ROM_HASH,scope='Bounded startup ordering and accepted explicit address-reference census; pointer and bulk aliases remain open.',
        operations=[dict(entry='1374',name='Startup installs sorter before frame resource services',
            contract='Startup calls313E, then2674,2684,31B8,22CE; publishes165E frame callback atC444 beforeSR2500 anddisplay-enablebit6. PriorC432bit5 interrupt-enable write is adjacent to the copied interval, not inside it. This proves local instruction order, not complete callback ancestry.',
            pending='All reset/state entry paths, interrupt eligibility before installation, indexed/bulk writes and live opcode mutations remain required.',instruction_evidence=startup)],
        explicit_references=refs,installer_calls=calls,
        interval=dict(start='FFC3CC',end_exclusive='FFC432',bytes=102,adjacent_register_shadow='FFC432',patch='FFC40C'),
        remaining=['Only accepted instruction boundaries are searched; unknown code can add references.',
            'Absolute addresses are normalized to24bits; no absence-of-alias claim from explicit reference census.',
            'A1 incrementing copy and A7 patch pointer write through registers; other pointer/indexed/bulk writers require lifetime ownership proof.',
            'Do not globally resolve the RAM call until initialization, live opcode/count domains and alias closure are established.'])

if __name__=='__main__':
    p=Path(__file__).resolve().parents[1]
    (p/'docs/stage9/sorter-installation-contract.json').write_text(json.dumps(catalogue(p),indent=2)+'\n')
    print('Sorter installation: one direct installer caller, two explicit interval references; aliases remain open')
