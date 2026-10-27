#pragma once
#include "core/level1_indexed_background_data.hpp"
#include <array>
#include <span>
#include <vector>
#include <stdexcept>
namespace rolo {
// Original mode3 publishes fixed backgroundY0. X is the unsigned WORD domain.
inline std::vector<std::uint8_t> raster_level1_background(std::uint16_t background_x,
        std::span<const std::uint16_t> palette){
    if(palette.size()<64)throw std::out_of_range("Level1 background palette extent");
    std::vector<std::uint8_t> rgba(320*224*4);
    for(unsigned y=0;y<224;++y)for(unsigned x=0;x<320;++x){
        const auto index=level1_indexed_background_data::pixels[y*512+((background_x+x)&511)];
        const auto color=palette[index];const auto at=(y*320+x)*4;
        rgba[at]=static_cast<std::uint8_t>(((color>>1)&7)*255/7);
        rgba[at+1]=static_cast<std::uint8_t>(((color>>5)&7)*255/7);
        rgba[at+2]=static_cast<std::uint8_t>(((color>>9)&7)*255/7);
        rgba[at+3]=255; // Plane background remains opaque, including index0.
    }
    return rgba;
}
}
