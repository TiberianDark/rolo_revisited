"""Offline documented Z80 instruction/control-flow decoder; no CPU execution.

Encoding reference: https://www.zilog.com/docs/z80/um0080.pdf
Undocumented index-register and prefix combinations stop explicitly.
"""
import argparse
import hashlib
import json
from collections import deque
from pathlib import Path

class Unsupported(ValueError): pass

R=['B','C','D','E','H','L','(HL)','A']
RP=['BC','DE','HL','SP']; RP2=['BC','DE','HL','AF']
CC=['NZ','Z','NC','C','PO','PE','P','M']
ALU=['ADD A,','ADC A,','SUB ','SBC A,','AND ','XOR ','OR ','CP ']

def decode(data,address):
    pc=address;flow='next';target=None;references=[];index=None
    def byte():
        nonlocal pc
        if pc>=len(data): raise Unsupported('Truncated instruction')
        v=data[pc];pc+=1;return v
    def word():
        lo=byte();return lo|(byte()<<8)
    def relative():
        displacement=byte();return (pc+(displacement if displacement<128 else displacement-256))&0xffff
    def h(v): return '$%04X'%v
    op=byte()
    if op in (0xdd,0xfd):
        index='IX' if op==0xdd else 'IY';op=byte()
        if op in (0xdd,0xfd,0xed): raise Unsupported('Undocumented/repeated index prefix')
    x,y,z=op>>6,(op>>3)&7,op&7;p,q=y>>1,y&1
    r=R.copy();rp=RP.copy();rp2=RP2.copy();hl=index or 'HL'
    if index: rp[2]=rp2[2]=index
    if op==0xcb:
        if index:
            d=byte();operand='(%s%+d)'%(index,d if d<128 else d-256);cb=byte()
            if cb&7!=6: raise Unsupported('Undocumented indexed CB register result')
        else: cb=byte();operand=r[cb&7]
        kind,bit=cb>>6,(cb>>3)&7
        if kind==0:
            if bit==6: raise Unsupported('Undocumented SLL')
            text=['RLC','RRC','RL','RR','SLA','SRA','SLL','SRL'][bit]+' '+operand
        else: text=['','BIT','RES','SET'][kind]+' '+str(bit)+','+operand
    elif op==0xed:
        ed=byte();p=(ed>>4)&3
        if ed&0xc7 in (0x43,0x4b):
            n=word();references.append(n)
            text='LD '+(RP[p]+',('+h(n)+')' if ed&8 else '('+h(n)+'),'+RP[p])
        elif ed&0xcf in (0x42,0x4a): text=('ADC' if ed&8 else 'SBC')+' HL,'+RP[p]
        elif ed&0xc7==0x40 and (ed>>3)&7!=6: text='IN '+R[(ed>>3)&7]+',(C)'
        elif ed&0xc7==0x41 and (ed>>3)&7!=6: text='OUT (C),'+R[(ed>>3)&7]
        elif ed in (0x45,0x4d): text='RETN' if ed==0x45 else 'RETI';flow='return'
        elif ed in (0x44,0x46,0x56,0x5e,0x47,0x4f,0x57,0x5f,0x67,0x6f):
            text={0x44:'NEG',0x46:'IM 0',0x56:'IM 1',0x5e:'IM 2',0x47:'LD I,A',0x4f:'LD R,A',0x57:'LD A,I',0x5f:'LD A,R',0x67:'RRD',0x6f:'RLD'}[ed]
        elif ed in (0xa0,0xa1,0xa2,0xa3,0xa8,0xa9,0xaa,0xab,0xb0,0xb1,0xb2,0xb3,0xb8,0xb9,0xba,0xbb):
            text={0xa0:'LDI',0xa1:'CPI',0xa2:'INI',0xa3:'OUTI',0xa8:'LDD',0xa9:'CPD',0xaa:'IND',0xab:'OUTD',0xb0:'LDIR',0xb1:'CPIR',0xb2:'INIR',0xb3:'OTIR',0xb8:'LDDR',0xb9:'CPDR',0xba:'INDR',0xbb:'OTDR'}[ed]
        else: raise Unsupported('Unsupported ED opcode $%02X'%ed)
    else:
        if index:
            memory=(x==1 and op!=0x76 and (y==6 or z==6)) or (x==2 and z==6) or (x==0 and z in (4,5,6) and y==6)
            pair=(x==0 and ((z==1 and (q or p==2)) or (z in (2,3) and p==2))) or op in (0xe1,0xe3,0xe5,0xe9,0xf9)
            if memory:
                d=byte();r[6]='(%s%+d)'%(index,d if d<128 else d-256)
            elif not pair: raise Unsupported('Unsupported/undocumented index-prefix form')
        if x==0:
            if z==0:
                if y<2: text=['NOP',"EX AF,AF'"][y]
                else:
                    target=relative();flow='jump' if y==3 else 'branch'
                    text=('DJNZ ' if y==2 else 'JR '+(CC[y-4]+',' if y>=4 else ''))+h(target)
            elif z==1:
                text='ADD '+hl+','+rp[p] if q else 'LD '+rp[p]+','+h(word())
            elif z==2:
                if p<2:operand='('+RP[p]+')'
                else:
                    n=word();references.append(n);operand='('+h(n)+')'
                register=hl if p==2 else 'A'
                text='LD '+(register+','+operand if q else operand+','+register)
            elif z==3: text=('DEC ' if q else 'INC ')+rp[p]
            elif z in (4,5): text=('INC ' if z==4 else 'DEC ')+r[y]
            elif z==6: text='LD '+r[y]+',$%02X'%byte()
            else: text=['RLCA','RRCA','RLA','RRA','DAA','CPL','SCF','CCF'][y]
        elif x==1:
            if op==0x76: text='HALT';flow='stop'
            else: text='LD '+r[y]+','+r[z]
        elif x==2: text=ALU[y]+r[z]
        elif z==0: text='RET '+CC[y];flow='conditional_return'
        elif z==1:
            if not q: text='POP '+rp2[p]
            elif p==0: text='RET';flow='return'
            elif p==1: text='EXX'
            elif p==2: text='JP ('+hl+')';flow='jump'
            else: text='LD SP,'+hl
        elif z==2: target=word();flow='branch';text='JP '+CC[y]+','+h(target)
        elif z==3:
            if y==0: target=word();flow='jump';text='JP '+h(target)
            elif y==2: text='OUT ($%02X),A'%byte()
            elif y==3: text='IN A,($%02X)'%byte()
            elif y==4: text='EX (SP),'+hl
            elif y==5: text='EX DE,HL'
            elif y>=6: text=['DI','EI'][y-6]
            else: raise Unsupported('Unexpected CB prefix')
        elif z==4: target=word();flow='call';text='CALL '+CC[y]+','+h(target)
        elif z==5:
            if not q: text='PUSH '+rp2[p]
            elif p==0: target=word();flow='call';text='CALL '+h(target)
            else: raise Unsupported('Unexpected prefix')
        elif z==6: text=ALU[y]+'$%02X'%byte()
        else: target=y*8;flow='call';text='RST '+h(target)
    return dict(address=address,size=pc-address,bytes=data[address:pc].hex(),text=text,
                flow=flow,target=target,references=references)

