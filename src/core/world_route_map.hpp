#pragma once
#include "core/world_route.hpp"
#include "core/world_route_data.hpp"
#include "core/world_map.hpp"
#include "core/actor_terrain.hpp"
#include "core/terrain_pattern_storage.hpp"
#include "core/terrain_camera_world.hpp"
namespace rolo {
// Original foreground metatile ring, shared pattern allocator and typed display.
// This adapter owns data/publications, never a CPU or hardware port executor.
struct WorldRouteMap final:WorldRouteServices,TerrainDescriptorServices {
    std::span<const std::uint8_t> flags;
    std::array<std::uint8_t,16384> backing{};
    std::vector<std::uint8_t> map,background;
    std::vector<std::vector<std::uint16_t>> macro_tiles;
    std::vector<TerrainMacroDefinition> macro_definitions;
    std::vector<std::uint16_t> quad_words;
    TerrainPatternStorage patterns;
    TerrainQuadMapping mapping{1}; // original world initializer1B52 F264=1
    TerrainMappedDisplay display{mapping};
    ActorState plane;TerrainCameraGlobals globals;
    std::uint16_t x_shift{};
    explicit WorldRouteMap(std::span<const std::uint8_t> progress):flags(progress){
        if(flags.size()<80)throw std::out_of_range("World route progress domain");
        map.assign(world_map_data::foreground.begin(),world_map_data::foreground.end());map.resize(map.size()+4);
        background=generate_world_map_background(flags);background.resize(background.size()+4);
        const auto count=world_map_word(world_map_data::macros,4);macro_tiles.resize(count);macro_definitions.resize(count);
        for(unsigned i=0;i<count;++i){const auto at=world_map_word(world_map_data::macros,6+i*2);
            const auto w=world_map_data::macros[at],h=world_map_data::macros[at+1];auto& tiles=macro_tiles[i];
            for(unsigned n=0;n<w*h;++n)tiles.push_back(world_map_word(world_map_data::macros,at+2+n*2));
            macro_definitions[i]={w,h,tiles};
        }
        for(unsigned i=0;i<world_map_data::common_quads.size();i+=2)quad_words.push_back(world_map_word(world_map_data::common_quads,i));
        for(unsigned i=0;i<world_map_data::quads.size();i+=2)quad_words.push_back(world_map_word(world_map_data::quads,i));
        ImmutableTerrainQuadServices quads(macro_definitions,quad_words,world_map_data::graphics,patterns);
        map_terrain_quads(mapping,TerrainMapView{map},quads);
        map_terrain_quads(mapping,TerrainMapView{background},quads);
        patterns.copy_patterns(world_map_data::common_patterns,0x594);
        std::fill(patterns.pixels.begin()+0xb2a0,patterns.pixels.begin()+0xb320,0);
        plane.word(4,64);plane.word(6,6);plane.word(8,0x1f80);plane.word(10,0x3f0);
        plane.word(12,0x1f80);plane.word(14,0x2000);plane.word(22,0xffff);
        plane.word(40,world_map_word(world_map_data::foreground,6));
    }
    WorldRouteMap(const WorldRouteMap&)=delete;
    WorldRouteMap& operator=(const WorldRouteMap&)=delete;
    TerrainMacroDefinition terrain_macro(std::uint8_t index)override{
        if(index>=macro_definitions.size())throw std::out_of_range("World original macro selector");return macro_definitions[index];
    }
    std::uint16_t terrain_macro_byte_count(std::uint8_t index)override{
        const auto macro=terrain_macro(index);return static_cast<std::uint16_t>(macro.width*macro.height*2);
    }
    void terrain_special_descriptor(const TerrainDescriptorRecord& record,std::uint16_t)override{
        // MAP0's highbyte0E dispatches $4694 -> $4904, literal RTS.
        if((record.type>>8)==0x0e)return;
        throw std::logic_error("Unbound world special descriptor");
    }
    void stream(std::uint16_t camera_x,std::uint16_t camera_y){
        plane.word(18,camera_x);plane.word(20,camera_y);
        TerrainStreamingCameraServices native(backing,TerrainMapView{map},*this,display,true);
        update_foreground_terrain_camera(plane,globals,native);
    }
    std::uint16_t route_tile(std::uint16_t x,std::uint16_t y)override{
        return actor_terrain_word(ActorTerrain{backing,{},{},x_shift},x,y);
    }
    bool route_section_available(std::uint16_t x,std::uint16_t y)override{return (flags[world_map_selector_at(x,y)]&1)!=0;}
    WorldRouteDescriptor route_descriptor(unsigned byte_offset)override{
        if(byte_offset%6||byte_offset/6>=world_route_data::descriptors.size())throw std::out_of_range("World six-byte route descriptor offset");
        const auto& d=world_route_data::descriptors[byte_offset/6];return {d.pointer,d.negate_x,d.negate_y};
    }
    std::uint8_t route_byte(std::uint32_t pointer)override{
        if(pointer<world_route_data::pool_start||pointer>=world_route_data::pool_end)throw std::out_of_range("World bounded route byte pointer");
        return world_route_data::route_bytes[pointer-world_route_data::pool_start];
    }
};
}
