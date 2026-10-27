#pragma once
#include "core/actor_state.hpp"
#include "core/animation.hpp"
#include "core/actor_motion.hpp"
namespace rolo {
// $B782..$B7B2; immutable six-byte direction table at $B7B2.
inline std::array<std::uint8_t,6> bounce_direction_bytes{};
inline void initialize_actor_bounce_motion(ActorState& actor,AnimationRandom& random){
 actor.byte(121,bounce_direction_bytes.at(random.between(0,6)));
 actor.longword(58,std::uint32_t(random.between(1,5))<<16);
 actor.longword(62,std::uint32_t(random.between(3,9))<<16);
 actor.byte(122,255);
}
// $B714: reload current definition after random initialization, then tail-dispatch.
template<class World>void update_actor_bounce_restart(std::uint32_t key,World& w){
 auto& a=w.pool.resolve(key);initialize_actor_bounce_motion(a,w.random);
 const auto callback=w.definition(a.longword(4)).longword(12);
 a.longword(42,callback);w.invoke_actor_callback(key,callback);
}
// $B726: initialize once, gravity/integration/landing, signed X clamp, restore onfloor.
template<class World>void update_actor_bounce_landing(std::uint32_t key,World& w){
 auto& a=w.pool.resolve(key);if(a.byte(117)&2)return;
 if(!a.byte(46)){a.byte(46,255);initialize_actor_bounce_motion(a,w.random);}
 actor_gravity(a);actor_integrate(a);w.enemy.land(a);
 auto x=a.word(12);if(signed_word(x)<=32)x=32;
 else{auto right=static_cast<std::uint16_t>(w.width-32);if(signed_word(x)>=signed_word(right))x=right;}
 a.word(12,x);
 if(a.byte(124)&1){const auto& d=w.definition(a.longword(4));a.byte(46,0);a.longword(42,d.longword(12));}
}

}
