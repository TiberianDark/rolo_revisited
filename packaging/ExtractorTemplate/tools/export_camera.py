"""Extract camera data and build offline arithmetic-reference fixtures; no CPU execution."""
import argparse,hashlib,json,random,struct
from pathlib import Path

ROM_SHA='9478d47cc1883df42f3714ea485aedd71b541274eb45a3aa7c49f4a3518305e9'
def word(v):return v&65535
def signed(v):return (v&32767)-(v&32768)

def layers(c,i,sine):
    x,y,left,right,top,bottom,phase=c
    px,py,oldx,width,height,freeze1,freeze2,mode,shift,tick=i
    fx,fy=x,y;flag=scroll=0;rows=[0]*32
    bx,by=x,y
    if mode in (0,1):bx=x>>1;by=y>>1;flag=255 if mode else 0
    elif mode==3:bx=x>>1;by=0;flag=255
    elif mode==4:flag=255
    elif mode==5:
        index=(-phase)&511
        bx=word((sine[(index+128)&511]*400)//65536+400)
        by=word((sine[index]*400)//65536+400)
        phase=word(phase+1);flag=255
    elif mode==6:fx=word(x+shift)
    elif mode==7:
        half=signed(x)>>1
        rows=list(map(word,[0]*12+[half>>3]+[half>>2]*2+[half>>1]*3+[half]*14))
        bx=by=0;flag=255;scroll=2
    elif mode==8:
        half=signed(x)>>1
        rows=list(map(word,[tick]*2+[signed(tick)>>1]*2+[half>>2]*12+[half]*16))
        bx=tick;by=0;flag=255;scroll=2
    elif mode==9:
        half=signed(x)>>1;quarter=half>>1
        rows=list(map(word,[quarter]*8+[half]*24));bx=word(quarter);by=0;flag=255;scroll=2
    return [x,y,left,right,top,bottom,phase,fx,fy,bx,by,flag,scroll]+rows

def reference(c,i,sine):
    # Label-specific arithmetic specification of $4D54..$4EA4, not a 68000 interpreter.
    x,y,left,right,top,bottom,phase=c
    px,py,oldx,width,height,f1,f2,mode,shift,tick=i
    if not(f1 or f2):
        d2=px;d1=word(px-oldx);d6=d1
        if signed(d6)<0:d6=word(-d6)
        d6=word(d6*2)
        if d6>15:d6=15
        d0=word(d2-x)
        if signed(d1)<0:
            if d0<=left:label=0x4db8
            elif d0>=120:label=0x4db4
            else:label=0x4da2
        else:
            if d0>=right:label=0x4e0a
            elif d0<200:label=0x4e06
            else:label=0x4df4
        if label==0x4da2:
            left=word(left+d6);right=word(right+d6);d2=word(d2-120)
        elif label==0x4db8:
            left=word(left+d6);right=word(right+d6)
            if right>320:left,right=200,320
            d2=word(d2-left)
        elif label==0x4df4:
            left=word(left-d6);right=word(right-d6);d2=word(d2-200)
        elif label==0x4e0a:
            right=word(right-d6);left=word(left-d6)
            if signed(left)<0:left,right=0,120
            d2=word(d2-right)
        else:d6=0
        if signed(d2)<0:d2=0
        if d2>word(width-320):d2=word(width-320)
        if d6:
            d2=word(d2-x)
            if signed(d2)<0:
                d6=word(-d6)
                if d2>d6:d6=d2
            elif d2<d6:d6=d2
            x=word(x+d6)
        if signed(py)<signed(word(y+top)):
            d0=word(py-top);y=d0 if signed(d0)>=0 else 0
        elif signed(py)>signed(word(y+bottom)):
            d0=word(py-bottom);limit=word(height-224)
            y=d0 if signed(d0)<=signed(limit) else limit
    return layers([x,y,left,right,top,bottom,phase],i,sine)

def initialize(c,i,sine):
    px,py,_,width,height,*_=i
    x=word(px-176)
    if signed(x)<0:x=0
    if signed(x)>signed(word(width-320)):x=word(width-320)
    y=word(py-160)
    if signed(y)<0:y=0
    elif signed(y)>signed(word(height-224)):y=word(height-224)
    state=reference([x,y,*c[2:]],i,sine)
    left=word(px-state[0]-60)
    if signed(left)<0:left=0
    state[2:6]=[left,word(left+120),134,154]
    return state

def export(rom,project):
    b=rom.read_bytes();assert hashlib.sha256(b).hexdigest()==ROM_SHA,'Unexpected ROM'
    sine=list(struct.unpack_from('>512h',b,0x1582a));modes=list(b[0x4aeda:0x4af2a]);assert max(modes)==9
    # Pin the directly consulted code ranges, detecting accidental input changes.
    code_hash=hashlib.sha256(b[0x4cb8:0x5060]).hexdigest()
    header='#pragma once\n#include <array>\n#include <cstdint>\nnamespace rolo::camera_data {\n'
    header+='inline constexpr std::array<std::int16_t,512> sine{'+','.join(map(str,sine))+'};\n'
    header+='inline constexpr std::array<std::uint8_t,80> modes{'+','.join(map(str,modes))+'};\n}\n'
    (project/'src/core/camera_data.hpp').write_text(header)
    rng=random.Random(0x4d54);cases=[]
    for n in range(1200):
        width=rng.choice([320,1280,1984,8192,16000]);height=rng.choice([224,1280,1440,16000])
        px=rng.randrange(width);py=rng.randrange(height)
        c=[rng.randrange(width-319),rng.randrange(height-223),rng.randrange(201),0,rng.choice([0,134]),rng.choice([0,154]),rng.randrange(65536)]
        c[3]=c[2]+120
        i=[px,py,word(px+rng.randrange(-32,33)),width,height,n%19==0,n%23==0,n%10,rng.randrange(65536),rng.randrange(65536)]
        init=n%7==0;out=(initialize if init else reference)(c,i,sine)
        cases.append((init,c,i,out))
    fixture='#pragma once\n#include <array>\n#include <cstdint>\nstruct CameraFixture {bool initialize;std::array<std::uint16_t,7> before;std::array<std::uint16_t,10> input;std::array<std::uint16_t,45> expected;};\n'
    fixture+='inline constexpr std::array<CameraFixture,'+str(len(cases))+'> camera_fixtures{{\n'
    for init,c,i,out in cases:
        fixture+='CameraFixture{'+str(init).lower()+',{'+','.join(map(str,c))+'},{'+','.join(str(int(v)) for v in i)+'},{'+','.join(map(str,out))+'}},\n'
    fixture+='}};\n';(project/'tests/camera_reference.hpp').write_text(fixture)
    scripted=[]
    for n in range(400):
        # World-map bounds are 1280x1280. Include alternate targets and low-word carry.
        c=[rng.randrange(224,737),rng.randrange(224,833),rng.randrange(65536),rng.randrange(65536)]
        i=[rng.randrange(1280),rng.randrange(1280),rng.randrange(1280),rng.randrange(1280),1280,1280,n%2]
        px,py,ax,ay,width,height,alternate=i
        if alternate:px,py=ax,ay
        tx=min(max(px-160,224),width-544);ty=min(max(py-112,224),height-448)
        dx,dy=tx-c[0],ty-c[1];major=max(abs(dx),abs(dy))
        if major:
            vx=(abs(dx)*65536)//major;vy=(abs(dy)*65536)//major
            if dx<0:vx=-vx
            if dy<0:vy=-vy
        else:vx=vy=0
        shift=next((k for k,limit in enumerate([10,20,40,80]) if major<=limit),3)
        x=((c[0]<<16)+c[2]+vx*(1<<shift))&0xffffffff
        y=((c[1]<<16)+c[3]+vy*(1<<shift))&0xffffffff
        scripted.append((c,i,[x>>16,y>>16,x&65535,y&65535]))
    fixture='#pragma once\n#include <array>\n#include <cstdint>\nstruct ScriptedCameraFixture {std::array<std::uint16_t,4> before;std::array<std::uint16_t,7> input;std::array<std::uint16_t,4> expected;};\n'
    fixture+='inline constexpr std::array<ScriptedCameraFixture,400> scripted_camera_fixtures{{\n'
    for c,i,out in scripted:fixture+='ScriptedCameraFixture{{'+','.join(map(str,c))+'},{'+','.join(map(str,i))+'},{'+','.join(map(str,out))+'}},\n'
    fixture+='}};\n';(project/'tests/scripted_camera_reference.hpp').write_text(fixture)
    (project/'docs/camera-export.json').write_text(json.dumps({'rom_sha256':ROM_SHA,'camera_code_sha256':code_hash,'selector_modes':modes,'sine_table':'0x1582a:512 signed words','fixtures':len(cases),'scripted_fixtures':400,'reference':'label-specific offline arithmetic specification; no ROM CPU execution','original_game_comparison':False},indent=2)+'\n')
    print('Exported all ten background modes and',len(cases),'camera arithmetic fixtures')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('rom',type=Path);parser.add_argument('--project',type=Path,default=Path('.'));args=parser.parse_args();export(args.rom,args.project)
