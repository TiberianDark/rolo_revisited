"""Extract traced sparse MAP layouts; diagnostic foreground images, no gameplay."""
import argparse, hashlib, json, struct
from pathlib import Path
from romtool import read_rom
from rolo_extract import font_evidence
from rolo_codec import decode_backward_lz
from rolo_stage2 import png_palette,bmp_rgb

def bmp_alpha(width,height,pixels,colors):
    if len(pixels)!=width*height: raise ValueError('Invalid alpha image dimensions')
    body=bytearray()
    for y in range(height-1,-1,-1):
        for index in pixels[y*width:(y+1)*width]:
            r,g,b=colors[index];body.extend((b,g,r,255 if index else 0))
    dib=struct.pack('<IiiHHIIiiII',108,width,height,1,32,3,len(body),0,0,0,0)
    dib+=struct.pack('<IIIII',0xff0000,0xff00,0xff,0xff000000,0x73524742)+bytes(48)
    return struct.pack('<2sIHHI',b'BM',122+len(body),0,0,122)+dib+body

def word(data, offset):
    if offset < 0 or offset + 2 > len(data): raise ValueError('Word outside data')
    return struct.unpack_from('>H', data, offset)[0]

def long(data, offset):
    if offset < 0 or offset + 4 > len(data): raise ValueError('Pointer outside data')
    return struct.unpack_from('>I', data, offset)[0]

def parse_map(data):
    if len(data) < 10 or data[:3] != b'MAP': raise ValueError('Invalid MAP header')
    width, height = word(data, 4), word(data, 6)
    # Dimensions are ROM words; image allocation has a separate pixel budget.
    # Three supplied levels are wider than 8192 pixels.
    if not width or not height or height % 16:
        raise ValueError('Unsupported map dimensions')
    rows = height // 16
    table_end = 8 + (rows + 1) * 2
    offsets = [word(data, 8 + i * 2) for i in range(rows + 1)]
    if offsets[0] < table_end or offsets[-1] > len(data): raise ValueError('Invalid row bounds')
    records = []
    for y in range(rows):
        start, end = offsets[y:y+2]
        if end < start or (end-start) % 4: raise ValueError('Invalid row interval')
        for p in range(start, end, 4):
            kind, x = word(data, p), word(data, p+2)
            records.append({'offset':p, 'type':kind, 'x':x, 'y':y*16,
                            'visual':kind < 0x400})
    return {'width':width,'height':height,'bank':data[3],'records':records,
            'row_offsets':offsets,'trailing_bytes':len(data)-offsets[-1]}

def initial_selection(rom, x=280, y=472):
    row = (y >> 6) - 4
    group, subrow = row & ~3, row & 3
    entry = 0x4baaa + group * 2
    pointer, stride, xbase = long(rom,entry), word(rom,entry+4), word(rom,entry+6)
    return rom[pointer + subrow*stride + (x >> 6) - xbase]

