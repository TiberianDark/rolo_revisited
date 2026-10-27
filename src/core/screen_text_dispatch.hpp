#pragma once
#include "core/screen_text_controls.hpp"
namespace rolo {
struct ScreenTextDispatchServices:ScreenTextServices {
 virtual void animate_glyph(ScreenTextState&)=0;
 virtual void update_wait(ScreenTextState&)=0;
 virtual void update_bar(ScreenTextState&)=0;
 virtual void begin_glyph(ScreenTextState&)=0;
 virtual void expand_glyph(std::uint32_t)=0;
 virtual std::uint32_t palette_transition(ScreenTextState&,std::uint32_t,bool)=0;
};
// $6D78: finite original ASCII/control streams; no instruction execution.
inline void dispatch_screen_text(ScreenTextState&s,std::span<const std::uint8_t>rom,std::span<const std::uint16_t>tiles,ScreenTextDispatchServices&p){
 if(!s.source)return;
 auto at=s.source;
 if(s.delay){--s.delay;return;}
 if(s.mode>=32&&s.mode<128){p.animate_glyph(s);return;}
 if(s.mode==1){p.update_wait(s);return;}
 if(s.mode==2){p.update_bar(s);return;}
 // Bounds catch malformed/cyclic data instead of following arbitrary ROM jumps.
 for(std::size_t steps=0;steps<rom.size();++steps){
  const auto c=screen_byte(rom,at);s.mode=c;
  if(c==32){s.x=static_cast<std::uint16_t>(s.x+1);continue;}
  if(c>32&&c<128){s.source=at;const auto glyph=0x27040u+(unsigned(c)-32)*32;p.begin_glyph(s);p.expand_glyph(glyph);s.wait_value=0x80000;s.wait_counter=0xa000;return;}
  switch(c){
   case 0:stop_screen_text(s);return;
   case 1:at=position_screen_text(s,rom,at);break;
   case 2:at=p.palette_transition(s,at,false);break;
   case 3:delay_screen_text(s,rom,at);return;
   case 4:at=redirect_screen_text(rom,at);break;
   case 5:wait_screen_text(s,rom,at);return;
   case 6:bar_screen_text(s,rom,at,tiles,p);return;
   case 7:demo_screen_text(s,at,rom,p);return;
   case 8:at=p.palette_transition(s,at,true);break;
   default:throw std::out_of_range("Unreviewed screen text control/glyph");
  }
 }
 throw std::out_of_range("Nonterminating screen text data");
}
}
