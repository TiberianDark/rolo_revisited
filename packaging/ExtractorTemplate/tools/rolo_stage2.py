"""Extract traced initial-state graphics and classify its object templates.

Reconstructs selected tilemap layers as images, not a console or game emulator.
Uses target palettes; sprites, fades and animated state are not reconstructed.
"""
import argparse
import binascii
import hashlib
import json
import struct
import zlib
from pathlib import Path
from romtool import read_rom,extract
from rolo_extract import font_evidence,indexed_pixels
from rolo_codec import decode_backward_lz

ROOTS = (0x13ecc,0x13f76,0x13f54,0x13f32,0x13f10)
GROUP_WORDS = {0x32c8+i*0x200:i for i in range(6)}


def u32(data,address): return struct.unpack_from('>I',data,address)[0]


def classify_initial_templates(data):
    found={}
    for root in ROOTS:
        pointer=root; seen=set()
        while pointer:
            if pointer in seen or len(seen)>=48: raise ValueError('Invalid template chain')
            seen.add(pointer)
            raw=extract(data,pointer,34)
            word=struct.unpack_from('>H',raw,8)[0]
            if word not in GROUP_WORDS: raise ValueError(f'Unknown template group word at {pointer:#x}')
            next_pointer=u32(raw,0)
            entry=found.setdefault(pointer,{'source':pointer,'size':34,'next':next_pointer,
                                          'group_word':word,'native_group':GROUP_WORDS[word],
                                          'roots':[]})
            entry['roots'].append(root)
            pointer=next_pointer
    return {'schema_version':1,'scope':'templates reached from five initial-state allocation roots',
            'allocator':0x28b0,'allocator_header_copy':0x28ea,'definition_group_offset':8,
            'queue_builder_rom_source':0x3152,'queue_builder_ram_destination':0xffc3cc,
            'active_list_builder':0x29ee,'active_list':0xff98c8,'active_count':0xffc5b8,
            'object_pool':0xff998c,'object_stride':130,'max_active_objects':48,
            'queue_bases':[0xff6d7a+i*98 for i in range(6)],'queue_word_capacity':49,
            'supported_group_words':{f'0x{word:04X}':group for word,group in GROUP_WORDS.items()},
            'observed_group_words':sorted({x['group_word'] for x in found.values()}),
            'definitions':[found[p] for p in sorted(found)],
            'global_instruction_vocabulary_complete':False,
            'terminal_sentinel_note':'Final zero list pointer patches 0xFFFF from ROM address zero; that word is not executed'}


def target_palettes(data):
    # $16F8 sets selector -1; $66DE shifts its signed word by four and
    # indexes table $4B08A, producing row $4B07A.
    pointers=[u32(data,0x4b07a+i*4) for i in range(4)]
    raw=b''.join(extract(data,p,32) for p in pointers)
    words=struct.unpack('>'+'H'*64,raw)
    if any(word & ~0x0eee for word in words): raise ValueError('Invalid CRAM target colour')
    colors=[tuple(((word>>shift)&7)*255//7 for shift in (1,5,9)) for word in words]
    return raw,colors,{'selector':-1,'pointer_table_base':0x4b08a,'selected_row':0x4b07a,
                      'palette_sources':pointers,'selector_write':0x16f8,'palette_setup':0x66de,
                      'phase':'target colours for initial state, not intermediate fade values',
                      'rgb_conversion':'linear 3-bit components mapped to 0..255; analog output not modeled'}


def png_palette(width,height,pixels,colors,scale=1):
    if width<=0 or height<=0 or len(pixels)!=width*height or not 1<=scale<=4:
        raise ValueError('Invalid PNG dimensions')
    if not 1<=len(colors)<=256 or any(index>=len(colors) for index in pixels):
        raise ValueError('Invalid palette indices')
    def chunk(kind,payload):
        return struct.pack('>I',len(payload))+kind+payload+struct.pack('>I',binascii.crc32(kind+payload)&0xffffffff)
    rows=b''.join((b'\0'+b''.join(bytes((p,))*scale for p in pixels[y*width:(y+1)*width]))*scale for y in range(height))
    return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width*scale,height*scale,8,3,0,0,0))
            +chunk(b'PLTE',bytes(channel for color in colors for channel in color))
            +chunk(b'IDAT',zlib.compress(rows))+chunk(b'IEND',b''))


