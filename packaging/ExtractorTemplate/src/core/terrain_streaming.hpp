#pragma once
#include "core/terrain_stream_rows.hpp"
#include "core/terrain_record_search.hpp"
#include <utility>
namespace rolo {
inline std::pair<std::uint16_t,std::uint16_t> terrain_map_row(TerrainMapView map,std::uint16_t row_index) {
    const auto start=map.word(8+row_index),end=map.word(10+row_index);
    if(signed_word(start)<0||signed_word(end)<0)throw std::invalid_argument("Unproved signed MAP offset domain");
    return {start,end};
}
// Native joining of $4158/$417A preparation, MAP spans, $422C/$4270 and copy.
inline unsigned stream_terrain_row(const ActorState& plane,std::span<std::uint8_t> backing,
        TerrainMapView map,std::uint16_t f374,std::uint16_t f2ca,bool bottom,TerrainDescriptorServices& services) {
    const auto row=prepare_terrain_stream_row(plane,backing,f374,bottom);
    if(!row.cleared||!row.within_height)return 0;
    const auto [start,end]=terrain_map_row(map,row.map_row_index);unsigned count=0;
    search_terrain_records(map,start,end,row.window_left,row.window_right,
        bottom?TerrainRecordSearch::ForwardWindow:TerrainRecordSearch::BackwardWindow,
        [&](const TerrainDescriptorRecord& record) {
            dispatch_terrain_descriptor(backing,plane,record,row.ring_cursor,f2ca,
                bottom?TerrainCopyMode::Replace:TerrainCopyMode::OnlyEmpty,services);++count;
        });
    return count;
}
// $42BC/$42E4 caller loop: clear column, predecrement budget, live MAP offsets.
inline unsigned stream_terrain_column(const ActorState& plane,std::span<std::uint8_t> backing,
        TerrainMapView map,std::uint16_t f374,std::uint16_t f2ca,bool right,TerrainDescriptorServices& services) {
    auto column=prepare_terrain_stream_column(plane,backing,f374,right);unsigned count=0;
    for(;;) {
        column.row_budget=static_cast<std::uint16_t>(column.row_budget-1);
        if(signed_word(column.row_budget)<0)return count;
        column.ring_cursor=static_cast<std::uint16_t>((column.ring_cursor+128)&plane.word(8));
        column.map_row_index=static_cast<std::uint16_t>(column.map_row_index+2);
        if(signed_word(column.map_row_index)<0)continue;
        const auto [start,end]=terrain_map_row(map,column.map_row_index);
        if(start==end)continue;
        if(column.map_row_index>=static_cast<std::uint16_t>(plane.word(40)>>3))return count;
        search_terrain_records(map,start,end,column.target_x,0,TerrainRecordSearch::ExactColumn,
            [&](const TerrainDescriptorRecord& record) {
                dispatch_terrain_descriptor(backing,plane,record,column.ring_cursor,f2ca,TerrainCopyMode::OrderedMetadata,services);++count;
            });
    }
}
// $4096: caller has already performed the $4020/$4030 backing clears.
inline unsigned fill_initial_terrain(const ActorState& plane,std::span<std::uint8_t> backing,
        TerrainMapView map,std::uint16_t f374,std::uint16_t f2ca,TerrainDescriptorServices& services) {
    auto row=static_cast<std::uint16_t>((plane.word(20)>>4)*2-18);
    auto cursor=static_cast<std::uint16_t>(f374-0x480);
    const auto aligned=static_cast<std::uint16_t>(plane.word(18)&0xfff0);
    const auto left=static_cast<std::uint16_t>(aligned<0x160?0:aligned-0x160);
    const auto right=static_cast<std::uint16_t>(left+0x400);
    auto budget=static_cast<std::uint16_t>(plane.word(4)-7);unsigned count=0;
    for(;;) {
        budget=static_cast<std::uint16_t>(budget-1);if(signed_word(budget)<0)return count;
        do {cursor=static_cast<std::uint16_t>((cursor+128)&plane.word(8));row=static_cast<std::uint16_t>(row+2);}
        while(signed_word(row)<0); // Initial negative rows do not consume another budget unit.
        const auto [start,end]=terrain_map_row(map,row);
        if(start==end)continue;
        if(row>=static_cast<std::uint16_t>(plane.word(40)>>3))return count;
        search_terrain_records(map,start,end,left,right,TerrainRecordSearch::ForwardWindow,
            [&](const TerrainDescriptorRecord& record) {
                if(dispatch_initial_terrain_descriptor(backing,plane,record,cursor,f2ca,right,services))++count;
            });
    }
}
}
