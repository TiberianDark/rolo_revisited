#pragma once
#include "core/player_trigger_dispatch.hpp"
namespace rolo {
// Typed original937A continuation, not an instruction interpreter. Host services
// own original63FA/66DE interrupt waits and ordered renderer publication.
struct TransportContinuationServices {
    virtual ~TransportContinuationServices()=default;
    virtual TriggerDestination destination(std::uint8_t parameter)=0;
    virtual void transport_sound(std::uint16_t command)=0;
    virtual void begin_black_fade()=0;
    virtual bool black_fade_finished()=0;
    virtual ActorState& live_controlled_actor()=0;
    virtual std::uint16_t live_controlled_type()=0;
    virtual void rebuild_phase(TriggerTransitionPhase phase)=0;
};
struct TransporterContinuation {
    TriggerDestination saved_destination{};
    bool waiting_black{};
    // Missingdestination has no sound, fade or state mutation. No Rolo-only gate.
    bool begin(std::uint8_t parameter,TransportContinuationServices& services){
        if(waiting_black)throw std::logic_error("Transport caller already suspended");
        const auto target=services.destination(parameter);if(target.negative)return false;
        saved_destination=target;services.transport_sound(0x1d);
        waiting_black=true;services.begin_black_fade();return true;
    }
    // Original D6/D7 WORDs survive63FA. ResolveC4E0 AFTERthat call returns.
    bool resume(TransportContinuationServices& services){
        if(!waiting_black||!services.black_fade_finished())return false;
        auto& actor=services.live_controlled_actor();
        actor.word(12,saved_destination.x);actor.word(14,0);
        actor.word(16,saved_destination.y);actor.word(18,0);
        actor.byte(121,0);actor.longword(58,0);actor.byte(122,0);actor.longword(62,0);
        for(const auto phase:{TriggerTransitionPhase::History684E,TriggerTransitionPhase::History6864,
                TriggerTransitionPhase::Camera4CB8,TriggerTransitionPhase::Foreground7292,TriggerTransitionPhase::Background72A2,
                TriggerTransitionPhase::State6960,TriggerTransitionPhase::State6AA6,TriggerTransitionPhase::Graphics31D6,
                TriggerTransitionPhase::Display25A8,TriggerTransitionPhase::State66DE})services.rebuild_phase(phase);
        if(services.live_controlled_type()==4)services.rebuild_phase(TriggerTransitionPhase::RoloAC34);
        waiting_black=false;return true;
    }
};
}
