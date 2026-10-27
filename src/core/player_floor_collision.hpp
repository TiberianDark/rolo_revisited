#pragma once
#include "core/actor_allocation.hpp"
#include "core/actor_terrain.hpp"
namespace rolo {
// $84F4..$85E8. Incoming actor fields clear before controlled A0 reload.
inline void player_floor_collision(ActorPool& pool,std::uint32_t& live_key,
        std::uint32_t controlled_key,const ActorTerrain& terrain,std::uint8_t& c545) {
    auto& incoming=pool.resolve(live_key);
    incoming.byte(124,static_cast<std::uint8_t>(incoming.byte(124)&0xbe));incoming.byte(120,0);
    live_key=controlled_key;auto& actor=pool.resolve(live_key);
    const auto reach=static_cast<std::uint16_t>(actor.word(58)+actor.word(62)+1);
    const bool ascending=(actor.byte(122)&128)!=0;
    int first=0;
    if(ascending) {
        if(signed_word(actor.word(62))>signed_word(actor.word(58)))return;
        c545=0;
        const auto numerator=static_cast<std::uint16_t>(actor.word(62)<<4);
        const auto denominator=actor.word(58);
        if(denominator){c545=static_cast<std::uint8_t>(numerator/denominator);first=1;}
    }
    for(int n=first;n<3;++n) {
        const auto y=static_cast<std::uint16_t>(actor.word(16)-(2-n)*16);
        const auto probe=actor_floor_probe(terrain,actor.word(12),y);
        if(!probe.found)continue;
        const auto distance=static_cast<std::uint16_t>(actor.word(16)-probe.y);
        if(signed_word(reach)<signed_word(distance))continue;
        // An accepted reach branches out of the probe sequence, even if rejected below.
        if(probe.y>actor.word(16))return;
        const auto shifted_x=static_cast<std::uint16_t>(actor.word(12)+terrain.x_shift);
        const auto offset=ActorTerrain::ring_offset(shifted_x,y);
        const bool inverted=(terrain.read(terrain.ring,offset)&16)!=0;
        const auto shape=static_cast<std::uint8_t>(probe.shape^(inverted?64:0));
        if(ascending&&static_cast<std::int8_t>(shape&63)<static_cast<std::int8_t>(c545))return;
        actor.byte(120,shape);actor.word(16,probe.y);actor.word(18,0);
        actor.byte(124,static_cast<std::uint8_t>((actor.byte(124)|1)&~16u));
        actor.word(66,actor.word(62));actor.byte(122,0);actor.longword(62,0);
        if(actor.word(68)){actor.word(68,0);actor.byte(124,static_cast<std::uint8_t>(actor.byte(124)|64));}
        return;
    }
}
}
