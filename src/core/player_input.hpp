#pragma once
#include <array>
#include <cstdint>
#include <stdexcept>
namespace rolo {
struct PlayerInputMapping {
    std::array<std::uint8_t,8> physical{},mapped{};
    std::array<std::uint8_t,8> destinations{0,1,2,3,4,5,6,7};
    std::uint8_t previous_complement{};
};
// $237C..$244E, after hardware read/replay supplies pressed bits in D0.
// C489 is previous complement; fresh press FF, held press FE, release zero.
inline void map_player_input(PlayerInputMapping& state,std::uint8_t pressed) {
    const auto newly_pressed=static_cast<std::uint8_t>(pressed&state.previous_complement);
    state.previous_complement=static_cast<std::uint8_t>(~pressed);
    state.physical.fill(0);state.mapped.fill(0);
    constexpr std::array<std::uint8_t,8> order{4,5,7,6,3,2,1,0};
    for(std::size_t bit=0;bit<order.size();++bit) {
        const auto mask=static_cast<std::uint8_t>(128u>>bit);
        if(!(pressed&mask))continue;
        const auto slot=order[bit];const auto value=static_cast<std::uint8_t>((newly_pressed&mask)?255:254);
        state.physical[slot]=value;
        const auto destination=state.destinations[slot];
        if(destination>=state.mapped.size())throw std::out_of_range("Unproved input mapping destination");
        state.mapped[destination]=value; // Aliased destinations overwrite in ROM order.
    }
}
}
