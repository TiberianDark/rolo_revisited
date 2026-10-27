#pragma once
#include "core/actor_terrain.hpp"
namespace rolo {
// $842E..$8482. Uses signed comparison between old/current aligned X.
inline void player_collision_tile_crossing(ActorState& actor,const ActorTerrain& terrain) {
    const auto old=static_cast<std::uint16_t>(actor.word(20)&0xfff0),current=static_cast<std::uint16_t>(actor.word(12)&0xfff0);
    if(old==current)return;
    const auto x=static_cast<std::uint16_t>(actor.word(12)+terrain.x_shift);
    const auto i=ActorTerrain::ring_offset(x,actor.word(16));
    const auto tile=static_cast<std::uint16_t>((terrain.read(terrain.ring,i)<<8)|terrain.read(terrain.ring,i+1));
    if(!(tile&0x4000))return;
    const auto descriptor=(tile&511u)*8+(signed_word(current)>signed_word(old)?4u:6u);
    if((terrain.read(terrain.collision,descriptor+1)&63)==1)
        actor.word(16,static_cast<std::uint16_t>((actor.word(16)&0xfff0)+1));
}
// $8482..$84F4. Zero horizontal direction follows the right-side path.
inline void player_collision_top_corner(ActorState& actor,const ActorTerrain& terrain) {
    const bool left=(actor.byte(121)&128)!=0;
    const auto x=static_cast<std::uint16_t>(actor.word(12)+(left?-8:8)+terrain.x_shift);
    const auto y=static_cast<std::uint16_t>(actor.word(16)-actor.word(38));
    const auto i=ActorTerrain::ring_offset(x,y);
    const auto tile=static_cast<std::uint16_t>((terrain.read(terrain.ring,i)<<8)|terrain.read(terrain.ring,i+1));
    if(!(tile&0x4000))return;
    if((terrain.read(terrain.collision,(tile&511u)*8+(left?7u:5u))&63)!=1)return;
    actor.word(12,static_cast<std::uint16_t>((x&0xfff0)+(left?23:-8)));
    actor.byte(124,static_cast<std::uint8_t>(actor.byte(124)|(left?2:4)));
}
}
