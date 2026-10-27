#pragma once
#include "core/display_setup.hpp"
namespace rolo {
struct SpriteFrameState {std::span<std::uint8_t> sat_storage;std::size_t sat_base=5;std::uint16_t resident_count{},word_count{};std::uint8_t resident_low{};};
struct SpriteFrameBuilder {SpriteFrameState&state;NativePublicationQueue&queue;std::size_t sat_cursor{};std::uint32_t queue_cursor{};};
struct SpriteFrameServices {virtual ~SpriteFrameServices()=default;virtual void build_resident_sprites(SpriteFrameState&,NativePublicationQueue&)=0;virtual void render_priority_list(std::uint32_t,SpriteFrameBuilder&)=0;};
// $31D6: native renderer services supply the copied renderer and list builders.
inline void publish_actor_sprite_frame(SpriteFrameState&state,NativePublicationQueue&queue,SpriteFrameServices&s){
 s.build_resident_sprites(state,queue);if(state.resident_count>80)throw std::out_of_range("Resident sprite count admission");state.resident_low=std::uint8_t(state.resident_count);state.word_count=std::uint16_t(state.resident_count*4);
 SpriteFrameBuilder build{state,queue,state.sat_base+state.resident_count*8,queue.cursor};
 if(build.sat_cursor>state.sat_storage.size()||state.sat_storage.size()-build.sat_cursor<8)throw std::out_of_range("Native SAT sentinel extent");for(unsigned i=0;i<8;++i)state.sat_storage[build.sat_cursor+i]=0;
 for(const auto key:{0xffff6d7au,0xffff6ddcu,0xfffff2d8u,0xffff6e3eu,0xffff6ea0u,0xffff6f02u,0xffff6f64u})s.render_priority_list(key,build);
 if(build.sat_cursor<5||build.sat_cursor-5>=state.sat_storage.size())throw std::out_of_range("Native SAT final link extent");state.sat_storage[build.sat_cursor-5]=0;
 if(build.queue_cursor<0xffffeb56u)throw std::out_of_range("Native SAT queue cursor");auto at=std::size_t(build.queue_cursor-0xffffeb56u);if(at>queue.bytes.size()||queue.bytes.size()-at<18)throw std::out_of_range("Native SAT queue packet extent");
 auto word=[&](std::uint16_t v){queue.bytes[at++]=std::uint8_t(v>>8);queue.bytes[at++]=std::uint8_t(v);};const auto count=state.word_count?state.word_count:std::uint16_t(4);
 word(0x9300|(count&255));word(0x9400|(count>>8));word(0x95de);word(0x96e4);word(0x977f);word(0x7400);word(0x0083);
 for(unsigned i=0;i<4;++i)queue.bytes[at+i]=0;queue.cursor=0xffffeb56u+std::uint32_t(at);
}
}
