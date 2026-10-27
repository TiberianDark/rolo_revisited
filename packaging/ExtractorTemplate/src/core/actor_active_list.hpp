#pragma once
#include "core/actor_lifetime.hpp"
#include "core/actor_visibility.hpp"
namespace rolo {
struct ActiveActorList {
    std::array<std::uint32_t,49> keys{};
    std::uint16_t count{};
};
struct ActiveActorServices:ActorLifetimeServices {
    virtual void clear_contact_root_word()=0; // CLR.W $FFFFF2D8, before $8E6C.
    virtual void release_completed_actor_reservations()=0; // Required native $8E6C binding.
};
// $29EE..$2AD8. Scan live records in pool order; disposal can mutate later records.
inline void rebuild_active_actor_list(ActorPool& pool,DeferredMarkerPool& markers,
        ActiveActorList& active,std::uint16_t reference_x,std::uint16_t reference_y,
        ActiveActorServices& services) {
    services.clear_contact_root_word();
    services.release_completed_actor_reservations();
    active.count=0;
    for(std::size_t index=0;index<pool.actors.size();++index) {
        auto& actor=pool.actors[index];
        if(signed_word(actor.word(0))<0)continue;
        actor.byte(117,actor_visibility_flags(actor,reference_x,reference_y));
        const auto identity=ActorPool::key(index);
        if(!retain_actor_lifetime(pool,identity,markers,reference_x,reference_y,services))continue;
        active.keys[active.count]=identity;
        actor.byte(126,static_cast<std::uint8_t>(actor.byte(126)&~64u));
        ++active.count;
    }
    active.keys[active.count]=0; // Do not clear unused trailing entries.
}
}
