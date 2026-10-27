#pragma once
#include "core/native_music_channels.hpp"
#include "core/sound_effect_data.hpp"

namespace rolo {
// Native semantic translation: driver 0A2E/0A32 submission and 0AA3-0B4C
// signed pitch delta, bit-3 block crossing, duration pairs and zero terminator.
class NativeSoundEffects {
    struct Slot {bool active{};unsigned id{},note{},phase=2,remaining{};std::uint16_t pitch{};};
    NativeMusicChannels& channels_;
    std::array<Slot,2> slots_{};
    unsigned alternate_=1; // $7882C helper: first channel 7, then 6 (logical 15/14).
    static MusicRecord event(unsigned command,unsigned value){
        MusicRecord e;e.command=std::uint8_t(command);e.channel=command&15;e.value=std::uint8_t(value);return e;
    }
    static void append(std::vector<FmRegisterWrite>&to,const std::vector<FmRegisterWrite>&from){to.insert(to.end(),from.begin(),from.end());}
public:
    explicit NativeSoundEffects(NativeMusicChannels&channels):channels_(channels){}
    static std::uint16_t shift(std::uint16_t pitch,std::uint8_t raw_delta){
        const int delta=raw_delta<128?int(raw_delta):int(raw_delta)-256;
        auto next=std::uint16_t(int(pitch)+delta);
        if((pitch^next)&0x0800)next=std::uint16_t(int(next)+(delta<0?-1024:1024));
        return next;
    }
    std::vector<FmRegisterWrite> submit(unsigned id){
        if(id>=91)throw std::out_of_range("Effect ID");
        const unsigned index=alternate_;alternate_^=1;
        auto&s=slots_[index];const unsigned logical=14+index;
        std::vector<FmRegisterWrite> out;
        if(s.active)append(out,channels_.apply(event(0x80|logical,s.note)));
        const auto offset=id*23;const auto program=effect_bank::descriptors[offset],note=effect_bank::descriptors[offset+1];
        if(!effect_bank::descriptors[offset+2])throw std::invalid_argument("Empty effect envelope");
        channels_.apply(event(0xc0|logical,program));
        append(out,channels_.apply(event(0x90|logical,note),127));
        s={true,id,note,2,effect_bank::descriptors[offset+2],NativeMusicChannels::note_frequency(note)};
        return out;
    }
    std::vector<FmRegisterWrite> step(){
        std::vector<FmRegisterWrite> out;
        for(unsigned index=0;index<2;++index){
            auto&s=slots_[index];if(!s.active)continue;
            const auto base=s.id*23;const unsigned logical=14+index;
            if(s.phase+1>=23)throw std::out_of_range("Effect envelope extent");
            s.pitch=shift(s.pitch,effect_bank::descriptors[base+s.phase+1]);
            auto writes=channels_.frequency(logical,s.note,s.pitch);
            if(writes.empty()){s.active=false;continue;} // Music/other effect stole this note.
            append(out,writes);
            if(--s.remaining)continue;
            s.phase+=2;if(s.phase>=23)throw std::out_of_range("Effect terminator missing");
            s.remaining=effect_bank::descriptors[base+s.phase];
            if(!s.remaining){append(out,channels_.apply(event(0x80|logical,s.note)));s.active=false;}
        }return out;
    }
    unsigned active()const{return unsigned(slots_[0].active)+unsigned(slots_[1].active);}
};
}