def walk(data,seeds):
    queue=deque(seeds);decoded={};claimed=set();stops=[];edges=[]
    while queue:
        a=queue.popleft()
        if a in decoded: continue
        if not 0<=a<len(data): stops.append(dict(address=a,reason='Outside copied driver'));continue
        if a in claimed: stops.append(dict(address=a,reason='Inside another instruction'));continue
        try:i=decode(data,a)
        except Unsupported as e:stops.append(dict(address=a,reason=str(e)));continue
        span=set(range(a,a+i['size']))
        if span&claimed:stops.append(dict(address=a,reason='Instruction overlap'));continue
        claimed.update(span);decoded[a]=i
        successors=[]
        if i['flow'] in ('next','call','branch','conditional_return'):successors.append(('fallthrough',a+i['size']))
        if i['flow'] in ('call','jump','branch'):
            if i['target'] is None:stops.append(dict(address=a,reason='Indirect '+i['flow']))
            else:successors.append((i['flow'],i['target']))
        for kind,target in successors:edges.append(dict(source=a,destination=target,kind=kind));queue.append(target)
    return dict(seeds=seeds,instructions=[decoded[a] for a in sorted(decoded)],stops=stops,edges=edges,
                scope='Static documented-instruction candidates; no execution or timing simulation')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('rom');p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    rom=Path(a.rom).read_bytes()
    from inventory_rom import ROM_HASH
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('Unexpected ROM revision')
    result=walk(rom[0x7e7a0:0x7f8c0],[0,8,16,24,32,40,48,56,0x66])
    result['calls']=[i for i in result['instructions'] if i['flow']=='call']
    result['entry_candidates']=sorted(set(result['seeds'])|{i['target'] for i in result['calls'] if i['target'] is not None})
    result['absolute_memory_references']=sorted({v for i in result['instructions'] for v in i['references']})
    result['counts']=dict(instructions=len(result['instructions']),calls=len(result['calls']),entry_candidates=len(result['entry_candidates']),stops=len(result['stops']))
    result.update(rom_sha256=ROM_HASH,source=0x7e7a0,copied_size=0x1120,reference='https://www.zilog.com/docs/z80/um0080.pdf')
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/'z80-driver.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (a.out/'z80-driver.asm').write_text('\n'.join('%04X [ROM %06X] %-10s %s'%(i['address'],0x7e7a0+i['address'],i['bytes'].upper(),i['text']) for i in result['instructions'])+'\n',encoding='utf-8')
    print('Z80 static instructions:',len(result['instructions']),'stops:',len(result['stops']))

if __name__=='__main__':main()
