"""Decode immutable text data from accepted immediate pointer producers."""
import hashlib,json,re
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder

def catalogue(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM revision')
    inv=json.loads((project/'docs/stage9/inventory.json').read_text());accepted=sorted({a for r in inv['routines'] for a in r['blocks']})
    refs=[Decoder(rom,a).decode() for a in accepted if any((v&0xffffff)==0xffc4ae for v in Decoder(rom,a).decode().get('references',[]))]
    producers=[]
    for i in refs:
        match=re.fullmatch(r'#\$([0-9A-F]{8}),\(\$FFFFC4AE\)\.L',i['operands'])
        if i['mnemonic']=='MOVE.L' and match:producers.append(dict(site=i['address'],pointer=int(match[1],16)))
    streams=[]
    for seed in sorted({q['pointer'] for q in producers if q['pointer']<len(rom)}):
        immediate_renderer=seed in (0x58d1,0x5925)
        at=seed;seen=set();events=[];reason='limit'
        for _ in range(4096):
            if at>=len(rom):reason='non-ROM redirect';break
            if at in seen:reason='data loop';break
            seen.add(at);start=at;b=rom[at];at+=1
            event=dict(address=start,byte=b)
            if immediate_renderer:
                event['kind']='terminator' if b==0 else 'newline' if b==13 else 'backspace' if b==8 else 'static glyph'
                events.append(event)
                if b==0:reason='terminator';break
                continue
            if 32<=b<=159:event['kind']='space' if b==32 else 'glyph'
            else:
                event.update(kind='control',offset=b*4)
                if b>8:events.append(event);reason='outside nine slots';break
                if b==0:events.append(event);reason='terminator';break
                if b==7:events.append(event);reason='menu state handoff';break
                size={1:2,3:1,4:4,5:4,6:3}.get(b,0)
                if b==5:at=(at+1)&~1
                raw=rom[at:at+size]
                if len(raw)!=size:events.append(event);reason='argument extent';break
                event.update(argument_address=at,arguments=raw.hex());at+=size
                if b==4:at=int.from_bytes(raw,'big');event['redirect']=at
            events.append(event)
        streams.append(dict(seed=seed,consumer='7094 (direct1A30/1A56)' if immediate_renderer else '6DA8 format hypothesis; caller association pending',producer_sites=[q['site'] for q in producers if q['pointer']==seed],events=events,stop_reason=reason,event_count=len(events),control_domain=sorted({e['byte'] for e in events if e['kind']=='control'})))
    def span(start,end):
        at=start;out=[]
        while at<end:
            if at not in accepted:raise ValueError(f'Unaccepted association boundary{at:X}')
            i=Decoder(rom,at).decode();out.append(i);at+=i['size']
        if at!=end:raise ValueError('Association extent')
        return out
    return dict(rom_sha256=ROM_HASH,scope='Immutable text-data traversal from explicit immediate C4AE producers.58D1/5925direct7094associationproved; other6DA8format interpretationsremainconditional. This is format decoding, not ROM instruction execution.',explicit_pointer_references=refs,immediate_producers=producers,streams=streams,static_consumer_association_evidence=span(0x1a06,0x1a5a),
        counts=dict(immediate_producers=len(producers),rom_seeds=len(streams),ram_or_external_immediate_producers=sum(q['pointer']>=len(rom) for q in producers),outside_slot_streams=sum(s['stop_reason']=='outside nine slots' for s in streams)),
        remaining=['Register-produced C4AE sources, RAM-generated strings and pointer/bulk/overlapping writers remain unclosed.','Menu command7 transfers control to state code; this data traversal stops rather than assuming its continuation.','A finite immutable corpus is not the complete runtime byte/redirect domain; keep6DF0globallyunresolved.'])

if __name__=='__main__':
    p=Path(__file__).resolve().parents[1];r=catalogue(p)
    (p/'docs/stage9/text-source-contract.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r['counts']))
