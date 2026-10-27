#pragma once
#include "core/terrain_descriptor.hpp"
#include <string>
namespace rolo {
struct TerrainMapView {
    std::span<const std::uint8_t> bytes;
    std::uint16_t word(std::ptrdiff_t offset) const {
        if(offset<0||static_cast<std::size_t>(offset)+2>bytes.size())throw std::out_of_range("Native MAP word extent at "+std::to_string(offset)+" of "+std::to_string(bytes.size()));
        return static_cast<std::uint16_t>((bytes[offset]<<8)|bytes[offset+1]);
    }
    TerrainDescriptorRecord record(std::ptrdiff_t offset) const {
        return {word(offset),word(offset+2),static_cast<std::uint32_t>(offset)};
    }
};
enum class TerrainRecordSearch {ForwardWindow,BackwardWindow,ExactColumn};
// $4270/$422C and $43E4..$4426. Visits retain original search/copy order.
template<class Visitor>
void search_terrain_records(TerrainMapView map,std::uint16_t start,std::uint16_t end,
        std::uint16_t left,std::uint16_t right,TerrainRecordSearch mode,Visitor&& visit) {
    if(start==end)return;
    if(end<start||(end-start)%4)throw std::invalid_argument("Unproved native MAP row interval");
    auto length=static_cast<std::uint16_t>(end-start);
    std::ptrdiff_t cursor=mode==TerrainRecordSearch::BackwardWindow?end:start;
    if(mode==TerrainRecordSearch::BackwardWindow) {
        while((length=static_cast<std::uint16_t>((length>>1)&0xfffc))>8) {
            cursor-=length;
            // $423C CMP.W (+2,A1),D5; $4240 BCS retains the lower
            // cursor only when D5 < record.x. Otherwise $4242 restores it.
            if(map.word(cursor+2)<=right)cursor+=length;
        }
        bool found_upper=false;
        for(;;) {
            cursor-=4;const auto record=map.record(cursor); // Read before lower-bound test.
            if(cursor<start)return;
            if(!found_upper&&record.x>=right)continue;
            found_upper=true;
            if(record.x<left)return;
            visit(record);
        }
    }
    bool exact_binary_match=false;
    while((length=static_cast<std::uint16_t>((length>>1)&0xfffc))>8) {
        cursor+=length;const auto x=map.word(cursor+2);
        if(x==left){exact_binary_match=true;break;}
        if(x>left)cursor-=length;
    }
    auto record=map.record(cursor);cursor+=4;
    if(!exact_binary_match) {
        for(;;) {
            if(cursor>end)return;
            if(record.x>=left)break;
            record=map.record(cursor);cursor+=4;
        }
        if(mode==TerrainRecordSearch::ExactColumn) {
            if(record.x==left)visit(record);
            return;
        }
        if(record.x>=right)return;
    }
    // Binary equality branches directly to dispatch, bypassing the right test.
    visit(record);
    if(mode==TerrainRecordSearch::ExactColumn)return;
    for(;;) {
        record=map.record(cursor);cursor+=4; // Original post-increment >end check.
        if(cursor>end||record.x>=right)return;
        visit(record);
    }
}
}
