#pragma once
#include "core/native_music_channels.hpp"
#include "core/native_sound_effects.hpp"
#include "ymfm_opn.h"
#include <memory>

namespace rolo {
// Offline/prototype FM music render. PSG, DAC samples and effects not yet mixed.
// Cadence and clock explicit: do not claim a reference recording match.
class NativeMusicRender {
    ymfm::ymfm_interface interface_;
    ymfm::ym2612 chip_{interface_};
    std::vector<std::uint8_t> data_;
    std::unique_ptr<MusicRecordReader> reader_;
    NativeMusicChannels channels_;
    NativeSoundEffects effects_{channels_};
    unsigned rate_,ticks_per_second_,delay_=1;
    std::uint64_t samples_{},next_tick_=0,ticks_{};
    bool ended_=false,loop_=false;
    void writes(const std::vector<FmRegisterWrite>&events){
        for(auto e:events){chip_.write(e.bank*2,e.address);chip_.write(e.bank*2+1,e.value);}
    }
    void tick(){
        ++ticks_;writes(effects_.step());if(ended_)return;
        if(--delay_)return;
        for(std::size_t budget=0;budget<=data_.size();++budget){
            auto e=reader_->next();writes(channels_.apply(e));
            if(e.end){if(loop_){reader_=std::make_unique<MusicRecordReader>(data_);delay_=1;}else ended_=true;return;}
            delay_=e.delay;if(delay_)return;
        }
        throw std::runtime_error("Music zero-delay event budget exceeded");
    }
public:
    explicit NativeMusicRender(std::vector<std::uint8_t> data,unsigned tick_rate=60,unsigned clock=7670454,bool loop=false)
        :data_(std::move(data)),rate_(chip_.sample_rate(clock)),ticks_per_second_(tick_rate),loop_(loop){
        if(!tick_rate || tick_rate>1000 || !rate_)throw std::invalid_argument("Music cadence");
        if(data_.empty())ended_=true;else reader_=std::make_unique<MusicRecordReader>(data_);
        chip_.reset();writes(channels_.reset());
        // Original driver initialization 018E: disable YM timer mode.
        chip_.write(0,0x27);chip_.write(1,0);
    }
    unsigned sample_rate()const{return rate_;}
    bool ended()const{return ended_;}
    void effect(unsigned id){writes(effects_.submit(id));}
    std::array<std::int16_t,2> sample(){
        if(samples_>=next_tick_){tick();next_tick_=(ticks_*rate_)/ticks_per_second_;}
        ymfm::ym2612::output_data output;chip_.generate(&output);++samples_;
        // Headroom for later effects; original mixer gain remains to calibrate.
        return {std::int16_t(std::clamp(output.data[0]/2,-32768,32767)),
                std::int16_t(std::clamp(output.data[1]/2,-32768,32767))};
    }
};
}
