#pragma once
#include "core/actor_allocation.hpp"
namespace rolo {
struct ActorSpawnFactoryInput {
    std::uint16_t parameter{},record_x{},row_byte_index{},controlled_x{};
    std::uint32_t marker{};
};
// $4A48..$4A84: caller has selected the definition pointer table.
// Normal463C cleared the high parameter byte; direct-table callers double it.
inline ActorAllocationRequest actor_spawn_factory_request(ActorSpawnFactoryInput input,
        std::span<const std::uint32_t> definitions){
    const auto even=static_cast<std::uint16_t>(input.parameter&0xfffe);
    const auto byte_offset=static_cast<std::uint16_t>(even*2);
    if(signed_word(byte_offset)<0||byte_offset%4||byte_offset/4>=definitions.size())
        throw std::out_of_range("Unbound spawn definition table read");
    const auto x=static_cast<std::uint16_t>(input.record_x+8);
    const auto y=static_cast<std::uint16_t>((static_cast<std::uint16_t>(input.row_byte_index+2)<<3)+1);
    auto facing=static_cast<std::uint8_t>((input.parameter&1)?255:0);
    // BMI uses wrapped result N; signed operand comparison is not equivalent.
    if(!(static_cast<std::uint16_t>(input.controlled_x-x)&0x8000))facing=static_cast<std::uint8_t>(~facing);
    return {definitions[byte_offset/4],static_cast<std::uint32_t>(x)<<16,
        static_cast<std::uint32_t>(y)<<16,input.marker,input.marker,static_cast<std::uint8_t>(facing&8)};
}
// $4A7C copies D1 into D7 without clearing D1: the incoming marker also
// remains the allocator's resource context until a graphics allocation replaces it.
inline ActorAllocationResult allocate_marker_actor(ActorPool& pool,
        ActorSpawnFactoryInput input,std::span<const std::uint32_t> definitions,
        ActorAllocationServices& services){
    return allocate_actor_chain(pool,actor_spawn_factory_request(input,definitions),services);
}
}
