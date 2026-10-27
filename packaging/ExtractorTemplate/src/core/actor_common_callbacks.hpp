#pragma once
#include "core/first_enemy.hpp"
#include "core/actor_allocation.hpp"
namespace rolo {
struct ActorDirectContactServices:FirstEnemyServices {
    virtual void hurt_controlled_actor(ActorState&)=0; // $976C direct path.
};
// $E14E: object contact precedes player contact/damage.
inline void update_actor_contact_only(ActorState& actor,FirstEnemyServices& services){
    services.object_contact(actor);if(services.player_contact(actor))services.player_damage(actor);
}
// $E1CE overwrites the whole facing byte after the live contact services.
inline void update_actor_contact_facing(ActorState& actor,FirstEnemyServices& services){
    update_actor_contact_only(actor,services);const auto& controlled=services.controlled_actor();
    const auto delta=static_cast<std::uint16_t>(actor.word(12)-controlled.word(12));
    actor.byte(118,(delta&0x8000)?0:8);
}
// $D89E: inactive gate, contacts, integer step3 and direction selection.
inline void update_actor_contact_walk(ActorState& actor,FirstEnemyServices& services){
    if(actor.byte(117))return;update_actor_contact_only(actor,services);
    actor_integer_x_step(actor,3);services.choose_direction(actor);
}
// $E1BC: direct hit then integer step6, including fractional preservation.
inline void update_actor_hit_walk(ActorState& actor,ActorDirectContactServices& services){
    if(services.player_contact(actor))services.hurt_controlled_actor(actor);
    actor_integer_x_step(actor,6);
}
// $E478: direct hit, ordinary gravity and integration, without a landing query.
inline void update_actor_hit_fall(ActorState& actor,ActorDirectContactServices& services){
    if(services.player_contact(actor))services.hurt_controlled_actor(actor);
    actor_gravity(actor);actor_integrate(actor);
}
// $E776: every grounded call supplies the original jump magnitude before gravity.
inline void update_actor_ground_bounce(ActorState& actor,FirstEnemyServices& services){
    if(actor.byte(124)&1){actor.byte(122,255);actor.longword(62,0x30000);}
    actor_gravity(actor);actor_integrate(actor);services.land(actor);
}
// $EF3C: integer velocity WORDs are signed modular steps, not LONG integration.
inline void update_actor_integer_hit_motion(ActorState& actor,std::uint8_t gate,
        ActorDirectContactServices& services){
    if(!gate&&services.player_contact(actor))services.hurt_controlled_actor(actor);
    actor.byte(116,actor.byte(117)?255:0);
    actor.word(12,static_cast<std::uint16_t>(actor.word(12)+actor.word(58)));
    actor.word(16,static_cast<std::uint16_t>(actor.word(16)+actor.word(62)));
}
// $E798: live roster order, exact definition WORD type, no sentinel admission.
template<class TypeLookup>void replace_actor_callbacks_by_type(ActorPool& pool,
        std::span<const std::uint32_t> roster,std::uint16_t type,std::uint32_t callback,TypeLookup&& lookup){
    if(roster.size()>48)throw std::out_of_range("Actor callback roster extent");
    for(auto key:roster){auto& actor=pool.resolve(key);if(lookup(actor)==type)actor.longword(42,callback);}
}
}
