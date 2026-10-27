#pragma once
#include "core/palette_effect_data.hpp"
#include <span>
#include <stdexcept>
namespace rolo {
struct PaletteEffectChannel {std::uint8_t current_twice{};std::int8_t delta{};};
struct PaletteEffect {
    std::uint16_t phase=112;
    std::uint8_t active{},count_minus_one{},rate{},counter{};
    std::array<std::array<PaletteEffectChannel,3>,16> channels{}; // B,G,R in record10..15.
};
// 2FF6 bounded16-colour caller domain. Original predecrements store B,G,R;
// neither current_twice nor delta is mutated by3060.
inline void initialize_palette_effect(PaletteEffect& effect,std::span<const std::uint16_t> current,
        std::span<const std::uint16_t> target,std::uint8_t rate=0){
    if(current.empty()||current.size()>16||target.size()!=current.size())throw std::out_of_range("Unproved palette effect colour extent");
    effect.active=0;effect.count_minus_one=static_cast<std::uint8_t>(current.size()-1);effect.rate=rate;effect.counter=0;effect.phase=112;
    for(unsigned i=0;i<current.size();++i)for(unsigned channel=0;channel<3;++channel){
        const auto shift=9-channel*4;const auto from=(current[i]>>shift)&7,to=(target[i]>>shift)&7;
        effect.channels[i][channel]={static_cast<std::uint8_t>(from*2),static_cast<std::int8_t>(int(to)-int(from))};
    }
    effect.active=255;
}
// 3060 returns whether palette memory changed (C48B publication dirty).
inline bool advance_palette_effect(PaletteEffect& effect,std::span<std::uint16_t> destination){
    if(!effect.active)return false;
    effect.counter=static_cast<std::uint8_t>(effect.counter-1);
    if(static_cast<std::int8_t>(effect.counter)>=0)return false;
    effect.counter=effect.rate;
    const unsigned count=unsigned(effect.count_minus_one)+1;if(count>16||destination.size()<count)throw std::out_of_range("Unproved active palette extent");
    for(unsigned i=0;i<count;++i){
        std::uint16_t colour=0;
        for(unsigned channel=0;channel<3;++channel){const auto& data=effect.channels[i][channel];
            const auto index=int(static_cast<std::int16_t>(effect.phase))+data.delta;
            if(index<0||index>=int(palette_effect_data::lookup.size()))throw std::out_of_range("Unproved palette interpolation lookup");
            const auto value=static_cast<std::uint8_t>(data.current_twice+palette_effect_data::lookup[index]);
            colour=static_cast<std::uint16_t>((colour<<4)|value);
        }
        destination[i]=colour;
    }
    effect.phase=static_cast<std::uint16_t>(effect.phase-15);
    if(static_cast<std::int16_t>(effect.phase)<0)effect.active=0;
    return true;
}
struct NativePaletteEffects {
    std::array<std::uint16_t,64> colours{};
    std::array<PaletteEffect,4> effects{};
    std::uint8_t inhibited_c48d=255,dirty_c48b{};
    bool waiting_black{};
    // 66DE starts all four effects and returns immediately. PreserveC48D:
    // the current main-state callback still owns its interrupt exclusion.
    void begin_level_palette(std::span<const std::uint16_t> target){
        if(target.size()!=64)throw std::out_of_range("Unproved level palette extent");
        for(unsigned bank=0;bank<4;++bank)initialize_palette_effect(effects[bank],std::span<const std::uint16_t>(colours).subspan(bank*16,16),target.subspan(bank*16,16));
    }
    // 63FA starts four records then releases the interrupt gate. It does not
    // busy-wait. The calling native transition resumes via complete_black().
    void begin_black(){
        for(unsigned bank=0;bank<4;++bank)initialize_palette_effect(effects[bank],std::span<const std::uint16_t>(colours).subspan(bank*16,16),palette_effect_data::black);
        waiting_black=true;inhibited_c48d=0;
    }
    // 14A4 palette branch; caller must provide the original interrupt clock.
    void interrupt_palette_step(){
        if(inhibited_c48d)return;
        for(unsigned bank=0;bank<4;++bank)if(advance_palette_effect(effects[bank],std::span<std::uint16_t>(colours).subspan(bank*16,16)))dirty_c48b=255;
    }
    bool complete_black(){
        if(!waiting_black||effects[3].active)return false;
        inhibited_c48d=255;waiting_black=false;return true;
    }
    // 22A8 clears dirty BEFORE the64-word transfer. A typed transfer service
    // binds publication; device completion/interrupt ordering is external.
    template<class Publish>bool publish(Publish&& transfer){
        if(!dirty_c48b)return false;dirty_c48b=0;transfer(std::span<const std::uint16_t>(colours));return true;
    }
};
}
