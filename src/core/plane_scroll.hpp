#pragma once
#include "core/actor_state.hpp"
#include <span>
#include <stdexcept>
namespace rolo {
struct PlaneScrollState {
    const std::uint16_t& foreground_x;const std::uint16_t& background_x;
    const std::uint16_t& foreground_y;const std::uint16_t& background_y;
};
struct PlaneScrollServices {
    virtual ~PlaneScrollServices()=default;
    virtual void prepare_horizontal_mode(std::uint8_t mode)=0;
    virtual std::uint16_t scroll_source_word(unsigned index)=0;
    virtual void horizontal_pair(std::uint16_t byte_offset,std::uint16_t foreground,std::uint16_t background)=0;
    virtual void queue_line_scroll_512_words()=0; //2468:7440→F000,512words,40000000
    virtual void prepare_vertical_scroll()=0;
    virtual void vertical_pair(std::uint16_t foreground,std::uint16_t background)=0;
};
// $6960..$6A26; offsets are published values, not camera coordinates to negate again.
inline void publish_horizontal_scroll(std::uint8_t mode,PlaneScrollState state,PlaneScrollServices& services){
    if(mode>3)throw std::out_of_range("Unproved horizontal-scroll selector");
    services.prepare_horizontal_mode(mode);
    switch(mode){
    case 0:{const auto fg=state.foreground_x,bg=state.background_x;services.horizontal_pair(0,fg,bg);return;}
    case 1:return; //69A8 literalRTS after mode registers.
    case 2:{
        const auto foreground=state.foreground_x; //HighwordD1 latched once before32 writes.
        for(unsigned i=0;i<32;++i){
            const auto background=static_cast<std::uint16_t>(0-services.scroll_source_word(i));
            services.horizontal_pair(static_cast<std::uint16_t>(i*32),foreground,background);
        }return;
    }
    case 3:services.queue_line_scroll_512_words();return;
    }
}
// $6AA6..$6AC6, both values read before the two original port writes.
inline void publish_vertical_scroll(PlaneScrollState state,PlaneScrollServices& services){
    services.prepare_vertical_scroll();const auto fg=state.foreground_y,bg=state.background_y;
    services.vertical_pair(fg,bg);
}
struct NativeScrollStorageServices:PlaneScrollServices {
    std::array<std::uint16_t,512>& horizontal;std::array<std::uint16_t,2>& vertical;
    std::span<const std::uint16_t> source;std::uint8_t& mode;
    NativeScrollStorageServices(std::array<std::uint16_t,512>& h,std::array<std::uint16_t,2>& v,
            std::span<const std::uint16_t> words,std::uint8_t& selected):horizontal(h),vertical(v),source(words),mode(selected){}
    void prepare_horizontal_mode(std::uint8_t selected)override{mode=selected;}
    std::uint16_t scroll_source_word(unsigned index)override{if(index>=source.size())throw std::out_of_range("Native scroll source extent");return source[index];}
    void horizontal_pair(std::uint16_t offset,std::uint16_t fg,std::uint16_t bg)override{
        if(offset&1)throw std::out_of_range("Native scroll alignment");horizontal.at(offset/2)=fg;horizontal.at(offset/2+1)=bg;
    }
    void prepare_vertical_scroll()override{} //Original8F02 access increment; typed pair uses no port state.
    void vertical_pair(std::uint16_t fg,std::uint16_t bg)override{vertical[0]=fg;vertical[1]=bg;}
    //Mode3 queue remains a required service; storage does not silently substitute a synchronous copy.
};
}
