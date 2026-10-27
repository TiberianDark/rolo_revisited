#pragma once
#include "core/level1_terrain_data.hpp"
#include "core/terrain_pattern_storage.hpp"
namespace rolo {
// Normal level entry $1D16 initializes F264=1 before $3C08.
// $3C4C..$3CD4: shared foreground/background mapping, common upload, final clear.
inline TerrainQuadMapping initialize_level1_terrain_patterns(TerrainPatternStorage& storage,
        std::span<const std::uint8_t> foreground=level1_terrain_data::map_bytes,
        std::span<const std::uint8_t> background=level1_terrain_data::background_map_bytes) {
    namespace data=level1_terrain_data;
    TerrainQuadMapping mapping(1);
    ImmutableTerrainQuadServices services(data::macros,data::quad_words,data::bank_patterns,storage);
    map_terrain_quads(mapping,TerrainMapView{foreground},services);
    map_terrain_quads(mapping,TerrainMapView{background},services);
    storage.copy_patterns(data::common_patterns,0x594);
    // Zero word at B2A0 followed by127 fill bytes with increment1 covers B2A0..B31F.
    // This is the completed native byte effect, not a hardware DMA implementation.
    std::fill(storage.pixels.begin()+0xb2a0,storage.pixels.begin()+0xb320,0);
    return mapping;
}
}