def level_inventory(rom):
    entries=[]
    # 80 camera-mode bytes at $4AEDA..$4AF2A correspond to selectors 0..79.
    for selector in range(1,80):
        packed=long(rom,0x4ab1a+selector*8);source=packed&0xffffff
        data=rom[source:source+4096] if rom[source:source+3]==b'MAP' else decode_backward_lz(rom,source)[0]
        if data[:3]!=b'MAP': raise ValueError('Invalid level inventory entry')
        entries.append({'selector':selector,'source':source,'spawn_selector':packed>>24,
                        'bank':data[3],'width':word(data,4),'height':word(data,6)})
    nodes=[]
    for group in range(3):
        entry=0x4baaa+group*8;pointer=long(rom,entry);stride=word(rom,entry+4)
        for index in range(stride*4):
            selector=rom[pointer+index]
            if selector: nodes.append({'group':group,'row':index//stride,'column':index%stride,'selector':selector})
    return {'rom_sha256':hashlib.sha256(rom).hexdigest(),'world_selector':0,
            'level_selector_slots':len(entries),'distinct_foreground_sources':len({r['source'] for r in entries}),
            'nonzero_world_nodes':len(nodes),'entries':entries,'world_nodes':nodes,
            'scope':'ROM catalogue: selector slots include shared layouts and special entry variants; not a playable level coverage claim'}

def render_foreground(rom, layout, tiles, quad_source, macro_source, viewport=None):
    origin_x,origin_y=0,0
    width,height=layout['width'],layout['height']
    if viewport is not None:
        origin_x,origin_y,width,height=viewport
        if origin_x<0 or origin_y<0 or width<=0 or height<=0 or origin_x+width>layout['width'] or origin_y+height>layout['height']:
            raise ValueError('Viewport outside map')
    if width*height > 16_777_216: raise ValueError('Image exceeds pixel budget')
    pixels=bytearray(width*height)
    cache={}
    def metatile(value):
        if value in cache: return cache[value]
        index=value&0x1ff
        source=0x6b452+index*8 if index<28 else quad_source+(index-28)*8
        output=bytearray(256)
        for cell in range(4):
            entry=word(rom,source+cell*2)
            pattern=entry&0x7ff
            # Common quads receive +$594 in $3DE2; their patterns are raw at $53DC2.
            raw=rom[0x53dc2+pattern*32:0x53dc2+(pattern+1)*32] if index<28 else tiles[pattern*32:(pattern+1)*32]
            # Level initialization $3CBC/$26C8 clears VRAM $B2A0..$B31F
            # after the common upload at $B280: common patterns 1..4.
            # Apply this to common patterns only, never bank-local tiles.
            if index<28 and 1<=pattern<=4: raw=bytes(32)
            if len(raw)!=32: raise ValueError('Pattern outside graphics bank')
            for py in range(8):
                for px in range(8):
                    sx=7-px if entry&0x800 else px; sy=7-py if entry&0x1000 else py
                    v=(raw[sy*4+sx//2] >> (0 if sx&1 else 4))&15
                    # $74AC/$74B2 write two longwords to successive VDP rows:
                    # top-left, top-right, bottom-left, bottom-right.
                    xx=(cell%2)*8+px; yy=(cell//2)*8+py
                    if value&0x800: xx=15-xx
                    if value&0x1000: yy=15-yy
                    output[yy*16+xx]=v+((entry>>13)&3)*16 if v else 0
        cache[value]=output
        return output
    for record in layout['records']:
        if not record['visual']: continue
        kind=record['type']; macro=macro_source+word(rom,macro_source+6+(kind&0x7f)*2)
        mw,mh=rom[macro:macro+2]
        if not mw or not mh or mw*mh>4096: raise ValueError('Invalid macro dimensions')
        flip=bool(kind&0xff00)
        for row in range(mh):
            for col in range(mw):
                value=word(rom,macro+2+(row*mw+col)*2)
                if not value: continue
                if flip: value^=0x1000
                block=metatile(value)
                x=record['x']+col*16-origin_x; y=record['y']+(mh-1-row if flip else row)*16-origin_y
                if x+16<=0 or y+16<=0 or x>=width or y>=height: continue
                for py in range(16):
                    if not 0<=y+py<height: continue
                    for px in range(16):
                        if 0<=x+px<width: pixels[(y+py)*width+x+px]=block[py*16+px]
    return pixels

def extract_map(rom, selector, out):
    if not 0<=selector<=127: raise ValueError('Selector outside investigated table range')
    packed=long(rom,0x4ab1a+selector*8); source=packed&0xffffff
    data=rom[source:source+4096] if rom[source:source+3]==b'MAP' else decode_backward_lz(rom,source)[0]
    layout=parse_map(data); bank=layout['bank']
    if bank>=17: raise ValueError('Bank outside traced tables')
    pointers={name:long(rom,table+bank*4) for name,table in
              [('graphics',0x4af2a),('quads',0x4af6e),('macros',0x4afb2),('collision',0x4aff6)]}
    tiles,codec=decode_backward_lz(rom,pointers['graphics'])
    palettes=[long(rom,0x4b08a+selector*16+i*4) for i in range(4)]
    palette=b''.join(rom[p:p+32] for p in palettes)
    colors=[tuple(((v>>s)&7)*255//7 for s in (1,5,9)) for v in struct.unpack('>64H',palette)]
    pixels=render_foreground(rom,layout,tiles,pointers['quads'],pointers['macros'])
    out.mkdir(parents=True,exist_ok=True)
    (out/'foreground.png').write_bytes(png_palette(layout['width'],layout['height'],pixels,colors))
    # Uncompressed 24-bit BMP is readable by SDL3 without an image extension.
    stride=(layout['width']*3+3)&~3
    body=bytearray()
    for y in range(layout['height']-1,-1,-1):
        for index in pixels[y*layout['width']:(y+1)*layout['width']]: body.extend(reversed(colors[index]))
        body.extend(bytes(stride-layout['width']*3))
    header=struct.pack('<2sIHHI',b'BM',54+len(body),0,0,54)
    header+=struct.pack('<IiiHHIIiiII',40,layout['width'],layout['height'],1,24,0,len(body),0,0,0,0)
    (out/'foreground.bmp').write_bytes(header+body)
    background=None
    if selector in (1,2):
        background_source=long(rom,0x4ab1a+selector*8+4)&0xffffff
        background_data,background_codec=decode_backward_lz(rom,background_source)
        background_layout=parse_map(background_data)
        background_pixels=render_foreground(rom,background_layout,tiles,pointers['quads'],pointers['macros'])
        (out/'background.map').write_bytes(background_data)
        (out/'background.png').write_bytes(png_palette(background_layout['width'],background_layout['height'],background_pixels,colors))
        (out/'background.bmp').write_bytes(bmp_rgb(background_layout['width'],background_layout['height'],background_pixels,colors))
        (out/'foreground-alpha.bmp').write_bytes(bmp_alpha(layout['width'],layout['height'],pixels,colors))
        background={'source':background_source,'codec':background_codec,**background_layout,
                    'camera_mode':rom[0x4aeda+selector],
                    'scroll':'mode 3 at $4F36: half horizontal camera, fixed vertical zero; viewer wraps the 512-pixel scene horizontally'}
    (out/'layout.map').write_bytes(data); (out/'graphics.tiles').write_bytes(tiles)
    (out/'target-palette.cram').write_bytes(palette)
    # F2FE is selected by $38C2. Preserve a bounded candidate table window;
    # its full extent and collision meanings still need independent tracing.
    (out/'collision-unclassified.bin').write_bytes(rom[pointers['collision']:pointers['collision']+512])
    manifest={'selector':selector,'spawn_selector':packed>>24,'source':source,
              'background_table_word':long(rom,0x4ab1a+selector*8+4),
              'rom_sha256':hashlib.sha256(rom).hexdigest(),'banks':pointers,'graphics_codec':codec,
              'palette_sources':palettes,**layout,
              'background':background,
              'scope':'Static map layers; first-level background scroll translated; priority, actors, collision behaviour and player camera not ported'}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rom');parser.add_argument('--out',required=True)
    parser.add_argument('--selectors',type=int,nargs='+',help='Explicit original MAP selectors to extract')
    args=parser.parse_args();rom=read_rom(args.rom);font_evidence(rom)
    Path(args.out).mkdir(parents=True,exist_ok=True)
    (Path(args.out)/'level-inventory.json').write_text(json.dumps(level_inventory(rom),indent=2)+'\n')
    selection=initial_selection(rom)
    for selector in sorted(set(args.selectors) if args.selectors else {0,1,selection}):
        result=extract_map(rom,selector,Path(args.out)/f'map-{selector:02d}')
        print(f"Map {selector}: {result['width']} x {result['height']}, {len(result['records'])} records")

if __name__=='__main__': main()
