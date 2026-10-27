#pragma once
#include "core/actor_definition.hpp"
#include "core/actor_reservations.hpp"
namespace rolo {
struct HeldObjectState {std::uint32_t base{},held{},stored_definition{};std::uint8_t stored_count{};};
struct HeldObjectServices {
    virtual ~HeldObjectServices()=default;
    virtual const ActorDefinition& held_definition(const ActorState&)=0;
    virtual std::uint32_t spawn_released_object(std::uint32_t definition,std::uint32_t x,
        std::uint32_t y,std::uint8_t facing)=0; //28B0; live diagnostic context domain still required.
};
// $7B74..$7C74. Shared pool/reservations; spawn failure does not roll back globals.
inline void release_held_object(ActorPool& pool,ActorReservationPool& reservations,
        HeldObjectState& state,HeldObjectServices& services) {
    auto& base=pool.resolve(state.base);auto& head=pool.resolve(base.longword(84));
    if(!head.byte(47))return;
    head.byte(47,0);
    const auto launch=[&](std::uint32_t identity) {
        auto& actor=pool.resolve(identity);actor.longword(58,0x80000);
        actor.byte(121,(actor.byte(118)&8)?255:1);
    };
    if(!state.stored_count) {
        const auto identity=state.held;auto& held=pool.resolve(identity);
        head.byte(46,0);head.byte(126,static_cast<std::uint8_t>(head.byte(126)&~2u));state.held=0;
        reservations.reserve(pool,identity);
        const auto& definition=services.held_definition(held);
        held.longword(42,(definition.byte(7)&4)?definition.longword(12):0xb498);
        held.byte(125,static_cast<std::uint8_t>(held.byte(125)&0xdd));
        held.longword(62,0);held.byte(122,0);launch(identity);return;
    }
    head.byte(46,255);head.byte(126,static_cast<std::uint8_t>(head.byte(126)&~2u));
    const auto definition=state.stored_definition;
    state.stored_count=static_cast<std::uint8_t>(state.stored_count-1);
    if(!state.stored_count) {state.stored_definition=0;if(!state.held)head.byte(46,0);}
    auto offset=static_cast<std::uint16_t>(head.word(32)+12);
    if(base.byte(118)&8)offset=static_cast<std::uint16_t>(0u-offset);
    const auto x=static_cast<std::uint16_t>(base.word(12)+offset);
    const auto y=static_cast<std::uint16_t>(base.word(16)+head.word(34));
    const auto spawned=services.spawn_released_object(definition,static_cast<std::uint32_t>(x)<<16,
        static_cast<std::uint32_t>(y)<<16,base.byte(118));
    if(!spawned)return;
    reservations.reserve(pool,spawned);launch(spawned);
}
}
