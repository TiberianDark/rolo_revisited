#pragma once
#include "core/player_collision_phase.hpp"
#include "core/player_ceiling_collision.hpp"
#include "core/player_floor_collision.hpp"
#include "core/player_side_collision.hpp"
#include "core/player_collision_followups.hpp"
#include "core/actor_definition.hpp"
namespace rolo {
struct PlayerTerrainCollisionServices:PlayerCollisionPhaseServices {
    ActorPool& pool;const std::uint32_t& controlled;const ActorTerrain& terrain;std::uint8_t& c545;
    PlayerTerrainCollisionServices(ActorPool& p,const std::uint32_t& c,const ActorTerrain& t,std::uint8_t& slope):pool(p),controlled(c),terrain(t),c545(slope){}
    PlayerTerrainCollisionServices(ActorPool& p,PlayerCollisionPhaseState& s,const ActorTerrain& t,std::uint8_t& slope):PlayerTerrainCollisionServices(p,s.controlled,t,slope){}
    void ceiling_collision(std::uint32_t& key) override {player_ceiling_collision(pool,key,controlled,terrain);}
    void floor_collision(std::uint32_t& key) override {player_floor_collision(pool,key,controlled,terrain,c545);}
    void side_collision(std::uint32_t& key) override {player_side_collision(pool.resolve(key),terrain);}
    void collision_followup_a(std::uint32_t&) override {player_collision_tile_crossing(pool.resolve(controlled),terrain);}
    void collision_followup_b(std::uint32_t&) override {player_collision_top_corner(pool.resolve(controlled),terrain);}
};
struct PlayerDefinedTerrainCollisionServices final:PlayerTerrainCollisionServices {
    std::span<const ActorDefinition> definitions;
    PlayerDefinedTerrainCollisionServices(ActorPool& p,const std::uint32_t& c,const ActorTerrain& t,
            std::uint8_t& slope,std::span<const ActorDefinition> d):PlayerTerrainCollisionServices(p,c,t,slope),definitions(d){}
    std::uint16_t collision_definition_type(const ActorState& actor) override {
        for(const auto& d:definitions)if(d.key==actor.longword(4))return d.word(10);
        throw std::logic_error("Shared collision actor definition unbound");
    }
};
}
