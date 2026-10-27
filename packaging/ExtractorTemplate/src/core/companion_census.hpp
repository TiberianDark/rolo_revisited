#pragma once
#include "core/terrain_record_search.hpp"
#include <array>
namespace rolo {
// 3E8A: count class0x12 markers before actor spawning; C552 is not updated here.
inline void count_level_companions(TerrainMapView map,std::uint16_t selector,
 std::uint16_t& remaining,std::array<std::uint8_t,80>& flags){
 const unsigned rows=map.word(6)>>4;std::uint16_t count=0;
 for(unsigned row=0;row<(rows?rows:1);++row){
  const unsigned start=map.word(8+row*2),end=map.word(10+row*2);
  if(start>=0x8000||end>=0x8000||end<start||(end-start)%4)throw std::out_of_range("Unproved census row offsets");
  for(unsigned at=start;at<end;at+=4)if((map.record(at).type>>8)==0x12)++count;
 }
 remaining=count;
 if(!count){if(selector>=flags.size())throw std::out_of_range("Unproved census selector");flags[selector]|=2;}
}
}
