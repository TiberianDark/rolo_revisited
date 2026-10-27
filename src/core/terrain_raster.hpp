#pragma once
#include "core/terrain_pattern_storage.hpp"
namespace rolo {
struct TerrainPixel {
    std::uint8_t palette_index{};
    bool priority{};
    bool opaque{};
};
// Read the immutable packed4bpp artwork through native pattern/name-table storage.
// Frame timing, plane/sprite composition and palette fades are caller responsibilities.
inline TerrainPixel terrain_pattern_pixel(const TerrainPatternStorage& patterns,std::uint16_t name,
        unsigned x,unsigned y) {
    if(x>=8||y>=8)throw std::out_of_range("Native tile pixel coordinates");
    const auto sx=(name&0x800)?7-x:x,sy=(name&0x1000)?7-y:y;
    const auto packed=patterns.pixels[(name&2047)*32+sy*4+sx/2];
    const auto nibble=static_cast<std::uint8_t>((packed>>((sx&1)?0:4))&15);
    return {static_cast<std::uint8_t>(nibble?(((name>>13)&3)*16+nibble):0),(name&0x8000)!=0,nibble!=0};
}
inline TerrainPixel terrain_plane_pixel(const TerrainPatternStorage& patterns,const TerrainMappedDisplay& display,
        unsigned x,unsigned y) {
    const auto name=display.names[((y>>3)&31)*64+((x>>3)&63)];
    return terrain_pattern_pixel(patterns,name,x&7,y&7);
}
inline std::array<std::uint8_t,4> terrain_pixel_rgba(TerrainPixel pixel,std::span<const std::uint16_t> palette) {
    if(pixel.palette_index>=palette.size())throw std::out_of_range("Native palette extent");
    const auto color=palette[pixel.palette_index];
    return {static_cast<std::uint8_t>(((color>>1)&7)*255/7),
            static_cast<std::uint8_t>(((color>>5)&7)*255/7),
            static_cast<std::uint8_t>(((color>>9)&7)*255/7),static_cast<std::uint8_t>(pixel.opaque?255:0)};
}
}
