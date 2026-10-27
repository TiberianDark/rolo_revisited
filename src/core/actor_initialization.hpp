#pragma once
#include "core/actor_state.hpp"
namespace rolo {
struct ActorInitialDefinition {
    std::uint32_t key{},callback{};
    std::uint16_t flags{},type{},selector{};
    std::uint8_t hit_counter{};
};
struct ActorInitializationServices {
    virtual ~ActorInitializationServices()=default;
    virtual std::uint16_t marker_word(std::uint32_t)=0;
    virtual void marker_word(std::uint32_t,std::uint16_t)=0;
    virtual std::uint8_t callback_override_flag(std::int16_t)=0;
};
// $28D8..$29C0 after a successful graphics-resource allocation. The caller
// passes the original resource start's low word, never an invented tile index.
// Free-stack/resource allocation and publication of the previous link follow separately.
inline void initialize_actor(ActorState& actor,const ActorInitialDefinition& definition,
        std::uint32_t x,std::uint32_t y,std::uint8_t facing,std::uint16_t resource_start,
        std::uint32_t marker,std::uint32_t head,std::uint32_t previous,
        ActorInitializationServices& services) {
    actor.longword(88,marker);
    if(marker) {
        actor.word(92,services.marker_word(marker));services.marker_word(marker,0x1700);
    }
    actor.word(0,definition.flags);actor.word(2,static_cast<std::uint16_t>(resource_start>>5));
    actor.longword(4,definition.key);actor.longword(12,x);actor.longword(16,y);actor.byte(118,facing);
    for(const auto offset:{8,46,50,58,62,106,20,24,98,28})actor.longword(offset,0);
    for(const auto offset:{119,124,125,120,121,122,116,117,123,129,126,128})actor.byte(offset,0);
    for(const auto offset:{54,56,36,38,32,34})actor.word(offset,0);
    actor.word(70,definition.selector);actor.word(72,0xffff);actor.byte(127,definition.hit_counter);
    actor.word(94,actor.word(12));actor.word(96,actor.word(16));
    const auto shifted=static_cast<std::uint16_t>((definition.type>>2)|((definition.type&0x8000)?0xc000:0));
    const auto callback=services.callback_override_flag(signed_word(shifted))?0xa8bcu:definition.callback;
    actor.longword(42,callback);actor.longword(76,head);actor.longword(80,previous);actor.longword(84,0);
}
}
