#pragma once
#include "core/level1_progress.hpp"
#include "core/level1_completion_data.hpp"
namespace rolo {
struct Level1Completion {
    bool requested{};
    std::uint16_t source_selector{},world_x{},world_y{},saved_x{},saved_y{};
    std::uint32_t destination_state{};
};
// $A50A: preserve selector before the world initializer clears F2F6.
// Full $1AFE initialization, fades and world-map frame services remain separate.
inline void request_level1_world_handoff(Level1Completion& completion,Level1ProgressState& progress){
    if(completion.requested)return;
    completion.requested=true;completion.source_selector=progress.selector;completion.destination_state=0x1a6e;
    if(signed_word(progress.selector)<0)return;
    level1_progress_flag(progress,progress.selector)|=1;
    const auto offset=std::size_t(progress.selector)*2;
    if(offset+1>=world_coordinate_bytes.size())throw std::out_of_range("Unbound world coordinate selector");
    if(world_coordinate_bytes[offset]==255)return;
    completion.world_x=completion.saved_x=static_cast<std::uint16_t>((world_coordinate_bytes[offset]<<4)-8);
    completion.world_y=completion.saved_y=static_cast<std::uint16_t>((world_coordinate_bytes[offset+1]<<4)-8);
}
}
