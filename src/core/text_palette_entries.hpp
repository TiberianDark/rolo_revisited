#pragma once
#include "core/palette_effect.hpp"
namespace rolo {
struct TextPaletteState{std::array<std::uint16_t,64>colours{};PaletteEffect effect;std::uint32_t cursor{};std::uint16_t attributes{},plane{},clear_offset{},clear_count{};std::uint8_t inhibited=255;unsigned bank{};};
struct TextPaletteServices{virtual ~TextPaletteServices()=default;virtual void clock(TextPaletteState&)=0;virtual void clear(std::uint16_t,std::uint16_t,std::uint32_t)=0;virtual void reset_text()=0;virtual void restore_palette()=0;virtual void resume_text(std::uint32_t)=0;};
inline void run_text_palette_transition(TextPaletteState&s,std::span<const std::uint16_t>target,bool full,TextPaletteServices&v){
 if(target.size()!=16)throw std::out_of_range("Text palette target extent");s.clear_offset=full?0:0xa00;s.clear_count=full?0xfff:0x3ff;const auto cursor=s.cursor;s.bank=(s.attributes>>13)&3;initialize_palette_effect(s.effect,std::span<const std::uint16_t>(s.colours).subspan(s.bank*16,16),target,4);s.inhibited=0;while(s.effect.active)v.clock(s);s.inhibited=255;v.clear(std::uint16_t(s.plane+s.clear_offset),s.clear_count,0x40000080);v.reset_text();v.restore_palette();s.cursor=cursor;v.resume_text(cursor);
}
}
