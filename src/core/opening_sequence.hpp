#pragma once
#include "core/startup_image_scene.hpp"
#include "core/startup_animation_scene.hpp"
#include "core/opening_data.hpp"
#include "core/entrance.hpp"
#include "core/palette_effect.hpp"
#include <vector>
namespace rolo {
// Native display-data sink for translated startup routines. No CPU/ROM instruction execution.
struct OpeningDisplay:TextTilePorts{
 std::array<std::uint8_t,65536> vram{};std::array<std::uint16_t,64> palette{};unsigned address{},code{},increment=2;bool pending{};
 void control_word(std::uint16_t v)override{if((v&0xc000)==0x8000){if((v>>8&31)==15)increment=v&255;pending=false;return;}if(!pending){address=(address&0xc000)|(v&0x3fff);code=(code&~3u)|(v>>14);pending=true;}else{address=(address&0x3fff)|((v&3)<<14);code=(code&3)|((v>>2)&0x3c);pending=false;}}
 void control_long(std::uint32_t v)override{pending=false;control_word(std::uint16_t(v>>16));control_word(std::uint16_t(v));}
 void data_word(std::uint16_t v)override{pending=false;if((code&15)==3)palette[(address&127)/2]=v;else if((code&15)==1){vram[address&65535]=std::uint8_t(v>>8);vram[(address+1)&65535]=std::uint8_t(v);}address=(address+increment)&65535;}
 void data_long(std::uint32_t v)override{data_word(std::uint16_t(v>>16));data_word(std::uint16_t(v));}
 unsigned word(unsigned at)const{return (unsigned(vram[at&65535])<<8)|vram[(at+1)&65535];}
 unsigned pixel(unsigned tile,unsigned x,unsigned y)const{if(tile&0x800)x=7-x;if(tile&0x1000)y=7-y;const auto b=vram[((tile&2047)*32+y*4+x/2)&65535];return (tile>>13&3)*16+((b>>((x&1)?0:4))&15);}
 std::vector<std::uint8_t> raster()const{
  std::vector<std::uint8_t> image(320*224,0);
  for(int plane=1;plane>=0;--plane)for(unsigned y=0;y<224;++y)for(unsigned x=0;x<320;++x){const unsigned scroll=word(0x2000+y*4+plane*2);const unsigned sx=(x-scroll)&1023,sy=y&255;const auto tile=word(0xa000+(sy/8)*256+(sx/8)*2);const auto p=pixel(tile,sx&7,sy&7);if(p&15)image[y*320+x]=std::uint8_t(p);}
  std::vector<unsigned> entries;unsigned at=0xdc00;for(unsigned i=0;i<80;++i){entries.push_back(at);const unsigned next=vram[(at+3)&65535]&127;if(!next)break;at=0xdc00+next*8;}
  for(auto i=entries.rbegin();i!=entries.rend();++i){at=*i;const int y=int(word(at)&511)-128,x=int(word(at+6)&511)-128;const unsigned w=((vram[at+2]>>2)&3)+1,h=(vram[at+2]&3)+1,tile=word(at+4);for(unsigned py=0;py<h*8;++py)for(unsigned px=0;px<w*8;++px){const int dx=x+int(px),dy=y+int(py);if(dx<0||dx>=320||dy<0||dy>=224)continue;const unsigned tx=(tile&0x800)?w-1-px/8:px/8,ty=(tile&0x1000)?h-1-py/8:py/8;const auto p=pixel((tile&0xf800)|((tile+tx*h+ty)&2047),px&7,py&7);if(p&15)image[dy*320+dx]=std::uint8_t(p);}}
  return image;
 }
};
struct OpeningSequence{
 enum class Phase{EA,Copyright,Entrance,Photo,Title};Phase phase=Phase::EA;unsigned ticks{},phase_ticks{};EntranceState entrance;OpeningDisplay display;std::array<std::uint8_t,65536> work{};StartupAnimationFrame startup;NativePaletteEffects colours;
 OpeningSequence(){build_startup_image_scene(opening_data::startup,work,0,display);startup.scroll=226;startup.divider=0;colours.colours=opening_data::colour;colours.inhibited_c48d=0;}
 void reset(){*this=OpeningSequence{};}
 void step(){++ticks;++phase_ticks;
  if(phase==Phase::EA){StartupAnimationScene scene(work,display);update_startup_animation_frame(startup,scene);if(startup.done){phase=Phase::Copyright;phase_ticks=0;}return;}
  if(phase==Phase::Copyright){if(phase_ticks>=180){phase=Phase::Entrance;phase_ticks=0;colours.colours.fill(0);colours.begin_level_palette(opening_data::colour);}return;}
  colours.interrupt_palette_step();
  if(phase==Phase::Entrance){const auto status=update_entrance(entrance);if(status!=AnimationResult::Ok)throw std::runtime_error("Opening entrance animation failed");if(entrance.tick==850){phase=Phase::Photo;phase_ticks=0;colours.colours.fill(0xeee);colours.begin_level_palette(opening_data::photo);}return;}
  if(phase==Phase::Photo&&phase_ticks>=8){phase=Phase::Title;phase_ticks=0;}
 }
 static void put_colour(std::vector<std::uint8_t>&out,unsigned at,std::uint16_t c){out[at*4]=std::uint8_t(((c>>1)&7)*255/7);out[at*4+1]=std::uint8_t(((c>>5)&7)*255/7);out[at*4+2]=std::uint8_t(((c>>9)&7)*255/7);out[at*4+3]=255;}
 static void text(std::vector<std::uint8_t>&out,const char*value,int x,int y,std::uint16_t colour){for(;*value;++value,x+=8){const auto c=static_cast<unsigned char>(*value);if(c<32||c>127)continue;for(int py=0;py<8;++py)for(int px=0;px<8;++px){const auto b=opening_data::font[(c-32)*32+py*4+px/2];const auto ink=(b>>((px&1)?0:4))&15;if(ink!=7&&ink!=0&&x+px>=0&&x+px<320&&y+py>=0&&y+py<224)put_colour(out,unsigned((y+py)*320+x+px),ink==6?std::uint16_t((colour>>1)&0x666):colour);}}}
 std::vector<std::uint8_t> raster()const{
  std::vector<std::uint8_t> out(320*224*4,0);for(unsigned i=0;i<320*224;++i)out[i*4+3]=255;
  if(phase==Phase::EA){auto image=display.raster();for(unsigned i=0;i<image.size();++i)put_colour(out,i,display.palette[image[i]]);return out;}
  if(phase==Phase::Copyright){text(out,"ROLO TO THE RESCUE",88,51,0x00a);text(out,"A VECTORDEAN GAME.",88,95,0x0a0);text(out,"@ 1992 ELECTRONIC ARTS.",64,112,0xa66);text(out,"LICENSED BY SEGA ENTERPRISES LTD.",24,208,0xeee);return out;}
  std::vector<std::uint8_t> image(320*224,0);const bool photo=phase==Phase::Photo||phase==Phase::Title;
  auto layer=[&](auto&pixels,int y,bool transparent){for(unsigned i=0;i<pixels.size();++i){const int at=int(i)+y*320;if(at>=0&&at<int(image.size())&&(!transparent||(pixels[i]&15)))image[at]=pixels[i];}};
  if(photo)layer(opening_data::photo_back,48,false);else layer(opening_data::back,48,false);
  if(!photo)for(unsigned index:{5u,4u,3u,2u,0u,1u}){auto d=entrance_draw(entrance.objects[index],entrance);if(!d)continue;for(auto&s:opening_data::sprites)if(s.source==d->graphics&&s.width==d->width&&s.height==d->height){for(unsigned y=0;y<s.height;++y)for(unsigned x=0;x<s.width;++x){const auto p=opening_data::sprite_pixels[s.offset+y*s.width+(d->flip_x?s.width-1-x:x)];const int dx=d->x+int(x),dy=d->y+int(y);if(p&&dx>=0&&dx<320&&dy>=0&&dy<224)image[dy*320+dx]=std::uint8_t((index<2?32:48)+p);}break;}}
  if(photo)layer(opening_data::photo_front,48,true);else layer(opening_data::front,48,true);layer(opening_data::logo,0,true);
  for(unsigned i=0;i<image.size();++i)put_colour(out,i,colours.colours[image[i]]);
  if(phase==Phase::Title&&phase_ticks>=50)text(out,"PRESS START TO PLAY",80,200,0x0a4);
  return out;
 }
};
}
