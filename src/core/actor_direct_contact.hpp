#pragma once
#include "core/actor_contact.hpp"
namespace rolo {
// $976C: this entry bypasses the grounded/vertical chooser at96C6.
inline int actor_direct_player_contact(ActorState& actor,ActorState& controlled,ContactGlobals& globals,DamageServices& services){
 if(globals.override_c512)return actor_player_damage(actor,controlled,globals,services);
 if((services.definition_byte7(actor)&1)||globals.action_gate_c511||globals.hit_gate_c519||globals.hit_gate_c51a||globals.hit_gate_c51b)return 0;
 globals.action_latch_c517=255;return 1;
}
}
