#pragma once
#include "core/player_side_collision.hpp"
namespace rolo {
// Direct $82A6/$830E entries accept the caller's D6 WORD reach and retain old flags.
inline void player_side_collision_entry(ActorState&a,const ActorTerrain&t,std::uint16_t reach,bool left){
 const auto x=a.word(12),y=static_cast<std::uint16_t>(a.word(16)-8);auto p=player_wall_probe(t,static_cast<std::uint16_t>(left?x+8:x-8),y,left);std::uint16_t target=0;bool accepted=false;
 if(p.found){target=static_cast<std::uint16_t>(left?p.x+8:p.x-8);const auto distance=static_cast<std::uint16_t>(left?target-x:x-target);accepted=signed_word(reach)>=signed_word(distance);}
 if(!accepted){p=player_wall_probe(t,static_cast<std::uint16_t>(left?x-8:x+8),y,left);if(p.found){target=static_cast<std::uint16_t>(left?p.x+8:p.x-8);accepted=left?target>=x:target<=x;}}
 if(accepted){a.word(12,target);a.word(14,0);a.byte(121,0);a.longword(58,0);a.byte(124,a.byte(124)|(left?2:4));}
}
}
