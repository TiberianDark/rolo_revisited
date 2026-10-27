#pragma once
#include "core/actor_active_list.hpp"
namespace rolo {
struct ActorScheduleState {
    std::uint32_t controlled{},base{},saved_controlled_callback{};
    std::array<std::uint32_t,3> secondary{};
    std::array<std::uint32_t,5> priority{};
};
// $C9AE..$CA0A. Repeated actor aliases read the mutation from earlier visits.
inline void build_priority_actor_list(ActorPool& pool,ActorScheduleState& state) {
    auto& controlled=pool.resolve(state.controlled);
    if(controlled.byte(124)&32)state.saved_controlled_callback=controlled.longword(98);
    std::size_t count=0;
    const auto append=[&](std::uint32_t identity) {
        auto& actor=pool.resolve(identity);const auto key=actor.longword(98);
        if(!key)return;
        state.priority[count++]=key;actor.longword(98,0);
        actor.byte(124,static_cast<std::uint8_t>(actor.byte(124)&~32u));
    };
    append(state.base);
    for(std::size_t index=0;index<state.secondary.size();++index)
        if(state.secondary[index])append(state.secondary[index]);
    state.priority[count]=0;
}
struct ActorCallbackServices {
    virtual ~ActorCallbackServices()=default;
    // Lookup must dispatch a translated native function; never execute this ROM key.
    virtual void invoke_actor_callback(std::uint32_t actor,std::uint32_t callback)=0;
};
// $A808..$A84C, for callbacks preserving the original A6 list cursor convention.
// List entries and callback fields are fetched live. No allocation-order sorting.
inline void update_actor_callbacks(ActorPool& pool,ActorScheduleState& state,
        ActiveActorList& active,ActorCallbackServices& services) {
    build_priority_actor_list(pool,state);
    const auto visit=[&](auto& list) {
        for(std::size_t index=0;index<list.size();++index) {
            const auto identity=list[index];if(!identity)return;
            auto& actor=pool.resolve(identity);const auto flags=actor.byte(126);
            actor.byte(126,static_cast<std::uint8_t>(flags|64));
            if(!(flags&64))services.invoke_actor_callback(identity,actor.longword(42));
        }
        throw std::logic_error("Native actor callback list missing sentinel");
    };
    visit(state.priority);visit(active.keys);
}
}
