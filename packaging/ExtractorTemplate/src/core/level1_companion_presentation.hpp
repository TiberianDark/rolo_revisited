#pragma once
#include "core/level1_companion_presentation_data.hpp"
#include "core/actor_state.hpp"
#include <stdexcept>
namespace rolo {
struct AlternateCompanionPresentationState {
    std::uint8_t f280{},c512{},c511{};
    std::uint16_t held_actor_low_word{},held_terminator{}; // F2D8 WORD then F2DA WORD
};
// $EFA8..$F044, invoked only as the original C512 alternate tail service.
inline void update_level1_alternate_presentation(ActorState& actor,std::uint32_t identity,
        const ActorState& base,const ActorState& head,AlternateCompanionPresentationState& state){
    if(!state.f280)return;
    state.held_actor_low_word=static_cast<std::uint16_t>(identity);state.held_terminator=0;
    if(!actor.byte(46)){actor.byte(46,255);actor.word(50,3000);}
    actor.word(50,static_cast<std::uint16_t>(actor.word(50)-1));
    if(signed_word(actor.word(50))<0){actor.byte(116,255);state.c512=0;state.c511=255;return;}
    actor.byte(118,base.byte(118));state.c511=0;
    actor.word(16,static_cast<std::uint16_t>(base.word(16)+head.word(34)-5));
    auto offset=static_cast<std::uint16_t>(head.word(32)+1);
    const auto selector=signed_word(base.word(70));
    const auto byte_offset=selector>=0?selector/2:-static_cast<int>((-selector+1)/2);
    if(byte_offset<0||(byte_offset&1)||static_cast<unsigned>(byte_offset/2)>=companion_presentation_data::head_x.size())throw std::out_of_range("EFA8 original selector table domain");
    auto extra=static_cast<std::uint16_t>(companion_presentation_data::head_x[byte_offset/2]);
    if(base.byte(118)&8){offset=static_cast<std::uint16_t>(0-offset);extra=static_cast<std::uint16_t>(0-extra);}
    actor.word(12,static_cast<std::uint16_t>(offset+base.word(12)+extra));
    actor.word(24,static_cast<std::uint16_t>(head.word(16)+head.word(34)-head.word(38)+7));
}
}
