#pragma once
#include "core/actor_state.hpp"
#include "core/actor_allocation.hpp"
namespace rolo {
struct EntryMarkerState {std::uint8_t pending_f26e{};std::uint16_t scratch_c494{};};
struct EntryMarkerAllocation {std::uint32_t key{};ActorState* returned_a4{};};
struct EntryMarkerServices {
 virtual ~EntryMarkerServices()=default;
 virtual void scan_entry_markers(std::uint8_t marker_class,std::uint32_t callback)=0;
 virtual ActorState& entry_controlled_actor()=0;
 virtual EntryMarkerAllocation allocate_entry_marker(const ActorAllocationRequest&)=0;
 virtual std::uint16_t reset_entry_camera()=0;
};
// 608A: clear request flag before invoking class5 scanner with callback identity60A6.
inline void scan_requested_entry_markers(EntryMarkerState& state,EntryMarkerServices& services){
 if(!state.pending_f26e)return;
 state.pending_f26e=0;services.scan_entry_markers(5,0x60a6);
}
// 60A6: accepted variants are hexadecimal14/15 (decimal20/21).
inline std::uint16_t relocate_entry_marker(std::uint8_t variant,std::uint16_t x,
 std::uint16_t y,std::uint16_t incoming_d2_high,std::uint32_t marker,
 EntryMarkerState& state,EntryMarkerServices& services){
 if((variant&0xfe)!=0x14)return 0;
 state.scratch_c494=y;auto& actor=services.entry_controlled_actor();
 actor.word(12,x);actor.longword(16,0); // X fraction14 deliberately survives.
 const auto allocated=services.allocate_entry_marker({0x152b8,(std::uint32_t(x)<<16)|incoming_d2_high,0,marker,0,0});
 if(allocated.key){
  if(!allocated.returned_a4)throw std::logic_error("Unbound allocator A4 handoff");
  allocated.returned_a4->longword(42,0xf046);allocated.returned_a4->word(54,state.scratch_c494);
 }
 return services.reset_entry_camera(); // Allocation failure still resets; scanner uses actual result.
}
}
