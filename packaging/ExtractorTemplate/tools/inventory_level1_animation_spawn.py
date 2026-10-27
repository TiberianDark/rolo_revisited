"""Pinned instruction-boundary evidence for Level1 scenery spawn carry."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder

RANGES=((0x1cb8,0x1cc6,'Normal frame camera/blink/animation order'),
    (0x4cb8,0x4d54,'Camera initialization ending in parallax producer'),
    (0x4eaa,0x4ef4,'Camera parallax producer and publication'),(0x4f00,0x4f04,'Mode3 dispatch slot'),
    (0x4f36,0x4f40,'Mode3 complete-long carry producer'),(0x948a,0x9514,'Player blink service'),
    (0x9514,0x9534,'Blink linked chain helpers'),(0xfcd4,0xfe28,'Actor animation selector/frame dispatch'),
    (0xfea0,0xffee,'Ordinary used animation controls preserving carry'),
    (0x716e,0x719a,'Shared RNG preserving D2'),(0x788ae,0x788b6,'Sound command handoff preserving carry'),
    (0x100a2,0x1011e,'Random-offset spawn and successful field copy'),(0x1011e,0x10134,'Random-hold preserving carry'),
    (0x28b0,0x29de,'Successful actor-chain allocation'),(0x34c2,0x34e8,'Successful graphics allocation'))

def catalogue(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
    inventory=json.loads((project/'docs/stage9/inventory.json').read_text())
    accepted={address for routine in inventory['routines'] for address in routine['blocks']}
    ranges=[]
    for start,end,name in RANGES:
        at=start;instructions=[]
        while at<end:
            if at not in accepted:raise ValueError(f'Unaccepted instruction boundary {at:06X}')
            decoded=Decoder(rom,at).decode()
            if at+decoded['size']>end:raise ValueError(f'Unaligned end {end:06X}')
            instructions.append(dict(address=f'{at:06X}',bytes=rom[at:at+decoded['size']].hex(),mnemonic=decoded['mnemonic'],operands=decoded['operands']))
            at+=decoded['size']
        ranges.append(dict(start=f'{start:06X}',end_exclusive=f'{end:06X}',name=name,sha256=hashlib.sha256(rom[start:end]).hexdigest(),instructions=instructions))
    keys=[0x13ecc,0x13eee,0x13f98,0x13fba,0x140ec]
    keys += [int(value,16) for value in json.loads((project/'docs/stage9/level1-object-export.json').read_text())['definitions']]
    definitions=[dict(address=f'{key:06X}',byte7=rom[key+7],animation_callback_enabled=bool(rom[key+7]&32)) for key in keys]
    if any(value['animation_callback_enabled'] for value in definitions):raise ValueError('New animation callback invalidates scoped carry domain')
    if rom[0x4aedb]!=3 or rom[0x4f3a:0x4f3e]!=bytes.fromhex('74ff7600'):raise ValueError('Mode3 carry producer differs')
    return dict(rom_sha256=ROM_HASH,scope='Pinned Level1 normal-frame Mode3 and current immutable definitions; no runtime instruction execution',
        initial_d2='FFFFFFFF',initial_d3='00000000',mode_source='04AEDB',mode=3,
        definitions=definitions,ranges=ranges,range_count=len(ranges),
        pending=['Other camera modes, RAM definitions and callback mutation domains','Allocation diagnostic5998 exceptional clobbers','Full independent original gameplay verification'])

if __name__=='__main__':
    project=Path(__file__).resolve().parents[1];report=catalogue(project)
    (project/'docs/stage9/level1-animation-spawn-carry.json').write_text(json.dumps(report,indent=2)+'\n')
    print(dict(ranges=report['range_count'],definitions=len(report['definitions']),initial_d2=report['initial_d2'],initial_d3=report['initial_d3']))
