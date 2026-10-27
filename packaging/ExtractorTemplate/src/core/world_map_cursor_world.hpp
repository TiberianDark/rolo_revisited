#pragma once
#include "core/world_map_cursor.hpp"
#include "core/graphics_pool.hpp"
#include "core/world_bunny_data.hpp"
#include "core/world_bunny.hpp"
namespace rolo {
// Isolated native cursor allocation for the development map scene. Full world
// actor/plane initialization and pause-camera allocation remain separate services.
struct WorldMapCursorWorld final:ActorAllocationServices {
    ActorPool pool;GraphicsPool graphics;
    ActorChainDefinition cursor_definition=world_cursor_data::definition.allocation();
    ActorChainDefinition bunny_definition=world_bunny_data::definition.allocation();
    std::uint32_t cursor_key{},bunny_key{};AnimationRandom random;
    explicit WorldMapCursorWorld(const WorldMapCursor& cursor,std::uint16_t reserved_patterns):random{3}{
        pool.initialize_free_stack();graphics.initialize(reserved_patterns);
        const auto result=allocate_actor_chain(pool,{0x13eaa,std::uint32_t(cursor.x)<<16,std::uint32_t(cursor.y)<<16,0,0,0},*this);
        if(!result.success)throw std::logic_error("World cursor allocation failed");
        cursor_key=result.head;initialize_world_map_cursor(pool.resolve(cursor_key));
        const auto bunny=allocate_actor_chain(pool,{0x14ede,0,0,0,0,0},*this);
        if(!bunny.success)throw std::logic_error("World bunny allocation failed");bunny_key=bunny.head;
    }
    const ActorChainDefinition& allocation_definition(std::uint32_t key)override{
        if(key==bunny_definition.initial.key)return bunny_definition;
        if(key!=cursor_definition.initial.key)throw std::out_of_range("World cursor definition");return cursor_definition;
    }
    GraphicsAllocation allocation_graphics(std::uint16_t size)override{return graphics.allocate(size,*this);}
    void allocation_diagnostic(std::uint32_t)override{throw std::logic_error("World cursor graphics exhausted");}
    std::uint16_t marker_word(std::uint32_t)override{throw std::logic_error("Cursor has no MAP marker");}
    void marker_word(std::uint32_t,std::uint16_t)override{throw std::logic_error("Cursor has no MAP marker");}
    std::uint8_t callback_override_flag(std::int16_t index)override{
        if(index!=0&&index!=1)throw std::out_of_range("World actor type gate");return 0;
    }
    void update_bunny(bool paused,const std::array<std::uint8_t,4>& input){update_world_bunny(pool.resolve(bunny_key),paused,input,1280,1280,random);}
    void step(){const auto result=animate_world_map_cursor(pool.resolve(cursor_key));if(result!=AnimationResult::Ok)throw std::logic_error("World cursor animation boundary");
        if(update_actor_animation_from_definition(pool.resolve(bunny_key),0x14ede,world_bunny_data::data)!=AnimationResult::Ok)throw std::logic_error("World bunny animation boundary");}
    ActorState& actor(){return pool.resolve(cursor_key);}
    ActorState& bunny(){return pool.resolve(bunny_key);}
};
}
