#pragma once
#include <SDL3/SDL.h>
#include "core/native_music_render.hpp"
#include "core/music_assignments.hpp"
#include "core/achievement_notifications.hpp"
#include <atomic>

namespace rolo {
// SDL-owned audio thread synthesizes from embedded original sequence data.
// No file access or rendering/gameplay work in the audio callback.
class HostMusic {
    SDL_AudioStream* stream_{};
    std::atomic<std::uint64_t> pending_{63};
    std::uint64_t serial_{},applied_=~std::uint64_t(0);
    std::atomic<bool> paused_{false},failed_{false};
    std::atomic<std::uint64_t> frames_{0};
    std::array<std::uint8_t,128> effects_{};
    std::atomic<unsigned> effect_read_{0},effect_write_{0},dropped_effects_{0};
    std::unique_ptr<NativeMusicRender> render_;
    unsigned cadence_;int current_=-1;
    std::atomic<bool> unlock_pending_{false};UnlockChime unlock_chime_;
    static void SDLCALL callback(void*context,SDL_AudioStream*stream,int additional,int){
        auto& self=*static_cast<HostMusic*>(context);
        try{
            const auto command=self.pending_.load();
            if(command!=self.applied_){
                self.applied_=command;self.render_.reset();
                const auto id=unsigned(command&63);
                if(id<33){
                    const auto first=music_bank::offsets[id],last=music_bank::offsets[id+1];
                    self.render_=std::make_unique<NativeMusicRender>(std::vector<std::uint8_t>(music_bank::bytes.begin()+first,music_bank::bytes.begin()+last),self.cadence_,7670454,bool(command&64));
                }else self.render_=std::make_unique<NativeMusicRender>(std::vector<std::uint8_t>{},self.cadence_);
            }
            auto read=self.effect_read_.load();const auto end=self.effect_write_.load();
            while(read!=end){if(self.render_)self.render_->effect(self.effects_[read%self.effects_.size()]);++read;}
            self.effect_read_.store(read);
            if(self.unlock_pending_.exchange(false))self.unlock_chime_.trigger();
            std::array<std::int16_t,2048> samples{};
            while(additional>0){
                const int frames=std::min(1024,(additional+3)/4);
                for(int i=0;i<frames;++i){
                    auto value=(!self.paused_.load()&&self.render_)?self.render_->sample():std::array<std::int16_t,2>{};
                    const auto chime=self.unlock_chime_.sample();for(auto& channel:value)channel=std::int16_t(std::clamp(int(channel)+int(chime),-32768,32767));
                    samples[i*2]=value[0];samples[i*2+1]=value[1];
                }
                if(!SDL_PutAudioStreamData(stream,samples.data(),frames*4)){self.failed_=true;return;}
                self.frames_.fetch_add(unsigned(frames));
                additional-=frames*4;
            }
        }catch(...){self.failed_=true;self.render_.reset();}
    }
public:
    explicit HostMusic(unsigned cadence=60,bool enable=true):cadence_(cadence){
        if(!enable||!SDL_InitSubSystem(SDL_INIT_AUDIO))return;
        SDL_AudioSpec spec{SDL_AUDIO_S16,2,53267};
        stream_=SDL_OpenAudioDeviceStream(SDL_AUDIO_DEVICE_DEFAULT_PLAYBACK,&spec,callback,this);
        if(stream_&&!SDL_ResumeAudioStreamDevice(stream_)){SDL_DestroyAudioStream(stream_);stream_=nullptr;}
    }
    ~HostMusic(){if(stream_)SDL_DestroyAudioStream(stream_);}
    HostMusic(const HostMusic&)=delete;HostMusic& operator=(const HostMusic&)=delete;
    void play(unsigned id,bool loop){
        if(id>=33||current_==int(id))return;current_=int(id);
        pending_.store((++serial_<<8)|id|(loop?64:0));
    }
    void request(const std::optional<MusicRequest>&r){if(r)play(r->id,r->loop);}
    void stop(){current_=-1;pending_.store((++serial_<<8)|63);}
    void pause(bool value){paused_.store(value);}
    bool available()const{return stream_!=nullptr;}
    void unlock_chime(){unlock_pending_.store(true);}
    void effect(unsigned id){
        if(id>=91)return;
        const auto write=effect_write_.load();
        if(write-effect_read_.load()>=effects_.size()){++dropped_effects_;return;}
        effects_[write%effects_.size()]=std::uint8_t(id);effect_write_.store(write+1);
    }
    unsigned dropped_effects()const{return dropped_effects_.load();}
    bool failed()const{return failed_.load();}
    std::uint64_t frames()const{return frames_.load();}
};
}
