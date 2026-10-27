#pragma once
#include "core/actor_state.hpp"
#include <array>
namespace rolo {
enum class PlayerMotionTables {Walk,Run};
struct PlayerDirectionState {
    std::array<std::uint8_t,8> mapped{};
    std::uint32_t acceleration{},override_acceleration{};
    PlayerMotionTables tables{PlayerMotionTables::Walk};
};
// $796C/$7994: literal directional handlers, including facing changes atselector24.
inline void player_left_input(ActorState& actor,std::uint32_t acceleration){
    actor.byte(118,static_cast<std::uint8_t>(actor.byte(118)|8));
    if(actor.word(70)==24)return;
    const auto direction=actor.byte(121);
    if(direction&&!(direction&128))acceleration=0u-acceleration;
    else actor.byte(121,255);
    actor.longword(46,actor.longword(46)+acceleration);
}
inline void player_right_input(ActorState& actor,std::uint32_t acceleration){
    actor.byte(118,static_cast<std::uint8_t>(actor.byte(118)&~8u));
    if(actor.word(70)==24)return;
    if(actor.byte(121)&128)acceleration=0u-acceleration;
    else actor.byte(121,1);
    actor.longword(46,actor.longword(46)+acceleration);
}
// $78E4..$79BE: after jump/action processing; mapped0/1 handlers are literal RTS.
inline void player_direction_input(ActorState& actor,PlayerDirectionState& state) {
    if(actor.byte(125)&8)return;
    if(state.mapped[5]){state.acceleration=0x10000;state.tables=PlayerMotionTables::Run;}
    else {state.acceleration=0x8000;state.tables=PlayerMotionTables::Walk;}
    if(state.override_acceleration)state.acceleration=state.override_acceleration;
    if(state.mapped[2])player_left_input(actor,state.acceleration);
    if(state.mapped[3])player_right_input(actor,state.acceleration);
}
}
