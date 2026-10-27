#pragma once
#include "core/player_ceiling_collision.hpp"
#include "core/level1_companions.hpp"
#include "core/display_setup.hpp"
#include "core/world_map_cursor.hpp"
namespace rolo {
struct CeilingStageServices{virtual ~CeilingStageServices()=default;virtual FloorProbe probe(std::uint16_t,std::uint16_t)=0;};
inline bool apply_ceiling_stage_surface(ActorState&a,std::uint16_t target){if(target<a.word(16))return false;a.word(16,std::uint16_t(target+1));a.word(18,0);if(static_cast<std::int8_t>(a.byte(122))>0)return true;a.byte(122,0);a.longword(62,0);a.byte(125,a.byte(125)|128);return false;}
inline void run_ceiling_stage(ActorState&a,std::uint16_t reach,CeilingStageServices&s,bool first){
 if(first){const auto p=s.probe(a.word(12),std::uint16_t(a.word(16)-a.word(38)+16));if(p.found){const auto target=std::uint16_t(p.y+a.word(38)),distance=std::uint16_t(target-a.word(16));if(signed_word(reach)>=signed_word(distance)&&apply_ceiling_stage_surface(a,target))return;}}
 const auto p=s.probe(a.word(12),std::uint16_t(a.word(16)-a.word(38)));if(!p.found)return;const auto target=std::uint16_t(p.y+a.word(38)),distance=std::uint16_t(target-a.word(16));if(signed_word(reach)>=signed_word(distance))(void)apply_ceiling_stage_surface(a,target);
}
inline void relocate_controlled_actor(ActorState&source,ActorState&controlled){const auto x=std::uint16_t(source.word(12)+source.word(20));controlled.word(20,controlled.word(12));controlled.word(12,x);controlled.word(14,0);controlled.longword(58,0);controlled.byte(121,0);const auto y=std::uint16_t(source.word(16)+source.word(24));controlled.word(24,controlled.word(16));controlled.word(16,y);controlled.word(18,0);controlled.longword(62,0);controlled.byte(122,0);}
enum class CompanionDeathRebuild{ClearForeground,ClearBackground,Camera,ForegroundTerrain,BackgroundTerrain,ForegroundScroll,BackgroundScroll,Render,FadeIn};
struct CompanionDeathRebuildServices{virtual ~CompanionDeathRebuildServices()=default;virtual void step(CompanionDeathRebuild)=0;virtual void transfer(GraphicsTransferRequest)=0;};
inline void finish_companion_death(std::uint32_t key,ActorPool&pool,Level1CompanionState&companions,std::uint8_t&effect,ContactGlobals&contact,CompanionDeathRebuildServices&s){auto&a=pool.resolve(key);a.byte(116,255);a.byte(125,a.byte(125)|4);detach_level1_companion(a,companions,pool);for(auto op:{CompanionDeathRebuild::ClearForeground,CompanionDeathRebuild::ClearBackground,CompanionDeathRebuild::Camera,CompanionDeathRebuild::ForegroundTerrain,CompanionDeathRebuild::BackgroundTerrain,CompanionDeathRebuild::ForegroundScroll,CompanionDeathRebuild::BackgroundScroll,CompanionDeathRebuild::Render})s.step(op);s.transfer({0xffffc9bc,0xf400,0x40000000,320});s.step(CompanionDeathRebuild::FadeIn);contact.hit_gate_c51a=0;effect=0;contact.action_latch_c517=0;}
struct WorldActorInitialization{std::uint16_t x{},y{},random_seed{};std::uint32_t controlled{},base{},bunny{};std::array<std::uint32_t,3>companions{};};
struct WorldActorAllocationServices:ActorAllocationServices{virtual void startup_reset()=0;};
inline bool initialize_world_actors(ActorPool&pool,WorldActorInitialization&g,WorldActorAllocationServices&s){const auto cursor=allocate_actor_chain(pool,{0x13eaa,std::uint32_t(g.x)<<16,std::uint32_t(g.y)<<16,0,0,0},s);if(!cursor.success){s.startup_reset();return false;}g.controlled=g.base=cursor.head;initialize_world_map_cursor(pool.resolve(cursor.head));g.companions.fill(0);const auto bunny=allocate_actor_chain(pool,{0x14ede,0,0,0,0,0},s);g.bunny=bunny.returned_key;g.random_seed=3;return true;}
}
