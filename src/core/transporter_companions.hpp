#pragma once
#include "core/actor_allocation.hpp"
#include "core/player_frame_history.hpp"
namespace rolo {
// $AC7A: D1 is nonnegative only for the two airborne callbacks.
inline bool reposition_airborne_transporter_companion(ActorState& companion,
        const ActorState& controlled){
    const auto callback=companion.longword(42);
    if(callback!=0xa9b0&&callback!=0xaa4a)return false;
    companion.word(12,controlled.word(12));
    companion.word(16,controlled.word(16));
    return true;
}
// $AC34/$AC7A: integer positions only. Slots retain original iteration order.
inline void reposition_transporter_companions(ActorPool& pool,
        std::span<const std::uint32_t,3> slots,const ActorState& controlled,
        const PlayerFrameHistory& history){
    for(const auto identity:slots){
        if(!identity)continue;
        auto& companion=pool.resolve(identity);
        if(!reposition_airborne_transporter_companion(companion,controlled)){
            const auto index=static_cast<std::uint16_t>(
                (history.cursor-companion.word(50)-16)&1023);
            // Original masks the base index only; do not invent per-byte wrap.
            if(static_cast<std::size_t>(index)+4>history.records.size())
                throw std::out_of_range("Transport companion history read extent");
            auto word=[&](unsigned offset){return static_cast<std::uint16_t>(
                (history.records[index+offset]<<8)|history.records[index+offset+1]);};
            companion.word(12,word(0));companion.word(16,word(2));
        }
    }
}
}
