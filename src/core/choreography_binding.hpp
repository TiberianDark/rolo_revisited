#pragma once
#include "core/actor_choreography_chain.hpp"
#include "core/actor_platform_contact.hpp"
#include "core/platform_surface.hpp"
namespace rolo {
// Native BA64 eleven-entry choreography and BA9E falling reward platforms.
// Original embedded BE08/BE1A/BE3E data are exported as typed arrays.
template<class World>void update_choreography_actor(World&w,std::uint32_t key,bool platform){
 auto&a=w.pool.resolve(key);
 if(!platform){
  switch(a.byte(50)){
  case 0:advance_choreography_phase(a,64);return;
  case 1:case 9:move_choreography_chain(w.pool,key,false);return;
  case 2:{advance_choreography_phase(a,16);auto cursor=key;
   for(unsigned i=0;i<9;++i){auto&part=w.pool.resolve(cursor);const auto y=part.longword(16);const auto r=allocate_actor_chain(w.pool,{level1_object_data::choreography_spawn[i],part.longword(12),(y&0xffff0000)|std::uint16_t(y+16),0,0,0},w);w.choreography_roster[i]=r.tail;if(r.success)w.pool.resolve(r.tail).longword(42,0xa84c);cursor=part.longword(84);}return;}
  case 3:move_choreography_roster(w.pool,key,w.choreography_roster,false);return;
  case 4:tick_choreography_phase(a,16);return;
  case 5:move_choreography_roster(w.pool,key,w.choreography_roster,true);return;
  case 6:retire_choreography_roster(w.pool,key,w.choreography_roster);return;
  case 7:move_choreography_chain(w.pool,key,true);return;
  case 8:rotate_choreography_chain(w.pool,key);return;
  case 10:{auto cursor=key;for(unsigned row=0;row<3;++row){const auto permutation=w.random.between(0,6)*3;for(unsigned col=0;col<3;++col){auto&part=w.pool.resolve(cursor);w.choreography_roster[row*3+col]=cursor;part.word(20,row*3+col);part.longword(42,0xba9e);part.longword(46,0xbe3e);part.longword(50,level1_object_data::choreography_permutations[permutation+col]);part.byte(54,16);part.byte(55,3);part.word(56,0);cursor=part.longword(84);}}return;}
  default:throw std::out_of_range("BA64 phase");}
 }
 struct Contact final:ActorPlatformContactServices{
  World&w;explicit Contact(World&v):w(v){}
  void restore_platform_actor(std::uint32_t rider)override{auto&p=w.pool.resolve(w.pool.resolve(rider).longword(98));const auto offset=p.longword(46)==0xbe46?4u:0u;PlatformPositionCache cache;restore_actor_platform_surface(w.pool,rider,cache,{std::uint8_t(p.word(36)/16),std::span<const std::uint16_t>(level1_object_data::choreography_tiles).subspan(offset,4)},{w.level_assets.terrain_bank().collision,player_data::shapes});}
 }contact(w);
 auto&c=w.pool.resolve(w.movement.controlled);
 if(!a.word(56)){
  ActorPlatformRoster roster{w.input.base_key,w.movement.controlled,w.companion_state.slots};update_controlled_platform_contact(w.pool,key,roster,contact);
  if(c.longword(98)!=key||!(c.byte(122)&128)||a.longword(46)==0xbe46||signed_word(c.word(16))<signed_word(a.word(16)))return;
  a.word(56,a.word(16));a.byte(122,255);a.longword(62,c.longword(62));c.byte(122,0);c.longword(62,0);
  for(;;){const auto r=allocate_actor_chain(w.pool,{a.longword(50),a.longword(12),std::uint32_t(std::uint16_t(a.word(16)-a.word(38)))<<16,0,0,0},w);if(!r.success)break;w.pool.resolve(r.head).longword(42,0xb726);a.byte(55,std::uint8_t(a.byte(55)-1));if(!a.byte(55))break;}
 }
 actor_gravity(a);actor_integrate(a);
 const auto group=level1_object_data::choreography_groups.at(a.word(20))/4;
 if(signed_word(a.word(56))<=signed_word(a.word(16))){a.word(16,a.word(56));a.word(18,0);a.longword(62,0);a.byte(122,0);a.word(56,0);for(unsigned i=0;i<3;++i)w.pool.resolve(w.choreography_roster.at(group+i)).word(70,4);}
 for(unsigned i=0;i<3;++i)w.pool.resolve(w.choreography_roster.at(group+i)).longword(46,0xbe46);
}
}
