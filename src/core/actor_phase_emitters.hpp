#pragma once
#include "core/actor_common_state.hpp"
#include "core/actor_phase_emitter_data.hpp"
namespace rolo {
struct PhaseEmitterContext{std::uint32_t resource=0,d2=0,d3=0;};
struct PhaseEmitterRequest{std::uint32_t definition,resource,x,y;std::uint8_t facing,marker;};
struct PhaseEmitterServices{virtual ~PhaseEmitterServices()=default;virtual void sound(std::uint16_t,ActorState*&,PhaseEmitterContext&)=0;virtual ActorState* allocate(ActorState*&,PhaseEmitterContext&,const PhaseEmitterRequest&)=0;};
inline std::uint32_t emitter_data_long(std::span<const std::uint8_t>b,unsigned at){if(at+3>=b.size())throw std::out_of_range("Emitter data");return(std::uint32_t(b[at])<<24)|(std::uint32_t(b[at+1])<<16)|(std::uint32_t(b[at+2])<<8)|b[at+3];}
// $ED6A -> $ED90, four original eight-byte velocity records.
inline void update_actor_phase_jump(ActorState*&a,PhaseEmitterContext&c,PhaseEmitterServices&s){
 if(actor_phase_changed(*a)){s.sound(60,a,c);a->word(70,4);const auto at=a->byte(53);if(at%8||at>24)throw std::out_of_range("ED90 jump phase");a->byte(53,(at+8)&31);a->byte(122,255);a->byte(121,phase_emitter_data::jump[at]);a->longword(58,emitter_data_long(phase_emitter_data::jump,at)&0xffffff);a->longword(62,emitter_data_long(phase_emitter_data::jump,at+4));return;}
 if(a->byte(124)&1){a->word(46,static_cast<std::uint16_t>(a->word(46)+4));a->word(14,0);a->longword(58,0);a->word(18,0);a->longword(62,0);}
}
// $ED6E -> $EE18, BYTE timer and eight 14-byte emission records.
inline void update_actor_phase_emission(ActorState*&a,PhaseEmitterContext&c,PhaseEmitterServices&s){
 if(actor_phase_changed(*a)){a->byte(51,0);a->byte(52,8);}auto timer=static_cast<std::uint8_t>(a->byte(52)-1);a->byte(52,timer);
 if(timer>=128){a->byte(52,8);const auto at=a->byte(51);if(at==112){a->word(46,0);return;}if(at%14||at>98)throw std::out_of_range("EE18 emission phase");const auto&b=phase_emitter_data::emit;a->word(70,b[at]);a->byte(118,b[at+1]);const auto def=emitter_data_long(b,at+2);
  const auto ox=std::bit_cast<std::int8_t>(b[at+6]),oy=std::bit_cast<std::int8_t>(b[at+7]);c.d2=(std::uint32_t(static_cast<std::uint16_t>(a->word(12)+ox))<<16)|(c.d2>>16);c.d3=(std::uint32_t(static_cast<std::uint16_t>(a->word(16)+oy))<<16)|(c.d3>>16);
  auto*saved=a;auto*child=s.allocate(a,c,{def,c.resource,c.d2,c.d3,a->byte(118),0});a=saved;
  if(child){child->byte(71,b[at+8]);child->byte(118,b[at+9]);child->byte(119,b[at+9]);child->word(58,std::uint16_t((b[at+10]<<8)|b[at+11]));child->word(62,std::uint16_t((b[at+12]<<8)|b[at+13]));s.sound(58,a,c);}a->byte(51,static_cast<std::uint8_t>(a->byte(51)+14));
 }if(std::bit_cast<std::int8_t>(a->byte(52))<=4)a->word(70,0);
}
}
