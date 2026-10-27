#pragma once
#include "core/game_over_text.hpp"
namespace rolo {
struct FatalDiagnosticState{TextLayoutState text;std::uint32_t source{};std::uint16_t selector{},display{},attributes{};std::array<std::uint8_t,9>hex{};bool halted=false;};
struct FatalDiagnosticServices:TextTilePorts{virtual void initialize(unsigned,FatalDiagnosticState&)=0;virtual void palette(FatalDiagnosticState&)=0;virtual void halt(FatalDiagnosticState&)=0;};
// $1076 supplies selector zero. Native fatal outcome replaces the endless TRAP wait.
inline void show_fatal_diagnostic(std::span<const std::uint8_t>rom,std::uint32_t fault_address,FatalDiagnosticState&s,FatalDiagnosticServices&p){
 const auto message=completion_rom_long(rom,0x116a);
 for(unsigned service:{0x13b8u,0x142au,0x1462u,0x146cu,0x31b8u})p.initialize(service,s);
 s.selector=65535;p.palette(s);s.display=std::uint16_t(s.display|64);p.control_word(s.display);
 s.text.base=0xc000;s.source=0x113e;s.text.x=6;s.text.y=3;s.attributes=0x6000;
 auto print=[&](){s.text.source=s.source;publish_plain_text(s.text,rom.subspan(s.source),s.attributes,p);};print();
 if(message>=rom.size())throw std::out_of_range("Fatal message extent");s.text.x=std::uint16_t((s.text.x&0xff00)|rom[message]);s.source=message+1;s.text.y=5;print();
 s.source=0x115b;print();s.hex=hexadecimal_text_number(fault_address);s.source=0xffffc4c0;s.text.source=s.source;publish_plain_text(s.text,s.hex,s.attributes,p);
 s.halted=true;p.halt(s);
}
}
