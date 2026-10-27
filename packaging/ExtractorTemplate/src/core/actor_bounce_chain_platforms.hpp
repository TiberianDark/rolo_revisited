#pragma once
#include "core/actor_displacement.hpp"
#include "core/actor_wave_motion.hpp"
namespace rolo {
// $BF54..$C022: D3highWORD is a retained caller value on the initial branch.
inline void update_actor_bounce_platform(ActorState& a,ActorState& controlled,std::uint32_t key,std::uint16_t incoming_d3_high){
 if(controlled.longword(98)==key&&(controlled.byte(124)&64)&&!a.byte(53)){
  a.word(50,a.word(16));const auto power=controlled.byte(67);a.byte(52,power);a.byte(56,power);a.byte(53,1);controlled.byte(124,controlled.byte(124)|8);
  const auto delta=static_cast<std::uint16_t>(controlled.word(66)+controlled.word(24)-controlled.word(16));
  actor_displace_and_measure(a,0,(std::uint32_t(delta)<<16)|incoming_d3_high);return;
 }
 const auto phase=a.byte(53);if(!phase){actor_displace_and_measure(a,0,0);return;}
 if(phase==1){const auto speed=a.byte(52);actor_carry_controlled(a,controlled,0,std::uint32_t(speed)<<16);a.byte(52,speed>>1);if(!a.byte(52))a.word(52,0x102);return;}
 const auto speed=std::uint16_t(a.byte(52)),distance=static_cast<std::uint16_t>(a.word(16)-a.word(50));
 if(signed_word(speed)<signed_word(distance)){actor_carry_negated_word(a,controlled,0,speed);return;}
 a.byte(53,0);actor_carry_negated_word(a,controlled,0,distance);controlled.byte(124,controlled.byte(124)|16);controlled.byte(122,255);
 auto power=static_cast<std::uint16_t>(std::uint16_t(a.byte(56))-2);if(signed_word(power)<0)power=0;controlled.word(62,power);
}
struct ChainPlatformServices {
 virtual ~ChainPlatformServices()=default;
 virtual std::uint8_t& definition_flags26(std::uint32_t)=0;
 virtual std::uint32_t allocate_platform_chain(std::uint32_t,std::uint32_t,std::uint32_t,std::uint32_t)=0;
};
// $C322/$C3EE: context is explicit retained incoming D1, never assumedzero.
inline void update_actor_chain_platform(ActorPool& pool,std::uint32_t key,bool alternate,std::uint32_t context,ChainPlatformServices& services){
 auto& a=pool.resolve(key);if(a.byte(116))return;auto& flags=services.definition_flags26(a.longword(4));flags|=8;
 if(!a.byte(122)){
  a.byte(122,255);const auto head=services.allocate_platform_chain(0x1450a,a.longword(12),a.longword(16),context);
  if(head){auto& root=pool.resolve(head);const auto tail=root.longword(84);pool.resolve(tail).longword(80,key);a.longword(84,tail);a.longword(80,head);a.longword(76,head);root.longword(84,key);}
 }
 const auto phase=a.word(50);if(!phase){a.word(56,alternate?0x380:0x300);a.byte(121,a.byte(121)^1);}
 const auto step=static_cast<std::uint32_t>(static_cast<std::int32_t>(signed_word(a.word(56))))<<8;
 a.longword(50,a.byte(121)?a.longword(50)-step:a.longword(50)+step);a.word(56,static_cast<std::uint16_t>(a.word(56)-16));
 const auto v=actor_wave_vector(phase,100,8);const auto parent=a.longword(76);if(!parent)return;
 auto x=pool.resolve(parent).longword(12),y=pool.resolve(parent).longword(16);auto cursor=key;
 for(unsigned i=0;i<6;++i){cursor=pool.resolve(cursor).longword(84);auto& child=pool.resolve(cursor);x+=v.x;y+=v.y;child.longword(12,x);child.longword(16,y);}
 x+=v.x;y+=v.y;actor_displace_and_measure(a,x-a.longword(12),y-a.longword(16)+a.longword(38)-0x100000u);
}
}
