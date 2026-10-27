"""Limited offline MC68000 decoder. Never executes instructions.

Only the explicitly implemented instruction forms are supported. Unknown forms
stop a path; this is a research aid, not a general-purpose disassembler.
"""
import argparse
import hashlib
import json
import struct
from collections import deque
from pathlib import Path
from romtool import read_rom

CONDITIONS = ('T','F','HI','LS','CC','CS','NE','EQ','VC','VS','PL','MI','GE','LT','GT','LE')


class Unsupported(ValueError):
    pass


def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits-1)) else value


class Decoder:
    def __init__(self, data, address):
        self.data, self.start, self.pc = data, address, address
        self.references = []

    def word(self):
        if self.pc+2 > len(self.data): raise Unsupported('Truncated word')
        value = struct.unpack_from('>H', self.data, self.pc)[0]; self.pc += 2
        return value

    def long(self):
        return (self.word() << 16) | self.word()

    def ea(self, mode, reg, size, immediate=True):
        if mode == 0: return f'D{reg}', None
        if mode == 1: return f'A{reg}', None
        if mode == 2: return f'(A{reg})', None
        if mode == 3: return f'(A{reg})+', None
        if mode == 4: return f'-(A{reg})', None
        if mode == 5: return f'({signed(self.word(),16):+d},A{reg})', None
        if mode == 6 or (mode == 7 and reg == 3):
            base = self.pc
            extension = self.word()
            if extension & 0x0700: raise Unsupported('Non-68000 index extension')
            index = ('A' if extension & 0x8000 else 'D')+str((extension >> 12)&7)
            index += '.L' if extension & 0x800 else '.W'
            base_text = f'A{reg}' if mode == 6 else 'PC'
            return f'({signed(extension & 255,8):+d},{base_text},{index})', None
        if mode != 7: raise Unsupported('Invalid effective address')
        if reg == 0:
            raw = self.word(); address = signed(raw,16) & 0xffffff
            self.references.append(address); return f'(${raw:04X}).W', address
        if reg == 1:
            raw = self.long(); address = raw & 0xffffff
            self.references.append(address); return f'(${raw:08X}).L', address
        if reg == 2:
            base = self.pc; displacement = signed(self.word(),16); address = (base+displacement)&0xffffff
            self.references.append(address); return f'(${address:06X},PC)', address
        if reg == 4 and immediate:
            value = self.long() if size == 4 else self.word()
            if size == 1: value &= 255
            return f'#${value:0{size*2}X}', None
        raise Unsupported('Invalid/unsupported effective address')

    def decode(self):
        if self.start < 0 or self.start % 2: raise Unsupported('Unaligned address')
        op = self.word(); mode, reg = (op >> 3)&7, op&7
        flow, target = 'next', None
        mnemonic, operands = '', ''
        if op in (0x4e75, 0x4e73, 0x4e77):
            mnemonic = {0x4e75:'RTS',0x4e73:'RTE',0x4e77:'RTR'}[op]; flow = 'return'
        elif op == 0x4e71: mnemonic = 'NOP'
        elif op == 0x4e70: mnemonic = 'RESET'
        elif op == 0x4e72:
            mnemonic, operands, flow = 'STOP', f'#${self.word():04X}', 'stop'
        elif op & 0xfff0 == 0x4e40:
            mnemonic, operands, flow = 'TRAP', f'#{op & 15}', 'stop'
        elif op & 0xfff8 == 0x4e50:
            mnemonic, operands = 'LINK', f'A{reg},#{signed(self.word(),16)}'
        elif op & 0xfff8 == 0x4e58: mnemonic, operands = 'UNLK', f'A{reg}'
        elif op & 0xfff0 == 0x4e60:
            mnemonic = 'MOVE.L'; operands = f'USP,A{reg}' if op & 8 else f'A{reg},USP'
        elif op & 0xffc0 in (0x4e80,0x4ec0):
            mnemonic = 'JSR' if op & 0xffc0 == 0x4e80 else 'JMP'
            operands, target = self.ea(mode,reg,4,False)
            flow = 'call' if mnemonic == 'JSR' else 'jump'
        elif op >> 12 == 6:
            condition = (op >> 8)&15
            displacement = signed(op&255,8)
            if not (op&255): displacement = signed(self.word(),16)
            target = (self.start+2+displacement)&0xffffff
            mnemonic = 'BRA' if condition == 0 else 'BSR' if condition == 1 else 'B'+CONDITIONS[condition]
            operands = f'${target:06X}'
            flow = 'jump' if condition == 0 else 'call' if condition == 1 else 'branch'
        elif op & 0xf0f8 == 0x50c8:
            condition = (op >> 8)&15
            target = (self.start+2+signed(self.word(),16))&0xffffff
            mnemonic, operands, flow = 'DB'+CONDITIONS[condition], f'D{reg},${target:06X}', 'branch'
        elif op & 0xf100 == 0x7000:
            mnemonic, operands = 'MOVEQ', f'#{signed(op&255,8)},D{(op >> 9)&7}'
        elif op & 0xf1c0 == 0x41c0:
            ea, _ = self.ea(mode,reg,4,False)
            mnemonic, operands = 'LEA', f'{ea},A{(op >> 9)&7}'
        elif op & 0xfb80 == 0x4880 and mode >= 2:
            mask = self.word(); size = 4 if op & 0x40 else 2
            names = []
            for bit in range(16):
                if mask & (1 << bit):
                    index = 15-bit if mode == 4 and not op & 0x400 else bit
                    names.append(('D' if index < 8 else 'A')+str(index&7))
            ea, _ = self.ea(mode,reg,size,False)
            regs = '/'.join(names)
            mnemonic = 'MOVEM.'+('L' if size == 4 else 'W')
            operands = f'{ea},{regs}' if op & 0x400 else f'{regs},{ea}'
        elif op & 0xfff8 == 0x4840: mnemonic, operands = 'SWAP', f'D{reg}'
        elif op & 0xfff8 in (0x4880,0x48c0):
            mnemonic, operands = 'EXT.'+('L' if op & 0x40 else 'W'), f'D{reg}'
        elif op & 0xffc0 == 0x4840:
            operands, _ = self.ea(mode,reg,4,False); mnemonic = 'PEA'
        elif op >> 12 in (1,2,3):
            size = {1:1,2:4,3:2}[op >> 12]; dest_mode, dest_reg = (op >> 6)&7, (op >> 9)&7
            source, _ = self.ea(mode,reg,size)
            destination, _ = self.ea(dest_mode,dest_reg,size,False)
            mnemonic = ('MOVEA' if dest_mode == 1 else 'MOVE')+'.'+{1:'B',2:'W',4:'L'}[size]
            operands = f'{source},{destination}'
        elif op & 0xffc0 in (0x40c0,0x44c0,0x46c0):
            ea, _ = self.ea(mode,reg,2)
            mnemonic = 'MOVE.W'
            operands = f'SR,{ea}' if op & 0xffc0 == 0x40c0 else f'{ea},'+('CCR' if op & 0xffc0 == 0x44c0 else 'SR')
        elif op & 0xff00 in (0x4200,0x4400,0x4600,0x4a00) and (op >> 6)&3 != 3:
            size = (1,2,4)[(op >> 6)&3]
            mnemonic = {0x4200:'CLR',0x4400:'NEG',0x4600:'NOT',0x4a00:'TST'}[op&0xff00]+'.'+{1:'B',2:'W',4:'L'}[size]
            operands, _ = self.ea(mode,reg,size,False)
        elif op >> 12 == 0 and op & 0xff00 in (0x0000,0x0200,0x0400,0x0600,0x0a00,0x0c00):
            code = (op >> 6)&3
            if code == 3: raise Unsupported('Immediate size')
            size = (1,2,4)[code]
            immediate, _ = self.ea(7,4,size)
            if op & 0x3f == 0x3c and op & 0xff00 in (0,0x200,0xa00):
                destination = 'SR' if size == 2 else 'CCR'
            else: destination, _ = self.ea(mode,reg,size,False)
            mnemonic = {0:'ORI',0x200:'ANDI',0x400:'SUBI',0x600:'ADDI',0xa00:'EORI',0xc00:'CMPI'}[op&0xff00]+'.'+{1:'B',2:'W',4:'L'}[size]
            operands = f'{immediate},{destination}'
        elif op & 0xf100 == 0x0100 or op & 0xff00 == 0x0800:
            if mode == 1: raise Unsupported('MOVEP not implemented')
            bit = f'D{(op >> 9)&7}' if op & 0x100 else f'#{self.word()}'
            mnemonic = ('BTST','BCHG','BCLR','BSET')[(op >> 6)&3]
            ea, _ = self.ea(mode,reg,4 if mode == 0 else 1,False); operands = f'{bit},{ea}'
        elif op >> 12 == 5:
            code = (op >> 6)&3
            if code == 3:
                mnemonic = 'S'+CONDITIONS[(op >> 8)&15]; operands, _ = self.ea(mode,reg,1,False)
            else:
                size = (1,2,4)[code]; ea, _ = self.ea(mode,reg,size,False)
                mnemonic = ('SUBQ' if op & 0x100 else 'ADDQ')+'.'+{1:'B',2:'W',4:'L'}[size]
                operands = f'#{((op >> 9)&7) or 8},{ea}'
        elif op & 0xf1f8 in (0xc140,0xc148,0xc188):
            kind = op&0xf1f8; rx = (op >> 9)&7
            operands = f'D{rx},D{reg}' if kind == 0xc140 else f'A{rx},A{reg}' if kind == 0xc148 else f'D{rx},A{reg}'
            mnemonic = 'EXG'
        elif op >> 12 in (8,9,11,12,13):
            family, om, dn = op >> 12, (op >> 6)&7, (op >> 9)&7
            if family in (9,13) and om not in (3,7) and op & 0xf130 in (0x9100,0xd100): raise Unsupported('ADDX/SUBX not implemented')
            if family in (8,12) and op & 0xf1f0 in (0x8100,0xc100): raise Unsupported('BCD not implemented')
            if family == 11 and om in (4,5,6) and op & 0xf138 == 0xb108:
                mnemonic = 'CMPM.'+('B','W','L')[om-4]
                operands = f'(A{reg})+,(A{dn})+'
            elif om in (3,7):
                size = 2 if om == 3 else 4
                ea, _ = self.ea(mode,reg,2 if family in (8,12) else size)
                if family in (8,12):
                    mnemonic = ('DIV' if family == 8 else 'MUL')+('S' if om == 7 else 'U')+'.W'; operands = f'{ea},D{dn}'
                else:
                    mnemonic = {9:'SUBA',11:'CMPA',13:'ADDA'}[family]+'.'+('W' if size == 2 else 'L'); operands = f'{ea},A{dn}'
            else:
                size = (1,2,4)[om&3]; ea, _ = self.ea(mode,reg,size)
                mnemonic = {8:'OR',9:'SUB',11:'CMP' if om < 4 else 'EOR',12:'AND',13:'ADD'}[family]+'.'+{1:'B',2:'W',4:'L'}[size]
                operands = f'{ea},D{dn}' if om < 4 else f'D{dn},{ea}'
        elif op >> 12 == 14:
            code = (op >> 6)&3
            if code == 3:
                if op & 0x0800: raise Unsupported('68020 bitfield form')
                mnemonic = ('AS','LS','ROX','RO')[(op >> 9)&3]+('L' if op&0x100 else 'R')+'.W'
                operands, _ = self.ea(mode,reg,2,False)
            else:
                size = (1,2,4)[code]
                mnemonic = ('AS','LS','ROX','RO')[(op >> 3)&3]+('L' if op&0x100 else 'R')+'.'+{1:'B',2:'W',4:'L'}[size]
                count = f'D{(op >> 9)&7}' if op & 0x20 else f'#{((op >> 9)&7) or 8}'
                operands = f'{count},D{reg}'
        else: raise Unsupported(f'Opcode ${op:04X} not implemented')
        return {'address': self.start, 'size': self.pc-self.start,
                'bytes': self.data[self.start:self.pc].hex(), 'mnemonic': mnemonic,
                'operands': operands, 'flow': flow, 'target': target, 'references': self.references}


