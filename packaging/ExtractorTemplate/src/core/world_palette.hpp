#pragma once
#include "core/world_map.hpp"
namespace rolo {
struct WorldPaletteCycle {std::uint8_t phase{},delay=6;};
// 9DD6: decrement BYTE including zero underflow. Every six calls advances2
// modulo8 and copies the SAME overlapping four words to three CRAM regions.
inline bool update_world_palette(WorldPaletteCycle& state,std::span<std::uint16_t> palette){
    state.delay=static_cast<std::uint8_t>(state.delay-1);if(state.delay)return false;
    if(palette.size()<64)throw std::out_of_range("World CRAM palette extent");
    state.delay=6;state.phase=static_cast<std::uint8_t>((state.phase+2)&7);
    for(const unsigned start:{10u,26u,58u})for(unsigned n=0;n<4;++n)
        palette[start+n]=world_map_word(world_map_data::palette_cycle,state.phase+n*2);
    return true;
}
}
