#pragma once
#include "core/actor_allocation.hpp"
namespace rolo {
struct ReplayInputState {std::uint8_t enabled{},mask{},latch{},counter{},ended{};std::size_t cursor{};};
// $5C94: immutable admitted duration/mask pairs, cursor retained at FF terminal.
inline void update_replay_input(ReplayInputState& s,std::span<const std::uint8_t> pairs){
 if(s.ended)return;if(s.cursor>=pairs.size()||pairs.size()-s.cursor<2)throw std::out_of_range("Replay pair extent");
 s.mask=pairs[s.cursor+1];if(s.mask==255){s.ended=255;s.mask=0;s.latch=255;return;}
 if(s.counter==pairs[s.cursor]){s.cursor+=2;s.counter=0;}else s.counter=static_cast<std::uint8_t>(s.counter+1);
}
// $5C58: sign-latch comes from old mask, then replay and input service.
template<class Sample>void sample_replay_input(ReplayInputState& s,std::span<const std::uint8_t> pairs,Sample&& sample){
 if(!s.enabled)return;s.latch=(s.mask&128)?255:0;update_replay_input(s,pairs);sample(s.mask);
}
// $3BF6 clears twenty WORDs at7410; retain adjacent bytes.
inline void clear_level_lookup_scratch(std::span<std::uint8_t,40> bytes){for(auto& b:bytes)b=0;}
// $6750: ascending full pool traversal; source reads remain live.
inline void synchronize_actor_parent_presentation(ActorPool& pool){
 for(auto& a:pool.actors){if(a.byte(0)&128)continue;const auto key=a.longword(76);if(!key)continue;
  const auto& source=pool.resolve(key);a.word(12,source.word(12));a.word(16,source.word(16));a.word(70,source.word(70));
  a.byte(118,source.byte(118));a.byte(121,source.byte(121));a.byte(122,source.byte(122));
 }
}
}
