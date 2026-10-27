#pragma once
#include "core/input_transfer_entries.hpp"
#include "core/startup_display_contracts.hpp"
#include "core/world_map.hpp"
#include "core/actor_state.hpp"
namespace rolo {
struct NativeFrameSignalServices{virtual ~NativeFrameSignalServices()=default;virtual void wait_event()=0;};
inline void wait_original_frame_signal(std::uint8_t&flag,NativeFrameSignalServices&s){flag=0;while(!flag)s.wait_event();}
inline void wait_original_frame_count(std::uint16_t&count,std::uint8_t&flag,NativeFrameSignalServices&s){do{wait_original_frame_signal(flag,s);count=std::uint16_t(count-1);}while(count!=65535);}
inline void initialize_input_mapping(NativeInputPollState&s,std::uint8_t&last_pressed,InputPortServices&ports){for(unsigned i=0;i<8;++i)s.mapping.destinations[i]=std::uint8_t(i);poll_original_input_bytes(s,ports);last_pressed=s.pressed;}
inline void submit_swapped_display_transfer(std::uint32_t source,std::uint16_t destination,std::uint32_t incoming_d2,std::uint32_t incoming_d3,DisplayPortState&state,DisplayPortServices&s){submit_immediate_display_transfer(source,destination,std::uint16_t(incoming_d3),incoming_d2,state,s);}
inline void clear_video_registers(VideoSetupPorts&p){for(auto w:{0x8004,0x8104,0x8200,0x8300,0x8400,0x8500,0x8700,0x8a00,0x8b00,0x8c00,0x8d00,0x8f00,0x9000,0x9100,0x9200})p.control(std::uint16_t(w));}
inline void clear_initial_video_memories(DisplaySetupServices&s){fill_name_table_words(0,0,0x8000,0x40000000,s);fill_name_table_words(0,0,64,0xc0000000,s);fill_name_table_words(0,0,40,0x40000010,s);}
inline std::uint8_t capture_world_actor_selector(const ActorState&a,std::uint16_t&x,std::uint16_t&y){x=a.word(12);y=a.word(16);return world_map_selector_at(x,y);}
}
