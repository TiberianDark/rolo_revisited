#pragma once
#include "core/actor_state.hpp"
#include "core/terrain_macro_copy.hpp"
namespace rolo {
struct TerrainMacroDefinition {std::uint8_t width{},height{};std::span<const std::uint16_t> tiles;};
struct TerrainDescriptorRecord {std::uint16_t type{},x{};std::uint32_t record_offset{};};
struct TerrainDescriptorServices {
    virtual ~TerrainDescriptorServices()=default;
    virtual TerrainMacroDefinition terrain_macro(std::uint8_t index)=0;
    virtual std::uint16_t terrain_macro_byte_count(std::uint8_t index)=0;
    virtual void terrain_special_descriptor(const TerrainDescriptorRecord& record,std::uint16_t ring_cursor)=0;
};
inline void copy_normal_terrain_descriptor(std::span<std::uint8_t> backing,const ActorState& plane,
        const TerrainDescriptorRecord& record,std::uint16_t ring_cursor,std::uint16_t f2ca,
        TerrainCopyMode mode,TerrainMacroDefinition macro,std::uint16_t byte_count) {
    const auto expected=static_cast<std::size_t>(macro.width)*macro.height*2;
    if(expected!=byte_count||byte_count>=0x8000||signed_word(plane.word(14))<0)
        throw std::invalid_argument("Unproved terrain macro count/separation domain");
    copy_terrain_macro(backing,{macro.tiles,macro.width,macro.height,
        static_cast<std::uint16_t>(record.x>>3),ring_cursor,f2ca,plane.word(14),
        static_cast<std::uint16_t>(record.record_offset),(record.type&0xff00)!=0,mode});
}
// $446C normal setup feeding typed $44C4/$4536/$45B4 continuations.
inline void dispatch_terrain_descriptor(std::span<std::uint8_t> backing,const ActorState& plane,
        const TerrainDescriptorRecord& record,std::uint16_t ring_cursor,std::uint16_t f2ca,
        TerrainCopyMode mode,TerrainDescriptorServices& services) {
    if(record.type>=0x400){services.terrain_special_descriptor(record,ring_cursor);return;}
    const auto index=static_cast<std::uint8_t>(record.type&127);
    const auto macro=services.terrain_macro(index);
    const auto byte_count=services.terrain_macro_byte_count(index);
    // Valid exported macros must agree with B1EC; signed ADDA.W domains remain explicit.
    copy_normal_terrain_descriptor(backing,plane,record,ring_cursor,f2ca,mode,macro,byte_count);
}
// $442A: special descriptors bypass the normal width/right clipping gate.
inline bool dispatch_initial_terrain_descriptor(std::span<std::uint8_t> backing,const ActorState& plane,
        const TerrainDescriptorRecord& record,std::uint16_t ring_cursor,std::uint16_t f2ca,
        std::uint16_t window_right,TerrainDescriptorServices& services) {
    if(record.type>=0x400){services.terrain_special_descriptor(record,ring_cursor);return true;}
    const auto index=static_cast<std::uint8_t>(record.type&127);
    const auto macro=services.terrain_macro(index);const auto count=services.terrain_macro_byte_count(index);
    const auto remaining=static_cast<std::uint16_t>((window_right>>3)-(record.x>>3)-macro.width*2);
    if(signed_word(remaining)<0)return false;
    copy_normal_terrain_descriptor(backing,plane,record,ring_cursor,f2ca,TerrainCopyMode::Replace,macro,count);
    return true;
}
}
