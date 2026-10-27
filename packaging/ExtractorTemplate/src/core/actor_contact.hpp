#pragma once
#include "core/actor_state.hpp"

namespace rolo {
inline std::uint16_t half_signed_word(std::uint16_t value) {
    return static_cast<std::uint16_t>((value>>1)|(value&0x8000));
}

// $9012..$90A0: mixed word-N guards and unsigned inclusive edge comparisons.
inline bool actor_player_contact(ActorState& actor,const ActorState& controlled) {
    auto finish=[&](bool hit) {
        actor.byte(123,hit?0xff:0);
        if(!hit) actor.byte(129,0);
        return hit;
    };
    if(actor.word(36)==0) return finish(false);
    const auto half=half_signed_word(controlled.word(36));
    const auto left=static_cast<std::uint16_t>(controlled.word(12)-half);
    const auto right=static_cast<std::uint16_t>(controlled.word(12)+half);
    const auto bottom=controlled.word(16);
    const auto top=static_cast<std::uint16_t>(bottom-controlled.word(38));
    auto edge=actor.word(34);
    if(actor.byte(119)&16) edge=static_cast<std::uint16_t>(0u-edge);
    edge=static_cast<std::uint16_t>(edge+actor.word(16)-8);
    if((edge&0x8000)||top>edge) return finish(false);
    edge=static_cast<std::uint16_t>(edge-actor.word(38)+16);
    if((edge&0x8000)||bottom<edge) return finish(false);
    edge=actor.word(32);
    if(actor.byte(118)&8) edge=static_cast<std::uint16_t>(0u-edge);
    edge=static_cast<std::uint16_t>(edge+actor.word(12)+half_signed_word(actor.word(36))-8);
    if((edge&0x8000)||left>edge) return finish(false);
    edge=static_cast<std::uint16_t>(edge-actor.word(36)+16);
    if((edge&0x8000)||right<edge) return finish(false);
    return finish(true);
}

struct ContactGlobals {
    std::uint8_t action_gate_c511{},override_c512{},vertical_gate_c515{},
        action_latch_c517{},hit_gate_c519{},hit_gate_c51a{},hit_gate_c51b{};
};
struct DamageServices {
    virtual ~DamageServices()=default;
    virtual std::uint8_t definition_byte7(const ActorState&)=0;
    virtual ActorState& damage_parent(const ActorState&)=0; // Original long76, when def7.4 set.
    virtual void sound_effect(std::uint16_t)=0;
    virtual void hit_counter_zero(ActorState&)=0; // $97AC, full successor contract required.
};

// $96C6..$97AC. Return values are original D0: -1,0,1, not damage quantities.
inline int actor_player_damage(ActorState& actor,ActorState& controlled,
        ContactGlobals& globals,DamageServices& services) {
    bool alternate=(controlled.byte(124)&1)!=0;
    if(!alternate && (globals.vertical_gate_c515&0x80)) {
        const auto edge=static_cast<std::uint16_t>(actor.word(16)-actor.word(38)+16);
        alternate=signed_word(controlled.word(16))>signed_word(edge);
    }
    if(alternate && globals.override_c512==0) {
        if((services.definition_byte7(actor)&1)||globals.action_gate_c511||
                globals.hit_gate_c519||globals.hit_gate_c51a||globals.hit_gate_c51b) return 0;
        globals.action_latch_c517=0xff;return 1;
    }
    if(actor.byte(129)||globals.hit_gate_c519||globals.hit_gate_c51a||globals.hit_gate_c51b) return 0;
    services.sound_effect(0x1e);
    controlled.byte(122,0xff);controlled.longword(62,0x65e00);
    controlled.byte(124,static_cast<std::uint8_t>(controlled.byte(124)|16));
    controlled.longword(106,0);controlled.word(72,0xffff);
    auto& target=(services.definition_byte7(actor)&16)?services.damage_parent(actor):actor;
    target.byte(129,0xff);
    if(target.byte(127)&0x80) return 0;
    target.byte(127,static_cast<std::uint8_t>(target.byte(127)-1));
    if(target.byte(127)==0) services.hit_counter_zero(target);
    return -1;
}
}
