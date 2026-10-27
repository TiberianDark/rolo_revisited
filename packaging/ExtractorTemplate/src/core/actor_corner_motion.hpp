#pragma once
#include "core/actor_terrain.hpp"
namespace rolo {
// $F75C: a failed original floor query marks downward travel complete.
inline void actor_corner_floor_limit(ActorState& actor,ActorState& parent,const ActorTerrain& terrain){
    if(actor_floor_probe(terrain,actor.word(12),actor.word(16)).found)return;
    actor.byte(119,actor.byte(119)|16);parent.byte(50,static_cast<std::uint8_t>(parent.byte(50)-1));
}
// $F776/$F792: signed limits and full preservation of unrelated flags.
inline void actor_corner_left_limit(ActorState& actor,ActorState& parent){
    if(signed_word(actor.word(12))>16)return;
    actor.byte(119,actor.byte(119)|8);actor.byte(118,actor.byte(118)&~8u);
    parent.byte(50,static_cast<std::uint8_t>(parent.byte(50)-1));
}
inline void actor_corner_right_limit(ActorState& actor,ActorState& parent){
    if(signed_word(actor.word(12))<=304)return;
    actor.byte(119,actor.byte(119)&~8u);actor.byte(118,actor.byte(118)|8);
    parent.byte(50,static_cast<std::uint8_t>(parent.byte(50)-1));
}
// $F7AE: signed top limit clears upward travel and consumes a parent count.
inline void actor_corner_top_limit(ActorState& actor,ActorState& parent){
    if(signed_word(actor.word(16))>16)return;
    actor.byte(119,actor.byte(119)&~16u);parent.byte(50,static_cast<std::uint8_t>(parent.byte(50)-1));
}
// Four $F6B4/$F6B8/$F6BC/$F6C0 entries. Vertical check/move precedes
// horizontal check/move; parent/actor aliases retain that exact write order.
inline void update_actor_corner_motion(ActorState& actor,ActorState& parent,const ActorTerrain& terrain,
        bool upward,bool rightward){
    if(upward)actor_corner_top_limit(actor,parent);else actor_corner_floor_limit(actor,parent,terrain);
    if(bool(actor.byte(119)&16)==upward)actor.word(16,static_cast<std::uint16_t>(actor.word(16)+(upward?-15:15)));
    if(rightward)actor_corner_right_limit(actor,parent);else actor_corner_left_limit(actor,parent);
    if(bool(actor.byte(119)&8)==rightward)actor.word(12,static_cast<std::uint16_t>(actor.word(12)+(rightward?15:-15)));
}
}
