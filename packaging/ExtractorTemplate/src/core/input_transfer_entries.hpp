#pragma once
#include "core/player_input.hpp"
#include "core/display_port_publication.hpp"
namespace rolo {
struct NativeInputPollState{std::uint8_t pressed=0,skip_mapping=0;PlayerInputMapping mapping;};
struct InputPortServices{virtual ~InputPortServices()=default;virtual void bus_request(bool)=0;virtual void bus_delay_iterations(unsigned)=0;virtual void direction(std::uint8_t)=0;virtual void data(std::uint8_t)=0;virtual std::uint8_t read_data()=0;};
inline void pulse_input_bus(InputPortServices&s){s.bus_request(false);s.bus_delay_iterations(11);s.bus_request(true);}
inline void poll_original_input_bytes(NativeInputPollState&state,InputPortServices&s){
 s.bus_request(true);s.direction(64);s.data(0);pulse_input_bus(s);const auto low=s.read_data();s.data(64);pulse_input_bus(s);const auto high=s.read_data();s.bus_request(false);state.pressed=static_cast<std::uint8_t>(~(((low&48)<<2)|(high&63)));if(!state.skip_mapping)map_player_input(state.mapping,state.pressed);
}
inline void submit_immediate_display_transfer(std::uint32_t source,std::uint16_t destination,std::uint16_t words,std::uint32_t command,DisplayPortState&state,DisplayPortServices&s){
 state.control|=16;s.control_word(state.control);s.control_word(0x8f02);s.control_word(0x9300|(words&255));s.control_word(0x9400|(words>>8));
 const auto shifted=source>>1;s.control_word(0x9500|(shifted&255));s.control_word(0x9600|((shifted>>8)&255));s.control_word(0x9700|((source>>17)&127));
 state.command_latch=(std::uint32_t(destination&0x3fff)<<16)|((destination>>14)&3)|128|command;s.control_word(std::uint16_t(state.command_latch>>16));s.control_word(std::uint16_t(state.command_latch));wait_display_transfer(s);state.control&=0xffef;s.control_word(state.control);
}
}
