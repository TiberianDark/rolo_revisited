#pragma once
#include <cstdint>
#include <span>
#include <stdexcept>
namespace rolo {
inline void startup_word(std::uint32_t& value,std::uint16_t low){value=(value&0xffff0000u)|low;}
struct StartupPatternState {std::uint32_t result{},tile{},base{},row{},attribute{},seed{},offset{},count{};};
struct StartupPatternPorts {virtual ~StartupPatternPorts()=default;virtual void data(std::uint16_t)=0;virtual void control(std::uint32_t)=0;};
// $075E. Caller supplies the actual finite writable coordinate records.
inline void publish_startup_pattern(StartupPatternState&s,std::uint16_t&x,std::uint16_t&y,StartupPatternPorts&p){
 x=std::uint16_t(128+s.row);p.data(x);startup_word(s.result,0xc00);startup_word(s.result,std::uint16_t(s.result|std::uint16_t(s.tile)));startup_word(s.tile,std::uint16_t(s.tile+1));p.data(std::uint16_t(s.result));
 y=std::uint16_t(0x8201+s.attribute);startup_word(s.attribute,std::uint16_t(s.attribute+4));p.data(y);startup_word(s.result,std::uint16_t(128+s.base));
}
// $0782: 8 pairs, then the last pair with D1.W replaced from D5.W.
inline void publish_startup_pattern_rows(StartupPatternState&s,std::span<std::uint16_t>x,std::span<std::uint16_t>y,StartupPatternPorts&p){
 if(x.size()<18||y.size()<18)throw std::out_of_range("Startup pattern record extent");
 s.count=7;unsigned index=0;
 for(unsigned row=0;row<8;++row){publish_startup_pattern(s,x[index],y[index],p);++index;p.data(std::uint16_t(s.result));publish_startup_pattern(s,x[index],y[index],p);++index;startup_word(s.result,std::uint16_t(s.result+32));p.data(std::uint16_t(s.result));startup_word(s.row,std::uint16_t(s.row+6));startup_word(s.count,std::uint16_t(s.count-1));}
 publish_startup_pattern(s,x[index],y[index],p);++index;p.data(std::uint16_t(s.result));startup_word(s.tile,std::uint16_t(s.seed));publish_startup_pattern(s,x[index],y[index],p);startup_word(s.result,std::uint16_t(s.result+32));p.data(std::uint16_t(s.result));
}
// $07A6: only the low words of D6/D7 are changed.
inline void startup_pattern_offset(StartupPatternState&s){startup_word(s.offset,std::uint16_t(s.seed));startup_word(s.count,std::uint16_t(s.attribute));startup_word(s.count,std::uint16_t(s.count<<2));startup_word(s.offset,std::uint16_t(s.offset+s.count));}
// $07B0: C006 is a supplied data LONG, not executable host/ROM memory.
inline void startup_pattern_mask(StartupPatternState&s,std::uint32_t input,std::uint32_t c006){
 s.row=c006;s.seed=(input<<16)|(input>>16);startup_word(s.attribute,std::uint16_t(s.seed));startup_word(s.seed,std::uint16_t(s.seed&7));startup_word(s.seed,std::uint16_t(s.seed<<2));
 auto word=std::uint16_t(s.attribute);for(unsigned n=0;n<3;++n)word=std::uint16_t((word>>1)|(word&0x8000));startup_word(s.attribute,std::uint16_t(word<<5));
}
// $080E: the D7.W=24 palette publication special case.
inline void publish_startup_colour(StartupPatternState&s,StartupPatternPorts&p){
 if(std::uint16_t(s.count)!=24)return;p.control(0xc0120000);p.data(std::uint16_t(s.result));p.control(0xc0020000);
 if(std::uint16_t(s.result)==0xe86)startup_word(s.result,0xe22);startup_word(s.result,std::uint16_t(s.result&0x666));p.data(std::uint16_t(s.result));
}
}
