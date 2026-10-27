#pragma once
#include <array>
#include <bit>
#include <cstdint>
#include <span>
#include <optional>

namespace rolo {
struct Frame {
    std::uint32_t descriptor, left_graphics, right_graphics;
    std::int16_t offset_x, offset_y;
    std::uint16_t width, height, bytes;
};
enum class AnimationOp { Frame, Jump, Repeat, Delay, RandomDelay, RandomJump,
                         VelocityRate, Hold, SetReturn, Return, RepeatWhileNegative, Sound, Retire,
                         RepeatWhileNonzero,RepeatWhileZero,RepeatWhileNonnegative,
                           RepeatWhilePositive,RepeatWhileNonpositive,WriteByte,RandomJumpNonzero,
                           SpawnRandom,SpawnInherited,RandomHold,
                           ClearFreeze,CountedJump,SetSelector,RepeatWhileAirborne,
                           RepeatWhileGrounded,Skip,SetBlink,ClearBlink };
struct AnimationNode {
    AnimationOp op;
    std::uint16_t parameter;
    int frame, next, target;
    std::uint32_t evidence_address;
};
struct AnimationProgram { std::uint32_t definition; std::uint16_t selector; std::uint8_t delay; int start; };
struct AnimationData {
    std::span<const Frame> frames;
    std::span<const AnimationNode> nodes;
    std::span<const AnimationProgram> programs;
};
// $716E: signed endpoint comparison, unsigned wrapped WORD divisor.
// SUB.W/BLE includes overflow: do not classify the wrapped difference by sign.
struct AnimationRandom {
    std::uint16_t seed{};
    std::uint16_t between(std::uint16_t lower, std::uint16_t upper) {
        const auto difference=static_cast<std::uint16_t>(upper-lower);
        if (std::bit_cast<std::int16_t>(upper)<=std::bit_cast<std::int16_t>(lower)) return 0;
        const auto product=static_cast<std::uint32_t>(seed ? seed : 3)*0x4e35u;
        seed=static_cast<std::uint16_t>(product);
        return static_cast<std::uint16_t>(lower+(product>>16)%difference);
    }
};
struct AnimationState {
    int program{-1}, next{-1}, current{-1}, return_to{-1};
    std::uint8_t counter{}, period{};
    bool frame_selected{};
};
struct AnimationEffects {
    virtual ~AnimationEffects()=default;
    virtual void animation_sound(std::uint16_t)=0;
    virtual void animation_retire()=0; // FEAE sets116=FF and125.2; disposal occurs later.
};
enum class AnimationResult { Ok, MissingProgram, InvalidData, ControlLimit, ScopeComplete, MissingEffects, Retired };

// Translated sequence controls operate on typed asset records, never CPU opcodes.
inline AnimationResult update_animation(AnimationState& state, const AnimationData& data,
        std::uint32_t definition, std::uint16_t selector, std::uint32_t velocity_x,
        AnimationRandom& random, std::int8_t vertical_direction=0, AnimationEffects* effects=nullptr) {
    state.frame_selected=false;
    if (state.program>=0 && static_cast<std::size_t>(state.program)>=data.programs.size()) return AnimationResult::InvalidData;
    int program=-1;
    for (std::size_t i=0;i<data.programs.size();++i)
        if (data.programs[i].definition==definition && data.programs[i].selector==selector) {
            program=static_cast<int>(i); break;
        }
    if (program<0) return AnimationResult::MissingProgram;
    // $FD62 compares sequence pointers, not selectors; aliases preserve timing.
    if (state.program<0 || data.programs[program].start!=data.programs[state.program].start) {
        state.program=program; state.next=data.programs[program].start;
        state.period=data.programs[program].delay; state.counter=0;
    } else state.program=program;
    state.counter=static_cast<std::uint8_t>(state.counter-1);
    if (state.counter!=0xff) return AnimationResult::Ok;
    state.counter=state.period;
    for (int controls=0;controls<128;++controls) {
        if (state.next<0 || static_cast<std::size_t>(state.next)>=data.nodes.size()) return AnimationResult::InvalidData;
        const auto& node=data.nodes[state.next];
        switch (node.op) {
        case AnimationOp::Frame:
            if (node.frame<0 || static_cast<std::size_t>(node.frame)>=data.frames.size()) return AnimationResult::InvalidData;
            state.current=node.frame; state.next=node.next; state.frame_selected=true; return AnimationResult::Ok;
        case AnimationOp::Jump: state.next=node.target; break;
        case AnimationOp::Repeat: state.frame_selected=true; return AnimationResult::Ok;
        case AnimationOp::Hold: state.counter=0xff; return AnimationResult::Ok;
        case AnimationOp::Delay: state.counter=static_cast<std::uint8_t>(node.parameter); state.next=node.next; break;
        case AnimationOp::RandomDelay:
            state.counter=static_cast<std::uint8_t>(random.between(node.parameter&0xff,node.parameter>>8));
            state.next=node.next; break;
        case AnimationOp::RandomJump:
            state.next=random.between(0,node.parameter)==0 ? node.target : node.next; break;
        case AnimationOp::VelocityRate:
            state.period=static_cast<std::uint8_t>((~(velocity_x>>16)&15u)>>2);
            state.next=node.next; break;
        case AnimationOp::SetReturn: state.return_to=node.target; state.next=node.next; break;
        case AnimationOp::Return: state.next=state.return_to; break;
        case AnimationOp::Sound:
            if(!effects)return AnimationResult::MissingEffects;
            effects->animation_sound(node.parameter);state.next=node.next;break;
        case AnimationOp::Retire:
            if(!effects)return AnimationResult::MissingEffects;
            effects->animation_retire();return AnimationResult::Retired;
        case AnimationOp::RepeatWhileNegative:
            if(node.parameter!=0x7a) return AnimationResult::InvalidData;
            state.counter=vertical_direction<0?0:state.period;
            state.next=vertical_direction<0?node.target:node.next;break;
        default:return AnimationResult::InvalidData; // Requires a live ActorState binding.
        }
    }
    return AnimationResult::ControlLimit;
}
} // namespace rolo


