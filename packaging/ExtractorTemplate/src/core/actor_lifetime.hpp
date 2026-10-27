#pragma once
#include "core/actor_disposal.hpp"
#include "core/actor_markers.hpp"
namespace rolo {
struct ActorLifetimeDefinition {std::uint32_t key{};std::uint16_t type{};std::uint8_t byte7{},byte26{};};
struct ActorLifetimeServices:ActorDisposalServices,MarkerRestoreServices {
    virtual ActorLifetimeDefinition lifetime_definition(const ActorState&)=0;
    virtual std::uint8_t lifetime_progress_flag(std::int16_t)=0;
    virtual void release_ram_definition(std::uint32_t)=0; // Push identity; do not erase its bytes before disposal reads them.
};
inline bool saved_spawn_in_far_bounds(const ActorState& actor,std::uint16_t x,std::uint16_t y) {
    if(actor.byte(116))return false;
    const auto lower_x=static_cast<std::uint16_t>(x-368),upper_x=static_cast<std::uint16_t>(lower_x+1056);
    const auto lower_y=static_cast<std::uint16_t>(y-240),upper_y=static_cast<std::uint16_t>(lower_y+704);
    return marker_in_bounds(actor.word(94),actor.word(96),lower_x,upper_x,lower_y,upper_y);
}
// $2AD8..$2BCE. True is retained (original D0=0); false is disposed (D0=-1).
inline bool retain_actor_lifetime(ActorPool& pool,std::uint32_t identity,DeferredMarkerPool& markers,
        std::uint16_t reference_x,std::uint16_t reference_y,ActorLifetimeServices& services) {
    auto& actor=pool.resolve(identity);const auto definition=services.lifetime_definition(actor);
    const auto status=actor.byte(116);
    if(!(status&128)) {
        if(status) {
            if(!(actor.byte(124)&1)&&!(actor.byte(117)&15))return true;
        } else {
            if(!(actor.byte(117)&0xf0)||(definition.byte26&8)||(actor.byte(125)&32))return true;
            if((definition.byte7&2)&&saved_spawn_in_far_bounds(actor,reference_x,reference_y))return true;
        }
    }
    if(actor.byte(126)&8) {actor.byte(126,static_cast<std::uint8_t>(actor.byte(126)|4));return true;}
    if(definition.type==0x18)services.release_ram_definition(definition.key);
    else {
        const auto shifted=static_cast<std::uint16_t>((definition.type>>2)|((definition.type&0x8000)?0xc000:0));
        if(services.lifetime_progress_flag(signed_word(shifted))&&actor.byte(47))return true;
    }
    const bool skip_marker=(definition.byte26&16)||((actor.byte(125)&4)&&(definition.byte26&32));
    if(!skip_marker)restore_or_defer_actor_marker(actor,markers,reference_x,reference_y,services);
    dispose_actor(pool,identity,services);
    return false;
}
}
