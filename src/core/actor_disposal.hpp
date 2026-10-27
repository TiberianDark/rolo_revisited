#pragma once
#include "core/actor_allocation.hpp"
namespace rolo {
struct ActorDisposalServices {
    virtual ~ActorDisposalServices()=default;
    virtual std::uint16_t disposal_resource_units(const ActorState&)=0;
    virtual void release_actor_graphics(std::uint32_t start,std::uint16_t size)=0;
};
// $2CBC..$2D1A. Source marker policy belongs to the caller, not this routine.
inline void dispose_actor(ActorPool& pool,std::uint32_t identity,ActorDisposalServices& services) {
    auto cursor=pool.cursor;auto& actor=pool.resolve(identity);
    if(!actor.longword(76)) {
        auto next=actor.longword(84);
        while(next) {auto& linked=pool.resolve(next);linked.byte(116,255);next=linked.longword(84);}
    }
    const auto units=services.disposal_resource_units(actor);
    if(units) {
        const auto start=static_cast<std::uint16_t>(actor.word(2)<<5);
        services.release_actor_graphics(start,units);
    }
    actor.byte(0,255);
    if(!cursor)throw std::out_of_range("Native actor free-stack underflow");
    pool.free_keys.at(--cursor)=identity;
    const auto previous=actor.longword(80),next=actor.longword(84);
    if(previous)pool.resolve(previous).longword(84,next);
    if(next)pool.resolve(next).longword(80,previous);
    pool.cursor=cursor;
}
}
