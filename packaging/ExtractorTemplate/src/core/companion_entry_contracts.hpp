#pragma once
#include "core/actor_state.hpp"
#include <span>
#include <stdexcept>
namespace rolo {
struct CompanionEntryGlobals{ActorState*controlled=nullptr;ActorState*base=nullptr;std::uint8_t c510=0,c513=0,c514=0,c519=0,c51b=0,c520=0,f2bc=0;};
enum class CompanionEntryStep{Waiting,Presentation,MirrorGround,Horizontal,Gravity,FollowTerrain,Integrate,Ceiling,Land,Inactive,Jump};
struct CompanionEntryServices{virtual ~CompanionEntryServices()=default;virtual void step(CompanionEntryStep,ActorState*&,CompanionEntryGlobals&,std::uint16_t=0,std::uint32_t=0)=0;};
// $A84E is a transaction over four globals, not a second player state.
inline void update_uncontrolled_rolo_entry(ActorState*&a,CompanionEntryGlobals&g,CompanionEntryServices&s){
 s.step(CompanionEntryStep::Waiting,a,g);if(g.c513&&signed_long(a->longword(62))>0x10000)a->longword(62,0x10000);
 auto*controlled=g.controlled;const auto action=g.c510,hit1=g.c519,hit2=g.c51b;g.controlled=g.base;g.c510=0;g.c519=0;g.c51b=0;s.step(CompanionEntryStep::Presentation,a,g);g.c51b=hit2;g.c519=hit1;g.c510=action;g.controlled=controlled;
}
inline void update_detached_companion_entry(ActorState*&a,CompanionEntryGlobals&g,CompanionEntryServices&s){
 auto&c=*g.controlled;const auto old=a->byte(46);a->byte(46,old|1);
 if(!(old&1)){a->word(52,0);a->byte(124,(a->byte(124)|1)&249);const auto direction=static_cast<std::uint8_t>(c.byte(121)^254);a->byte(121,direction);a->byte(118,a->byte(118)&~8u);if(direction==0||direction>=128)a->byte(118,a->byte(118)|8);}
 auto speed=static_cast<std::uint16_t>(c.word(58)+2);if(signed_word(speed)>15)speed=15;a->word(58,speed);
 if(a->byte(124)&16)return;
 if(a->byte(124)&6){const auto x=a->word(12),oldx=a->word(52);a->word(52,x);if(oldx!=x){s.step(CompanionEntryStep::Jump,a,g);return;}a->byte(121,static_cast<std::uint8_t>(0-a->byte(121)));a->byte(118,a->byte(118)^8);}
 if((a->byte(124)&129)==128)s.step(CompanionEntryStep::Jump,a,g);
}
struct CompanionHistoryView{std::span<const std::uint8_t>bytes;std::uint16_t cursor=0;std::uint8_t absolute_rom_0d=0;std::uint8_t byte(unsigned at)const{return bytes[at];}std::uint16_t word(unsigned at)const{if(at+1>=bytes.size())throw std::out_of_range("History source extent");return std::uint16_t((bytes[at]<<8)|bytes[at+1]);}};
// $AB3C direct entry, including exact D2 value passed to the inactive fallback.
inline void update_companion_history_entry(ActorState*&a,CompanionEntryGlobals&g,const CompanionHistoryView&h,std::uint16_t incoming_d2,CompanionEntryServices&s){
 const auto definition=a->longword(4);auto*controlled=g.controlled;a->byte(46,a->byte(46)&~8u);const auto at=static_cast<std::uint16_t>((h.cursor-a->word(50))&1023),prior=static_cast<std::uint16_t>((at-16)&1023);auto d2=incoming_d2;
 bool copy=!g.c514&&!g.f2bc&&!(h.byte(at+14)&32);
 auto abs=[](std::uint16_t v){return v&32768?static_cast<std::uint16_t>(0-v):v;};
 if(copy&&!(a->byte(124)&16))copy=signed_word(abs(static_cast<std::uint16_t>(a->word(16)-controlled->word(16))))>signed_word(a->word(52))||signed_word(abs(static_cast<std::uint16_t>(a->word(12)-controlled->word(12))))>signed_word(a->word(52));
 if(copy){d2=h.word(prior);copy=d2==a->word(12);if(copy){d2=h.word(prior+2);copy=d2==a->word(16);}}
 if(copy){a->byte(46,a->byte(46)|8);a->word(12,h.word(at));a->word(16,h.word(at+2));a->word(70,h.word(at+4));a->byte(121,h.byte(at+6));a->byte(122,h.byte(at+7));a->word(58,h.word(at+8));a->word(62,h.word(at+10));a->byte(118,h.byte(at+12));a->byte(120,h.absolute_rom_0d);a->byte(124,h.byte(at+14)&~32u);s.step(CompanionEntryStep::MirrorGround,a,g,at,definition);if(g.c520>=128&&!g.c510)s.step(CompanionEntryStep::Horizontal,a,g,at,definition);return;}
 if(a->byte(117)){s.step(CompanionEntryStep::Inactive,a,g,d2,definition);return;}
 s.step(CompanionEntryStep::Gravity,a,g,at,definition);s.step(CompanionEntryStep::FollowTerrain,a,g,at,definition);s.step(CompanionEntryStep::Integrate,a,g,at,definition);s.step(CompanionEntryStep::Horizontal,a,g,at,definition);s.step(CompanionEntryStep::Ceiling,a,g,at,definition);s.step(CompanionEntryStep::Land,a,g,at,definition);
}
}
