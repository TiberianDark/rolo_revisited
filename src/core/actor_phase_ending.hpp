#pragma once
#include "core/actor_state.hpp"
namespace rolo {
inline void actor_begin_short_countdown(ActorState&a){a.byte(50,std::uint8_t(a.byte(50)+1));a.byte(51,64);}
inline void actor_step_short_countdown(ActorState&a){auto count=std::uint8_t(a.byte(51)-1);a.byte(51,count);if(!count){a.byte(50,std::uint8_t(a.byte(50)+1));a.byte(51,16);}}
struct ActorPhaseRead{bool changed{};std::uint32_t value{};};
inline ActorPhaseRead read_actor_phase_entry(ActorState&a,std::uint32_t incoming){const auto phase=a.word(46);if(phase==a.word(48))return {false,(incoming&0xffff0000u)|phase};a.word(48,phase);return {true,0xffffffffu};}
inline void update_actor_long_pause(ActorState&a){if(read_actor_phase_entry(a,0).changed){a.word(70,0);a.word(50,200);}a.word(50,std::uint16_t(a.word(50)-1));if(a.byte(50)&128)a.word(46,0);}
inline void ending_wait_actor(std::uint8_t actor_ready,std::uint16_t&timer){if(!actor_ready)timer=std::uint16_t(timer-1);}
struct EndingCompletionServices{virtual ~EndingCompletionServices()=default;virtual std::uint16_t completion_percent()=0;virtual void fade_black()=0;};
inline void ending_completion_state(std::uint32_t&state,EndingCompletionServices&s){if(s.completion_percent()!=100){state=0x9b34;return;}s.fade_black();state=0x9a88;}
}