def map_pixels(vram,raw_map,width_cells,height_cells,attribute_base):
    if len(vram)!=0x10000 or width_cells<=0 or height_cells<=0 or len(raw_map)!=width_cells*height_cells*2:
        raise ValueError('Invalid tilemap or tile storage')
    width,height=width_cells*8,height_cells*8
    pixels=bytearray(width*height); opaque=bytearray(width*height)
    for cell,raw in enumerate(struct.unpack('>'+'H'*(len(raw_map)//2),raw_map)):
        # $6670 masks source to an 11-bit tile index, then adds D0.
        entry=((raw&0x7ff)+attribute_base)&0xffff
        start=(entry&0x7ff)*32; palette=((entry>>13)&3)*16
        for y in range(8):
            for x in range(8):
                tx=7-x if entry&0x800 else x; ty=7-y if entry&0x1000 else y
                byte=vram[start+ty*4+tx//2]
                index=byte>>4 if tx%2==0 else byte&15
                pos=((cell//width_cells)*8+y)*width+(cell%width_cells)*8+x
                pixels[pos]=palette+index; opaque[pos]=bool(index)
    return width,height,bytes(pixels),bytes(opaque)


def bmp_rgb(width,height,pixels,colors):
    if width<=0 or height<=0 or len(pixels)!=width*height or any(p>=len(colors) for p in pixels):
        raise ValueError('Invalid BMP dimensions or indices')
    stride=(width*3+3)&~3; rows=bytearray()
    for y in range(height-1,-1,-1):
        for p in pixels[y*width:(y+1)*width]: rows.extend(reversed(colors[p]))
        rows.extend(bytes(stride-width*3))
    header=b'BM'+struct.pack('<IHHI',54+len(rows),0,0,54)
    dib=struct.pack('<IiiHHIIiiII',40,width,height,1,24,0,len(rows),2835,2835,0,0)
    return header+dib+bytes(rows)


def reconstruct(data):
    font,_=font_evidence(data)
    templates=classify_initial_templates(data)
    palette_raw,colors,palette_evidence=target_palettes(data)
    vram=bytearray(0x10000); banks=[]; blobs={}
    for name,source,destination,callsite in (
        ('initial-scene-tiles',0x28a80,0x1540,0x652c),
        ('title-logo-tiles',0x44f1c,0x7300,0x6582)):
        decoded,evidence=decode_backward_lz(data,source)
        if len(decoded)%32 or destination+len(decoded)>0x10000: raise ValueError('Invalid decoded tile bank')
        vram[destination:destination+len(decoded)]=decoded
        blobs[name+'.tiles']=decoded
        evidence.update({'asset_id':'research.'+name,'callsite':callsite,'vram_destination':destination,
                         'tile_count':len(decoded)//32,'sha256':hashlib.sha256(decoded).hexdigest()})
        banks.append(evidence)
    if [x['decoded_size'] for x in banks] != [0x5dc0,0x1600]: raise ValueError('Inspected block sizes changed')
    layers=[]; layer_pixels={}
    for name,source,width,height,base,destination,callsite in (
        ('scene-background',0x2b680,40,14,0x00aa,0xe300,0x65b2),
        ('scene-frame',0x2bae0,40,14,0x80aa,0xc300,0x65c8),
        ('title-logo',0x4592c,40,6,0xe398,0xc000,0x6564)):
        raw=extract(data,source,width*height*2); blobs[name+'.tilemap']=raw
        image=map_pixels(vram,raw,width,height,base)
        layer_pixels[name]=image
        layers.append({'asset_id':'research.'+name,'source':source,'size':len(raw),
                       'width_cells':width,'height_cells':height,'loader':0x664c,'callsite':callsite,
                       'attribute_base':base,'vram_destination':destination,'sha256':hashlib.sha256(raw).hexdigest()})
    # Reconstruct only the proven 40x20 cells: logo rows 0..5, scene rows 6..19.
    # This is a cropped layer composition, not a full 320x224 title screenshot.
    composition=bytearray(320*160)
    for name,y,transparent in (('title-logo',0,False),('scene-background',48,False),('scene-frame',48,True)):
        width,height,pixels,mask=layer_pixels[name]
        for index,value in enumerate(pixels):
            if not transparent or mask[index]: composition[y*320+index]=value
    glyph_width,glyph_height,glyphs=indexed_pixels(font)
    font_colors=[colors[16+i] for i in range(16)]
    images={'title-layers.png':png_palette(320,160,composition,colors,2),
            'title-layers.bmp':bmp_rgb(320,160,composition,colors),
            'font.initial-state-palette.png':png_palette(glyph_width,glyph_height,glyphs,font_colors,4)}
    for name,(width,height,pixels,mask) in layer_pixels.items():
        images[name+'.png']=png_palette(width,height,pixels,colors,2)
    manifest={'schema_version':1,'rom_sha256':hashlib.sha256(data).hexdigest(),
              'banks':banks,'layers':layers,'palette':palette_evidence,
              'font_mapping':{'routine':0x702c,'ascii_first':0x20,'tile_base':0x7b4,
                              'tile_word':'((character - 0x20 + 0x7B4) OR text_attributes) & 0xFFFF',
                              'attribute_shadow':0xffc4b6,'palette_selection':'text attribute bits 13..14',
                              'preview_context':'initial-state target palette bank 1; not a universal font palette'},
              'composition':{'width':320,'height':160,'phase':'static target-palette layer reconstruction',
                             'scene_y':48,'sprites_included':False,'fades_included':False,'gameplay_ported':False,
                             'limitations':['Only selected tilemap layers; not a full frame','No sprites, animation, state logic or sound',
                                            'No original hardware frame comparison yet']}}
    return blobs,images,palette_raw,templates,manifest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rom'); parser.add_argument('--out',required=True)
    args=parser.parse_args()
    try:
        blobs,images,palette,templates,manifest=reconstruct(read_rom(args.rom))
        out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
        for name,blob in {**blobs,**images,'initial-target-palette.cram':palette}.items(): (out/name).write_bytes(blob)
        for name,result in (('stage2.manifest.json',manifest),('initial-object-groups.json',templates)):
            (out/name).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print('Decoded 750 scene tiles and 176 logo tiles; reconstructed three static title layers')
        print('Classified seven initial-state object templates; global vocabulary remains unverified')
    except (ValueError,OSError,struct.error) as error: parser.exit(2,f'Error: {error}\n')


if __name__ == '__main__': main()
