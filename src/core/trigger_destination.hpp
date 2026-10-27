#pragma once
#include "core/player_trigger_dispatch.hpp"
#include "core/terrain_record_search.hpp"
namespace rolo {
// 3EE4: first matching class11 marker, not the paired class8 trigger.
// Bounded exported MAP domain: nonnegative monotone row offsets.
inline TriggerDestination find_trigger_destination(TerrainMapView map,std::uint8_t parameter){
    const auto rows=static_cast<std::uint16_t>(map.word(6)>>4);
    // Original enters row zero before its unsigned row-count comparison.
    const auto visited_rows=rows?rows:1;
    for(std::uint16_t row=0;row<visited_rows;++row){
        const auto start=map.word(8+row*2),end=map.word(10+row*2);
        if(start>=0x8000||end>=0x8000||end<start||(end-start)%4)throw std::out_of_range("Unproved destination row offsets");
        for(std::uint32_t at=start;at<end;at+=4){
            const auto record=map.record(at);
            if((record.type>>8)==0x11&&static_cast<std::uint8_t>(record.type)==parameter)
                return {false,static_cast<std::uint16_t>(record.x+8),static_cast<std::uint16_t>(row<<4)};
        }
    }
    return {true,0,0}; // Original D0=-1/N; unused coordinates are not a return contract.
}
}
