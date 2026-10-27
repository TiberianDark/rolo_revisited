#pragma once
#include "core/startup_pattern_publication.hpp"
#include <array>
namespace rolo {
struct StartupSlopeResult{std::uint32_t temporary{};std::uint16_t counter{};};
inline StartupSlopeResult adjust_startup_rows(std::span<std::uint16_t>rows,std::uint16_t step,StartupPatternPorts&p){if(rows.size()<18)throw std::out_of_range("Startup row extent");auto delta=std::uint32_t(std::int32_t(static_cast<std::int16_t>(step))*-4);for(unsigned n=0;n<9;++n){for(unsigned i=0;i<2;++i){auto&word=rows[n*2+i];word=std::uint16_t(word+delta);p.data(word);}delta=(delta&0xffff0000u)|std::uint16_t(delta+step);}return {delta,65535};}
inline std::uint16_t publish_startup_attributes(std::span<const std::uint16_t>rows,std::uint16_t attributes,StartupPatternPorts&p){if(rows.size()<18)throw std::out_of_range("Startup attribute extent");std::uint16_t value=0;for(unsigned n=0;n<18;++n){value=std::uint16_t((rows[n]&0xefff)|attributes);p.data(value);}return value;}
inline void publish_startup_centered_rows(std::uint16_t origin,std::uint16_t width,StartupPatternPorts&p,bool centered){auto left=origin,right=std::uint16_t(origin+32);if(centered){auto gap=std::uint16_t(32-width);gap=std::uint16_t((gap>>1)|(gap&0x8000));left=std::uint16_t(left+gap);right=std::uint16_t(right-gap);}left=std::uint16_t(left+128);right=std::uint16_t(right+128);for(unsigned n=0;n<9;++n){p.data(left);p.data(right);}}
inline void publish_startup_tile_pairs(std::uint16_t count,std::uint16_t first,std::uint16_t last,StartupPatternPorts&p){first|=0xc00;last|=0xc00;for(unsigned n=0;n<count;++n){p.data(first);first=std::uint16_t(first+1);p.data(first);first=std::uint16_t(first+1);}p.data(first);p.data(last);}
}
