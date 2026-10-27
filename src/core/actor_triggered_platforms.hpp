#pragma once
#include "core/actor_platform_family.hpp"
namespace rolo {
struct PlatformObjectContactService {virtual ~PlatformObjectContactService()=default;virtual void object_contact(ActorState&)=0;};
// $C582: probe one further step using temporary fullLONG displacement.
inline void update_actor_grid_platform(ActorState& a,const ActorState& controlled,std::uint32_t key,PlatformDirectionService& s){
 if(a.word(52)){a.word(52,static_cast<std::uint16_t>(a.word(52)-1));actor_displace_and_measure(a,0,0);return;}
 if(!actor_supported_by(controlled,key))return;
 if(!a.word(50)){a.word(50,4);a.word(52,20);return;}
 const auto phase=a.word(50);if(phase!=4&&phase!=8&&phase!=12&&phase!=16)throw std::out_of_range("Grid platform phase");
 constexpr std::array<std::int16_t,4> dxs{0,2,0,-2},dys{-2,0,2,0};const unsigned index=phase/4-1;
 const auto dx=std::uint32_t(std::uint16_t(dxs[index]))<<16,dy=std::uint32_t(std::uint16_t(dys[index]))<<16;
 actor_displace_and_measure(a,dx,dy);a.byte(121,0);a.longword(12,a.longword(12)+dx);a.longword(16,a.longword(16)+dy);
 s.choose_direction(a);a.longword(12,a.longword(12)-dx);a.longword(16,a.longword(16)-dy);
 if(a.byte(121)){a.word(50,static_cast<std::uint16_t>((a.word(50)&15)+4));a.word(52,20);}
}
// $C61A/$C6AA/$C730: shared global gate latches once the first short move ends.
inline void update_actor_triggered_platform(ActorState& a,const ActorState& controlled,std::uint32_t key,
 std::uint8_t& gate,std::uint16_t origin,unsigned kind,PlatformObjectContactService& s){
 if(kind>2)throw std::out_of_range("Triggered platform kind");
 const unsigned axis=kind==0?16:12;const bool negative=kind==1;
 std::uint32_t delta=0;
 if(!gate){
  if(kind==0){if(!actor_supported_by(controlled,key))return;}
  if(!a.word(50)){
   if(kind){s.object_contact(a);if(!(a.byte(125)&64))return;}
   a.word(50,static_cast<std::uint16_t>(a.word(axis)+(negative?-16:16)));a.word(52,0);
  }
  const bool at_limit=negative?a.word(50)>=a.word(axis):a.word(50)<=a.word(axis);
  if(at_limit)gate=255;
  else{auto rate=static_cast<std::uint16_t>(a.word(52)+64);const unsigned max=kind==0?128:512;if(signed_word(rate)>int(max))rate=max;a.word(52,rate);delta=std::uint32_t(rate)<<8;}
 }else{
  const auto distance=static_cast<std::uint16_t>(negative?origin-a.word(axis):a.word(axis)-origin-(kind==0?224:320));
  if(signed_word(distance)>32)return;
  if(!a.byte(50)){a.byte(50,255);delta=0x100000;}
 }
 if(negative)delta=0u-delta;actor_displace_and_measure(a,kind?delta:0,kind?0:delta);
}
}
