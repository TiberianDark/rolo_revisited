#pragma once
#include "core/actor_state.hpp"
#include <array>
#include <stdexcept>
#include <span>
namespace rolo {
// $881C..$8838: grounded frames preserve68; airborne count wraps as a word.
inline void player_airborne_count(ActorState& controlled,std::uint8_t c524) {
    if(!c524&&!(controlled.byte(124)&1))controlled.word(68,static_cast<std::uint16_t>(controlled.word(68)+1));
}
struct PlayerHistorySelectorServices {
    virtual ~PlayerHistorySelectorServices()=default;
    virtual std::uint16_t history_selector_word(std::int16_t byte_offset)=0; //6814 + signed D0.W
};
struct ImmutablePlayerHistorySelector final:PlayerHistorySelectorServices {
    std::span<const std::uint8_t> bytes;
    explicit ImmutablePlayerHistorySelector(std::span<const std::uint8_t> data):bytes(data){}
    std::uint16_t history_selector_word(std::int16_t offset) override {
        if(offset<0||static_cast<std::size_t>(offset)+2>bytes.size())throw std::out_of_range("Unproved history selector read extent");
        return static_cast<std::uint16_t>((bytes[offset]<<8)|bytes[offset+1]);
    }
};
struct PlayerFrameHistory {
    std::uint16_t cursor{};
    std::array<std::uint8_t,1024> records{};
};
// $6796..$6814: base actor F4E4, not necessarily the controlled actor.
inline void record_player_frame_history(PlayerFrameHistory& history,std::uint32_t main_state,
        const ActorState& base,PlayerHistorySelectorServices& services) {
    if(main_state!=0x1c6c)return;
    history.cursor=static_cast<std::uint16_t>((history.cursor+16)&1023);
    const auto at=history.cursor;
    if(static_cast<std::size_t>(at)+16>history.records.size())throw std::out_of_range("Unproved native history cursor alignment");
    auto word=[&](unsigned offset,std::uint16_t value) {
        history.records[at+offset]=static_cast<std::uint8_t>(value>>8);
        history.records[at+offset+1]=static_cast<std::uint8_t>(value);
    };
    word(0,base.word(12));word(2,base.word(16));
    word(4,services.history_selector_word(signed_word(static_cast<std::uint16_t>(base.word(70)>>1))));
    history.records[at+6]=base.byte(121);history.records[at+7]=base.byte(122);
    word(8,base.word(58));word(10,base.word(62));
    history.records[at+12]=base.byte(118);history.records[at+13]=base.byte(120);
    auto flags=base.byte(124);if(flags&32)flags=static_cast<std::uint8_t>(flags&~1u);
    history.records[at+14]=flags; // Byte15 is deliberately untouched.
}
}
