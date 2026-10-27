#pragma once
#include "core/world_map.hpp"
#include "core/world_tile_animation_data.hpp"
#include <array>
namespace rolo {
using WorldMapRgba=std::vector<std::uint8_t>;
// Original plane priorities: B low, A low, B high, A high.
inline WorldMapRgba raster_world_map(std::span<const std::uint8_t> flags,int origin_x,int origin_y,std::span<const std::uint16_t> palette={},unsigned viewport_width=320,unsigned animation_tick=0){
    if(viewport_width!=320&&viewport_width!=400)throw std::invalid_argument("World viewport width");
    auto background=generate_world_map_background(flags);
    std::vector<std::uint8_t> indices(viewport_width*224);
    auto paint=[&](std::span<const std::uint8_t> map,bool priority){
        const unsigned rows=world_map_word(map,6)/16;
        for(unsigned row=0;row<rows;++row){
            const auto start=world_map_word(map,8+row*2),end=world_map_word(map,10+row*2);
            for(unsigned at=start;at<end;at+=4){
                const auto type=world_map_word(map,at);if(type>=0x400)continue;
                const unsigned offset=world_map_word(world_map_data::macros,6+(type&127)*2);
                const auto width=world_map_data::macros[offset],height=world_map_data::macros[offset+1];
                const int base_x=world_map_word(map,at+2)-origin_x,base_y=static_cast<int>(row*16)-origin_y;
                if(base_x>=int(viewport_width)||base_x+width*16<=0||base_y>=224||base_y+height*16<=0)continue;
                for(unsigned my=0;my<height;++my)for(unsigned mx=0;mx<width;++mx){
                    const auto original=world_map_word(world_map_data::macros,offset+2+(my*width+mx)*2);
                    if(!original)continue;
                    const bool macro_flip=(type&0xff00)!=0;
                    const auto value=static_cast<std::uint16_t>(original|(macro_flip?0x1000:0));
                    const unsigned quad=value&511;
                    const auto data=quad<28?std::span<const std::uint8_t>(world_map_data::common_quads):std::span<const std::uint8_t>(world_map_data::quads);
                    const unsigned quad_offset=(quad<28?quad:quad-28)*8;
                    for(unsigned py=0;py<16;++py)for(unsigned px=0;px<16;++px){
                        const int x=base_x+mx*16+px,y=base_y+(macro_flip?height-1-my:my)*16+py;
                        if(x<0||x>=int(viewport_width)||y<0||y>=224)continue;
                        const unsigned qx=(value&0x800)?15-px:px,qy=(value&0x1000)?15-py:py;
                        const auto tile=static_cast<std::uint16_t>(world_map_word(data,quad_offset+((qy/8)*2+qx/8)*2)|(value&0xfe00));
                        if(static_cast<bool>(tile&0x8000)!=priority)continue;
                        const unsigned pattern=tile&2047,sx=(tile&0x800)?7-px%8:px%8,sy=(tile&0x1000)?7-py%8:py%8;
                        if(quad<28&&pattern>=1&&pattern<=4)continue;
                        const auto patterns=quad<28?std::span<const std::uint8_t>(world_map_data::common_patterns):std::span<const std::uint8_t>(world_map_data::graphics);
                        const unsigned byte=pattern*32+sy*4+sx/2;
                        if(byte>=patterns.size())throw std::out_of_range("World bank pattern");
                        unsigned ink=(patterns[byte]>>(sx&1?0:4))&15;
                        // Original FAA0 bank0 publishes into the bank-local quad cache.
                        // MAP artwork contains diagnostic letters until these two uploads.
                        for(const auto& track:world_tile_animation_data::tracks){
                            if(quad!=28+track.cache_byte_offset/8)continue;
                            const auto cursor=((animation_tick?animation_tick-1:0)/(track.delay+1))%track.sequence_count;
                            const auto frame=world_tile_animation_data::sequences[track.sequence_first+cursor];
                            const auto tile_index=(qy/8)*2+qx/8;
                            const auto address=track.first+frame*128+tile_index*32+sy*4+sx/2;
                            ink=(world_tile_animation_data::patterns.at(address)>>(sx&1?0:4))&15;
                        }
                        if(ink)indices[y*viewport_width+x]=static_cast<std::uint8_t>(((tile>>13)&3)*16+ink);
                    }
                }
            }
        }
    };
    paint(background,false);paint(world_map_data::foreground,false);
    paint(background,true);paint(world_map_data::foreground,true);
    WorldMapRgba out(viewport_width*224*4);
    for(unsigned p=0;p<indices.size();++p){const auto word=palette.empty()?world_map_word(world_map_data::palette,indices[p]*2):palette[indices[p]];
        out[p*4]=static_cast<std::uint8_t>(((word>>1)&7)*255/7);
        out[p*4+1]=static_cast<std::uint8_t>(((word>>5)&7)*255/7);
        out[p*4+2]=static_cast<std::uint8_t>(((word>>9)&7)*255/7);out[p*4+3]=255;}
    return out;
}
}
