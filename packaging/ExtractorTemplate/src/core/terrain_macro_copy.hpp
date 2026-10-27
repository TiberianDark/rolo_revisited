#pragma once
#include <cstdint>
#include <span>
#include <stdexcept>
namespace rolo {
enum class TerrainCopyMode {Replace,OnlyEmpty,OrderedMetadata};
struct TerrainMacroCopy {
    std::span<const std::uint16_t> tiles;
    std::uint8_t width{},height{};
    std::uint16_t column_byte{},ring_row{},row_mask{},metadata_separation{},metadata{};
    bool flagged{};
    TerrainCopyMode mode{TerrainCopyMode::Replace};
};
// $44C4/$4536/$45B4 bodies, with $446C handoffs represented as native data.
// Backing contains both tile words and the parallel record-offset words.
inline void copy_terrain_macro(std::span<std::uint8_t> backing,const TerrainMacroCopy& input) {
    const auto count=static_cast<std::size_t>(input.width)*input.height;
    if(!input.width||!input.height||input.tiles.size()!=count)
        throw std::invalid_argument("Unproved terrain macro dimensions/data extent");
    auto read=[&](std::size_t offset) {
        if(offset+2>backing.size())throw std::out_of_range("Native terrain macro word extent");
        return static_cast<std::uint16_t>((backing[offset]<<8)|backing[offset+1]);
    };
    auto write=[&](std::size_t offset,std::uint16_t value) {
        if(offset+2>backing.size())throw std::out_of_range("Native terrain macro word extent");
        backing[offset]=static_cast<std::uint8_t>(value>>8);backing[offset+1]=static_cast<std::uint8_t>(value);
    };
    const auto width_bytes=static_cast<std::uint16_t>(input.width*2-2);
    auto row=static_cast<std::uint16_t>(input.ring_row+(input.height-1)*128);
    std::size_t source=input.flagged?0:count;
    for(unsigned y=0;y<input.height;++y) {
        row=static_cast<std::uint16_t>(row&input.row_mask);
        auto column=static_cast<std::uint16_t>(input.column_byte+(input.flagged?0:width_bytes));
        for(unsigned x=0;x<input.width;++x) {
            column=static_cast<std::uint16_t>(column&0x7e);
            auto tile=input.flagged?input.tiles[source++]:input.tiles[--source];
            const auto offset=static_cast<std::size_t>(row)+column;
            if(tile) {
                const auto metadata_offset=offset+input.metadata_separation;
                bool allowed=true;
                if(input.mode==TerrainCopyMode::OnlyEmpty)allowed=read(offset)==0;
                else if(input.mode==TerrainCopyMode::OrderedMetadata)allowed=input.metadata>=read(metadata_offset);
                if(allowed) {
                    if(input.flagged)tile^=0x1000;
                    write(offset,tile);write(metadata_offset,input.metadata);
                }
            }
            column=static_cast<std::uint16_t>(input.flagged?column+2:column-2);
        }
        row=static_cast<std::uint16_t>(row-128);
    }
}
}
