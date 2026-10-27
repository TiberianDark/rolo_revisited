#pragma once
#include "core/actor_state.hpp"
#include <span>
#include <stdexcept>
namespace rolo {
struct TerrainRowPreparation {
    bool cleared{},within_height{};
    std::uint16_t map_row_index{},ring_cursor{},window_left{},window_right{};
};
// $4158/$417A through $4210: original two-row clears before MAP traversal.
// ActorState is used only as a checked big-endian byte record for the plane descriptor.
inline TerrainRowPreparation prepare_terrain_stream_row(const ActorState& descriptor,
        std::span<std::uint8_t> backing,std::uint16_t f374,bool entering_bottom) {
    auto row=static_cast<std::uint16_t>((descriptor.word(20)>>4)*2);
    std::uint16_t cursor{},clear_end{};
    if(!entering_bottom) {
        row=static_cast<std::uint16_t>(row-16);
        if(signed_word(row)<0)return {false,false,row};
        cursor=static_cast<std::uint16_t>(f374-0x400);clear_end=cursor;
    } else {
        row=static_cast<std::uint16_t>(row+descriptor.word(6)*2+28);
        cursor=static_cast<std::uint16_t>(((descriptor.word(6)+14)<<7)+f374);
        clear_end=static_cast<std::uint16_t>(cursor+0x380);
    }
    clear_end=static_cast<std::uint16_t>((clear_end&descriptor.word(8))+0x80);
    const auto clear_start=static_cast<std::size_t>(clear_end)-128;
    const auto second=clear_start+descriptor.word(14);
    if(clear_end<128||clear_start+128>backing.size()||second+128>backing.size())
        throw std::out_of_range("Native terrain backing row extent");
    for(std::size_t n=0;n<128;++n)backing[clear_start+n]=0;
    for(std::size_t n=0;n<128;++n)backing[second+n]=0;
    const bool valid=row<static_cast<std::uint16_t>(descriptor.word(40)>>3);
    if(!valid)return {true,false,row,cursor};
    const auto aligned=static_cast<std::uint16_t>(descriptor.word(18)&0xfff0);
    const auto left=static_cast<std::uint16_t>(aligned<0x160?0:aligned-0x160);
    return {true,true,row,cursor,left,static_cast<std::uint16_t>(left+0x310)};
}
struct TerrainColumnPreparation {
    std::uint16_t map_row_index{},ring_cursor{},target_x{},column_byte{},row_budget{};
};
// $42BC/$42E4 through $43B2: clear one word in each backing row before refill.
inline TerrainColumnPreparation prepare_terrain_stream_column(const ActorState& descriptor,
        std::span<std::uint8_t> backing,std::uint16_t f374,bool entering_right) {
    const auto row=static_cast<std::uint16_t>((descriptor.word(20)>>4)*2-18);
    const auto cursor=static_cast<std::uint16_t>(f374-0x480);
    const auto target=static_cast<std::uint16_t>(entering_right?
        (descriptor.word(18)&0xfff0)+0x1a0:(descriptor.word(18)-0x160)&0xfff0);
    const auto clear_x=static_cast<std::uint16_t>(target+(entering_right?0xf0:0));
    const auto column=static_cast<std::uint16_t>((clear_x>>3)&0x7e);
    // DBF executes at least once even when the shifted row count is zero.
    const auto blocks=descriptor.word(4)>>4;
    const auto iterations=blocks?static_cast<std::size_t>(blocks):65536u;
    const auto rows=iterations*32;
    if(column+(rows-1)*128+2>backing.size())throw std::out_of_range("Native terrain backing column extent");
    for(std::size_t n=0;n<rows;++n){backing[column+n*128]=0;backing[column+n*128+1]=0;}
    return {row,cursor,target,column,static_cast<std::uint16_t>(descriptor.word(4)-7)};
}
}
