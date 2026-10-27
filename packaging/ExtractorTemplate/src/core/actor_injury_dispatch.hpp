#pragma once
#include "core/actor_state.hpp"
#include <stdexcept>
namespace rolo {
struct ActorInjuryGlobals { std::uint8_t gate=0;std::uint16_t timer=0; };
struct ActorInjuryServices {
 virtual ~ActorInjuryServices()=default;
 virtual bool contact(ActorState*&)=0; // $9012 returned Z, exposed as contact.
 virtual bool damage_negative(ActorState*&)=0; // $96C6 returned N.
 virtual void reveal(ActorState*&)=0; // $D3FE may replace live A5.
 virtual void spawn_scene(ActorState*&,std::uint32_t,std::uint32_t,std::uint32_t,std::uint32_t,std::uint8_t,std::uint8_t)=0;
 virtual void phase(ActorState*&,std::uint32_t)=0;
 virtual void gravity(ActorState*&)=0;
 virtual void integrate(ActorState*&)=0;
 virtual void land(ActorState*&)=0;
};
inline void actor_injury_scene(ActorState*& a,bool alternate,ActorInjuryServices& s){
 s.reveal(a);s.spawn_scene(a,0x14e78,alternate?0x1140000:0xa00000,alternate?0x1510000:0x1230000,0,0,0);
}
inline void actor_phase_dispatch(ActorState*& a,std::uint32_t entry,ActorInjuryServices& s){
 const auto offset=a->word(46);std::uint32_t target=0;
 switch(entry){
 case 0xea4c:{constexpr std::uint32_t targets[]{0xea98,0xeb1a,0xeb4a,0xeb9e,0xebc8};if(offset%4||offset>16)throw std::out_of_range("EA4C phase");target=targets[offset/4];break;}
 case 0xed18:{constexpr std::uint32_t targets[]{0xed72,0xed90,0xee18};if(offset%4||offset>8)throw std::out_of_range("ED18 phase");target=targets[offset/4];break;}
 case 0xf046:{constexpr std::uint32_t targets[]{0xf060,0xf0e2,0xf12c};if(offset%4||offset>8)throw std::out_of_range("F046 phase");target=targets[offset/4];break;}
 case 0xf194:{constexpr std::uint32_t targets[]{0xf1ae,0xf25e,0xf2a0};if(offset%4||offset>8)throw std::out_of_range("F194 phase");target=targets[offset/4];break;}
 default:throw std::out_of_range("Unknown phase caller");
 }s.phase(a,target);
}
// $ECC4: early selector14 bypasses every service. Recheck live selector after damage.
inline void update_actor_injury_transition(ActorState*& a,ActorInjuryGlobals& g,ActorInjuryServices& s){
 if(a->word(70)==20||g.gate||!s.contact(a)||!s.damage_negative(a))return;
 if(a->word(70)==20){actor_injury_scene(a,false,s);return;}
 g.timer=0;g.gate=10;
}
// $ED18: reward branch returns without motion; phase service may change A5.
inline void update_actor_injury_motion(ActorState*& a,ActorInjuryGlobals& g,ActorInjuryServices& s){
 if(a->word(70)==20)return;
 if(!g.gate&&s.contact(a)&&s.damage_negative(a)){
  if(a->word(70)==20){actor_injury_scene(a,false,s);return;}
  g.timer=0;g.gate=10;
 }
 if(a->byte(117))return;actor_phase_dispatch(a,0xed18,s);s.gravity(a);s.integrate(a);s.land(a);
}
// $EA4C: reward selector8, otherwise BCLR3 then dispatch even with117 nonzero.
inline void update_actor_injury_phase(ActorState*& a,ActorInjuryGlobals& g,ActorInjuryServices& s){
 if(!g.gate&&s.contact(a)&&s.damage_negative(a)){
  if(a->word(70)==8){actor_injury_scene(a,true,s);return;}
  g.timer=0;g.gate=10;
 }
 a->byte(118,a->byte(118)&~8u);actor_phase_dispatch(a,0xea4c,s);
}
inline void update_actor_replacement_dispatch(ActorState*& a,ActorInjuryServices& s){a->byte(118,a->byte(118)&~8u);actor_phase_dispatch(a,0xf046,s);}
inline void update_actor_facing_phase_dispatch(ActorState*& a,ActorInjuryServices& s){a->byte(118,a->byte(118)&~8u);actor_phase_dispatch(a,0xf194,s);}
inline void update_actor_byte50_dispatch(ActorState*& a,ActorInjuryServices& s){
 constexpr std::uint32_t targets[]{0xbdfc,0xbdd2,0xbd88,0xbd60,0xbd4e,0xbd2c,0xbd0a,0xbcd0,0xbc32,0xbdd2,0xbb8e};
 const auto index=a->byte(50);if(index>=11)throw std::out_of_range("BA64 phase");s.phase(a,targets[index]);
}
}
