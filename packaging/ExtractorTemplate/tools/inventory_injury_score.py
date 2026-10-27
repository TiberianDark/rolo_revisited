"""Reproduce static injury/blink/score handoff contracts for the pinned ROM."""
from pathlib import Path
import hashlib,json
from inventory_rom import ROM_HASH
from m68k_static import Decoder

def catalogue(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
    inv=json.loads((project/'docs/stage9/inventory.json').read_text())
    accepted={a for r in inv['routines'] for a in r['blocks']}
    specs=[
        (0x948a,0x9534,'Player contact blink','player_contact_resolution.hpp',
         'F2BC skips. C519 or zeroC511 clears125bit1 across livecontrolled-link chain. NegativeC511 sets1,C50A/C50C0600 and returns. PositiveC511 subtracts0100 fromcounter; negative reloadsdelay, toggles125bit1, subtracts0040 delay, clearsC511 andchainbit1 ifdelaynegative.948A normalframe precedesFCD4; local949? set-chain entry9504 remains separate/unreached on thisnormalpath.'),
        (0x9534,0x95de,'Frame-end contact resolution','player_contact_resolution.hpp',
         'C518 invokes63FA thenstate165E/C461zero. C51A type4 tail1D94; otherscall9642. IfC519zero andC516nonzero request sound16,setC519FF,clearC524,setC511FF. IfC5CDzero,C511zero,C517nonzero request16 then95DE. NonzeroC522 tail1CEE preservesC516/C517; otherwise clearboth. C516 is the SAME byte written byplayer-position bounds/surfaceeffects, notanindependent copy.'),
        (0x95de,0x9642,'Companion loss or Rolo injury','player_contact_resolution.hpp',
         'Type4 checks three6402/6406/640A companion keys inreverseorder withDBNE. Firstnonzero iscleared,callbackADD0,125bit2set,46/47cleared;controlled122FF/62=65E00,C511FF/C51BFF. Noavailablecompanion orothertype setsC519FF/C511FF. CompanioncallbackADD0 andfulltransition9642 remainrequirednativeconsumers.'),
        (0x997e,0x99c6,'Score award and threshold progression','score_award.hpp',
         'ADD.L amount toC52Ewraps. Unsigned nextthresholdC528<=total awardsone lifevia9A04. AdvanceC52Cword4; positive nexttablelong stored. NegativeFFFFFFFFsentinel uses(table[index-4]-table[index-8])+currentthreshold andretainspriorindex. Initialtable1000000,2000000,FFFFFFFF yieldsone lifeeachmillion. Wrappedthreshold domains rejectedexplicitly; allothercallers andtableoffset mutationspending.'),
        (0x99c6,0x99d6,'Score threshold initialization','score_award.hpp',
         'ClearC52Cword andloadfirsttablelong99D6intoC528. DoesnotclearC52Etotal; nativeScoreAwardState defaultmodelsfreshinitialization only. Loaded/resumedtotalproducerdomainsremainpending.'),
        (0x9a04,0x9a1a,'Signed-byte life addition and cap','score_award.hpp',
         'ADD.B C51D toamount, CMP.B63 then signedBLE. Clamp99 onlyifsignedresult>99; byteoverflow to128..255 isnegative andnotclamped. Originalsignedpostadditionconditionretained.'),
    ]
    operations=[]
    for start,end,name,source,contract in specs:
        evidence=[];at=start
        while at<end:
            if at not in accepted:raise ValueError(f'Unaccepted boundary {at:06X}')
            i=Decoder(rom,at).decode();evidence.append(dict(address=f'{at:06X}',bytes=rom[at:at+i['size']].hex(),mnemonic=i['mnemonic'],operands=i['operands']));at+=i['size']
        if at!=end:raise ValueError('Unaligned range')
        operations.append(dict(entry=f'{start:06X}',end_exclusive=f'{end:06X}',name=name,contract=contract,
            native_sources=['src/core/'+source],instruction_evidence=evidence,range_sha256=hashlib.sha256(rom[start:end]).hexdigest(),
            pending='Full normalframe binding, transition tails, companionADD0 behaviour, HUD/queue/audio and original-reference comparison remain incomplete.'))
    values=[int.from_bytes(rom[a:a+4],'big') for a in (0x99d6,0x99da,0x99de)]
    if values!=[1000000,2000000,0xffffffff]:raise ValueError('Threshold bytes differ')
    return dict(rom_sha256=ROM_HASH,operations=operations,score_table=dict(source='0099D6',end_exclusive='0099E2',values=values,sha256=hashlib.sha256(rom[0x99d6:0x99e2]).hexdigest()),
        shared_state_aliases=[dict(address='FFFFC516',producers=['8202 player position bounds','9196 surface effects'],consumer='9534 injury resolution',native_binding='movement.bounds.c516'),
            dict(address='FFFFC51D',producers=['9A04 life addition'],consumers=['7748 damage countdown/death'],native_binding='movement.c51d')],
        scope='Pinned local contracts and bounded native bindings. Not full injury/respawn/HUD/gameplay or original1:1 verification.')

def verify(project):
    if json.loads((project/'docs/stage9/injury-score-contract.json').read_text())!=catalogue(project):raise ValueError('Stale injury/score contract')

if __name__=='__main__':
    project=Path(__file__).resolve().parents[1];report=catalogue(project)
    (project/'docs/stage9/injury-score-contract.json').write_text(json.dumps(report,indent=2)+'\n')
    print({'pinned_ranges':len(report['operations']),'thresholds':report['score_table']['values']})
