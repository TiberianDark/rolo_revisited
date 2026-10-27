#pragma once
#include "core/level1_terrain_data.hpp"
#include "core/terrain_raster.hpp"
#include "core/all_native_level_data.hpp"
namespace rolo {
// Dynamic macro84 artwork comes from terrain quads, not an immutable actor
// graphics pointer. Use its original indexed pixels and the live sprite bank.
inline void raster_dynamic_macro(const all_native_level_data::TerrainBank& terrain,unsigned index,unsigned bank,std::span<const std::uint16_t> palette,std::span<std::uint8_t> rgba){
 if(index>=terrain.macros.size()||bank>3)throw std::out_of_range("Forest macro index");
 const auto macro=terrain.macros[index];const unsigned width=macro.width*16,height=macro.height*16;
 if(rgba.size()!=width*height*4)throw std::out_of_range("Forest macro raster extent");
 for(unsigned y=0;y<height;++y)for(unsigned x=0;x<width;++x){
  const auto quad=macro.tiles[(y/16)*macro.width+x/16]&511;
  const auto tile=terrain.quads[quad*4+(y%16/8)*2+x%16/8]&2047;
  const auto packed=terrain.patterns[tile*32+(y%8)*4+(x%8)/2];
  const auto ink=std::uint8_t((packed>>(x&1?0:4))&15);
  const auto color=terrain_pixel_rgba({std::uint8_t(ink?bank*16+ink:0),false,ink!=0},palette);
  std::copy(color.begin(),color.end(),rgba.begin()+(y*width+x)*4);
 }
}
inline void raster_forest_macro(unsigned index,unsigned bank,std::span<const std::uint16_t> palette,std::span<std::uint8_t> rgba){raster_dynamic_macro(all_native_level_data::bank(1),index,bank,palette,rgba);}
inline void raster_forest_log(unsigned bank,std::span<const std::uint16_t> palette,std::span<std::uint8_t> rgba){raster_forest_macro(84,bank,palette,rgba);}
}
