#pragma once
#include "core/startup_animation_frame.hpp"
#include "core/startup_layout_entries.hpp"
#include "core/startup_logo_raster.hpp"
#include <algorithm>
namespace rolo {
class StartupAnimationScene:public StartupAnimationServices {
 std::array<std::uint8_t,65536>&ram;TextTilePorts&ports;
 std::array<std::uint16_t,18> read(unsigned at){std::array<std::uint16_t,18>r{};for(auto&v:r){v=std::uint16_t((ram[at]<<8)|ram[at+1]);at+=2;}return r;}
 struct Adapter:StartupPatternPorts{TextTilePorts&p;explicit Adapter(TextTilePorts&v):p(v){}void data(std::uint16_t v)override{p.data_word(v);}void control(std::uint32_t v)override{p.control_long(v);}};
public:
 StartupAnimationScene(std::array<std::uint8_t,65536>&r,TextTilePorts&p):ram(r),ports(p){}
 void control_word(std::uint16_t v)override{ports.control_word(v);}void control_long(std::uint32_t v)override{ports.control_long(v);}void data_word(std::uint16_t v)override{ports.data_word(v);}void data_long(std::uint32_t v)override{ports.data_long(v);}
 void upload_logo_plane()override{control_long(0x49200001);for(unsigned at=0xd2e4;at<0xdbe4;at+=4)data_long((std::uint32_t(ram[at])<<24)|(std::uint32_t(ram[at+1])<<16)|(ram[at+2]<<8)|ram[at+3]);}
 void draw_phase(StartupAnimationFrame&s,std::uint16_t phase)override{
  if(phase>24||s.loop>2)throw std::out_of_range("Original startup phase domain");
  Adapter adapter(ports);control_long(0x40000003);control_word(0x8f08);
  constexpr std::array<unsigned,3> attrs{0xc030,0xc0c0,0xc078},xbase{0xc00c,0xc09c,0xc054},attrcmd{0x5c04,0x5c94,0x5d24},xcmd{0x5c00,0x5c90,0x5d20};
  constexpr std::array<std::array<std::uint32_t,3>,3>colourcmd{{{0xc00c0000,0xc0080000,0xc00a0000},{0xc0140000,0xc01a0000,0xc0060000},{0xc0160000,0xc01c0000,0xc0040000}}};
  constexpr std::array<std::array<std::uint16_t,3>,3>early{{{0xa0,0xa0,0x4e4},{0xa42,0xa42,0xe86},{0x8a,0x8a,0xce}}},late{{{0x4e4,0x8e8,0xa0},{0xe86,0xeca,0xa42},{0xce,0x8ee,0x8a}}};
  if(phase==7||phase==20){for(unsigned i=0;i<3;++i){control_long(colourcmd[s.loop][i]);data_word((phase==7?early:late)[s.loop][i]);}control_word(std::uint16_t(attrcmd[s.loop]));auto values=read(attrs[s.loop]);publish_startup_attributes(values,phase==7?0x1000:0,adapter);}
  control_word(std::uint16_t(xcmd[s.loop]));auto values=read(xbase[s.loop]);adjust_startup_rows(values,phase<13?65535:1,adapter);for(unsigned i=0;i<18;++i){ram[xbase[s.loop]+i*2]=std::uint8_t(values[i]>>8);ram[xbase[s.loop]+i*2+1]=std::uint8_t(values[i]);}
  const auto count=std::uint16_t(phase/3);
  if(s.loop==0){control_word(0x5c06);publish_startup_centered_rows(std::uint16_t(104-phase),std::uint16_t(count*4),adapter,true);control_word(0x5c02);publish_startup_tile_pairs(count,1,0,adapter);}
  else if(s.loop==2){control_word(0x5d26);publish_startup_centered_rows(std::uint16_t(152+phase),std::uint16_t(count*4),adapter,false);control_word(0x5d1a);data_word(0xc24);publish_startup_tile_pairs(count,37,0,adapter);}
  else {control_word(0x5c8a);data_word(0xc12);publish_startup_tile_pairs(count,19,0,adapter);}
  if(phase==24){control_long(0xc0120000);const std::uint16_t colour=s.loop==0?0x4e4:s.loop==2?0xce:0xe86;data_word(colour);control_long(0xc0020000);data_word(std::uint16_t((colour==0xe86?0xe22:colour)&0x666));}
  if(s.loop==1){std::fill(ram.begin()+0xd2e4,ram.begin()+0xdbe4,0);const unsigned width=std::min(unsigned(count)*2+4,16u),inset=16-width;StartupLogoEdges edges{32+inset,31-inset,0,0};raster_startup_logo_edges(std::span<std::uint8_t>(ram).subspan(0xd2e4),edges);for(unsigned i=0;i<4;++i)ram[0xc006+i]=std::uint8_t(edges.pattern>>(24-i*8));}
 }
};
}
