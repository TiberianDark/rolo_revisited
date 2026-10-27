#pragma once
#include "core/actor_definition.hpp"
#include "core/actor_motion.hpp"
#include "core/animation.hpp"
#include "core/score_award.hpp"
namespace rolo {
struct Level1CollectibleServices {
    virtual ~Level1CollectibleServices()=default;
    virtual bool collectible_contact(ActorState&)=0; // $9012: true iff returned Z clear.
    virtual const ActorDefinition& collectible_definition(const ActorState&)=0;
    virtual void collectible_score(std::uint32_t)=0; // $997E including thresholds.
    virtual std::uint8_t& collectible_lives()=0;
    virtual void collectible_sound(std::uint16_t)=0;
    virtual AnimationRandom& collectible_random()=0; // Shared C4BE, also used by animations.
};
// $9958..$997E: score and sound remain explicit service requests.
inline void collect_level1_scored_item(ActorState& actor,const ActorDefinition& definition,Level1CollectibleServices& world) {
        actor.longword(42,0xb7c0);actor.byte(125,actor.byte(125)|4);
        world.collectible_score(definition.longword(28));world.collectible_sound(15);
}
// $99E2..$9A04: sound occurs before retirement-state publication.
inline void collect_level1_extra_life(ActorState& actor,Level1CollectibleServices& world) {
        world.collectible_sound(64);actor.longword(42,0xb7c0);actor.byte(125,actor.byte(125)|4);
        add_player_lives(world.collectible_lives(),1);
}
// $B702..$B714, bounded immutable Level1 collection dispatch.
inline void update_level1_collectible(ActorState& actor,Level1CollectibleServices& world) {
    if(!world.collectible_contact(actor))return;
    const auto& definition=world.collectible_definition(actor);
    const auto callback=definition.longword(22);
    if(callback==0x9958)collect_level1_scored_item(actor,definition,world);
    else if(callback==0x99e2)collect_level1_extra_life(actor,world);
    else throw std::logic_error("Unbound collectible definition callback");
}
// $B7D8..$B804. The RNG upper endpoint is exclusive; SUBQ affects the byte only.
inline void initialize_collected_item_motion(ActorState& actor,AnimationRandom& random) {
    actor.byte(121,static_cast<std::uint8_t>(random.between(0,3)-1));
    actor.longword(58,0x30000);actor.longword(62,std::uint32_t(random.between(3,9))<<16);
    actor.byte(122,255);
}
// $B7C0..$B7D8. Retirement is controlled by existing animation/lifetime services.
inline void update_collected_item(ActorState& actor,AnimationRandom& random) {
    if(!actor.byte(46)){actor.byte(46,255);initialize_collected_item_motion(actor,random);}
    actor_gravity(actor);actor_integrate(actor);
}
}
