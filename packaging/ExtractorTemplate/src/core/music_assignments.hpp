#pragma once
#include "core/music_sequence_data.hpp"
#include <optional>
#include <stdexcept>
namespace rolo {
struct MusicRequest {unsigned id{};bool loop{};};
// $5D08 level pair/delay/playlist selection; $5CE6 delayed request.
struct LevelMusicAssignment {
    unsigned previous_cue=255,cycle=0,timer=65535,tune=0;
    std::optional<MusicRequest> begin(unsigned selector,bool region=false,bool visited=false,unsigned reward=0){
        if(selector>=80)throw std::out_of_range("Music level selector");
        timer=0;std::optional<MusicRequest> request;
        const unsigned cue=music_bank::level_pairs[selector*2];
        if(cue!=255&&cue!=previous_cue){
            if(cue<27||cue>32)throw std::out_of_range("Music entry cue");
            previous_cue=cue;request=MusicRequest{cue,false};timer=music_bank::delays[cue-27];
            if(region)timer=timer*6/5;
        }
        tune=music_bank::level_pairs[selector*2+1];
        if(tune==255){cycle=(cycle+1)&15;tune=music_bank::cycle[cycle];}
        if(visited&&reward==255&&(tune==8||tune==14))tune=9;
        return request;
    }
    std::optional<MusicRequest> step(){
        if(timer&32768)return {};
        timer=(timer-1)&65535;
        if(timer&32768)return MusicRequest{tune,true};return {};
    }
};
}
