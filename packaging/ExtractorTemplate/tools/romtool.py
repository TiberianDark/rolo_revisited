"""Read-only Mega Drive ROM analysis and explicitly bounded extraction. Python 3.10+."""
import argparse
import hashlib
import json
import math
import re
import struct
from collections import Counter
from pathlib import Path


def number(value):
    return int(value, 0)


def read_rom(path):
    data = Path(path).read_bytes()
    if len(data) < 0x200 or len(data) % 2:
        raise ValueError('ROM must be at least 512 bytes and have an even byte count')
    if data[0x100:0x104] != b'SEGA':
        raise ValueError('Expected raw big-endian ROM; interleaved/copier formats are not supported')
    return data


def analyze(data):
    u32 = lambda offset: struct.unpack_from('>I', data, offset)[0]
    text = lambda offset, size: data[offset:offset + size].decode('ascii', errors='replace').rstrip(' \x00')
    checksum = sum(struct.unpack('>' + 'H' * ((len(data)-512)//2), data[512:])) & 0xffff
    stored = struct.unpack_from('>H', data, 0x18e)[0]
    vectors = [{'index': i, 'offset': f'0x{i*4:06X}', 'value': f'0x{u32(i*4):08X}',
                'bus_address': f'0x{u32(i*4) & 0xffffff:06X}',
                'in_rom_even': (u32(i*4) & 0xffffff) < len(data) and u32(i*4) % 2 == 0} for i in range(64)]
    blocks = []
    for start in range(0x200, len(data), 0x1000):
        block = data[start:min(start+0x1000, len(data))]
        counts = Counter(block)
        entropy = -sum((n/len(block))*math.log2(n/len(block)) for n in counts.values())
        blocks.append({'start': start, 'end_exclusive': start+len(block), 'entropy': round(entropy, 3),
                       'zero_bytes': counts[0], 'ff_bytes': counts[255]})
    # Opcode-shaped matches only: scanning data does not establish executable code.
    references = []
    for offset in range(0x200, len(data)-5, 2):
        opcode = data[offset:offset+2]
        if opcode in (b'\x4e\xb9', b'\x4e\xf9'):
            target = u32(offset+2)
            if target < len(data) and target % 2 == 0:
                references.append({'offset': offset, 'kind': 'JSR abs.l' if opcode == b'\x4e\xb9' else 'JMP abs.l', 'target': target})
    strings = [{'offset': m.start(), 'text': m.group().decode('ascii')} for m in re.finditer(rb'[ -~]{8,}', data)]
    warnings = []
    if checksum != stored: warnings.append('Header checksum mismatch')
    if u32(0x1a0) != 0 or u32(0x1a4)+1 != len(data): warnings.append('Declared ROM range differs from file')
    if not vectors[1]['in_rom_even']: warnings.append('Reset vector is not an even ROM address')
    return {'size_bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
            'sha1': hashlib.sha1(data).hexdigest(),
            'header': {'console': text(0x100,16), 'copyright': text(0x110,16), 'domestic_title': text(0x120,48),
                       'overseas_title': text(0x150,48), 'product': text(0x180,14), 'io': text(0x190,16),
                       'region': text(0x1f0,16), 'rom_start': u32(0x1a0), 'rom_end': u32(0x1a4),
                       'ram_start': u32(0x1a8), 'ram_end': u32(0x1ac), 'sram_raw_hex': data[0x1b0:0x1bc].hex()},
            'checksum': {'stored': stored, 'computed': checksum, 'matches': stored == checksum},
            'vectors': vectors, 'warnings': warnings, 'blocks': blocks,
            'unverified_absolute_control_flow_candidates': references, 'ascii_strings': strings}


def extract(data, start, size):
    if start < 0 or size <= 0 or start+size > len(data):
        raise ValueError('Extraction range must be nonempty and entirely inside ROM')
    return data[start:start+size]


def tiles_ppm(data):
    if not data or len(data) % 32:
        raise ValueError('Raw 4bpp tiles require a positive multiple of 32 bytes')
    count = len(data)//32
    width, height = 16*8, ((count+15)//16)*8
    pixels = bytearray(width*height*3)
    for tile in range(count):
        for index, value in enumerate(data[tile*32:(tile+1)*32]):
            for half, shade in enumerate((value >> 4, value & 15)):
                x = (tile % 16)*8 + (index % 4)*2 + half
                y = (tile//16)*8 + index//4
                p = (y*width+x)*3
                pixels[p:p+3] = bytes([shade*17]*3)
    return f'P6\n{width} {height}\n255\n'.encode()+pixels


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    a = sub.add_parser('analyze'); a.add_argument('rom'); a.add_argument('--out', required=True)
    for command in ('extract', 'tiles'):
        a = sub.add_parser(command); a.add_argument('rom'); a.add_argument('--start', type=number, required=True)
        a.add_argument('--size', type=number, required=True); a.add_argument('--out', required=True)
    args = parser.parse_args()
    try:
        data = read_rom(args.rom)
        output = Path(args.out); output.parent.mkdir(parents=True, exist_ok=True)
        if args.command == 'analyze':
            result = analyze(data)
            output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
            print(json.dumps({k: result[k] for k in ('size_bytes','sha256','header','checksum','warnings')}, indent=2))
            return 1 if result['warnings'] else 0
        blob = extract(data, args.start, args.size)
        output.write_bytes(tiles_ppm(blob) if args.command == 'tiles' else blob)
        print(f'Wrote {output} from 0x{args.start:X}..0x{args.start+args.size:X} (end exclusive)')
        return 0
    except (ValueError, OSError) as error:
        parser.exit(2, f'Error: {error}\n')


if __name__ == '__main__':
    raise SystemExit(main())
