#pragma once
#include "core/terrain_quad_mapping.hpp"
#include "core/terrain_display.hpp"
#include <algorithm>
namespace rolo {
// Decoded immutable artwork and native name-table storage. Queue timing is separate.
struct TerrainPatternStorage {
    std::array<std::uint8_t,2048*32> pixels{};
    void copy_patterns(std::span<const std::uint8_t> source,std::uint16_t destination) {
        const auto start=static_cast<std::size_t>(destination)*32;
        if(source.size()%32||start+source.size()>pixels.size())throw std::out_of_range("Native pattern upload extent");
        std::copy(source.begin(),source.end(),pixels.begin()+start);
    }
};
struct ImmutableTerrainQuadServices final:TerrainQuadServices {
    std::span<const TerrainMacroDefinition> macros;
    std::span<const std::uint16_t> words;
    std::span<const std::uint8_t> graphics;
    TerrainPatternStorage& storage;
    ImmutableTerrainQuadServices(std::span<const TerrainMacroDefinition> m,std::span<const std::uint16_t> w,
            std::span<const std::uint8_t> g,TerrainPatternStorage& s):macros(m),words(w),graphics(g),storage(s){}
    TerrainMacroDefinition quad_macro(std::uint8_t index) override {
        if(index>=macros.size())throw std::out_of_range("Native macro bank extent");return macros[index];
    }
    std::array<std::uint16_t,4> source_quad(std::uint16_t index) override {
        const auto first=static_cast<std::size_t>(index)*4;
        if(first+4>words.size())throw std::out_of_range("Native quad bank extent");
        return {words[first],words[first+1],words[first+2],words[first+3]};
    }
    void upload_terrain_pattern(std::uint16_t source,std::uint16_t destination) override {
        const auto first=static_cast<std::size_t>(source)*32;
        if(first+32>graphics.size())throw std::out_of_range("Native source pattern extent");
        storage.copy_patterns(graphics.subspan(first,32),destination);
    }
};
struct TerrainMappedDisplay final:TerrainDisplayServices {
    TerrainQuadMapping& mapping;
    std::array<std::uint16_t,2048> names{};
    explicit TerrainMappedDisplay(TerrainQuadMapping& m):mapping(m){}
    std::array<std::uint16_t,4> terrain_quad_patterns(std::uint16_t index) override {
        if(index>=mapping.quads.size())throw std::out_of_range("Native display quad extent");return mapping.quads[index];
    }
    void terrain_name_row(std::uint16_t offset,std::uint16_t left,std::uint16_t right) override {
        if(offset%2||static_cast<std::size_t>(offset)/2+2>names.size())throw std::out_of_range("Native name row extent");
        names[offset/2]=left;names[offset/2+1]=right;
    }
};
}
