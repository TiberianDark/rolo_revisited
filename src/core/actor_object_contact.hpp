#pragma once
#include "core/actor_contact.hpp"
#include <span>

namespace rolo {
struct ObjectContactServices {
    virtual ~ObjectContactServices()=default;
    virtual std::span<ActorState* const> contact_roots()=0; // Ordered record list6BDC.
    virtual ActorState* next_contact_link(const ActorState&)=0;
    virtual std::uint16_t definition_type(const ActorState&)=0; // Definition word10.
    virtual ActorState& defeat_contact_actor(ActorState&)=0; // 97AC returned actor A0.
    virtual void defeat_contact_body(ActorState&)=0;
    virtual std::uint16_t contact_actor_handle(const ActorState&)=0; // Lowword identity for74.
    virtual void contact_sound(std::uint16_t)=0;
};

// Rectangle fragment within $8F22; unlike9012, no inset or negative-edge guards.
inline bool actor_object_overlap(const ActorState& body,const ActorState& candidate) {
    const auto half=half_signed_word(body.word(36));
    const auto left=static_cast<std::uint16_t>(body.word(12)-half);
    const auto right=static_cast<std::uint16_t>(left+half+half);
    const auto bottom=body.word(16),top=static_cast<std::uint16_t>(bottom-body.word(38));
    if(top>candidate.word(16)) return false;
    const auto other_top=static_cast<std::uint16_t>(candidate.word(16)-candidate.word(38));
    if(bottom<other_top) return false;
    const auto other_half=half_signed_word(candidate.word(36));
    const auto other_right=static_cast<std::uint16_t>(candidate.word(12)+other_half);
    if(left>other_right) return false;
    const auto other_left=static_cast<std::uint16_t>(other_right-other_half-other_half);
    return right>=other_left;
}

// $8F22..$8F74: first overlapping actor in a valid finite linked chain.
// Returned pointer replaces original matched A0 / nonzero D6 native API.
template<class Next>
ActorState* actor_find_object_overlap(const ActorState& body,ActorState* head,Next next){
    for(auto* candidate=head;candidate;candidate=next(*candidate))
        if(actor_object_overlap(body,*candidate))return candidate;
    return nullptr;
}

// $8EAA..$8F22: only first matching root/link, previous bit6 suppresses re-hit.
inline bool actor_object_contact(ActorState& body,ObjectContactServices& services) {
    ActorState* hit=nullptr;
    for(auto* root:services.contact_roots()) {
        hit=actor_find_object_overlap(body,root,[&](const auto& candidate){return services.next_contact_link(candidate);});
        if(hit) break;
    }
    if(!hit) {body.byte(125,static_cast<std::uint8_t>(body.byte(125)&~64u));return false;}
    if(services.definition_type(*hit)==0x24) {
        hit->byte(126,static_cast<std::uint8_t>(hit->byte(126)|4));
        hit=&services.defeat_contact_actor(*hit); // A0 can now identify another linked actor.
    } else hit->byte(121,static_cast<std::uint8_t>(0u-hit->byte(121)));
    hit->byte(125,static_cast<std::uint8_t>(hit->byte(125)|64));
    body.word(74,services.contact_actor_handle(*hit));
    const bool previous=(body.byte(125)&64)!=0;
    body.byte(125,static_cast<std::uint8_t>(body.byte(125)|64));
    if(!previous) {
        services.contact_sound(0x1e);
        const auto old=body.byte(127);body.byte(127,static_cast<std::uint8_t>(old-2));
        if(old<=2) services.defeat_contact_body(body); // BHI after byte subtract, including borrow.
    }
    return true;
}
}
