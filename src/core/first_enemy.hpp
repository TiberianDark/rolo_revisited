#pragma once
#include "core/actor_motion.hpp"
#include <utility>

namespace rolo {
// Required shared services stay explicit until their own native contracts close.
// This does not run enemy gameplay in the SDL preview yet.
struct FirstEnemyServices {
    virtual ~FirstEnemyServices()=default;
    virtual ActorState* linked_actor(const ActorState&)=0;
    virtual ActorState& controlled_actor()=0;
    virtual void object_contact(ActorState&)=0; // $8EAA
    virtual bool player_contact(ActorState&)=0; // $9012, returned Z
    virtual void player_damage(ActorState&)=0; // $96C6
    virtual void gravity(ActorState& actor) {actor_gravity(actor);} // $CD8E
    virtual void integrate(ActorState& actor) {actor_integrate(actor);} // $CFCE
    virtual void land(ActorState&)=0; // $CF46
    virtual void choose_direction(ActorState&)=0; // $D168
};

// $B566..$B702 for definition $13F98. Caller owns stable body/link records.
inline void update_first_enemy(ActorState& body,FirstEnemyServices& services) {
    auto contact=[&](ActorState& actor) {
        if(services.player_contact(actor)) services.player_damage(actor);
    };
    if(body.byte(46)==0) {
        if(body.byte(117)!=0) return;
        services.object_contact(body);
        if(body.word(70)==0x30) return;
        body.word(70,4);
        auto* linked=services.linked_actor(body);
        if(linked) {
            linked->word(12,body.word(12));linked->word(16,body.word(16));
            linked->word(70,body.word(70));
            for(const auto field:{118,121,122}) linked->byte(field,body.byte(field));
        }
        contact(body);
        if(body.byte(124)&1) {
            // $D042 changes integer X and only the highword of velocity58.
            actor_integer_x_step(body,1);
        }
        services.gravity(body);services.integrate(body);services.land(body);services.choose_direction(body);
        linked=services.linked_actor(body);
        if(!linked) return;
        if(body.byte(47)!=0) {body.byte(47,static_cast<std::uint8_t>(body.byte(47)-1));return;}
        const auto& controlled=services.controlled_actor();
        auto delta=static_cast<std::uint16_t>(body.word(16)-controlled.word(16));
        // BPL/NEG.W then signed BGT, including the -32768 wrap case.
        if(signed_word(delta)<0) delta=static_cast<std::uint16_t>(0u-delta);
        if(signed_word(delta)>8) return;
        auto source=body.word(12),target=controlled.word(12);
        if(body.byte(118)&8) std::swap(source,target);
        delta=static_cast<std::uint16_t>(target-source);
        if(delta&0x8000) return; // BMI uses result N, not overflow-aware comparison.
        if(signed_word(delta)>100) return;
        body.byte(46,20);linked->longword(50,0x00060000);return;
    }
    body.word(70,0);
    auto* linked=services.linked_actor(body);
    if(!linked) {body.byte(46,0);return;}
    if(linked->word(70)==0x30) return;
    linked->word(70,0x2c);linked->word(16,body.word(16));linked->byte(118,body.byte(118));
    services.object_contact(body);services.object_contact(*linked);
    contact(body);contact(*linked);
    body.byte(46,static_cast<std::uint8_t>(body.byte(46)-1));
    if(body.byte(46)==0) {
        body.byte(46,1);
        const auto step=linked->longword(50);
        auto position=linked->longword(12);
        linked->byte(118,body.byte(118));
        if(linked->byte(118)&8) {
            position-=step;
            if(signed_long(position)>=signed_long(body.longword(12))) {
                position=body.longword(12);body.byte(46,0);body.byte(47,50);
            }
        } else {
            position+=step;
            if(signed_long(position)<=signed_long(body.longword(12))) {
                position=body.longword(12);body.byte(46,0);body.byte(47,50);
            }
        }
        linked->longword(12,position);linked->longword(50,step-0x3000u);
    }
    body.byte(121,0);body.longword(58,0);
    services.gravity(body);services.integrate(body);services.land(body);
}
}
