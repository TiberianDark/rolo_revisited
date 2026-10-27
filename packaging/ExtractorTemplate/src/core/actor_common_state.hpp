#pragma once
#include "core/actor_allocation.hpp"
#include "core/actor_motion.hpp"
namespace rolo {
// $C142: signed WORD upper clamp after wrapped +64, then zero-extended LONG <<8.
inline std::uint32_t actor_increment_vertical_drive(ActorState& actor){
    auto value=static_cast<std::uint16_t>(actor.word(52)+64);
    if(signed_word(value)>128)value=128;
    actor.word(52,value);return std::uint32_t(value)<<8;
}
// $C988: live aliasing order matters if the controlled record is the platform.
inline void actor_carry_controlled(ActorState& actor,ActorState& controlled,
        std::uint32_t delta_x,std::uint32_t delta_y){
    actor.longword(12,actor.longword(12)+delta_x);actor.word(58,0);
    actor.longword(16,actor.longword(16)+delta_y);actor.word(62,0);
    controlled.word(16,static_cast<std::uint16_t>(actor.word(16)-actor.word(38)+1));
}
// $D940: branch on the wrapped subtraction N flag, preserving other facing bits.
inline void actor_face_from_controlled(ActorState& actor,const ActorState& controlled){
    const auto delta=static_cast<std::uint16_t>(actor.word(12)-controlled.word(12));
    actor.byte(118,(delta&0x8000)?actor.byte(118)&~8u:actor.byte(118)|8u);
}
// $EF28: returned Boolean replaces original Z-clear convention.
inline bool actor_phase_changed(ActorState& actor){
    const auto next=static_cast<std::uint16_t>(actor.word(46)+1);
    if(next==actor.word(48))return false;actor.word(48,next);return true;
}
// $ED66/$ED72 and $F3FC/$F410: two original wait-entry durations.
inline void actor_phase_wait(ActorState& actor,std::uint16_t reload){
    if(actor_phase_changed(actor)){actor.word(50,reload);actor.word(70,0);}
    const auto timer=static_cast<std::uint16_t>(actor.word(50)-1);actor.word(50,timer);
    if(signed_word(timer)<0)actor.word(46,static_cast<std::uint16_t>(actor.word(46)+4));
}
inline void actor_short_phase_wait(ActorState& actor){actor_phase_wait(actor,10);}
inline void actor_long_phase_wait(ActorState& actor){actor_phase_wait(actor,25);}
// $EA06: linked actor is resolved only on the negative signed gate branch.
inline void actor_hide_linked_on_gate(ActorState& actor,ActorPool& pool,std::uint8_t gate){
    if(!(gate&128))return;actor.word(70,4);auto& linked=pool.resolve(actor.longword(84));
    linked.byte(125,linked.byte(125)|2);
}
// $D558: the seven original state bytes, no neighbouring storage.
inline void clear_shared_actor_work(std::span<std::uint8_t,7> bytes){for(auto& byte:bytes)byte=0;}
// $5CE6: negative timer is disabled; zero expires on this call.
template<class Music>void update_delayed_music(std::uint16_t& timer,std::uint8_t command,Music&& music){
    if(signed_word(timer)<0)return;timer=static_cast<std::uint16_t>(timer-1);
    if(signed_word(timer)<0)music(std::uint32_t(command),0xffffffffu);
}
// $7968/$796A and $BEBC..$BEDC -> $C85A..$C86A are literal RTS branches.
inline void actor_noop_callback(ActorState&){}
}
