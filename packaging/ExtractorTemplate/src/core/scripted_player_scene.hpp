#pragma once
#include "core/actor_allocation.hpp"
#include "core/actor_motion.hpp"
namespace rolo {
struct ScriptedPlayerSceneState{std::uint32_t controlled{},falling{},live{},main_state{},acceleration{},drag{};std::uint16_t width{},idle{};std::uint8_t credits{},pressed{};};
struct ScriptedPlayerSceneServices{virtual ~ScriptedPlayerSceneServices()=default;virtual void music(std::uint16_t,std::uint16_t)=0;virtual void movement()=0;virtual void fade_black()=0;virtual void wait_input_event()=0;virtual void admit_level()=0;virtual void presentation()=0;};
inline void update_scripted_player_scene(ActorPool&pool,ScriptedPlayerSceneState&s,ScriptedPlayerSceneServices&v){
 auto&initial=pool.resolve(s.controlled);
 if(signed_word(initial.word(12))<=102){v.music(7,0);initial.word(12,102);initial.byte(121,0);initial.longword(58,0);initial.longword(46,0);s.idle=0;s.live=s.falling;auto&falling=pool.resolve(s.live);actor_gravity(falling);actor_integrate(falling);if(signed_word(falling.word(16))<151){falling.word(46,300);return;}falling.word(16,151);if(!(s.pressed&240)){falling.word(46,std::uint16_t(falling.word(46)-1));if(signed_word(falling.word(46))>=0)return;}v.fade_black();while(s.pressed)v.wait_input_event();s.main_state=0x165e;return;}
 if(!(s.credits&128)&&signed_word(initial.word(12))>=220){pool.resolve(s.live).word(12,236);v.fade_black();v.admit_level();return;}
 s.width=320;s.acceleration=0x3000;s.drag=0;initial.byte(124,initial.byte(124)|8);v.movement();s.live=s.controlled;auto&current=pool.resolve(s.live);current.word(16,152);current.byte(124,(current.byte(124)|1)&~16u);current.byte(122,0);current.longword(62,0);
}
inline void scripted_player_scene_entry(ActorPool&pool,ScriptedPlayerSceneState&s,ScriptedPlayerSceneServices&v){update_scripted_player_scene(pool,s,v);v.presentation();}
}
