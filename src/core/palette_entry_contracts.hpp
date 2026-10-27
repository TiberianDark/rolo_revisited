#pragma once
#include "core/palette_effect.hpp"
#include <vector>
#include <bit>
namespace rolo {
// $66DE: selector*16 is a WORD shift followed by signed WORD address addition.
inline void begin_selected_level_palette(NativePaletteEffects&p,std::span<const std::uint8_t>rom,std::uint16_t selector){
 auto word=[&](std::size_t at){if(at+1>=rom.size())throw std::out_of_range("Palette ROM word");return std::uint16_t((rom[at]<<8)|rom[at+1]);};
 auto ptr=[&](std::size_t at){return (std::uint32_t(word(at))<<16)|word(at+2);};
 const auto shifted=static_cast<std::uint16_t>(selector<<4);const auto table=std::int64_t(0x4b08a)+std::bit_cast<std::int16_t>(shifted);std::array<std::uint16_t,64>target{};
 for(unsigned bank=0;bank<4;++bank){const auto source=ptr(std::size_t(table)+bank*4);for(unsigned i=0;i<16;++i)target[bank*16+i]=word(source+i*2);}p.begin_level_palette(target);
}
struct PaletteInterruptState{std::uint8_t tick_latch=0,audio_enabled=0;std::uint16_t frame=0;};
struct PaletteInterruptServices{virtual ~PaletteInterruptServices()=default;virtual void poll(PaletteInterruptState&,NativePaletteEffects&)=0;virtual void audio_first(PaletteInterruptState&,NativePaletteEffects&)=0;virtual void audio_second(PaletteInterruptState&,NativePaletteEffects&)=0;virtual void publish(std::span<const std::uint16_t>,PaletteInterruptState&,NativePaletteEffects&)=0;};
inline void update_palette_interrupt_tail(PaletteInterruptState&s,NativePaletteEffects&p,PaletteInterruptServices&v){
 s.tick_latch=255;s.frame=static_cast<std::uint16_t>(s.frame+1);v.poll(s,p);
 if(s.audio_enabled){v.audio_first(s,p);v.audio_second(s,p);}if(p.inhibited_c48d)return;p.interrupt_palette_step();p.publish([&](auto colours){v.publish(colours,s,p);});
}
struct PaletteBurstServices{virtual ~PaletteBurstServices()=default;virtual void enter_critical()=0;virtual void control_word(std::uint16_t)=0;virtual void control_long(std::uint32_t)=0;virtual void colour_word(std::uint16_t)=0;virtual void leave_critical()=0;};
// $5998 original error colour port burst, represented as typed device requests.
inline void publish_allocation_failure_palette(std::uint16_t seed,PaletteBurstServices&s){s.enter_critical();s.control_word(0x8f00);s.control_word(0x8700);s.control_long(0xc0000000);for(unsigned i=0;i<0x5000;++i){seed=static_cast<std::uint16_t>((seed-0x101)&0xe0e);s.colour_word(seed);}s.colour_word(0);s.control_word(0x8f02);s.leave_critical();}
}
