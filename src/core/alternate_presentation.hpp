#pragma once
#include "core/actor_allocation.hpp"
namespace rolo {
struct AlternatePresentationState {std::uint8_t animation_phase{},c511{},c512{};};
struct AlternatePresentationServices {
    virtual ~AlternatePresentationServices()=default;
    virtual void publish_contact_actor_word(std::uint16_t)=0; // F2D8 actor low word and zero next word.
    virtual std::uint16_t alternate_x_word(std::int16_t byte_offset)=0; // DB16 indexed by ASR.W selector1.
};
// $EFA8..$F046: incoming actor is A5, not inferred from controlled/base globals.
inline void update_alternate_presentation(ActorPool& pool,std::uint32_t actor_key,
        std::uint32_t base_key,AlternatePresentationState& state,AlternatePresentationServices& services) {
    if(!state.animation_phase)return;
    auto& actor=pool.resolve(actor_key);
    services.publish_contact_actor_word(static_cast<std::uint16_t>(actor_key));
    if(!actor.byte(46)){actor.byte(46,255);actor.word(50,3000);}
    actor.word(50,static_cast<std::uint16_t>(actor.word(50)-1));
    if(signed_word(actor.word(50))<0) {
        actor.byte(116,255);state.c512=0;state.c511=255;return;
    }
    auto& base=pool.resolve(base_key);auto& head=pool.resolve(base.longword(84));
    actor.byte(118,base.byte(118));state.c511=0;
    actor.word(16,static_cast<std::uint16_t>(base.word(16)+head.word(34)-5));
    auto x=static_cast<std::uint16_t>(head.word(32)+1);
    const auto selector=base.word(70);
    const auto index=static_cast<std::uint16_t>((selector>>1)|(selector&0x8000));
    auto adjustment=services.alternate_x_word(signed_word(index));
    if(base.byte(118)&8){x=static_cast<std::uint16_t>(-x);adjustment=static_cast<std::uint16_t>(-adjustment);}
    actor.word(12,static_cast<std::uint16_t>(x+base.word(12)+adjustment));
    actor.word(24,static_cast<std::uint16_t>(head.word(16)+head.word(34)-head.word(38)+7));
}
}
