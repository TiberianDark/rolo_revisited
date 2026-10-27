#pragma once
#include "core/actor_state.hpp"
#include <span>
#include <stdexcept>

namespace rolo {
struct ActorTerrain {
    // Native copies of F30A's 64x64 word ring, F2FE's collision table,
    // and immutable $4A71A shape profiles. This is data, never ROM execution.
    std::span<const std::uint8_t> ring,collision,profiles;
    std::uint16_t x_shift{}; // F268, applies to8728 but not874C.
    std::uint8_t read(std::span<const std::uint8_t> data,std::size_t i) const {
        if(i>=data.size()) throw std::out_of_range("Native terrain data extent");
        return data[i];
    }
    static std::size_t ring_offset(std::uint16_t x,std::uint16_t y) {
        return ((x&0x3f0u)>>3)+((y&0x3f0u)<<3);
    }
};
struct FloorProbe {bool found{};std::uint16_t y{};std::uint8_t shape{};};
// $8728 returns the raw tile word, independently of floor solidity.
inline std::uint16_t actor_terrain_word(const ActorTerrain& terrain,std::uint16_t x,std::uint16_t y) {
    const auto index=ActorTerrain::ring_offset(static_cast<std::uint16_t>(x+terrain.x_shift),y);
    return static_cast<std::uint16_t>((terrain.read(terrain.ring,index)<<8)|terrain.read(terrain.ring,index+1));
}
// $8680/$8728/$879A floor query; found corresponds to returned D0's N flag.
inline FloorProbe actor_floor_probe(const ActorTerrain& t,std::uint16_t x,std::uint16_t y) {
    x=static_cast<std::uint16_t>(x+t.x_shift);
    const auto index=ActorTerrain::ring_offset(x,y);
    const auto tile=static_cast<std::uint16_t>((t.read(t.ring,index)<<8)|t.read(t.ring,index+1));
    if(!(tile&0x4000))return {};
    const bool inverted=(tile&0x1000)!=0;
    const auto descriptor=(tile&0x1ffu)*8+(inverted?2u:0u);
    const auto offset=t.read(t.collision,descriptor),shape=t.read(t.collision,descriptor+1);
    const auto profile_x=((shape&64)?static_cast<std::uint16_t>(~x):x)&15u;
    const auto profile=t.read(t.profiles,(shape&63u)*16+profile_x);
    if(profile&128)return {};
    const auto base=static_cast<std::uint16_t>(y&0xfff0u);
    const auto surface=static_cast<std::uint16_t>(inverted?base+31u-offset-profile:base+16u-offset+profile);
    return {true,surface,shape};
}
// $874C canonical entry. ANDI.W03F0/ASR.W3 yields <=126, so the
// subsequent MOVE.B cannot set bit14: its descriptor branch is unreachable.
inline std::uint8_t actor_terrain_class(const ActorTerrain& t,std::uint16_t x,std::uint16_t y) {
    const auto high=t.read(t.ring,ActorTerrain::ring_offset(x,y));
    return (high&32)?0:static_cast<std::uint8_t>((high&14)>>1);
}
// $CF46..$CFCE. Word arithmetic wraps before unsigned landing comparisons.
inline void actor_land(ActorState& actor,const ActorTerrain& terrain) {
    if(actor.byte(124)&32)return;
    actor.byte(124,static_cast<std::uint8_t>(actor.byte(124)&0xbe));actor.byte(120,0);
    if(actor.byte(117))return;
    const auto reach=static_cast<std::uint16_t>(actor.word(58)+actor.word(62)+2);
    if(static_cast<std::int8_t>(actor.byte(122))<0&&signed_word(actor.word(62))>signed_word(actor.word(58)))return;
    auto result=actor_floor_probe(terrain,actor.word(12),static_cast<std::uint16_t>(actor.word(16)-16));
    auto close_enough=[&] {return result.found&&reach>=static_cast<std::uint16_t>(actor.word(16)-result.y);};
    if(!close_enough()) {
        result=actor_floor_probe(terrain,actor.word(12),actor.word(16));
        if(!close_enough())return;
    }
    actor.word(16,result.y);actor.word(18,0);actor.byte(122,0);actor.longword(62,0);
    actor.byte(124,static_cast<std::uint8_t>((actor.byte(124)|1)&0xe7));actor.byte(120,result.shape);
}
struct ActorTerrainServices {
    virtual ~ActorTerrainServices()=default;
    virtual const ActorTerrain& actor_terrain()=0;
    virtual std::uint16_t terrain_world_width()=0; // F330.
    virtual std::uint8_t definition_byte26(const ActorState&)=0;
};
inline void actor_choose_direction(ActorState& actor,ActorTerrainServices& services) {
    auto right=[&] {actor.byte(118,static_cast<std::uint8_t>(actor.byte(118)&~8u));actor.byte(121,1);};
    auto left=[&] {actor.byte(118,static_cast<std::uint8_t>(actor.byte(118)|8u));actor.byte(121,255);};
    const auto x=actor.word(12);
    if(signed_word(x)<=0){right();return;}
    if(signed_word(services.terrain_world_width())<=signed_word(x)){left();return;}
    const auto terrain_class=actor_terrain_class(services.actor_terrain(),x,static_cast<std::uint16_t>(actor.word(16)-16));
    if(terrain_class<=(services.definition_byte26(actor)&7))return;
    right();if(!(x&8))left();
}
}
