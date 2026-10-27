#pragma once
#include "core/level1_companion_menu_data.hpp"
#include <algorithm>
#include <array>
#include <span>
#include <stdexcept>
#include <vector>
namespace rolo {
struct CompanionMenuSprite {std::uint16_t y{},size_link{},attribute{},x{};};
struct CompanionMenuPortrait {bool present{};std::uint16_t tile{},width{};std::uint8_t height{};};
inline std::uint16_t companion_menu_word(std::span<const std::uint8_t> bytes,unsigned offset){
    if(offset+1>=bytes.size())throw std::out_of_range("Menu immutable word");
    return static_cast<std::uint16_t>((bytes[offset]<<8)|bytes[offset+1]);
}
inline CompanionMenuSprite companion_menu_sprite(std::span<const std::uint8_t> data,unsigned offset){
    return {companion_menu_word(data,offset),companion_menu_word(data,offset+2),
        companion_menu_word(data,offset+4),companion_menu_word(data,offset+6)};
}
// $3CA2 resident graphics, with original blank pattern publication at B2A0.
inline void install_companion_menu_patterns(std::span<std::uint8_t> vram){
    if(vram.size()<65536)throw std::out_of_range("Menu needs original VRAM pattern namespace");
    std::copy(level1_companion_menu_data::patterns.begin(),level1_companion_menu_data::patterns.end(),vram.begin()+0xb280);
    std::fill_n(vram.begin()+0xb2a0,128,0);
}
// $3934 order, omitting only the separately captured five status sprites.
inline std::vector<CompanionMenuSprite> companion_menu_sprites(unsigned selection,std::uint8_t controlled,
        const std::array<CompanionMenuPortrait,3>& portraits){
    if(selection>=6)throw std::out_of_range("Menu selector");
    std::vector<CompanionMenuSprite> out;
    for(unsigned n=0;n<4;++n)out.push_back(companion_menu_sprite(level1_companion_menu_data::selection_sprites,selection*32+n*8));
    for(unsigned n=0;n+7<level1_companion_menu_data::static_sprites.size();n+=8){
        if(companion_menu_word(level1_companion_menu_data::static_sprites,n)&0x8000)break;
        out.push_back(companion_menu_sprite(level1_companion_menu_data::static_sprites,n));
    }
    if(controlled)for(unsigned n=0;n<3;++n)if(2-n!=static_cast<unsigned>(controlled-1))
        out.push_back(companion_menu_sprite(level1_companion_menu_data::inactive_sprites,n*8));
    for(unsigned n=0;n<3;++n)if(portraits[n].present){
        const auto& p=portraits[n];auto sprite=companion_menu_sprite(level1_companion_menu_data::companion_sprites,n*8);
        const auto w=std::min<unsigned>(p.width&255,32),h=std::min<unsigned>(p.height,32);
        if(!w||!h)throw std::out_of_range("Menu portrait dimensions");
        // Original dimensions derive the hardware size nibble, then center.
        sprite.size_link=static_cast<std::uint16_t>((((w-1)/8)*4+(h-1)/8)<<8);
        sprite.attribute=static_cast<std::uint16_t>(p.tile|sprite.attribute);
        sprite.y=static_cast<std::uint16_t>(sprite.y+(32-w)/2);
        sprite.x=static_cast<std::uint16_t>(sprite.x+(32-h)/2);
        out.push_back(sprite);
    }
    return out;
}
// Output CRAM indices0..63, transparent sprite pixels retain the plane color.
// Caller supplies all resident palettes; the menu fade touches banks0/1 only.
inline std::array<std::uint8_t,320*224> raster_companion_menu(std::span<const std::uint8_t> vram,
        unsigned selection,std::uint8_t controlled,const std::array<CompanionMenuPortrait,3>& portraits){
    if(vram.size()<65536)throw std::out_of_range("Menu VRAM domain");
    std::array<std::uint8_t,320*224> image{};
    auto pixel=[&](unsigned tile,unsigned x,unsigned y){const auto b=vram[(tile&0x7ff)*32+y*4+x/2];return static_cast<unsigned>((x&1)?b&15:b>>4);};
    for(unsigned y=0;y<224;++y)for(unsigned x=0;x<320;++x){
        const auto word=static_cast<std::uint16_t>(companion_menu_word(level1_companion_menu_data::layout,((y/8)*40+x/8)*2)+0xe5dd);
        const auto px=(word&0x800)?7-x%8:x%8,py=(word&0x1000)?7-y%8:y%8;
        image[y*320+x]=static_cast<std::uint8_t>(((word>>13)&3)*16+pixel(word,px,py));
    }
    auto sprites=companion_menu_sprites(selection,controlled,portraits);
    // Earlier SAT entries win, so paint the list backwards.
    for(auto it=sprites.rbegin();it!=sprites.rend();++it){const auto&s=*it;
        const unsigned columns=((s.size_link>>10)&3)+1,rows=((s.size_link>>8)&3)+1;
        for(unsigned y=0;y<rows*8;++y)for(unsigned x=0;x<columns*8;++x){
            const int dx=static_cast<int>(s.x)-128+x,dy=static_cast<int>(s.y)-128+y;
            if(dx<0||dy<0||dx>=320||dy>=224)continue;
            const unsigned px=(s.attribute&0x800)?columns*8-1-x:x,py=(s.attribute&0x1000)?rows*8-1-y:y;
            const auto ink=pixel(s.attribute+(px/8)*rows+py/8,px%8,py%8);
            if(ink)image[dy*320+dx]=static_cast<std::uint8_t>(((s.attribute>>13)&3)*16+ink);
        }
    }
    return image;
}
}
