#pragma once
#include "core/local_achievements.hpp"
#include "core/actor_state.hpp"
#include <cstdlib>
namespace rolo {
// Local challenge state covers one uninterrupted level attempt.
struct AchievementAttempt {
 bool eligible=true,damaged=false,life_lost=false,rode_cart=false;std::uint32_t entry_score=0;
 void hurt(){damaged=true;}
 void debug(){eligible=false;}
 void died(){eligible=false;life_lost=true;}
 AchievementBits completed(std::uint32_t score)const{
  if(!eligible||life_lost)return 0;AchievementBits bits=0;
  if(!damaged)bits|=achievement_bit(42);if(score==entry_score)bits|=achievement_bit(43);return bits;
 }
 AchievementBits creek(unsigned selector,unsigned controlled_type,const ActorState& a,std::uint32_t score)const{
  // Selector8 original final-shore MAP record982: x3232,y768.
  return selector==8&&controlled_type==4&&eligible&&!life_lost&&score==entry_score&&(a.byte(124)&1)&&a.word(12)>=3232&&a.word(12)<3632&&a.word(16)>=736&&a.word(16)<=800?achievement_bit(10):0;
 }
 AchievementBits boss(unsigned index)const{return eligible&&!damaged&&!life_lost?achievement_bit(index):0;}
};
struct CompanionAchievementAttempt {
 unsigned previous_type=0;std::uint16_t previous_y=0,launch_y=0,water_x=0;bool previous_ground=false,rabbit_jump=false,was_water=false,crossing=false;
 AchievementBits observe(unsigned type,const ActorState& a,bool water){
  AchievementBits bits=0;const bool ground=a.byte(124)&1;
  if(type!=previous_type){rabbit_jump=crossing=was_water=previous_ground=false;}
  if(type==16&&(a.byte(125)&8))bits|=achievement_bit(38);
  if(type==8&&a.word(70)==52&&(a.byte(126)&2))bits|=achievement_bit(40);
  if(type==20){if(previous_ground&&!ground&&(a.byte(122)&128)){rabbit_jump=true;launch_y=previous_y;}
   if(rabbit_jump&&ground){if(int(launch_y)-int(a.word(16))>=32)bits|=achievement_bit(39);rabbit_jump=false;}}
  if(type==12){if(water&&!was_water&&previous_ground){crossing=true;water_x=a.word(12);}
   if(!water&&was_water){if(crossing&&ground&&std::abs(int(a.word(12))-int(water_x))>=16)bits|=achievement_bit(41);crossing=false;}}
  previous_type=type;previous_ground=ground;previous_y=a.word(16);was_water=water;return bits;
 }
};
}
