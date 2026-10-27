#pragma once
#include "core/startup_image_codec.hpp"
#include "core/startup_pattern_publication.hpp"
#include "core/startup_pixel_range.hpp"
#include "core/text_tile_publication.hpp"
#include <algorithm>
namespace rolo {
// $986 startup asset/geometry payload; device requests are native typed ports.
inline std::uint16_t build_startup_image_scene(std::span<const std::uint8_t>rom,std::array<std::uint8_t,65536>&ram,std::uint16_t initial,TextTilePorts&ports){
 auto word=[&](unsigned a){return std::uint16_t((ram.at(a)<<8)|ram.at(a+1));};
 auto put=[&](unsigned a,std::uint32_t v){for(unsigned i=0;i<4;++i)ram.at(a+i)=std::uint8_t(v>>(24-i*8));};
 auto emit=[&](unsigned base){for(unsigned i=0;i<576;++i){auto a=base+i*4;ports.data_long((std::uint32_t(word(a))<<16)|word(a+2));}};
 ports.data_word(initial);ports.data_word(initial);
 for(unsigned row=0;row<9;++row){unsigned height=rom[0xc46+row];for(unsigned col=0;col<height;++col){std::uint32_t pattern=col?0x66666666:0x44444444;for(unsigned y=0;y<8;++y){if(col+1==height&&col)pattern=0x55555555;put(0xc0e4+row*256+col*4+y*32,pattern);}}if(row<8){put(0xc0e4+row*256+height*4,0x55555555);put(0xc0e4+row*256+height*4+32,0x55555555);}}
 ports.control_long(0x40200001);emit(0xc0e4);
 std::uint32_t left=32u<<16,right=left,cap_left=left;unsigned caps=0;
 for(unsigned row=0;row<9;++row){int height=rom[0xc46+row];for(unsigned col=0;col<6;++col){std::uint32_t pattern=0xbbbbbbbb;if(height>0){if(height==1)pattern=0x22222222;if(!col)pattern=0xeeeeeeee;write_startup_pixel_range(std::span<std::uint8_t>(ram).subspan(0xc9ec+row*256+col*4),left,right,pattern);}
  if(!height){pattern=0x22222222;unsigned size=rom[0xc6a+caps++];if(size)write_startup_pixel_range(std::span<std::uint8_t>(ram).subspan(0xc9ec+row*256+col*4),left,left+(size<<16),pattern);write_startup_pixel_range(std::span<std::uint8_t>(ram).subspan(0xc9ec+row*256+col*4),cap_left,right,pattern);}
  put(0xc006,pattern);--height;left-=0x97b4;right+=0x97b4;cap_left+=0x4bda;
 }}
 ports.control_long(0x52200001);emit(0xc9e4);
 ports.control_long(0x5c000003);
 struct Adapter:StartupPatternPorts{TextTilePorts&p;explicit Adapter(TextTilePorts&v):p(v){}void data(std::uint16_t v)override{p.data_word(v);}void control(std::uint32_t v)override{p.control_long(v);}}adapter(ports);
 StartupPatternState s;s.tile=1;s.base=80;s.row=72;s.attribute=0;s.seed=18;
 auto rows=[&](unsigned xat,unsigned yat){std::array<std::uint16_t,18>x{},y{};publish_startup_pattern_rows(s,x,y,adapter);for(unsigned i=0;i<18;++i){ram[xat+i*2]=std::uint8_t(x[i]>>8);ram[xat+i*2+1]=std::uint8_t(x[i]);ram[yat+i*2]=std::uint8_t(y[i]>>8);ram[yat+i*2+1]=std::uint8_t(y[i]);}};
 rows(0xc00c,0xc030);startup_word(s.base,136);startup_word(s.row,72);startup_word(s.attribute,72);startup_word(s.seed,36);rows(0xc09c,0xc0c0);startup_word(s.base,176);startup_word(s.row,70);startup_word(s.attribute,144);startup_word(s.seed,0);rows(0xc054,0xc078);
 const auto size=unsigned(rom[0xc7c])+(unsigned(rom[0xc7d])<<8);const auto decoded=decode_startup_image(rom.subspan(0xc80),size);std::copy(decoded.bytes.begin(),decoded.bytes.end(),ram.begin()+0xdbe4);std::copy(decoded.dictionary.begin(),decoded.dictionary.end(),ram.begin()+0xe7e4);
 unsigned cursor=0xdbe4;const auto patterns=word(cursor);cursor+=2;const auto height=word(cursor);cursor+=2;const auto width=word(cursor);cursor+=2;
 ports.control_long(0xc0000000);for(unsigned i=0;i<16;++i){ports.data_word(word(cursor));cursor+=2;}
 ports.control_long(0x40200000);const auto count=std::uint16_t(patterns*8);for(unsigned i=0;i<(count?count:65536u);++i){ports.data_long((std::uint32_t(word(cursor))<<16)|word(cursor+2));cursor+=4;}
 ports.control_long(0x40000002);std::uint16_t tile=0x8001,command=0x720c;
 for(unsigned y=0;y<(height?height:65536u);++y){ports.control_word(command);command=std::uint16_t(command+256);for(unsigned x=0;x<(width?width:65536u);++x){ports.data_word(tile);++tile;}}
 for(auto v:{0x7044,0x7144,0x710c}){ports.control_word(std::uint16_t(v));ports.data_word(tile++);ports.data_word(tile++);}ports.control_word(0x7136);ports.data_word(tile);
 ram[0xc000]=0;ram[0xc001]=0xe2;return 65535;
}
}
