#pragma once
#include "core/first_enemy.hpp"
#include "core/actor_contact.hpp"
#include "core/actor_defeat.hpp"
#include "core/actor_object_contact.hpp"
#include "core/actor_terrain.hpp"
#include <stdexcept>

namespace rolo {
// Native connection of B566 -> 9012 -> 96C6 -> 97AC. World ownership, definition
// data, allocations, sound, terrain and object-contact remain required services.
struct FirstEnemyCombatServices:FirstEnemyServices,DamageServices,DefeatServices {
    virtual ContactGlobals& contact_globals()=0;
    bool player_contact(ActorState& actor) override {
        return actor_player_contact(actor,controlled_actor());
    }
    void player_damage(ActorState& actor) override {
        (void)actor_player_damage(actor,controlled_actor(),contact_globals(),*this);
    }
    void hit_counter_zero(ActorState& actor) override {
        actor_hit_counter_zero(actor,*this);
    }
};

// World implementations supply the ordered contact list and stable identities.
// Keep unsupported metadata returns explicit rather than inventing an actor.
struct FirstEnemyObjectCombatServices:FirstEnemyCombatServices,ObjectContactServices {
    void object_contact(ActorState& actor) override {
        (void)actor_object_contact(actor,*this);
    }
    ActorState& defeat_contact_actor(ActorState& actor) override {
        auto* result=actor_hit_counter_zero(actor,*this);
        if(!result) throw std::logic_error("Contact defeat returned definition data; actor target is unresolved");
        return *result;
    }
    void defeat_contact_body(ActorState& actor) override {
        (void)actor_hit_counter_zero(actor,*this);
    }
    void contact_sound(std::uint16_t effect) override {sound_effect(effect);}
};
struct FirstEnemyWorldCombatServices:FirstEnemyObjectCombatServices,ActorTerrainServices {
    void land(ActorState& actor) override {actor_land(actor,actor_terrain());}
    void choose_direction(ActorState& actor) override {actor_choose_direction(actor,*this);}
};
}
