#pragma once
#include "core/display_setup.hpp"
namespace rolo {
struct DisplayPortState {std::uint16_t control{},secondary_counter{};std::uint32_t command_latch{};};
struct DisplayPortServices {virtual ~DisplayPortServices()=default;virtual void control_word(std::uint16_t)=0;virtual void control_long(std::uint32_t)=0;virtual void data_word(std::uint16_t)=0;virtual std::uint16_t status_word()=0;};
inline void wait_display_transfer(DisplayPortServices&s){while(s.status_word()&2){}}
// $25A8/$260A: 14BYTE packets terminated by a zero firstLONG.
inline void drain_display_publication(NativePublicationQueue& q,DisplayPortState& state,bool secondary,DisplayPortServices&s){
 state.control|=16;s.control_word(state.control);s.control_word(secondary?0x8f01:0x8f02);
 auto word=[&](std::size_t at){if(at>=q.bytes.size()||q.bytes.size()-at<2)throw std::out_of_range("Display packet word extent");return std::uint16_t((q.bytes[at]<<8)|q.bytes[at+1]);};
 auto longword=[&](std::size_t at){return (std::uint32_t(word(at))<<16)|word(at+2);};
 std::size_t at=0;for(;;){const auto first=longword(at);at+=4;if(!first)break;s.control_long(first);s.control_long(longword(at));at+=4;for(unsigned i=0;i<3;++i){s.control_word(word(at));at+=2;}wait_display_transfer(s);}
 state.control&=0xffef;s.control_word(state.control);for(unsigned i=0;i<4;++i)q.bytes[i]=0;q.cursor=secondary?0xffffe448u:0xffffeb56u;if(secondary)state.secondary_counter=128;
}
// $26C8: fullWORD fill value/count; zero count is still submitted to the device.
inline void fill_display_bytes(std::uint16_t value,std::uint32_t destination,std::uint16_t count,std::uint32_t control,DisplayPortState& state,DisplayPortServices&s){
 state.control|=16;s.control_word(state.control);s.control_word(0x8f01);s.control_word(0x9300|(count&255));s.control_word(0x9400|(count>>8));s.control_word(0x9780);
 const auto address=std::uint16_t(destination);state.command_latch=(std::uint32_t(address&0x3fff)<<16)|((address>>14)&3)|0x80|control;
 s.control_word(std::uint16_t(state.command_latch>>16));s.control_word(std::uint16_t(state.command_latch));s.data_word(value);wait_display_transfer(s);
 state.control&=0xffef;s.control_word(state.control);
}
}
