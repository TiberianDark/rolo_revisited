#pragma once
#include "core/local_achievements.hpp"
#include <span>
namespace rolo {
// Original world jigsaw slots: forest/desert halves of group0, West group1, village group2.
inline constexpr std::array<unsigned,16> region0_pieces{9,7,12,29,77,3,5,10,2,4,8,11,1,13,6,16};
inline constexpr std::array<unsigned,9> region0_animals{7,3,10,2,4,8,11,1,6};
inline constexpr std::array<unsigned,16> region1_pieces{18,19,20,17,26,25,23,30,31,21,28,22,32,27,33,24};
inline constexpr std::array<unsigned,11> region1_animals{18,19,20,25,23,30,31,21,28,22,32};
inline constexpr std::array<unsigned,28> region2_pieces{41,40,36,37,54,55,57,49,48,44,43,15,56,69,39,34,45,42,59,58,61,52,50,47,14,60,51,73};
inline constexpr std::array<unsigned,14> region2_animals{40,37,54,55,48,43,56,39,42,59,58,61,50,14};
inline constexpr std::array<unsigned,10> region3_pieces{72,64,68,78,67,65,66,38,63,62};
inline constexpr std::array<unsigned,3> region3_animals{64,65,66};
inline bool achievement_all_flags(const std::array<std::uint8_t,80>&flags,std::span<const unsigned> selectors,unsigned mask){for(auto n:selectors)if(!(flags[n]&mask))return false;return !selectors.empty();}
inline AchievementBits regional_achievement_events(const std::array<std::uint8_t,80>&before,const std::array<std::uint8_t,80>&after){
 AchievementBits bits=0;
 if(!achievement_all_flags(before,region0_pieces,1)&&achievement_all_flags(after,region0_pieces,1))bits|=achievement_bit(6);
 if(!achievement_all_flags(before,region0_animals,2)&&achievement_all_flags(after,region0_animals,2))bits|=achievement_bit(9);
 if(!achievement_all_flags(before,region1_pieces,1)&&achievement_all_flags(after,region1_pieces,1))bits|=achievement_bit(14);
 if(!achievement_all_flags(before,region1_animals,2)&&achievement_all_flags(after,region1_animals,2))bits|=achievement_bit(13);
 if(!achievement_all_flags(before,region2_pieces,1)&&achievement_all_flags(after,region2_pieces,1))bits|=achievement_bit(19);
 if(!achievement_all_flags(before,region2_animals,2)&&achievement_all_flags(after,region2_animals,2))bits|=achievement_bit(18);
 if(!achievement_all_flags(before,region3_pieces,1)&&achievement_all_flags(after,region3_pieces,1))bits|=achievement_bit(21);
 if(!achievement_all_flags(before,region3_animals,2)&&achievement_all_flags(after,region3_animals,2))bits|=achievement_bit(20);
 return bits;
}
}
