#pragma once
#include "core/actor_active_list.hpp"
#include "core/actor_definition.hpp"
#include "core/actor_animation.hpp"
#include "core/actor_scheduler.hpp"
namespace rolo {
struct ActorAnimationListServices {
    virtual ~ActorAnimationListServices()=default;
    virtual const ActorDefinition& animation_definition(std::uint32_t key)=0;
    virtual void animation_callback(std::uint32_t identity,std::uint32_t callback)=0;
    virtual void animate_actor(std::uint32_t identity,ActorState& actor,const ActorDefinition& definition)=0;
};
// FCD4..FD44 + FE0A..FE1E. Definition identity and actor identity survive callback,
// but referenced bytes and the next list entry remain live; parent fractions retained.
inline void update_actor_animation_list(ActorPool& pool,const ActiveActorList& active,
        std::uint8_t& animation_phase_f280,ActorAnimationListServices& services){
    animation_phase_f280=255;
    for(std::size_t index=0;index<active.keys.size();++index){
        const auto identity=active.keys[index];
        if(!identity){animation_phase_f280=0;return;}
        auto& actor=pool.resolve(identity);
        const auto& definition=services.animation_definition(actor.longword(4));
        if(definition.byte(7)&32)services.animation_callback(identity,actor.longword(42));
        if(definition.word(10)!=0x18){
            const auto parent=actor.longword(76);
            if(parent&&!(definition.byte(26)&64)){
                const auto& source=pool.resolve(parent);
                actor.word(12,source.word(12));actor.word(16,source.word(16));actor.word(70,source.word(70));
                actor.byte(118,source.byte(118));actor.byte(121,source.byte(121));actor.byte(122,source.byte(122));
            }
        }
        if(definition.longword(18))services.animate_actor(identity,actor,definition);
    }
    throw std::out_of_range("Unproved animation-list terminal extent");
}
struct BoundActorAnimationListServices final:ActorAnimationListServices {
    std::span<const ActorDefinition> definitions;const AnimationData& data;
    ActorCallbackServices& callbacks;ActorAnimationSound& sound;
    BoundActorAnimationListServices(std::span<const ActorDefinition> defs,const AnimationData& assets,
            ActorCallbackServices& functions,ActorAnimationSound& commands):definitions(defs),data(assets),callbacks(functions),sound(commands){}
    const ActorDefinition& animation_definition(std::uint32_t key)override{
        for(const auto& definition:definitions)if(definition.key==key)return definition;
        throw std::out_of_range("Unbound native animation definition");
    }
    void animation_callback(std::uint32_t identity,std::uint32_t callback)override{callbacks.invoke_actor_callback(identity,callback);}
    void animate_actor(std::uint32_t,ActorState& actor,const ActorDefinition& definition)override{
        const auto result=update_actor_animation_from_definition(actor,definition.key,data,&sound);
        if(result!=AnimationResult::Ok&&result!=AnimationResult::Retired)throw std::out_of_range("Unbound native animation program/control domain");
    }
};
}
