#pragma once
#include "core/actor_wave_motion.hpp"
namespace rolo {
// Original C5E4 phase, C5E6 quadrant, C5E7 frame cache, C5E8 completion,
// C5E9/C5EA contact latches; F268 offset, F330 display, F2BA timer.
struct ActorPhaseGlobals {
 std::uint16_t frame=0,phase=0,offset=0,display=0,timer=0;
 std::uint8_t last_frame=0,quadrant=0,completed=0,second=0,third=0;
 std::array<std::uint8_t,4> gates{};
};
struct ActorPhaseServices {
 virtual ~ActorPhaseServices()=default;
 virtual bool object_contact(ActorState*&)=0;
 virtual ActorState& controlled()=0;
 virtual void reveal(ActorState*&)=0;
 virtual void spawn_scene(ActorState*&,std::uint32_t,std::uint32_t,std::uint32_t,std::uint32_t,std::uint8_t,std::uint8_t)=0;
 virtual void emit(ActorState*&)=0; // $D77C remains a separate contract.
 virtual void sound(std::uint16_t)=0;
};
inline void update_actor_phase_wave(ActorPhaseGlobals& g,ActorPhaseServices& s){
 const auto low=static_cast<std::uint8_t>(g.frame);if(g.last_frame==low)return;g.last_frame=low;g.display=0x280;if(g.completed)return;
 auto phase=static_cast<std::uint16_t>((g.phase+2)&511);auto quadrant=g.quadrant;
 if(!phase)quadrant=static_cast<std::uint8_t>((quadrant+1)&3);
 if(quadrant>3)throw std::out_of_range("Phase quadrant");g.phase=phase;g.quadrant=quadrant;
 constexpr std::uint16_t amplitude[]{100,100,100,194};g.offset=static_cast<std::uint16_t>((actor_wave_vector(phase,amplitude[quadrant],1).x>>16)+448);
 if(!(g.frame&(g.quadrant==3?1:3)))s.sound(61);
}
inline void reset_actor_phase_wave(ActorPhaseGlobals& g){g.phase=0;g.quadrant=0;g.last_frame=0;g.completed=0;g.second=0;g.third=0;}
inline bool phase_actor_position(ActorState*& a,ActorPhaseGlobals& g,ActorPhaseServices& s){
 update_actor_phase_wave(g,s);if(!a->word(46)){a->word(46,a->word(12));reset_actor_phase_wave(g);return false;}
 a->word(12,static_cast<std::uint16_t>(a->word(46)-g.offset));return true;
}
inline void phase_actor_contact_gate(ActorState*&a,ActorPhaseGlobals&g,ActorPhaseServices&s){if(s.object_contact(a)){g.timer=0;g.gates[0]=8;g.gates[3]=8;}}
// $D57E: completion is latched before reveal/allocation and survives allocation failure.
inline void update_actor_phase_completion(ActorState*&a,ActorPhaseGlobals&g,ActorPhaseServices&s){
 if(!phase_actor_position(a,g,s)||g.gates[0]||!g.third)return;
 phase_actor_contact_gate(a,g,s);if(a->word(70)!=4)return;g.completed=255;s.reveal(a);s.spawn_scene(a,0x14e78,0x2300000,0x2010000,0,0,0);g.gates.fill(1);g.timer=0;
}
// $D624: signed WORD comparison uses playerY-playerHeight with wrap.
inline void update_actor_phase_first(ActorState*&a,ActorPhaseGlobals&g,ActorPhaseServices&s){
 if(!phase_actor_position(a,g,s))return;
 if(!g.gates[0]){phase_actor_contact_gate(a,g,s);if(a->word(70)==12){g.second=255;return;}}
 if(a->byte(48)){s.emit(a);return;}if(g.quadrant==3||(g.frame&127)!=63)return;
 auto&c=s.controlled();const auto top=static_cast<std::uint16_t>(c.word(16)-c.word(38)),bottom=static_cast<std::uint16_t>(a->word(16)+a->word(34));a->word(70,signed_word(bottom)<signed_word(top)?4:8);
}
// $D6C6: the phase3 window uses offset&FFF8==0130 instead of frame&127.
inline void update_actor_phase_second(ActorState*&a,ActorPhaseGlobals&g,ActorPhaseServices&s){
 if(!phase_actor_position(a,g,s))return;
 if(!g.gates[0]&&g.second){phase_actor_contact_gate(a,g,s);if(a->word(70)==12){g.third=255;return;}}
 if(a->byte(48)){s.emit(a);return;}
 if(g.quadrant==3){if((g.offset&0xfff8)!=0x130)return;}else if(g.frame&127)return;
 const auto edge=static_cast<std::uint16_t>(a->word(16)+a->word(34)-a->word(38));a->word(70,signed_word(edge)<signed_word(s.controlled().word(16))?4:8);
}
}
