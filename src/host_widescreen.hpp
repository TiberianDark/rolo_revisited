#pragma once
#include "core/level1_indexed_background_data.hpp"
#include "core/terrain_raster.hpp"
#include <algorithm>
#include <vector>
namespace rolo {
// Expanded viewport fits inside the original actor near range [-80,+400].
inline int wide_camera_x(int original,int map_width,unsigned width){return std::clamp(original-int(width-320)/2,0,std::max(0,map_width-int(width)));}
inline std::vector<std::uint8_t> wide_companion_menu(std::span<const std::uint8_t> original,unsigned width){
 if(original.size()!=320*224||width<320||width>400)throw std::invalid_argument("Wide menu extent");
 std::vector<std::uint8_t> image(width*224);const unsigned inset=(width-320)/2;
 for(unsigned y=0;y<224;++y)for(unsigned x=0;x<width;++x){
  // The original top 32 rows contain the repeating jigsaw backdrop only.
  image[y*width+x]=x>=inset&&x<inset+320?original[y*320+x-inset]:original[(y%32)*320+((x+32-inset%32)%32)];
 }return image;
}
// The original display publisher refreshes only 21 metatile columns. Extra
// widescreen pixels must use the current 64x64 terrain backing, rather than
// stale names left outside that original publication window. Keep this host
// display separate from collision, streaming state and the original name table.
inline TerrainMappedDisplay wide_terrain_display(std::span<const std::uint8_t> backing,TerrainQuadMapping& mapping,
        std::uint16_t x,std::uint16_t y,unsigned width,unsigned height){
 TerrainMappedDisplay display(mapping);
 const unsigned left=unsigned(x)&~15u,top=unsigned(y)&~15u;
 for(unsigned row=top;row<unsigned(y)+height;row+=16)for(unsigned column=left;column<unsigned(x)+width;column+=16){
  const auto offset=std::uint16_t(((column&0x3f0)>>3)+((row&0x3f0)<<3));
  display_terrain_cell(backing,offset,display);
 }return display;
}
inline std::vector<std::uint8_t> wide_forest_background(std::uint16_t x,std::span<const std::uint16_t>palette,unsigned width){
 std::vector<std::uint8_t> pixels(width*224*4);
 for(unsigned y=0;y<224;++y)for(unsigned column=0;column<width;++column){
  const auto index=level1_indexed_background_data::pixels[y*512+((x+column)&511)];auto rgba=terrain_pixel_rgba({index,false,true},palette);
  std::copy(rgba.begin(),rgba.end(),pixels.begin()+(y*width+column)*4);
 }return pixels;
}
}
