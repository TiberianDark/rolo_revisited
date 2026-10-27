#pragma once
#include "core/camera_data.hpp"
#include "core/actor_displacement.hpp"
namespace rolo {
struct ActorWaveVector {std::uint32_t x,y;};
// $CCF8: signed products, doubled modulo32, highWORD sign extension, then
// two original unsigned divisions represented by an exact 16.16 quotient.
inline ActorWaveVector actor_wave_vector(std::uint16_t phase,std::uint16_t amplitude,std::uint16_t divisor){
 const unsigned index=phase&511;
 auto scale=[&](unsigned i){const auto product=static_cast<std::uint32_t>(static_cast<std::int32_t>(camera_data::sine[i])*signed_word(amplitude));return signed_word(static_cast<std::uint16_t>((product*2u)>>16));};
 const auto cosine=scale(index),sine=scale((index+128)&511);
 auto fraction=[&](std::int16_t v)->std::uint32_t {
  if(signed_word(divisor)<=1)return static_cast<std::uint32_t>(static_cast<std::uint16_t>(v))<<16;
  const auto magnitude=v<0?unsigned(-int(v)):unsigned(v);
  const auto fixed=static_cast<std::uint32_t>((std::uint64_t(magnitude)<<16)/(divisor-1));
  return v<0?0u-fixed:fixed;
 };
 return {fraction(sine),fraction(cosine)};
}
// $C160/$C18E/$C1BC/$C1F8, entered through four selector54 branch slots.
inline void update_actor_wave_platform(ActorState& a,unsigned kind){
 if(kind>3)throw std::out_of_range("Wave platform kind");
 if(kind==1){if(!a.word(24))a.longword(24,a.longword(16));}
 else if(!a.word(20)){a.longword(20,a.longword(12));if(kind>=2)a.longword(24,a.longword(16));}
 const auto phase=a.word(50);a.word(50,static_cast<std::uint16_t>(phase+2));auto v=actor_wave_vector(phase,80,1);
 auto x=v.x+a.longword(20),y=v.y+a.longword(24);
 if(kind==3&&signed_long(v.y)<0)y=(0u-v.y)+a.longword(24);
 const auto dx=kind==1?0u:x-a.longword(12),dy=kind==0?0u:y-a.longword(16);
 actor_displace_and_measure(a,dx,dy);
}
// $D918: sixteen-phase increment precedes the wave call; integer output only.
inline void update_actor_small_orbit(ActorState& a){
 a.word(50,static_cast<std::uint16_t>(a.word(50)+16));auto v=actor_wave_vector(a.word(50),8,1);
 a.word(12,static_cast<std::uint16_t>((v.x>>16)+a.word(20)));
 a.word(16,static_cast<std::uint16_t>((v.y>>16)+a.word(24)));
}
}
