#pragma once
#include "core/actor_pattern_data.hpp"
#include "core/terrain_raster.hpp"
namespace rolo {
inline void raster_actor_patterns(std::span<const std::uint8_t> patterns,unsigned width,unsigned height,
        unsigned bank,std::span<const std::uint16_t> palette,std::span<std::uint8_t> rgba){
    if(!width||!height||width%8||height%8||bank>3||patterns.size()!=std::size_t(width)*height/2||rgba.size()!=std::size_t(width)*height*4)
        throw std::out_of_range("Native actor indexed raster extent");
    for(unsigned y=0;y<height;++y)for(unsigned x=0;x<width;++x){
        // 3396..343E:32px sprite chunks first, then tile columns inside each.
        const auto chunk_x=(x/32)*32,chunk_y=(y/32)*32;
        const auto chunk_height=std::min(32u,height-chunk_y);
        const auto tile=(chunk_y/8)*(width/8)+(chunk_x/8)*(chunk_height/8)+((x-chunk_x)/8)*(chunk_height/8)+(y-chunk_y)/8;
        const auto packed=patterns[tile*32+(y&7)*4+(x&7)/2];
        const auto ink=static_cast<std::uint8_t>((packed>>((x&1)?0:4))&15);
        const auto color=terrain_pixel_rgba({static_cast<std::uint8_t>(ink?bank*16+ink:0),false,ink!=0},palette);
        for(unsigned c=0;c<4;++c)rgba[(std::size_t(y)*width+x)*4+c]=color[c];
    }
}
inline void raster_actor_frame(std::uint32_t source,unsigned width,unsigned height,unsigned bank,
        std::span<const std::uint16_t> palette,std::span<std::uint8_t> rgba){
    for(const auto& frame:actor_pattern_data::frames)
        if(frame.source==source&&frame.width==width&&frame.height==height){
            raster_actor_patterns(std::span<const std::uint8_t>(actor_pattern_data::bytes).subspan(frame.offset,frame.size),width,height,bank,palette,rgba);return;
        }
    throw std::out_of_range("Unexported native actor indexed frame");
}
}
