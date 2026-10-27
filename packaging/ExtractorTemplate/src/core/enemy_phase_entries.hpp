#pragma once
#include "core/actor_phase_ending.hpp"
#include "core/graphic_actor_shared_entries.hpp"
#include "core/actor_motion.hpp"
#include "core/animation.hpp"
#include "core/actor_allocation.hpp"
namespace rolo {
struct EnemyPhaseServices{virtual ~EnemyPhaseServices()=default;virtual bool floor_nonnegative(std::uint16_t,std::uint16_t)=0;virtual void floor_contact(ActorState&)=0;virtual std::uint32_t spawn(std::uint32_t,std::uint32_t,std::uint32_t)=0;};
inline void enemy_begin_fall(ActorState&a,EnemyPhaseServices&s){if(s.floor_nonnegative(a.word(12),std::uint16_t(a.word(16)+59)))a.byte(46,std::uint8_t(a.byte(46)+1));actor_gravity(a);if(signed_long(a.longword(62))>0x50000)a.longword(62,0x50000);actor_integrate(a);}
inline void enemy_buoyant_turn(ActorState&a,AnimationRandom&random,EnemyPhaseServices&s){s.floor_contact(a);a.word(70,4);adjust_actor_vertical_force(a,0x4000);actor_integrate(a);if(!a.byte(47)){if(a.byte(122)&128){const auto n=std::uint8_t(random.between(3,9));a.byte(47,n);a.byte(48,n);}return;}a.byte(47,std::uint8_t(a.byte(47)-1));if(!a.byte(47)){a.byte(46,std::uint8_t(a.byte(46)+1));a.word(50,250);}}
inline void enemy_finish_rise(ActorState&a){actor_gravity(a);if(a.byte(122)&128){actor_integrate(a);return;}a.byte(122,0);a.longword(62,0);a.byte(46,std::uint8_t(a.byte(46)+1));}
inline void enemy_bob_wait(ActorState&a,std::uint16_t frame){actor_integrate(a);a.longword(62,0);constexpr std::int8_t offsets[]{0,0,1,0,1,1,0,1,0,0,-1,0,-1,-1,0,-1};const auto n=(frame+a.byte(48))&15;a.word(16,std::uint16_t(a.word(16)+offsets[n]));a.word(50,std::uint16_t(a.word(50)-1));if(!a.word(50))a.word(70,8);}
struct EnemyBurstRecord{std::uint32_t definition;std::array<std::uint8_t,4>bytes;};
inline std::array<EnemyBurstRecord,6> enemy_burst_records{};
inline void enemy_spawn_burst(ActorPool&pool,std::uint32_t key,EnemyPhaseServices&s){auto&a=pool.resolve(key);a.word(46,std::uint16_t(a.word(46)+4));a.word(70,4);for(unsigned i=0;i<6;++i){const auto&record=enemy_burst_records[i];const auto child=s.spawn(record.definition,a.longword(12),a.longword(16));if(!child)continue;auto&b=pool.resolve(child);b.longword(46,key);b.word(50,std::uint16_t(5-i));b.byte(122,255);b.byte(121,record.bytes[0]);b.byte(59,record.bytes[1]);b.byte(60,record.bytes[2]);b.byte(63,record.bytes[3]);}}
inline void enemy_burst_pause(ActorState&a,std::uint16_t frame,std::uint16_t&sound){if(read_actor_phase_entry(a,0).changed)a.word(50,100);if(!(frame&7))sound=53;a.word(50,std::uint16_t(a.word(50)-1));if(a.byte(50)&128)a.word(46,std::uint16_t(a.word(46)+4));}
inline void enemy_burst_blink(ActorState&a,std::uint16_t&sound){if(read_actor_phase_entry(a,0).changed){a.word(50,25);a.byte(52,4);}const std::uint16_t selector=(a.byte(52)&1)?4:0;if(selector!=a.word(70)){a.word(70,selector);sound=21;}a.word(50,std::uint16_t(a.word(50)-1));if(a.byte(50)&128){a.word(50,25);a.byte(52,std::uint8_t(a.byte(52)-1));if(a.byte(52)&128)a.word(46,std::uint16_t(a.word(46)+4));}}
inline void enemy_burst_end(ActorState&a,std::uint16_t&sound){if(read_actor_phase_entry(a,0).changed){a.word(70,4);a.word(50,50);sound=17;}a.word(50,std::uint16_t(a.word(50)-1));if(a.byte(50)&128)a.word(46,std::uint16_t(a.word(46)+4));}
}
