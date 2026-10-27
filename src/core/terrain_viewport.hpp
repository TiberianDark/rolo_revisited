#pragma once
#include "core/terrain_raster.hpp"
namespace rolo {
// Native plane pixels from the same streamed names used by the world. The two
// priority layers allow the host to place original actors between plane groups.
inline void raster_terrain_viewport(const TerrainPatternStorage& patterns,
        const TerrainMappedDisplay& display,std::span<const std::uint16_t> palette,
        std::uint16_t camera_x,std::uint16_t camera_y,unsigned width,unsigned height,
        std::span<std::uint8_t> low,std::span<std::uint8_t> high) {
    const auto size=static_cast<std::size_t>(width)*height*4;
    if(low.size()!=size||high.size()!=size)throw std::invalid_argument("Terrain viewport buffer extent");
    for(unsigned y=0;y<height;++y)for(unsigned x=0;x<width;++x){
        const auto pixel=terrain_plane_pixel(patterns,display,
            static_cast<std::uint16_t>(camera_x+x),static_cast<std::uint16_t>(camera_y+y));
        const auto rgba=terrain_pixel_rgba(pixel,palette);
        const auto at=(static_cast<std::size_t>(y)*width+x)*4;
        for(unsigned component=0;component<4;++component){
            low[at+component]=pixel.priority?0:rgba[component];
            high[at+component]=pixel.priority?rgba[component]:0;
        }
    }
}
}