def walk(data, seeds, limit=5000, excluded=()):
    if limit <= 0: raise ValueError('Instruction limit must be positive')
    if any(len(pair) != 2 or pair[0] < 0 or pair[0] >= pair[1] or pair[1] > len(data) for pair in excluded):
        raise ValueError('Invalid excluded ROM range')
    queue = deque(seeds); decoded = {}; stops = []; edges = []; claimed = {}
    while queue and len(decoded) < limit:
        address = queue.popleft()
        if address in decoded: continue
        if address < 0x200 or address >= len(data) or address % 2:
            stops.append({'address': address, 'reason': 'Outside even ROM code address'}); continue
        if any(start <= address < end for start,end in excluded):
            stops.append({'address': address, 'reason': 'Explicit data exclusion'}); continue
        if address in claimed:
            stops.append({'address': address, 'reason': 'Target inside another instruction'}); continue
        try: instruction = Decoder(data,address).decode()
        except Unsupported as error:
            stops.append({'address': address, 'reason': str(error)}); continue
        if any(byte in claimed for byte in range(address,address+instruction['size'])):
            stops.append({'address': address, 'reason': 'Overlapping instruction'}); continue
        decoded[address] = instruction
        for byte in range(address,address+instruction['size']): claimed[byte] = address
        successors = []
        if instruction['flow'] in ('next','call','branch'): successors.append(('fallthrough',address+instruction['size']))
        if instruction['flow'] in ('call','branch','jump'):
            if instruction['target'] is None: stops.append({'address': address, 'reason': 'Unresolved indirect '+instruction['flow']})
            else: successors.append((instruction['flow'],instruction['target']))
        for kind,destination in successors:
            edges.append({'source':address,'destination':destination,'kind':kind}); queue.append(destination)
    return {'rom_sha256':hashlib.sha256(data).hexdigest(), 'decoder':'local limited MC68000 static decoder v0.1',
            'interpretation':'possible direct control flow; no execution, data-flow analysis or proof of reachability',
            'seeds':seeds, 'instructions': [decoded[a] for a in sorted(decoded)], 'edges':edges,
            'stops':stops, 'limit_reached':bool(queue), 'excluded':list(excluded)}


def listing(result):
    return '\n'.join(f"{i['address']:06X}  {i['bytes'].upper():<24} {i['mnemonic']:<9} {i['operands']}" for i in result['instructions'])+'\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rom'); parser.add_argument('--seed', type=lambda s:int(s,0), action='append', required=True)
    parser.add_argument('--limit',type=int,default=5000); parser.add_argument('--out',required=True)
    parser.add_argument('--exclude',action='append',default=[],help='start:end ROM data ranges, end exclusive')
    args = parser.parse_args()
    exclusions = [tuple(int(s,0) for s in value.split(':')) for value in args.exclude]
    result = walk(read_rom(args.rom),args.seed,args.limit,exclusions)
    output = Path(args.out); output.parent.mkdir(parents=True,exist_ok=True)
    output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    output.with_suffix('.asm').write_text(listing(result),encoding='utf-8')
    print(f"Decoded {len(result['instructions'])} instructions; {len(result['stops'])} stops; limit reached={result['limit_reached']}")


if __name__ == '__main__': main()
