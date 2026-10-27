"""Compare native camera CSV with the ROM arithmetic specification and rendered artwork."""
import argparse,csv,hashlib,json,re,struct
from pathlib import Path
from PIL import Image,ImageChops
from export_camera import ROM_SHA,initialize,reference

def verify(rom,project):
    b=rom.read_bytes();assert hashlib.sha256(b).hexdigest()==ROM_SHA
    sine=struct.unpack_from('>512h',b,0x1582a);mode=b[0x4aedb]
    directory=project/'docs/player-captures'
    rows=list(csv.DictReader((directory/'player.csv').open()))
    c=[0]*7;i=[184,752,0,1984,1440,0,0,mode,0,0]
    c=initialize(c,i,sine)[:7];c=initialize(c,i,sine)[:7]
    previous_x=184
    fields=['camera_x','camera_y','camera_left','camera_right','camera_top','camera_bottom','background_x','background_y']
    for row in rows:
        x=int(row['x'])//65536;y=int(row['y'])//65536
        out=reference(c,[x,y,previous_x,1984,1440,0,0,mode,0,int(row['tick'])],sine)
        expected=out[:6]+out[9:11]
        assert [int(row[k]) for k in fields]==expected,(row['tick'],expected)
        c=out[:7];previous_x=x
    pack=(project/'bin/player-assets.rla').read_bytes();at=12;graphics={}
    for _ in range(struct.unpack_from('<I',pack,8)[0]):
        kind,source,palette,w,h,size=struct.unpack_from('<6I',pack,at);at+=24
        graphics[source,w,h]=Image.frombytes('RGBA',(w,h),pack[at:at+size]);at+=size
    text=(project/'src/core/player_animation_data.hpp').read_text()
    frames=[[int(v,0) for v in match.groups()] for match in re.finditer(r'Frame\{(0x[0-9a-f]+),(0x[0-9a-f]+),(0x[0-9a-f]+),(-?\d+),(-?\d+),(\d+),(\d+),(\d+)\}',text)]
    assets=project/'assets/extracted/maps/map-01'
    foreground=Image.open(assets/'foreground-alpha.bmp').convert('RGBA')
    background=Image.open(assets/'background.bmp').convert('RGBA')
    captures=[]
    for tick in [20,65,120,200,300]:
        row=rows[tick-1];cx=int(row['camera_x']);cy=int(row['camera_y'])
        image=Image.new('RGBA',(320,224));offset=int(row['background_x'])%512
        for x in range(320):image.paste(background.crop(((offset+x)%512,0,(offset+x)%512+1,224)),(x,0))
        image=Image.alpha_composite(image,foreground.crop((cx,cy,cx+320,cy+224)))
        for key in ['body_frame','head_frame']:
            index=int(row[key])
            if index<0:continue
            _,left,right,ox,oy,w,h,size=frames[index]
            facing=int(row['facing_left']);selected=right if facing else left
            source=selected or (left if facing else right)
            sprite=graphics[source,w,h]
            if not selected:sprite=sprite.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            px=int(row['x'])//65536+(-ox if facing else ox)-w//2-cx
            py=int(row['y'])//65536+oy-h-cy
            image.alpha_composite(sprite,(px,py))
        expected=image.convert('RGB').resize((960,672),Image.Resampling.NEAREST)
        actual=Image.open(directory/f'player-{tick}.bmp').convert('RGB').crop((0,0,960,672))
        assert ImageChops.difference(expected,actual).getbbox() is None,('pixels',tick)
        captures.append(tick)
    report={'level_camera_trace_rows_matched':len(rows),'artwork_captures_pixel_matched':captures,
            'normal_camera_fixtures':1200,'scripted_camera_fixtures':400,'background_modes':10,
            'viewport':[320,224],'rom_arithmetic_reference':True,'original_game_recording_comparison':False,
            'all_game_camera_states_verified':False,'full_gameplay_ported':False}
    (project/'docs/verification.camera.json').write_text(json.dumps(report,indent=2)+'\n')
    print(len(rows),'camera updates and',len(captures),'full-size artwork captures match the offline reference')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('rom',type=Path);parser.add_argument('--project',type=Path,default=Path('.'));args=parser.parse_args();verify(args.rom,args.project)
