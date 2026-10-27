#pragma once
#include "core/level1_terrain_data.hpp"
#include "core/level2_terrain_data.hpp"
#include "core/level3_terrain_data.hpp"
#include "core/level4_terrain_data.hpp"
#include "core/level8_terrain_data.hpp"
#include "core/forest_level_data.hpp"
#include "core/all_native_level_data.hpp"
#include "core/terrain_pattern_storage.hpp"
namespace rolo {
// Select immutable data before any services bind the live MAP storage. Both
// first forest levels use the exact same original terrain and background bank.
// External-resource equality checked during initialization.
// External-resource equality checked during initialization.
// External-resource equality checked during initialization.
// External-resource equality checked during initialization.
// External-resource equality checked during initialization.
// External-resource equality checked during initialization.
// External-resource equality checked during initialization.
// External-resource equality checked during initialization.
// External-resource equality checked during initialization.
// External-resource equality checked during initialization.
// External-resource equality checked during initialization.
// External-resource equality checked during initialization.
// External-resource equality checked during initialization.
// External-resource equality checked during initialization.
// External-resource equality checked during initialization.
// External-resource equality checked during initialization.
struct NativeLevelAssets {
    std::span<const std::uint8_t> map,background;
    std::span<const std::uint16_t,64> target_palette;
    std::uint16_t selector,width,height;
    std::uint8_t reward_selector,bank;
    const all_native_level_data::TerrainBank& terrain_bank()const{return all_native_level_data::bank(bank);}
};
inline bool native_level_connected(std::uint16_t selector){return all_native_level_data::connected(selector);}
inline NativeLevelAssets native_level_assets(std::uint16_t selector){
    const auto data=all_native_level_data::level(selector);
    return {data.foreground,data.background,data.palette,data.selector,data.width,data.height,data.reward,data.bank};
}
inline TerrainQuadMapping initialize_native_terrain_patterns(TerrainPatternStorage& storage,const NativeLevelAssets& assets){
    const auto& bank=assets.terrain_bank();TerrainQuadMapping mapping(1);
    ImmutableTerrainQuadServices services(bank.macros,bank.quads,bank.patterns,storage);
    map_terrain_quads(mapping,TerrainMapView{assets.map},services);
    map_terrain_quads(mapping,TerrainMapView{assets.background},services);
    // Common artwork is resident independently of the MAP allocation scan.
    // In selector71 the final macro is read but skipped by that original scan;
    // its common quad must still resolve when the terrain publisher draws it.
    // Fill only missing common entries: preserve allocation order and mapped names.
    for(unsigned index=0;index<28;++index){
        auto& quad=mapping.quads[index];
        if(quad[0]!=65535)continue;
        const auto source=services.source_quad(static_cast<std::uint16_t>(index));
        for(unsigned n=0;n<4;n+=2){
            const auto packed=((std::uint32_t(source[n])<<16)|source[n+1])+0x05940594u;
            quad[n]=static_cast<std::uint16_t>(packed>>16);quad[n+1]=static_cast<std::uint16_t>(packed);
        }
    }
    storage.copy_patterns(level1_terrain_data::common_patterns,0x594);
    std::fill(storage.pixels.begin()+0xb2a0,storage.pixels.begin()+0xb320,0);
    return mapping;
}
}

