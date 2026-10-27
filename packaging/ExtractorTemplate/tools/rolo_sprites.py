"""Extract statically reachable initial sprite frames; does not execute game logic."""
import argparse, hashlib, json, struct
from pathlib import Path
from romtool import read_rom, extract
from rolo_extract import font_evidence
from rolo_stage2 import target_palettes, png_palette

CASES=((0x13ecc,0),(0x13eee,0),(0x13f76,0),(0x13f54,0),(0x13f32,0x38),(0x13f10,0x34),(0x144e8,0))

def sequence_frames(data,start):
    """Bounded static union through known controls, without choosing conditions."""
    pending=[start]; seen=set(); frames=[]; controls=[]
    while pending:
        p=pending.pop()
        if p in seen: continue
        if len(seen)>=128: raise ValueError('Sequence traversal limit')
        seen.add(p)
        word=struct.unpack('>i',extract(data,p,4))[0]
        if word>0:
            if word>>24: raise ValueError('Tagged frame requires separate tracing')
            frames.append(word); pending.append(p+4)
        else:
            command=-(word>>16); parameter=word&65535
            controls.append({'address':p,'command':command,'parameter':parameter})
            if command==0: pending.append(int.from_bytes(extract(data,p+4,4),'big'))
            elif command in (4,8,60,68,80): pass # repeat, deactivate, hold, return, or selector change
            elif command in (12,40,52,56,72,96,104,108,112,116): pending.append(p+4)
            elif command in (44,48,64,76): pending.extend((int.from_bytes(extract(data,p+4,4),'big'),p+8))
            elif command in (16,20,24,28,32,36,84,88): pending.extend((p-4,p+4))
            elif command in (92,100): pending.append(p+8) # next longword is a spawned definition, not a frame
            else: raise ValueError(f'Untraced animation control {command} at {p:#x}')
    return sorted(set(frames)),controls

def frame_record(data,address):
    left,right,x,y,w,h,size=struct.unpack('>IIhhHHH',extract(data,address,18))
    if not w or not h or w%8 or h%8 or w*h//2!=size or size>0x4000:
        raise ValueError('Invalid frame geometry')
    return {'descriptor':address,'graphics':[left,right],'offset_x':x,'offset_y':y,'width':w,'height':h,'byte_count':size}

def sprite_pixels(raw,width,height):
    """Follow $3396..$343E: 32px chunks, tiles down columns within chunks."""
    if width<=0 or height<=0 or width%8 or height%8 or len(raw)!=width*height//2:
        raise ValueError('Invalid sprite geometry')
    pixels=bytearray(width*height); tile=0
    for cy in range(0,height,32):
        for cx in range(0,width,32):
            for tx in range(min(32,width-cx)//8):
                for ty in range(min(32,height-cy)//8):
                    for y in range(8):
                        for x in range(8):
                            value=raw[tile*32+y*4+x//2]
                            pixels[(cy+ty*8+y)*width+cx+tx*8+x]=value>>4 if x%2==0 else value&15
                    tile+=1
    return bytes(pixels)

def extract_sprites(data,out):
    font_evidence(data); out.mkdir(parents=True,exist_ok=True)
    _,colors,_=target_palettes(data); cases=[]; sheet=bytearray(512*320); cell=0
    for definition,selector in CASES:
        table=int.from_bytes(extract(data,definition+18,4),'big')
        entry=extract(data,table+selector,4); start=int.from_bytes(entry[1:],'big')
        descriptors,controls=sequence_frames(data,start); frames=[]
        bank=(int.from_bytes(extract(data,definition+6,2),'big')>>13)&3
        for descriptor in descriptors:
            frame=frame_record(data,descriptor); variants=[]
            for direction,source in enumerate(frame['graphics']):
                if not source: continue
                raw=extract(data,source,frame['byte_count']); pixels=sprite_pixels(raw,frame['width'],frame['height'])
                name=f'sprite-{definition:05x}-{descriptor:05x}-{direction}'
                (out/(name+'.tiles')).write_bytes(raw)
                (out/(name+'.png')).write_bytes(png_palette(frame['width'],frame['height'],pixels,colors[bank*16:bank*16+16],4))
                variants.append({'source':source,'file':name,'sha256':hashlib.sha256(raw).hexdigest()})
                if cell>=40: raise ValueError('Contact sheet capacity exceeded')
                ox=(cell%8)*64; oy=(cell//8)*64
                for y in range(frame['height']):
                    for x in range(frame['width']):
                        sheet[(oy+y)*512+ox+x]=bank*16+pixels[y*frame['width']+x] if pixels[y*frame['width']+x] else 0
                cell+=1
            frame['variants']=variants;frames.append(frame)
        cases.append({'definition':definition,'selector':selector,'table':table,'sequence':start,'delay_byte':entry[0],
                      'frame_period_note':'counter reload is delay_byte; ordinary frame change takes delay_byte + 1 calls; controls can alter timing',
                      'palette_bank':bank,'frames':frames,'controls':controls})
    (out/'initial-sprite-sheet.png').write_bytes(png_palette(512,320,sheet,colors,2))
    result={'rom_sha256':hashlib.sha256(data).hexdigest(),'animation_routine':0xfcd4,'descriptor_reader':0xfda8,
            'graphics_selector':0xfdd8,'sprite_builder':0x328c,'cases':cases,'sheet_variants':cell,
            'scope':'static reachable frame union for seven definitions; target palettes, no timeline or title composition',
            'gameplay_ported':False,'hardware_frame_comparison':False}
    (out/'stage3.manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('rom');parser.add_argument('--out',required=True)
    args=parser.parse_args();result=extract_sprites(read_rom(args.rom),Path(args.out));print('Extracted',result['sheet_variants'],'sprite variants')



