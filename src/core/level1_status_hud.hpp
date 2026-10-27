#pragma once
#include "core/level1_status_hud_data.hpp"
#include "core/level1_progress.hpp"
namespace rolo {
struct Level1StatusHud {
    std::array<std::uint8_t,384> portrait=level1_status_hud_data::portrait;
    std::array<std::uint8_t,256> lives{},score_left{},score_right{},rewards{};
};
// $5060/$51D0: native pattern publications for the five original HUD sprites.
// No hardware queue is executed. C550/C551 latch only after reward-curve arrival.
template<class Sound>
inline void publish_level1_status_hud(Level1StatusHud& hud,std::uint8_t lives,std::uint32_t score,
        Level1ProgressState& progress,Sound&& sound){
    auto digit=[](auto& target,unsigned offset,unsigned value){
        if(value>=10)throw std::out_of_range("Original HUD decimal glyph domain");
        std::copy_n(level1_status_hud_data::digits.begin()+value*64,64,target.begin()+offset);
    };
    std::copy(level1_status_hud_data::life_label.begin(),level1_status_hud_data::life_label.end(),hud.lives.begin());
    if(static_cast<std::int8_t>(lives)>=0){digit(hud.lives,128,lives/10);digit(hud.lives,192,lives%10);}
    std::array<unsigned,8> digits{};
    for(int n=7;n>=0;--n){digits[n]=score%10;score/=10;}
    if(score)throw std::out_of_range("Original eight-digit score domain");
    for(unsigned n=0;n<4;++n){digit(hud.score_left,n*64,digits[n]);digit(hud.score_right,n*64,digits[n+4]);}
    auto reward=[&](std::uint8_t& latch,auto& data,unsigned offset){
        if(static_cast<std::int8_t>(latch)>0){latch=255;sound(37);std::copy(data.begin(),data.end(),hud.rewards.begin()+offset);}
    };
    reward(progress.key_c550,level1_status_hud_data::key,0);
    reward(progress.piece_c551,level1_status_hud_data::piece,128);
}
}
