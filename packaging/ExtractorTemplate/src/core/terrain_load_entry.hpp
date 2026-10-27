#pragma once
#include "core/native_level_assets.hpp"
#include "core/display_setup.hpp"
namespace rolo {
enum class TerrainLoadStep{ResetPlanes,ClearSprites,ResetWordQueue,ResetByteQueue,ClearForeground,ClearBackground,EmptyMenu,SelectForeground,SelectBackground,InitializePlanes,PublishMenu};
struct TerrainLoadState{std::uint8_t flag{};std::uint16_t next_pattern=1;};
struct TerrainLoadServices{virtual ~TerrainLoadServices()=default;virtual void step(TerrainLoadStep)=0;virtual void initial_fill(std::uint16_t,std::uint16_t,std::uint32_t,std::uint16_t)=0;virtual void common_transfer(GraphicsTransferRequest)=0;virtual void final_fill(std::uint16_t,std::uint16_t,std::uint32_t)=0;};
inline TerrainQuadMapping load_native_terrain_entry(TerrainLoadState&s,const NativeLevelAssets&assets,TerrainPatternStorage&storage,TerrainLoadServices&v){
 s.flag=0;for(auto op:{TerrainLoadStep::ResetPlanes,TerrainLoadStep::ClearSprites,TerrainLoadStep::ResetWordQueue,TerrainLoadStep::ResetByteQueue,TerrainLoadStep::ClearForeground,TerrainLoadStep::ClearBackground,TerrainLoadStep::EmptyMenu,TerrainLoadStep::SelectForeground,TerrainLoadStep::SelectBackground,TerrainLoadStep::InitializePlanes,TerrainLoadStep::PublishMenu})v.step(op);v.initial_fill(0,119,0x40000080,32);
 const auto&bank=assets.terrain_bank();TerrainQuadMapping mapping(s.next_pattern);ImmutableTerrainQuadServices services(bank.macros,bank.quads,bank.patterns,storage);map_terrain_quads(mapping,TerrainMapView{assets.map},services);map_terrain_quads(mapping,TerrainMapView{assets.background},services);s.next_pattern=mapping.next_pattern;storage.copy_patterns(level1_terrain_data::common_patterns,0x594);v.common_transfer({0x53dc2,0xb280,0x40000080,0x6b0});std::fill(storage.pixels.begin()+0xb2a0,storage.pixels.begin()+0xb320,0);v.final_fill(0xb2a0,127,0x40000000);return mapping;
}
}
