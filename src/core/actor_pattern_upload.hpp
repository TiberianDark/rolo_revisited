#pragma once
#include "core/actor_pattern_data.hpp"
#include "core/actor_state.hpp"
#include <algorithm>
#include <span>
#include <stdexcept>
namespace rolo {
inline void install_actor_pattern_frame(std::span<std::uint8_t> vram,const ActorState& actor){
    if(!actor.longword(28)||!actor.word(36)||!actor.word(38))return;
    for(const auto& frame:actor_pattern_data::frames){
        if(frame.source!=actor.longword(28)||frame.width!=actor.word(36)||frame.height!=actor.word(38))continue;
        const auto destination=std::size_t(actor.word(2)&2047)*32;
        if(destination+frame.size>vram.size())throw std::out_of_range("Actor resident pattern extent");
        std::copy_n(actor_pattern_data::bytes.begin()+frame.offset,frame.size,vram.begin()+destination);return;
    }
    throw std::logic_error("Unexported actor portrait frame");
}
}
