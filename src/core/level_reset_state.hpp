#pragma once
#include <array>
#include <cstdint>
#include <stdexcept>
namespace rolo {
// Native snapshot of the original shared state page; no instruction execution.
struct LevelResetState {
 std::array<std::uint8_t,65536> bytes{};
 std::uint16_t word(unsigned at)const{return static_cast<std::uint16_t>((bytes.at(at)<<8)|bytes.at(at+1));}
 void word(unsigned at,std::uint16_t v){bytes.at(at)=v>>8;bytes.at(at+1)=v;}
};
inline void reset_level_contact_state(LevelResetState& s){
 for(unsigned at: {0xc516,0xc517,0xc519,0xc51a,0xc51b,0xc522})s.bytes[at]=0;
 s.bytes[0xc511]=255;
 for(unsigned at: {0xf281,0xf282,0xc518,0xf2bc,0xc524,0xf2b5,0xf2b6,0xf2b7,0xf2b8})s.bytes[at]=0;
 s.word(0xf2ba,0);s.bytes[0xc512]=0;
 for(unsigned at=0xf2d4;at<0xf2d8;++at)s.bytes[at]=0;
 const auto selector=s.word(0xf2f6);if(selector>=80)throw std::out_of_range("Unproved startup flag selector");
 auto& flag=s.bytes[0xc558+selector];s.bytes[0xc552]=(flag&2)?255:0;
 const auto visited=flag&4;flag|=4;s.bytes[0xc553]=visited?255:0;
 s.word(0xc490,0);s.word(0xc4be,3);
 s.bytes[0xc488]=s.bytes[0xc489]=s.bytes[0xc544]=0;s.word(0xc4d6,250);
 s.word(0xf268,0);s.word(0xf26a,0);
 for(unsigned at=0xc4d8;at<0xc4dc;++at)s.bytes[at]=0;
 s.word(0xf2b0,0);s.word(0xf2b2,0);s.bytes[0xf2b4]=10;
}
struct HudResetFill {std::uint32_t d0,d1;std::uint16_t d2;std::uint32_t d3;};
template<class FillService> void reset_level_hud_publication(LevelResetState& s,FillService&& fill){
 s.bytes[0xc551]=0;s.bytes[0xc550]=0;
 fill(HudResetFill{0,0xb100,0xff,0x40000000}); // Original 26C8 service request; completion is separate.
}
}
