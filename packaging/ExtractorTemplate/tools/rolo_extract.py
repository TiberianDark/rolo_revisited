"""Extract the code-traced font bank from the exact inspected Rolo ROM.

No emulator or third-party dependencies. Palette-index PNGs use a diagnostic
grayscale palette, not the original game palette.
"""
import argparse
import binascii
import hashlib
import json
import struct
import zlib
from pathlib import Path
from romtool import read_rom, extract

ROM_SHA256 = '9478d47cc1883df42f3714ea485aedd71b541274eb45a3aa7c49f4a3518305e9'


def startup_integrity(data):
    # Derived from $7FFB0: $1FFEC iterations over longwords, skipping $18C.
    if len(data) != 0x80000: raise ValueError('Expected 512 KiB Rolo ROM')
    values = struct.unpack('>' + 'I' * (0x7ffb0//4), data[:0x7ffb0])
    computed = (sum(values)-values[0x18c//4]) & 0xffffffff
    return {'range_start':0, 'range_end_exclusive':0x7ffb0,
            'excluded_start':0x18c, 'excluded_end_exclusive':0x190,
            'iterations':0x1ffec, 'computed':computed, 'expected':0x32ea75c6,
            'matches':computed == 0x32ea75c6}


def font_evidence(data):
    if hashlib.sha256(data).hexdigest() != ROM_SHA256:
        raise ValueError('ROM differs from inspected revision; offsets must be re-established')
    callsite = data[0x31b8:0x31d4]
    if (callsite[:2] != bytes.fromhex('203c') or callsite[6:8] != bytes.fromhex('223c')
        or callsite[12:14] != bytes.fromhex('243c') or callsite[18:20] != bytes.fromhex('263c')
        or callsite[24:26] != bytes.fromhex('6100')):
        raise ValueError('DMA callsite signature differs')
    source, destination, words, command = [struct.unpack_from('>I',callsite,o)[0] for o in (2,8,14,20)]
    loader = 0x31d2 + struct.unpack_from('>h',callsite,26)[0]
    if (source,destination,words,command,loader) != (0x27040,0xf680,0x480,0x40000000,0x2468):
        raise ValueError('DMA arguments differ from inspected values')
    blob = extract(data,source,words*2)
    return blob, {'schema_version':1, 'asset_id':'research.font-bank-27040',
                  'asset_id_status':'provisional research name', 'rom_sha256':ROM_SHA256,
                  'source_start':source, 'source_end_exclusive':source+len(blob),
                  'encoded_size':len(blob), 'decoded_size':len(blob), 'codec':'raw',
                  'asset_sha256':hashlib.sha256(blob).hexdigest(),
                  'callsite':0x31b8, 'call_instruction':0x31d0, 'loader':loader,
                  'loader_kind':'68000-to-VDP DMA, registers 19 through 23',
                  'dma_word_count':words, 'vram_destination':destination,
                  'first_vram_tile':destination//32, 'tile_count':len(blob)//32,
                  'tile_width':8, 'tile_height':8, 'bits_per_pixel':4,
                  'packing':'row-major, high nibble then low nibble',
                  'palette_association':None, 'preview_palette':'diagnostic grayscale indices 0..15',
                  'classification':'font and symbol tiles, visually inspected',
                  'confidence':{'source_length_and_destination':'code-traced', 'font_identity':'visual',
                                'original_colors':'not established', 'character_mapping':'not established'}}


def indexed_pixels(blob):
    if not blob or len(blob)%32: raise ValueError('Tile bytes must be a positive multiple of 32')
    count = len(blob)//32; width = 128; height = ((count+15)//16)*8
    pixels = bytearray(width*height)
    for tile in range(count):
        for byte_index,value in enumerate(blob[tile*32:(tile+1)*32]):
            x = (tile%16)*8+(byte_index%4)*2
            y = (tile//16)*8+byte_index//4
            pixels[y*width+x:y*width+x+2] = bytes((value>>4,value&15))
    return width,height,bytes(pixels)


def png_indexed(width,height,pixels,scale=1):
    if width <= 0 or height <= 0 or len(pixels) != width*height or not 1 <= scale <= 8:
        raise ValueError('Invalid image dimensions or scale')
    if any(p > 15 for p in pixels): raise ValueError('Only 4bpp palette indices are accepted')
    def chunk(kind,payload):
        return struct.pack('>I',len(payload))+kind+payload+struct.pack('>I',binascii.crc32(kind+payload)&0xffffffff)
    scanlines = bytearray()
    for y in range(height):
        row = b''.join(bytes([p])*scale for p in pixels[y*width:(y+1)*width])
        scanlines.extend((b'\0'+row)*scale)
    palette = bytes(channel for index in range(16) for channel in (index*17,)*3)
    return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width*scale,height*scale,8,3,0,0,0))
            +chunk(b'PLTE',palette)+chunk(b'IDAT',zlib.compress(bytes(scanlines)))+chunk(b'IEND',b''))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rom'); parser.add_argument('--out',required=True)
    args = parser.parse_args()
    try:
        data = read_rom(args.rom); blob,manifest = font_evidence(data)
        integrity = startup_integrity(data)
        if not integrity['matches']: raise ValueError('Game startup integrity check failed')
        output = Path(args.out); output.mkdir(parents=True,exist_ok=True)
        manifest['startup_integrity'] = integrity
        (output/'font.tiles').write_bytes(blob)
        width,height,pixels = indexed_pixels(blob)
        (output/'font.indexed.png').write_bytes(png_indexed(width,height,pixels))
        (output/'font.preview.png').write_bytes(png_indexed(width,height,pixels,4))
        (output/'font.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
        print(f'Extracted {len(blob)//32} raw font/symbol tiles; original palette and character mapping remain unknown')
    except (ValueError,OSError) as error: parser.exit(2,f'Error: {error}\n')


if __name__ == '__main__': main()
