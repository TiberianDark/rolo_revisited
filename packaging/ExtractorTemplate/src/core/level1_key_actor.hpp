#pragma once
#include "core/first_enemy.hpp"
#include "core/level1_reward_curve.hpp"
namespace rolo {
struct Level1KeyActorServices:FirstEnemyServices,RewardCurveServices {
    virtual void key_actor_sound(std::uint16_t)=0;
};
// $B2E6 for definition144A4. This is the marker-param5 object, whose defeat
// successor flies to the key HUD counter C550; appearance does not define AI.
inline void update_level1_key_proximity(ActorState& actor,FirstEnemyServices& services) {
    if(actor.byte(117))return;actor.word(70,0);
    auto distance=static_cast<std::uint16_t>(actor.word(12)-services.controlled_actor().word(12));
    if(distance&0x8000)distance=static_cast<std::uint16_t>(0u-distance);
    if(distance<=100)actor.longword(42,0xb314);
}
// $B314..$B386.
inline void update_level1_key_actor(ActorState& actor,Level1KeyActorServices& services) {
    if(actor.byte(117))return;
    services.object_contact(actor);
    if(actor.word(70)!=0x30&&services.player_contact(actor))services.player_damage(actor);
    if(actor.word(70)==0x30){
        services.key_actor_sound(8);actor.word(70,0x34);
        start_reward_curve(actor,280,41,0xffffc550,services);return;
    }
    actor.word(70,4);if(actor.byte(124)&1)actor_integer_x_step(actor,1);
    services.gravity(actor);services.integrate(actor);services.land(actor);services.choose_direction(actor);
}
}
