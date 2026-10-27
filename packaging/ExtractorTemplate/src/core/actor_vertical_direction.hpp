#pragma once
#include "core/actor_terrain.hpp"
namespace rolo {
// $D11A..$D168: midpoint terrain-class gate and vertical-direction selection.
// True replaces original D0=0 (direction applied), false replaces D0=-1.
inline bool actor_select_vertical_direction(ActorState& a,ActorTerrainServices& services,std::uint16_t& scratch_c494){
 const auto height=a.word(38);
 const auto half=static_cast<std::uint16_t>((height>>1)|(height&0x8000u));
 scratch_c494=static_cast<std::uint16_t>(a.word(16)-half);
 const auto cls=actor_terrain_class(services.actor_terrain(),a.word(12),scratch_c494);
 if(!cls)return false;
 if(cls<=(services.definition_byte26(a)&7))return false;
 a.byte(122,(scratch_c494&8)?1:255);return true;
}
}
