#pragma once
#include "core/actor_state.hpp"
#include <stdexcept>
namespace rolo {
struct ScoreAwardState {std::uint32_t total{},next_threshold=1000000;std::uint16_t table_offset{};};
// $997E..$99E2 plus $9A04..$9A1A. C51D is a signed-tested byte after ADD.B.
inline void add_player_lives(std::uint8_t& lives,std::uint8_t amount){
    auto value=static_cast<std::uint8_t>(lives+amount);
    if(static_cast<std::int8_t>(value)>99)value=99;lives=value;
}
inline void award_score(ScoreAwardState& state,std::uint32_t amount,std::uint8_t& lives){
    state.total+=amount;
    while(state.next_threshold<=state.total){
        add_player_lives(lives,1);
        const auto offset=static_cast<std::uint16_t>(state.table_offset+4);
        if(offset==4){state.next_threshold=2000000;state.table_offset=4;}
        else if(offset==8){state.next_threshold+=1000000;} // FFFFFFFF sentinel: (table4-table0)+live threshold.
        else throw std::out_of_range("Unproved score threshold table domain");
        // Original wraps long arithmetic and may not terminate for some states;
        // refuse that domain instead of adding an invented maximum iteration count.
        if(state.next_threshold<1000000)throw std::out_of_range("Unproved wrapped score threshold progression");
    }
}
}
