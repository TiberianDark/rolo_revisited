#pragma once
#include "core/actor_terrain.hpp"
namespace rolo {
// $D168 return Z, needed by C08A. ST does not replace the BSET Z result.
inline bool actor_choose_direction_nonzero(ActorState& a,ActorTerrainServices& services){
 const auto x=a.word(12);
 if(signed_word(x)<=0){a.byte(118,a.byte(118)&~8u);a.byte(121,1);return true;}
 if(signed_word(services.terrain_world_width())<=signed_word(x)){
  const bool old=a.byte(118)&8;a.byte(118,a.byte(118)|8);a.byte(121,255);return old;
 }
 const auto type=actor_terrain_class(services.actor_terrain(),x,static_cast<std::uint16_t>(a.word(16)-16));
 const auto allowed=services.definition_byte26(a)&7;
 if(type<=allowed)return type!=allowed;
 a.byte(118,a.byte(118)&~8u);a.byte(121,1);
 if(x&8)return true;a.byte(118,a.byte(118)|8);a.byte(121,255);return false;
}
}
