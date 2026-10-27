#pragma once
#include "core/actor_phase_emitters.hpp"
#include "core/actor_graphic_phase_data.hpp"
namespace rolo {
struct GraphicPhaseGlobals{std::uint8_t gate=0,scene=0;std::uint16_t timer=0,frame=0;};
struct GraphicPhaseServices:PhaseEmitterServices{virtual bool contact(ActorState*&,PhaseEmitterContext&)=0;virtual bool damage_negative(ActorState*&,PhaseEmitterContext&)=0;virtual void hurt(ActorState*&,PhaseEmitterContext&)=0;virtual ActorState& controlled()=0;};
inline std::uint16_t graphic_data_word(std::span<const std::uint8_t>b,unsigned at){return std::uint16_t((b[at]<<8)|b[at+1]);}
inline void update_actor_graphic_phase(ActorState*&a,unsigned phase,PhaseEmitterContext&c,GraphicPhaseGlobals&g,GraphicPhaseServices&s){
 if(phase==0){actor_long_phase_wait(*a);return;}
 if(phase==4){
  if(actor_phase_changed(*a)){a->word(20,a->word(12));a->word(24,a->word(16));auto next=static_cast<std::uint16_t>(a->word(56)+4);if(next%4||next>16)throw std::out_of_range("F5A2 anchor offset");auto x=graphic_data_word(graphic_phase_data::anchors,next);if(x&32768){next=0;x=graphic_data_word(graphic_phase_data::anchors,0);}a->word(22,x);a->word(26,graphic_data_word(graphic_phase_data::anchors,next+2));a->word(56,next);a->word(50,100);}
  const unsigned offset=(a->word(50)&1)*2;a->word(12,a->word(20+offset));a->word(16,a->word(24+offset));if(!(g.frame&15))s.sound(82,a,c);a->word(50,static_cast<std::uint16_t>(a->word(50)-1));if(signed_word(a->word(50))<=0)a->word(46,0);return;
 }
 if(phase>3)throw std::out_of_range("Graphic actor phase");if(actor_phase_changed(*a)){a->word(70,static_cast<std::uint16_t>(phase*4));s.sound(phase==1?85:phase==2?74:65,a,c);}
 if(!a->word(70)){a->word(46,static_cast<std::uint16_t>(a->word(46)+4));return;}if(!a->byte(52))return;a->byte(52,0);
 if(phase==1){c.d2=std::uint32_t(static_cast<std::uint16_t>(a->word(12)+((a->byte(118)&8)?-26:26)))<<16;c.d3=(std::uint32_t(static_cast<std::uint16_t>(a->word(16)-16))<<16)|(c.d3>>16);auto*saved=a;auto*child=s.allocate(a,c,{0x1540c,c.resource,c.d2,c.d3,a->byte(118),0});a=saved;if(child)child->byte(50,17);return;}
 unsigned data=0;for(unsigned counter=2;;--counter){c.resource=counter;
  if(phase==2){c.d2=a->longword(12);c.d3=(std::uint32_t(static_cast<std::uint16_t>(a->word(16)-16))<<16)|65535;}
  else{c.d2=std::uint32_t(static_cast<std::uint16_t>(a->word(12)+((a->byte(118)&8)?-10:10)))<<16;c.d3=(std::uint32_t(static_cast<std::uint16_t>(a->word(16)-32))<<16)|(c.d3>>16);}
  auto*saved=a;auto*child=s.allocate(a,c,{phase==2?0x1573cu:0x1571au,c.resource,c.d2,c.d3,static_cast<std::uint8_t>(phase==2?a->byte(118):0),0});a=saved;
  if(child){if(phase==2){child->byte(122,graphic_phase_data::directions[data++]);child->word(46,a->word(16));}else{child->word(70,graphic_data_word(graphic_phase_data::projectiles,data));data+=2;child->word(50,graphic_data_word(graphic_phase_data::projectiles,data));data+=2;child->word(52,graphic_data_word(graphic_phase_data::projectiles,data));data+=2;child->word(48,200);}}
  c.resource=static_cast<std::uint16_t>(counter-1);if(!counter)break;
 }
}
inline void update_actor_graphic_contact(ActorState*&a,PhaseEmitterContext&c,GraphicPhaseGlobals&g,GraphicPhaseServices&s){
 if(!g.gate&&a->word(46)!=16&&s.contact(a,c)){
  if(a->longword(8)==0x4457c){if(s.damage_negative(a,c)){if(a->word(70)==16){c.d2=0xa00000;c.d3=0xb00000;s.allocate(a,c,{0x14e78,c.resource,c.d2,c.d3,0,0});g.scene=255;return;}g.timer=0;g.gate=10;}}
  else s.hurt(a,c);
 }
 const auto offset=a->word(46);if(offset%4||offset>16)throw std::out_of_range("F394 phase offset");update_actor_graphic_phase(a,offset/4,c,g,s);a->byte(118,a->byte(118)|8);if(signed_word(s.controlled().word(12))>signed_word(a->word(12)))a->byte(118,a->byte(118)&~8u);
}
}
