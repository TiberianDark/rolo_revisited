#pragma once
#include "core/terrain_record_search.hpp"
#include <array>
namespace rolo {
struct TerrainQuadMapping {
    std::array<std::uint16_t,2048> patterns;
    std::array<std::array<std::uint16_t,4>,512> quads;
    std::array<std::uint8_t,128> visited{};
    std::uint16_t next_pattern{};
    explicit TerrainQuadMapping(std::uint16_t first):next_pattern(first) {
        patterns.fill(65535);for(auto& quad:quads)quad.fill(65535);
    }
};
struct TerrainQuadServices {
    virtual ~TerrainQuadServices()=default;
    virtual TerrainMacroDefinition quad_macro(std::uint8_t index)=0;
    virtual std::array<std::uint16_t,4> source_quad(std::uint16_t index)=0;
    virtual void upload_terrain_pattern(std::uint16_t source,std::uint16_t destination)=0;
};
// $3E04: publish cache before upload, then increment the WORD cursor.
inline std::uint16_t allocate_terrain_quad_pattern(TerrainQuadMapping& state,
        std::uint16_t source,TerrainQuadServices& services){
    if(source>=state.patterns.size())throw std::out_of_range("Terrain pattern source index");
    const auto destination=state.next_pattern;
    state.patterns[source]=destination;
    services.upload_terrain_pattern(source,destination);
    state.next_pattern=static_cast<std::uint16_t>(state.next_pattern+1);
    return destination;
}
// $3D0C..$3E02/$3E04: first-seen allocation, including literal packed-long common offset.
inline void map_terrain_macro_quads(TerrainQuadMapping& state,std::uint8_t index,TerrainQuadServices& services) {
    if(index>=state.visited.size())throw std::out_of_range("Unproved native visited macro index");
    if(state.visited[index])return;
    state.visited[index]=255;const auto macro=services.quad_macro(index);
    if(macro.tiles.empty()||macro.tiles.size()!=static_cast<std::size_t>(macro.width)*macro.height)
        throw std::invalid_argument("Unproved native macro quad extent");
    for(const auto tile:macro.tiles) {
        const auto quad_index=static_cast<std::uint16_t>(tile&511);
        const auto source=services.source_quad(quad_index);auto& output=state.quads[quad_index];
        if(quad_index<28) {
            for(unsigned n=0;n<4;n+=2) {
                const auto packed=((static_cast<std::uint32_t>(source[n])<<16)|source[n+1])+0x05940594u;
                output[n]=static_cast<std::uint16_t>(packed>>16);output[n+1]=static_cast<std::uint16_t>(packed);
            }
            continue;
        }
        for(unsigned n=0;n<4;++n) {
            const auto source_index=static_cast<std::uint16_t>(source[n]&2047);auto& mapped=state.patterns[source_index];
            if(signed_word(mapped)<0) {
                (void)allocate_terrain_quad_pattern(state,source_index,services);
            }
            output[n]=static_cast<std::uint16_t>(mapped|(source[n]&0xf800));
        }
    }
}
// $3CD6..$3D0C: initial MAP scan reads then advances before the terminal comparison.
inline void map_terrain_quads(TerrainQuadMapping& state,TerrainMapView map,TerrainQuadServices& services) {
    const auto rows=static_cast<std::uint16_t>((map.word(6)>>4)*2);
    const auto start=map.word(8),end=map.word(8+rows);
    if(signed_word(start)<0||signed_word(end)<0)throw std::invalid_argument("Unproved native MAP quad scan offset");
    std::ptrdiff_t cursor=start;
    for(;;) {
        const auto record=map.record(cursor);cursor+=4;
        if(cursor>=end)return;
        if(record.type<0x400)map_terrain_macro_quads(state,static_cast<std::uint8_t>(record.type),services);
    }
}
}
