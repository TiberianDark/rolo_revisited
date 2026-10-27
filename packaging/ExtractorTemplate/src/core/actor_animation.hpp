#pragma once
#include "core/actor_state.hpp"
#include "core/animation.hpp"

namespace rolo {
struct ActorAnimationSound {
    virtual ~ActorAnimationSound()=default;
    virtual void actor_animation_sound(std::uint16_t)=0;
};
struct ActorAnimationSpawnServices {
    virtual ~ActorAnimationSpawnServices()=default;
    virtual void actor_animation_spawn_inherited(ActorState&,std::uint32_t){throw std::logic_error("Inherited animation spawn service not connected");}
    virtual void actor_animation_spawn_random(ActorState& parent,std::uint32_t definition,
        std::uint16_t range,AnimationRandom& random)=0;
};
inline const AnimationNode* actor_animation_node(const AnimationData& data,std::uint32_t key) {
    for(const auto& node:data.nodes)if(node.evidence_address==key)return &node;
    return nullptr;
}
inline const AnimationNode* actor_animation_target(const AnimationData& data,int index) {
    if(index<0||static_cast<std::size_t>(index)>=data.nodes.size())return nullptr;
    return &data.nodes[index];
}
// $FD44..$FE0A for exported immutable programs and their supported controls.
// Actor fields102/106/110 are asset record keys, never executable pointers.
// Outer list/callback/parent-copy processing atFCE4..FD44 is separate.
inline AnimationResult update_actor_animation_from_definition(ActorState& actor,std::uint32_t definition_key,const AnimationData& data,
                                             ActorAnimationSound* sound=nullptr,AnimationRandom* random=nullptr,
                                             ActorAnimationSpawnServices* spawn=nullptr,std::uint8_t* frozen_c524=nullptr) {
    const auto selector=actor.word(70);
    if(selector!=actor.word(72)) {
        actor.word(72,selector);
        const AnimationProgram* program=nullptr;
        for(const auto& candidate:data.programs)
            if(candidate.definition==definition_key&&candidate.selector==selector){program=&candidate;break;}
        if(!program)return AnimationResult::MissingProgram;
        const auto* start=actor_animation_target(data,program->start);
        if(!start)return AnimationResult::InvalidData;
        if(start->evidence_address!=actor.longword(106)) {
            actor.longword(106,start->evidence_address);
            actor.longword(102,start->evidence_address-4);
            actor.byte(115,program->delay);actor.byte(114,0);
        }
    }
    actor.byte(114,static_cast<std::uint8_t>(actor.byte(114)-1));
    if(actor.byte(114)==255) {
        actor.byte(114,actor.byte(115));
        const auto* node=actor_animation_node(data,actor.longword(102)+4);
        bool finished=false;
        for(int controls=0;controls<128&&!finished;++controls) {
            if(!node)return AnimationResult::InvalidData;
            switch(node->op) {
            case AnimationOp::Frame: {
                if(node->frame<0||static_cast<std::size_t>(node->frame)>=data.frames.size())return AnimationResult::InvalidData;
                const auto& frame=data.frames[node->frame];
                actor.longword(102,node->evidence_address);
                if(!(actor.byte(125)&16)) {
                    actor.word(32,static_cast<std::uint16_t>(frame.offset_x));
                    actor.word(34,static_cast<std::uint16_t>(frame.offset_y));
                }
                actor.word(36,frame.width);actor.word(38,frame.height);actor.word(40,frame.bytes);
                finished=true;break;
            }
            case AnimationOp::Jump:node=actor_animation_target(data,node->target);break;
            case AnimationOp::Repeat:node=actor_animation_node(data,node->evidence_address-4);break;
            case AnimationOp::SetReturn: {
                const auto* target=actor_animation_target(data,node->target);
                if(!target)return AnimationResult::InvalidData;
                actor.longword(110,target->evidence_address);
                node=actor_animation_target(data,node->next);break;
            }
            case AnimationOp::Return:node=actor_animation_node(data,actor.longword(110));break;
            case AnimationOp::ClearFreeze:
                if(!frozen_c524)return AnimationResult::MissingEffects;
                *frozen_c524=0;node=actor_animation_target(data,node->next);break;
            case AnimationOp::CountedJump: {
                auto count=actor.byte(128);bool jump=true;
                if(count){count=static_cast<std::uint8_t>(count-1);jump=count!=0;}
                else count=static_cast<std::uint8_t>(node->parameter);
                actor.byte(128,count);
                node=actor_animation_target(data,jump?node->target:node->next);break;
            }
            case AnimationOp::SetSelector:
                actor.word(70,node->parameter);return AnimationResult::Ok;
            case AnimationOp::RepeatWhileAirborne:case AnimationOp::RepeatWhileGrounded: {
                const bool repeat=bool(actor.byte(124)&1)==(node->op==AnimationOp::RepeatWhileGrounded);
                actor.byte(114,repeat?0:actor.byte(115));
                node=actor_animation_target(data,repeat?node->target:node->next);break;
            }
            case AnimationOp::Skip:node=actor_animation_target(data,node->next);break;
            case AnimationOp::SetBlink:
                actor.byte(125,actor.byte(125)|2);node=actor_animation_target(data,node->next);break;
            case AnimationOp::ClearBlink:
                actor.byte(125,actor.byte(125)&~2u);node=actor_animation_target(data,node->next);break;
            case AnimationOp::Sound:
                if(!sound)return AnimationResult::MissingEffects;
                sound->actor_animation_sound(node->parameter);
                node=actor_animation_target(data,node->next);break;
            case AnimationOp::Delay:
                actor.byte(114,static_cast<std::uint8_t>(node->parameter));node=actor_animation_target(data,node->next);break;
            case AnimationOp::VelocityRate:
                actor.byte(115,static_cast<std::uint8_t>(((~actor.word(58))&15)>>2));node=actor_animation_target(data,node->next);break;
            case AnimationOp::WriteByte:
                if((node->parameter>>8)>=130)return AnimationResult::InvalidData;
                actor.byte(node->parameter>>8,static_cast<std::uint8_t>(node->parameter));node=actor_animation_target(data,node->next);break;
            case AnimationOp::RandomDelay:
                if(!random)return AnimationResult::MissingEffects;
                actor.byte(114,static_cast<std::uint8_t>(random->between(node->parameter&255,node->parameter>>8)));
                node=actor_animation_target(data,node->next);break;
            case AnimationOp::SpawnInherited:
                if(!spawn)return AnimationResult::MissingEffects;
                spawn->actor_animation_spawn_inherited(actor,static_cast<std::uint32_t>(node->frame));
                node=actor_animation_target(data,node->next);break;
            case AnimationOp::SpawnRandom:
                if(!random||!spawn)return AnimationResult::MissingEffects;
                spawn->actor_animation_spawn_random(actor,static_cast<std::uint32_t>(node->frame),node->parameter,*random);
                node=actor_animation_target(data,node->next);break;
            case AnimationOp::RandomHold:
                if(!random)return AnimationResult::MissingEffects;
                actor.byte(114,static_cast<std::uint8_t>(random->between(node->parameter&255,node->parameter>>8)));
                actor.longword(102,node->evidence_address);finished=true;break;
            case AnimationOp::RandomJump:case AnimationOp::RandomJumpNonzero: {
                if(!random)return AnimationResult::MissingEffects;
                const bool zero=random->between(0,node->parameter)==0;
                node=actor_animation_target(data,(zero==(node->op==AnimationOp::RandomJump))?node->target:node->next);break;
            }
            case AnimationOp::RepeatWhileNonzero:case AnimationOp::RepeatWhileZero:
            case AnimationOp::RepeatWhileNonnegative:case AnimationOp::RepeatWhileNegative:
            case AnimationOp::RepeatWhilePositive:case AnimationOp::RepeatWhileNonpositive: {
                if(node->parameter>=130)return AnimationResult::InvalidData;
                const auto value=static_cast<std::int8_t>(actor.byte(node->parameter));bool repeat=false;
                switch(node->op){
                case AnimationOp::RepeatWhileNonzero:repeat=value!=0;break;
                case AnimationOp::RepeatWhileZero:repeat=value==0;break;
                case AnimationOp::RepeatWhileNonnegative:repeat=value>=0;break;
                case AnimationOp::RepeatWhileNegative:repeat=value<0;break;
                case AnimationOp::RepeatWhilePositive:repeat=value>0;break;
                default:repeat=value<=0;break;
                }
                actor.byte(114,repeat?0:actor.byte(115));
                node=actor_animation_target(data,repeat?node->target:node->next);break;
            }
            case AnimationOp::Retire:
                actor.byte(116,255);actor.byte(125,static_cast<std::uint8_t>(actor.byte(125)|4));
                return AnimationResult::Retired;
            case AnimationOp::Hold:
                actor.longword(102,node->evidence_address-4);actor.byte(114,255);finished=true;break;
            default:return AnimationResult::InvalidData; // Other command domains require native translation.
            }
        }
        if(!finished)return AnimationResult::ControlLimit;
    }
    const auto* current=actor_animation_node(data,actor.longword(102));
    if(!current)return AnimationResult::InvalidData;
    // FDC6 only consumes words whose first byte is zero. Exported frame
    // descriptors have this property; negative control records leave graphics.
    if(current->op!=AnimationOp::Frame)return AnimationResult::Ok;
    if(current->frame<0||static_cast<std::size_t>(current->frame)>=data.frames.size())return AnimationResult::InvalidData;
    const auto& frame=data.frames[current->frame];
    const bool facing_left=(actor.byte(118)&8)!=0;
    auto graphics=facing_left?frame.right_graphics:frame.left_graphics;
    if(graphics) actor.byte(119,static_cast<std::uint8_t>(actor.byte(119)&0xf7));
    else {
        graphics=facing_left?frame.left_graphics:frame.right_graphics;
        actor.byte(119,static_cast<std::uint8_t>(actor.byte(119)|8));
    }
    actor.longword(28,graphics);
    return AnimationResult::Ok;
}
inline AnimationResult update_actor_animation(ActorState& actor,const AnimationData& data,ActorAnimationSound* sound=nullptr){
    return update_actor_animation_from_definition(actor,actor.longword(4),data,sound);
}
}
