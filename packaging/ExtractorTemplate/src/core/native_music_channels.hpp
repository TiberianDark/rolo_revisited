#pragma once
#include "core/audio_bank_data.hpp"
#include "core/music_record_reader.hpp"
#include <algorithm>
#include <array>
#include <vector>

namespace rolo {
struct FmRegisterWrite {std::uint8_t bank{},address{},value{};};
// Native translation of regular music path, not a Z80 interpreter.
// 0536/0545/055E queues; 0588 release; 05F2 pitch; 0620 key-on;
// 068F-073C allocation; 0810/0821 program lookup; 04FF register upload.
// Percussion channel 9 remains separate. Effects use logical channels 14/15.
class NativeMusicChannels {
    struct Voice {int logical=-1,note=-1;};
    std::array<Voice,5> voices_{};
    std::array<std::uint8_t,16> programs_{};
    std::vector<unsigned> free_{4,3,2,1,0}, active_;
    static void remove(std::vector<unsigned>&list,unsigned voice){
        list.erase(std::remove(list.begin(),list.end(),voice),list.end());
    }
    void key_off(unsigned voice,std::vector<FmRegisterWrite>&out){
        // Original EB table: 00,01,02,80,81 (sixth FM voice reserved).
        const auto key=std::uint8_t(voice<3?voice:voice+1);
        out.push_back({0,0x28,key});
        voices_[voice]={};remove(active_,voice);remove(free_,voice);free_.push_back(voice);
    }
public:
    NativeMusicChannels(){for(unsigned i=0;i<programs_.size();++i)programs_[i]=std::uint8_t(i);}
    std::vector<FmRegisterWrite> reset(){
        std::vector<FmRegisterWrite> out;
        for(int v=4;v>=0;--v)out.push_back({0,0x28,std::uint8_t(v<3?v:v+1)});
        voices_={};free_={4,3,2,1,0};active_.clear();return out;
    }
    std::vector<FmRegisterWrite> apply(const MusicRecord&event,std::uint8_t velocity=88){
        if(event.end)return reset();
        const unsigned channel=event.channel;
        if(channel>=16 || channel==9)throw std::invalid_argument("Unsupported music channel");
        const auto kind=event.command&0xf0;
        if(kind==0xc0){
            if(event.value>=32)throw std::out_of_range("Music program outside loaded bank");
            programs_[channel]=event.value;return {};
        }
        if(kind!=0x80 && kind!=0x90)throw std::invalid_argument("Unsupported channel event");
        if(velocity>127)throw std::out_of_range("Music velocity domain");
        std::vector<FmRegisterWrite> out;
        for(unsigned v=0;v<5;++v)
            if(voices_[v].logical==int(channel) && voices_[v].note==event.value){key_off(v,out);break;}
        if(kind==0x80 || velocity==0)return out;
        unsigned voice;
        if(free_.empty()){
            voice=active_.front();key_off(voice,out);
        }
        voice=free_.front();free_.erase(free_.begin());active_.push_back(voice);
        voices_[voice]={int(channel),event.value};
        const unsigned program=programs_[channel];
        if(program>=32)throw std::out_of_range("Music program outside loaded bank");
        std::array<std::uint8_t,46> patch{};
        std::copy_n(audio_data::patches.begin()+program*46,46,patch.begin());
        // Signed-byte note wrapping from 05F2; restrict to positive note data.
        if(event.value>127)throw std::out_of_range("Music note domain");
        int note=event.value;while(note<12)note+=12;while(note>=96)note-=12;note-=12;
        patch[40]=audio_data::frequency_low[unsigned(note)];
        patch[41]=audio_data::frequency_high[unsigned(note)];
        const auto scale=[&](unsigned offset){
            const unsigned level=patch[offset]+16-((unsigned(velocity)+7)>>3);
            patch[offset]=std::uint8_t(level>=128?127:level);
        };
        scale(19);const auto algorithm=patch[44]&7;
        if(algorithm>=4)scale(18);if(algorithm>=5)scale(17);if(algorithm==7)scale(16);
        const auto bank=std::uint8_t(voice>=3), slot=std::uint8_t(voice%3);
        for(auto reg:audio_data::registers)out.push_back({bank,std::uint8_t(reg+slot),patch[reg/4]});
        out.push_back({0,0x28,std::uint8_t(0xf0|(voice<3?voice:voice+1))});
        return out;
    }
    unsigned active_voices()const{return unsigned(active_.size());}
    static std::uint16_t note_frequency(unsigned note){
        if(note>127)throw std::out_of_range("Music note domain");
        while(note<12)note+=12;while(note>=96)note-=12;note-=12;
        return std::uint16_t(audio_data::frequency_low[note]|(unsigned(audio_data::frequency_high[note])<<8));
    }
    std::vector<FmRegisterWrite> frequency(unsigned logical,unsigned note,std::uint16_t value)const{
        for(unsigned v=0;v<5;++v)if(voices_[v].logical==int(logical)&&voices_[v].note==int(note)){
            const auto bank=std::uint8_t(v>=3),slot=std::uint8_t(v%3);
            return {{bank,std::uint8_t(0xa4+slot),std::uint8_t(value>>8)},
                    {bank,std::uint8_t(0xa0+slot),std::uint8_t(value)}};
        }return {};
    }
};
}
