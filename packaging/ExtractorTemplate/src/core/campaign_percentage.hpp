#pragma once
#include "core/achievement_regions.hpp"
#include <array>
#include <cstdint>
namespace rolo {
inline std::uint16_t campaign_completion_percentage(const std::array<std::uint8_t,80>& flags){
 // The campaign selector set is exactly the union of the regional piece
 // selectors. Keep one authoritative list instead of embedding a duplicate.
 unsigned completed=0;
 for(auto node:region0_pieces)if(flags[node]&2)++completed;
 for(auto node:region1_pieces)if(flags[node]&2)++completed;
 for(auto node:region2_pieces)if(flags[node]&2)++completed;
 for(auto node:region3_pieces)if(flags[node]&2)++completed;
 return static_cast<std::uint16_t>(completed*100/70);
}
}
