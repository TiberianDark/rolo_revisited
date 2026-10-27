#pragma once
#include "core/world_map_data.hpp"
#include <algorithm>
#include <span>
#include <stdexcept>
#include <vector>
namespace rolo {
inline std::array<std::uint16_t,4> world_map_absent_edges{};
inline std::array<std::uint16_t,4> world_map_missing_next_to_present{};
inline std::array<std::uint16_t,4> world_map_present_next_to_missing{};
inline std::uint16_t world_map_word(std::span<const std::uint8_t> bytes,unsigned at){
    if(at+1>=bytes.size())throw std::out_of_range("World MAP read");return static_cast<std::uint16_t>((bytes[at]<<8)|bytes[at+1]);
}
inline void world_map_put_word(std::vector<std::uint8_t>& bytes,unsigned at,std::uint16_t value){
    if(at+2>bytes.size())bytes.resize(at+2);bytes[at]=static_cast<std::uint8_t>(value>>8);bytes[at+1]=static_cast<std::uint8_t>(value);
}
inline std::uint8_t world_map_selector_at(std::uint16_t x,std::uint16_t y){
    const int row=static_cast<int>(y>>6)-4;
    if(row<0||row>=12)throw std::out_of_range("World route row");
    for(const auto&p:world_map_data::pieces)if(p.group==row/4&&p.row==row%4&&
            static_cast<int>(x>>6)-p.xbase==p.column)return p.selector;
    throw std::out_of_range("World route column");
}
struct WorldMapCursor {std::uint16_t x=280,y=472,target_x=280,target_y=472;};
struct WorldMapCamera {std::uint16_t x{},y{};};
inline std::vector<std::array<std::uint16_t,2>> completed_world_map_nodes(std::span<const std::uint8_t> flags){
    std::vector<std::array<std::uint16_t,2>> result;
    const auto map=std::span<const std::uint8_t>(world_map_data::foreground);
    for(unsigned row=0;row<world_map_word(map,6)/16;++row){
        for(unsigned at=world_map_word(map,8+row*2);at<world_map_word(map,10+row*2);at+=4){
            if((world_map_word(map,at)>>8)!=14)continue;
            const auto x=static_cast<std::uint16_t>(world_map_word(map,at+2)+5),y=static_cast<std::uint16_t>(row*16);
            const auto selector=world_map_selector_at(x,y);
            if(selector>=flags.size())throw std::out_of_range("Completed world node flag");
            if(flags[selector]&2)result.push_back({x,y});
        }
    }
    return result;
}
// $9E3A: literal signed lower-then-upper clamps, in that order.
inline WorldMapCamera initialize_world_map_camera(const WorldMapCursor& cursor,std::uint16_t width,std::uint16_t height){
    auto clamp=[](std::uint16_t coordinate,int half,int upper){
        auto value=static_cast<std::int16_t>(static_cast<std::uint16_t>(coordinate-half));
        if(value<224)value=224;
        const auto limit=static_cast<std::int16_t>(static_cast<std::uint16_t>(upper));
        if(value>limit)value=limit;
        return static_cast<std::uint16_t>(value);
    };
    return {clamp(cursor.x,160,width-544),clamp(cursor.y,112,height-448)};
}
// $A50A: returning from a nonnegative selector always earns its puzzle bit.
inline void apply_world_map_completion(std::int16_t selector,std::span<std::uint8_t> flags,WorldMapCursor& cursor){
    if(selector<0)return;
    if(static_cast<unsigned>(selector)>=flags.size()||selector>=80)throw std::out_of_range("World completion selector");
    flags[selector]|=1;
    const auto x=world_map_data::return_coordinates[selector*2];if(x==255)return;
    const auto y=world_map_data::return_coordinates[selector*2+1];
    cursor.x=cursor.target_x=static_cast<std::uint16_t>(x*16-8);
    cursor.y=cursor.target_y=static_cast<std::uint16_t>(y*16-8);
}
// $A608: two-bit edge shape and the neighboring completion flag choose its macro.
inline std::uint16_t world_map_edge_macro(const world_map_data::Piece& piece,unsigned direction,std::span<const std::uint8_t> flags){
    if(direction>=4||piece.selector>=flags.size())throw std::out_of_range("World edge domain");
    const bool present=(flags[piece.selector]&1)!=0;
    const auto shape=(piece.edges>>(direction*2))&3;
    bool neighbor=false;
    if(shape==2){const auto index=piece.neighbors[direction];if(index>=flags.size())throw std::out_of_range("World neighbor flag");neighbor=(flags[index]&1)!=0;}
    if(!present)return shape==2&&neighbor?world_map_missing_next_to_present[direction]:world_map_absent_edges[direction];
    return shape==2&&!neighbor?world_map_present_next_to_missing[direction]:0;
}
// A744: emit two original type/X records per puzzle column.
inline void append_jigsaw_pair_row(std::vector<std::uint8_t>& map,unsigned& record,
        unsigned stride,unsigned xbase,unsigned first_delta,unsigned second_delta){
    auto x=static_cast<std::uint16_t>(xbase<<6);
    for(unsigned col=0;col<stride;++col){
        world_map_put_word(map,record,0x1700);world_map_put_word(map,record+2,x);record+=4;
        x=static_cast<std::uint16_t>(x+first_delta);
        world_map_put_word(map,record,0x1700);world_map_put_word(map,record+2,x);record+=4;
        x=static_cast<std::uint16_t>(x+second_delta);
    }
}
// A720: five records per column, with the third sparse row stored last.
inline void append_jigsaw_five_records(std::vector<std::uint8_t>& map,unsigned& record,
        unsigned stride,unsigned xbase){
    append_jigsaw_pair_row(map,record,stride,xbase,16,48);
    append_jigsaw_pair_row(map,record,stride,xbase,48,16);
    auto x=static_cast<std::uint16_t>(xbase<<6);
    for(unsigned col=0;col<stride;++col){
        x=static_cast<std::uint16_t>(x+16);
        world_map_put_word(map,record,0x1700);world_map_put_word(map,record+2,x);record+=4;
        x=static_cast<std::uint16_t>(x+48);
    }
}
// A6C0: fixed original sparse row table and unmasked record template.
inline std::vector<std::uint8_t> build_world_jigsaw_template(){
    std::vector<std::uint8_t> map(world_map_data::foreground.begin(),world_map_data::foreground.begin()+8);
    unsigned record=world_map_word(world_map_data::foreground,8),table=8;
    auto offset=[&](unsigned value){world_map_put_word(map,table,static_cast<std::uint16_t>(value));table+=2;};
    for(unsigned row=0;row<16;++row)offset(record);
    for(unsigned group=0;group<3;++group){
        const auto& first=*std::find_if(world_map_data::pieces.begin(),world_map_data::pieces.end(),[&](auto&p){return p.group==group;});
        for(unsigned row=0;row<4;++row){
            const unsigned start=record;
            append_jigsaw_five_records(map,record,first.stride,first.xbase);
            offset(start);offset(start+first.stride*8);
            offset(start+first.stride*16);offset(start+first.stride*16);
        }
    }
    for(unsigned row=0;row<17;++row)offset(record);
    if(table!=world_map_word(world_map_data::foreground,8))throw std::logic_error("World MAP row table extent");
    return map;
}
// A57A: apply completion and neighbor edge masks to the canonical template.
inline void apply_world_jigsaw_masks(std::vector<std::uint8_t>& map,std::span<const std::uint8_t> flags){
    if(flags.size()<80)throw std::out_of_range("World progress array");
    for(const auto&p:world_map_data::pieces){
        const unsigned row=16+p.group*16+p.row*4;
        const unsigned start=world_map_word(map,8+row*2),center=start+p.column*8;
        if(!(flags[p.selector]&1))world_map_put_word(map,center,0);
        const std::array<unsigned,4> addresses{center+p.stride*8+4,center+p.stride*8,
            center+p.stride*16-p.column*4,center+4};
        for(unsigned direction=0;direction<4;++direction){
            const auto value=world_map_edge_macro(p,direction,flags);
            if(value)world_map_put_word(map,addresses[direction],value);
        }
    }
}
// A558: copy header, build A6C0 template, then run A57A mask stage.
inline std::vector<std::uint8_t> generate_world_map_background(std::span<const std::uint8_t> flags){
    auto map=build_world_jigsaw_template();apply_world_jigsaw_masks(map,flags);return map;
}
}
