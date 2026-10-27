#pragma once
#include "core/actor_terrain.hpp"
namespace rolo {
struct WallProbe {bool found{};std::uint16_t x{};};
// $85E8/$8634, using $8728 and descriptor readers $87F6/$87DC.
inline WallProbe player_wall_probe(const ActorTerrain& terrain,std::uint16_t x,
        std::uint16_t y,bool left) {
    x=static_cast<std::uint16_t>(x+terrain.x_shift);
    const auto index=ActorTerrain::ring_offset(x,y);
    const auto tile=static_cast<std::uint16_t>((terrain.read(terrain.ring,index)<<8)|terrain.read(terrain.ring,index+1));
    if(!(tile&0x4000))return {};
    const auto descriptor=(tile&511u)*8+(left?6u:4u);
    const auto offset=terrain.read(terrain.collision,descriptor);
    const auto shape=terrain.read(terrain.collision,descriptor+1);
    if(((tile>>6)^shape)&64)y=static_cast<std::uint16_t>(~y);
    const auto profile=terrain.read(terrain.profiles,(shape&63u)*16+(y&15u));
    if(profile&128)return {};
    const auto base=x&0xfff0u;
    return {true,static_cast<std::uint16_t>(left?base-16u+offset+profile:base+15u-offset+profile)};
}
// $827A..$8376. Signed reach checks, unsigned fallback bounds, word wrapping.
inline void player_side_collision(ActorState& actor,const ActorTerrain& terrain) {
    actor.byte(124,static_cast<std::uint8_t>(actor.byte(124)&0xf9));
    const auto reach=static_cast<std::uint16_t>(actor.word(58)+actor.word(62)+1);
    auto side=[&](bool left) {
        auto x=actor.word(12);const auto y=static_cast<std::uint16_t>(actor.word(16)-8);
        auto probe=player_wall_probe(terrain,static_cast<std::uint16_t>(left?x+8:x-8),y,left);
        if(probe.found) {
            const auto target=static_cast<std::uint16_t>(left?probe.x+8:probe.x-8);
            const auto distance=static_cast<std::uint16_t>(left?target-x:x-target);
            if(signed_word(reach)>=signed_word(distance)) {
                actor.word(12,target);actor.word(14,0);actor.byte(121,0);actor.longword(58,0);
                actor.byte(124,static_cast<std::uint8_t>(actor.byte(124)|(left?2:4)));return;
            }
        }
        probe=player_wall_probe(terrain,static_cast<std::uint16_t>(left?x-8:x+8),y,left);
        if(!probe.found)return;
        const auto target=static_cast<std::uint16_t>(left?probe.x+8:probe.x-8);
        if(left?target<x:target>x)return;
        actor.word(12,target);actor.word(14,0);actor.byte(121,0);actor.longword(58,0);
        actor.byte(124,static_cast<std::uint8_t>(actor.byte(124)|(left?2:4)));
    };
    const auto direction=signed_word(static_cast<std::uint16_t>(static_cast<std::int8_t>(actor.byte(121))));
    if(direction<0)side(true);
    else if(direction>0)side(false);
    else {side(true);if(!(actor.byte(124)&2))side(false);}
}
}
