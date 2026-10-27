#pragma once
#include "core/first_enemy_combat.hpp"
#include "core/actor_definition.hpp"
#include "core/actor_reservations.hpp"
namespace rolo {
// World binding: every contact/movement service resolves the same actor pool.
// Sound and allocation remain required concrete host services, never silent stubs.
struct FirstEnemyActorWorld:FirstEnemyWorldCombatServices {
    ActorPool& pool;ActorReservationPool& reservations;ContactGlobals& globals;
    std::uint32_t& controlled;const ActorTerrain& terrain;
    std::uint16_t& world_width;std::span<const ActorDefinition> definitions;
    std::array<ActorState*,8> roots{};std::size_t root_count{};
    FirstEnemyActorWorld(ActorPool& p,ActorReservationPool& r,ContactGlobals& g,
            std::uint32_t& c,const ActorTerrain& t,std::uint16_t& width,std::span<const ActorDefinition> d)
        :pool(p),reservations(r),globals(g),controlled(c),terrain(t),world_width(width),definitions(d){}
    const ActorDefinition& definition(const ActorState& actor) const {
        for(const auto& d:definitions)if(d.key==actor.longword(4))return d;
        throw std::logic_error("World actor definition not bound");
    }
    ActorState* linked_actor(const ActorState& actor) override {
        const auto next=actor.longword(84);return next?&pool.resolve(next):nullptr;
    }
    ActorState& controlled_actor() override{return pool.resolve(controlled);}
    ContactGlobals& contact_globals() override{return globals;}
    ActorState* next_linked_actor(const ActorState& actor) override{return linked_actor(actor);}
    ActorState* next_contact_link(const ActorState& actor) override{return linked_actor(actor);}
    ActorState& damage_parent(const ActorState& actor) override{return pool.resolve(actor.longword(76));}
    std::uint8_t definition_byte7(const ActorState& actor) override{return definition(actor).byte(7);}
    std::uint8_t definition_byte26(const ActorState& actor) override{return definition(actor).byte(26);}
    std::uint16_t definition_type(const ActorState& actor) override{return definition(actor).word(10);}
    DefeatDefinition defeat_definition(const ActorState& actor) override {
        const auto& d=definition(actor);return {d.word(32),d.longword(28)};
    }
    const ActorTerrain& actor_terrain() override{return terrain;}
    std::uint16_t terrain_world_width() override{return world_width;}
    std::uint16_t contact_actor_handle(const ActorState& actor) override {
        for(std::size_t i=0;i<pool.actors.size();++i)
            if(&pool.actors[i]==&actor)return static_cast<std::uint16_t>(ActorPool::key(i));
        throw std::logic_error("Contact actor outside world pool");
    }
    std::span<ActorState* const> contact_roots() override {
        root_count=0;auto key=reservations.head;
        while(key) {
            if(root_count==roots.size())throw std::logic_error("World reservation cycle");
            const auto& node=reservations.resolve(key);
            roots[root_count++]=&pool.resolve(0xffff0000u|node.actor);key=node.next;
        }
        return {roots.data(),root_count};
    }
};
// Concrete contact/movement world. Allocation and the sound command word are
// shared with the host's actor lifecycle and audio consumer respectively.
struct FirstEnemyAllocatedWorld:FirstEnemyActorWorld {
    ActorAllocationServices& allocation_services;std::uint16_t& sound_command;
    FirstEnemyAllocatedWorld(ActorPool& p,ActorReservationPool& r,ContactGlobals& g,
            std::uint32_t& c,const ActorTerrain& t,std::uint16_t& width,
            std::span<const ActorDefinition> d,ActorAllocationServices& allocation,std::uint16_t& sound)
        :FirstEnemyActorWorld(p,r,g,c,t,width,d),allocation_services(allocation),sound_command(sound){}
    void sound_effect(std::uint16_t effect) override{sound_command=effect;} // $788AE handoff, not playback.
    void spawn_secondary(std::uint32_t definition,std::uint32_t x,std::uint32_t y) override {
        // $97DA caller: no marker, facing0; retains allocator's partial failure semantics.
        (void)allocate_actor_chain(pool,{definition,x,y,0,0,0},allocation_services);
    }
};
}
