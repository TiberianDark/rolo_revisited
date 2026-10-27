#pragma once
#include "core/terrain_camera_update.hpp"
#include <array>
#include <span>
#include <stdexcept>
namespace rolo {
struct TerrainDisplayServices {
    virtual ~TerrainDisplayServices()=default;
    virtual std::array<std::uint16_t,4> terrain_quad_patterns(std::uint16_t index)=0;
    virtual void terrain_name_row(std::uint16_t byte_offset,std::uint16_t left,std::uint16_t right)=0;
};
// Typed name-table row writes replace VDP command/data writes; no CPU/VDP execution.
inline void display_terrain_cell(std::span<const std::uint8_t> backing,std::uint16_t offset,TerrainDisplayServices& services) {
    if(static_cast<std::size_t>(offset)+2>backing.size())throw std::out_of_range("Native display terrain extent");
    const auto tile=static_cast<std::uint16_t>((backing[offset]<<8)|backing[offset+1]);
    auto patterns=services.terrain_quad_patterns(tile&511);
    const auto flags=static_cast<std::uint16_t>(tile&0x9000);
    for(auto& pattern:patterns)pattern=static_cast<std::uint16_t>(pattern|flags);
    auto top=static_cast<std::uint16_t>((offset*2)&0xf7c);
    auto bottom=static_cast<std::uint16_t>(top|128);
    if(flags&0x1000){const auto temp=top;top=bottom;bottom=temp;}
    services.terrain_name_row(top,patterns[0],patterns[1]);
    services.terrain_name_row(bottom,patterns[2],patterns[3]);
}
// $745A row tail: 21 metatiles, right-to-left, after the native refill.
inline void display_terrain_row(const ActorState& plane,const TerrainCameraGlobals& g,
        std::span<const std::uint8_t> backing,bool bottom,TerrainDisplayServices& services) {
    const auto row=static_cast<std::uint16_t>(bottom?(g.f374+0x700)&plane.word(8):g.f374);
    auto column=static_cast<std::uint16_t>(g.f372+40);
    for(unsigned n=0;n<21;++n){display_terrain_cell(backing,static_cast<std::uint16_t>(row+(column&126)),services);column=static_cast<std::uint16_t>(column-2);}
}
// $7500 column tail: 15 metatiles, bottom-to-top, after the native refill.
inline void display_terrain_column(const ActorState& plane,const TerrainCameraGlobals& g,
        std::span<const std::uint8_t> backing,bool right,TerrainDisplayServices& services) {
    const auto column=static_cast<std::uint16_t>(right?(g.f372+40)&126:g.f372);
    auto row=static_cast<std::uint16_t>(g.f374+0x700);
    for(unsigned n=0;n<15;++n){display_terrain_cell(backing,static_cast<std::uint16_t>((row&plane.word(8))+column),services);row=static_cast<std::uint16_t>(row-128);}
}
// $75D0..$7666 full display: 16 rows of32 metatiles, bottom/right first.
inline void display_full_terrain(const ActorState& plane,const TerrainCameraGlobals& g,
        std::span<const std::uint8_t> backing,TerrainDisplayServices& services) {
    for(int row=0x780;row>=0;row-=128)
        for(int column=62;column>=0;column-=2)
            display_terrain_cell(backing,static_cast<std::uint16_t>(((g.f374+row)&plane.word(8))+((g.f372+column)&126)),services);
}
}
