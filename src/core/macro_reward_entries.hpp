#pragma once
#include "core/actor_phase_emitters.hpp"
#include "core/animation.hpp"
#include "core/macro_reward_data.hpp"
namespace rolo {
struct MacroRewardGlobals{ActorState*controlled=nullptr;std::uint8_t collected=0;};
struct MacroRewardServices:PhaseEmitterServices{virtual void collision(ActorState*&)=0;virtual ActorState* attachment(const ActorState&)=0;virtual std::uint8_t definition_flags(const ActorState&)=0;virtual void refresh_macro(ActorState*&,std::uint8_t)=0;virtual ActorState& group_actor(std::int16_t,unsigned)=0;virtual void land(ActorState*&)=0;virtual void contact(ActorState*&)=0;};
inline void update_breakable_macro_entry(ActorState*&a,PhaseEmitterContext&c,MacroRewardGlobals&g,MacroRewardServices&s,bool grouped,std::span<const std::uint8_t>rom){
 if(!a->word(56)){s.collision(a);auto&controlled=*g.controlled;if(s.attachment(controlled)!=a||!(controlled.byte(122)&128)||(grouped&&a->longword(46)==0xbe46)||signed_word(controlled.word(16))<signed_word(a->word(16)))return;
  a->word(56,a->word(16));a->byte(122,255);a->longword(62,controlled.longword(62));controlled.byte(122,0);controlled.longword(62,0);
  for(;;){const auto def=a->longword(50);c.d2=a->longword(12);c.d3=std::uint32_t(static_cast<std::uint16_t>(a->word(16)-a->word(38)))<<16;auto*saved=a;auto*child=s.allocate(a,c,{def,c.resource,c.d2,c.d3,0,0});a=saved;if(!child)break;child->longword(42,grouped||!(s.definition_flags(*child)&8)?0xb726:0xb714);a->byte(55,static_cast<std::uint8_t>(a->byte(55)-1));if(!a->byte(55))break;}
 }
 actor_gravity(*a);actor_integrate(*a);const auto anchor=a->word(56);const bool settled=signed_word(anchor)<=signed_word(a->word(16));
 if(settled){a->word(16,anchor);a->word(18,0);a->longword(62,0);a->byte(122,0);a->word(56,0);if(!grouped){a->longword(42,0xb804);a->byte(92,0);const auto index=a->byte(54);if(index<128){a->byte(93,index);s.refresh_macro(a,index);}return;}}
 if(grouped){auto offset=[&](){const auto index=a->word(20);const auto address=std::int64_t(0xbb84)+signed_word(index);if(address<0||std::size_t(address)>=rom.size())throw std::out_of_range("Group lookup");return signed_word(std::uint16_t((index&0xff00)|rom[std::size_t(address)]));};if(settled){const auto at=offset();for(unsigned i=0;i<3;++i)s.group_actor(at,i).word(70,4);}const auto at=offset();for(unsigned i=0;i<3;++i)s.group_actor(at,i).longword(46,0xbe46);}
}
inline void update_rising_reward_source(ActorState*&a,PhaseEmitterContext&c,MacroRewardGlobals&g,MacroRewardServices&s){
 if(!a->byte(50)){a->byte(50,255);g.collected=0;a->byte(53,100);a->byte(52,a->byte(53));}
 if(std::bit_cast<std::int8_t>(g.collected)>=3){if(a->word(16))a->word(16,static_cast<std::uint16_t>(a->word(16)-1));return;}
 const auto old=a->byte(52);a->byte(52,static_cast<std::uint8_t>(old-1));if(old)return;auto timer=a->byte(53);if(std::bit_cast<std::int8_t>(timer)<=40)timer=41;timer=static_cast<std::uint8_t>(timer-2);a->byte(53,timer);a->byte(52,timer);c.d2=a->longword(12);c.d3=a->longword(16);s.allocate(a,c,{0x1474c,c.resource,c.d2,c.d3,0,0});
}
inline void update_rising_reward_item(ActorState*&a,PhaseEmitterContext&c,MacroRewardGlobals&g,AnimationRandom&random,MacroRewardServices&s){
 if(!a->byte(46)){a->byte(46,255);const auto index=random.between(0,6);a->byte(121,macro_reward_data::directions[index]);const auto speed=random.between(1,5);c.resource=4;a->longword(58,std::uint32_t(speed)<<15);a->byte(122,255);a->longword(62,0x80000);return;}
 if(a->byte(124)&1){if(std::bit_cast<std::int8_t>(g.collected)>=3){a->longword(42,0xb7c0);a->byte(46,0);}return;}
 actor_gravity(*a);actor_integrate(*a);s.land(a);if(a->byte(124)&1)g.collected=static_cast<std::uint8_t>(g.collected+1);s.contact(a);if(!a->byte(123))return;
 a->longword(42,0xb7c0);a->word(70,4);a->byte(46,0);const auto index=random.between(0,17);c.resource=17;c.d2=a->longword(12);c.d3=a->longword(16);auto*child=s.allocate(a,c,{macro_reward_data::rewards[index],c.resource,c.d2,c.d3,0,0});if(child)child->longword(42,0xb726);
}
}
