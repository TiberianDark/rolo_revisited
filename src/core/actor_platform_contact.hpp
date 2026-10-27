#pragma once
#include "core/actor_allocation.hpp"
#include "core/actor_contact.hpp"
namespace rolo {
struct ActorPlatformRoster {std::uint32_t base{},controlled{};std::array<std::uint32_t,3> companions{};};
struct ActorPlatformContactServices {
    virtual ~ActorPlatformContactServices()=default;
    virtual void restore_platform_actor(std::uint32_t candidate)=0; // $8A68 with A5=candidate.
};
// $90D2: delta N tests precede signed extent comparisons.
inline void attach_actor_to_platform(ActorPool& pool,std::uint32_t platform_key,
        std::uint32_t candidate_key,ActorPlatformContactServices& services){
    auto& p=pool.resolve(platform_key);auto& a=pool.resolve(candidate_key);
    const auto left=static_cast<std::uint16_t>(p.word(12)-half_signed_word(p.word(36)));
    const auto top=static_cast<std::uint16_t>(p.word(16)-p.word(38));
    const auto dx=static_cast<std::uint16_t>(a.word(12)-left),dy=static_cast<std::uint16_t>(a.word(16)-top);
    if(!(dx&0x8000)&&signed_word(dx)<signed_word(p.word(36))&&!(dy&0x8000)&&
            signed_word(dy)<signed_word(static_cast<std::uint16_t>(p.word(38)+16))){
        a.longword(98,platform_key);services.restore_platform_actor(candidate_key);
        if(a.byte(124)&32){p.byte(123,255);return;}
    }
    a.longword(98,0);p.byte(123,0);
}
// $90A0: base first, then three live slots, skipping actors already attached.
inline void update_platform_roster_contact(ActorPool& pool,std::uint32_t platform_key,
        ActorPlatformRoster& roster,ActorPlatformContactServices& services){
    const auto base=roster.base;
    if(!pool.resolve(base).longword(98))attach_actor_to_platform(pool,platform_key,base,services);
    for(unsigned i=0;i<3;++i){const auto key=roster.companions[i];if(key&&!pool.resolve(key).longword(98))
        attach_actor_to_platform(pool,platform_key,key,services);}
}
// $9132: already attached returns without clearing the platform contact byte.
inline void update_controlled_platform_contact(ActorPool& pool,std::uint32_t platform_key,
        const ActorPlatformRoster& roster,ActorPlatformContactServices& services){
    auto& p=pool.resolve(platform_key);const auto key=roster.controlled;auto& a=pool.resolve(key);
    if(a.longword(98))return;
    const auto left=static_cast<std::uint16_t>(p.word(12)-half_signed_word(p.word(36)));
    const auto top=static_cast<std::uint16_t>(p.word(16)-p.word(38));
    const auto dx=static_cast<std::uint16_t>(a.word(12)-left),dy=static_cast<std::uint16_t>(a.word(16)-top);
    const auto adjusted=static_cast<std::uint16_t>(dy-a.word(38)+8);
    if(!(dx&0x8000)&&signed_word(dx)<signed_word(p.word(36))&&!(dy&0x8000)&&
            signed_word(adjusted)<=signed_word(p.word(38))){
        a.longword(98,platform_key);services.restore_platform_actor(key);p.byte(123,255);return;
    }
    a.longword(98,0);p.byte(123,0);
}
// $B804: exact callback alias of the roster contact caller.
inline void update_actor_platform_callback(ActorPool& pool,std::uint32_t platform_key,
        ActorPlatformRoster& roster,ActorPlatformContactServices& services){
    update_platform_roster_contact(pool,platform_key,roster,services);
}
}
