#pragma once
#include "core/player_side_collision.hpp"
namespace rolo {
// $CE22: standalone velocity/reach body; does not clear existing side bits.
inline void actor_horizontal_collision_body(ActorState& actor,const ActorTerrain& terrain){
    const auto direction=static_cast<std::int8_t>(actor.byte(121));
    if(!actor.byte(117)&&direction){
        const bool left=direction<0;
        const auto x=actor.word(12),y=static_cast<std::uint16_t>(actor.word(16)-8);
        const auto reach=static_cast<std::uint16_t>(actor.word(58)+1);
        const auto limit=static_cast<std::uint16_t>(left?x+reach:x-reach);
        auto probe=player_wall_probe(terrain,static_cast<std::uint16_t>(left?x+16:x-16),y,left);
        auto accepted=[&](WallProbe result){return result.found&&(left?result.x<=limit:result.x>=limit);};
        if(!accepted(probe))probe=player_wall_probe(terrain,x,y,left);
        if(accepted(probe)){
            actor.word(12,static_cast<std::uint16_t>(left?probe.x+1:probe.x-1));actor.word(14,0);
            actor.byte(124,actor.byte(124)|(left?2:4));
        }
    }
}
// $8488: standalone top-corner followup, including inactive/stationary actors.
inline void actor_top_corner_collision(ActorState& actor,const ActorTerrain& terrain){
    const auto direction=static_cast<std::int8_t>(actor.byte(121));
    const bool left=direction<0;
    const auto x=static_cast<std::uint16_t>((left?actor.word(12)-8:actor.word(12)+8)+terrain.x_shift);
    const auto y=static_cast<std::uint16_t>(actor.word(16)-actor.word(38));
    const auto offset=ActorTerrain::ring_offset(x,y);
    const auto tile=static_cast<std::uint16_t>((terrain.read(terrain.ring,offset)<<8)|terrain.read(terrain.ring,offset+1));
    if(!(tile&0x4000))return;
    const auto descriptor=(tile&511u)*8+(left?6u:4u);
    if((terrain.read(terrain.collision,descriptor+1)&63)!=1)return;
    actor.word(12,static_cast<std::uint16_t>(left?(x&0xfff0)+23:(x&0xfff0)-8));
    actor.byte(124,actor.byte(124)|(left?2:4)); // Fraction14 is deliberately retained here.
}
// $CE14: clear side flags, then both original calls unconditionally.
inline void actor_horizontal_collision(ActorState& actor,const ActorTerrain& terrain){
    actor.byte(124,actor.byte(124)&0xf9);
    actor_horizontal_collision_body(actor,terrain);
    actor_top_corner_collision(actor,terrain);
}
}
