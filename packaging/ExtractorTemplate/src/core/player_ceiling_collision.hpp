#pragma once
#include "core/actor_allocation.hpp"
#include "core/actor_terrain.hpp"
namespace rolo {
inline FloorProbe player_ceiling_probe(const ActorTerrain& terrain,std::uint16_t x,std::uint16_t y) {
    x=static_cast<std::uint16_t>(x+terrain.x_shift);
    const auto i=ActorTerrain::ring_offset(x,y);
    const auto tile=static_cast<std::uint16_t>((terrain.read(terrain.ring,i)<<8)|terrain.read(terrain.ring,i+1));
    if(!(tile&0x4000))return {};
    const bool inverted=(tile&0x1000)!=0;
    const auto descriptor=(tile&511u)*8+(inverted?0u:2u);
    const auto offset=terrain.read(terrain.collision,descriptor),shape=terrain.read(terrain.collision,descriptor+1);
    const auto profile=terrain.read(terrain.profiles,(shape&63u)*16+(((shape&64)?static_cast<std::uint16_t>(~x):x)&15u));
    if(profile&128)return {};
    const auto base=y&0xfff0u;
    return {true,static_cast<std::uint16_t>(inverted?base+offset-profile:base-16u+offset+profile),shape};
}
// $8376..$842E: clear incoming actor's bit, then reload controlled A0.
// Native probe iteration replaces the three literal A2 continuation labels.
inline void player_ceiling_collision(ActorPool& pool,std::uint32_t& live_key,
        std::uint32_t controlled_key,const ActorTerrain& terrain) {
    auto& incoming=pool.resolve(live_key);
    incoming.byte(125,static_cast<std::uint8_t>(incoming.byte(125)&127));
    live_key=controlled_key;auto& actor=pool.resolve(live_key);
    const auto reach=static_cast<std::uint16_t>(actor.word(58)+actor.word(62)+1);
    const auto direction=static_cast<std::int8_t>(actor.byte(122));
    for(int n=direction>0?2:0;n<3;++n) {
        const auto y=static_cast<std::uint16_t>(actor.word(16)-actor.word(38)+(2-n)*16);
        const auto probe=player_ceiling_probe(terrain,actor.word(12),y);
        if(!probe.found)continue;
        const auto target=static_cast<std::uint16_t>(probe.y+actor.word(38));
        const auto distance=static_cast<std::uint16_t>(target-actor.word(16));
        if(signed_word(reach)<signed_word(distance)||target<actor.word(16))continue;
        actor.word(16,static_cast<std::uint16_t>(target+1));actor.word(18,0);
        if(direction<=0) {
            actor.byte(122,0);actor.longword(62,0);
            actor.byte(125,static_cast<std::uint8_t>(actor.byte(125)|128));
        }
        return;
    }
}
}
