#pragma once
#include "core/text_tile_publication.hpp"
namespace rolo {
struct ScreenTextState{std::uint32_t source{},return_source{},wait_value{},demo_source{};std::uint16_t x{},y{},wait_counter{},saved_selector{},work_word{};std::uint8_t mode{},delay{},bar_x{},bar_y{},bar_width{},bar_last{},demo_index{},work_a{},work_b{};};
inline std::uint8_t screen_byte(std::span<const std::uint8_t>b,std::uint32_t&at){if(at>=b.size())throw std::out_of_range("Screen text operand");return b[at++];}
inline std::uint32_t screen_long(std::span<const std::uint8_t>b,std::uint32_t&at){std::uint32_t v=0;for(unsigned i=0;i<4;++i)v=(v<<8)|screen_byte(b,at);return v;}
inline void stop_screen_text(ScreenTextState&s){s.source=0;s.mode=0;}
inline std::uint32_t position_screen_text(ScreenTextState&s,std::span<const std::uint8_t>b,std::uint32_t at){s.x=std::uint16_t((s.x&0xff00)|screen_byte(b,at));s.y=std::uint16_t((s.y&0xff00)|screen_byte(b,at));return at;}
inline void delay_screen_text(ScreenTextState&s,std::span<const std::uint8_t>b,std::uint32_t at){s.delay=screen_byte(b,at);s.source=at;}
inline std::uint32_t redirect_screen_text(std::span<const std::uint8_t>b,std::uint32_t at){return screen_long(b,at);}
inline void wait_screen_text(ScreenTextState&s,std::span<const std::uint8_t>b,std::uint32_t at){at=(at+1)&~1u;s.wait_value=screen_long(b,at);s.source=at;s.mode=1;s.wait_counter=0;}
struct ScreenFill{std::uint32_t value{},destination{},command{};std::uint16_t count{};};
struct ScreenTextServices:TextTilePorts{virtual void fill(ScreenFill)=0;virtual void demo_handoff()=0;};
inline void bar_screen_text(ScreenTextState&s,std::span<const std::uint8_t>b,std::uint32_t at,std::span<const std::uint16_t>tiles,ScreenTextServices&p){
 s.bar_x=screen_byte(b,at);s.bar_y=screen_byte(b,at);s.bar_width=screen_byte(b,at);s.bar_last=std::uint8_t(s.bar_width*8-1);s.source=at;s.mode=2;
 p.fill({0,0x840,0x40000000,0x4ff});
 const auto destination=std::uint32_t(0xc000+unsigned(s.bar_y)*128+unsigned(s.bar_x)*2);
 const auto columns=std::uint8_t(s.bar_width-1);(void)publish_text_rectangle(tiles,destination,0x6042,columns,0,p);
}
inline void demo_screen_text(ScreenTextState&s,std::uint32_t at,std::span<const std::uint8_t>rom,ScreenTextServices&p){
 s.return_source=at;const auto index=s.demo_index;if(index>4)throw std::out_of_range("Original demo table index");
 s.demo_index=std::uint8_t(index==4?0:index+1);s.work_a=s.work_b=0;s.work_word=0;
 auto table=std::uint32_t(0x7000+index*4);auto ptr=screen_long(rom,table);
 const auto hi=screen_byte(rom,ptr),lo=screen_byte(rom,ptr);s.saved_selector=std::uint16_t((hi<<8)|lo);s.demo_source=ptr+1;p.demo_handoff();
}
}
