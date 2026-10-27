#include "core/native_music_render.hpp"
#include <fstream>
#include <iostream>
#include <iterator>
#include <cmath>
static void le(std::ostream&out,std::uint32_t value,unsigned count){for(unsigned i=0;i<count;++i)out.put(char(value>>(8*i)));}
int main(int argc,char**argv){try{
    const bool effect=argc>1&&std::string(argv[1])=="--effect";
    if(argc<(effect?4:3)||argc>(effect?5:4))throw std::invalid_argument("Usage: rolo_audio_render input.seq output.wav [seconds] OR --effect ID output.wav [seconds]");
    const unsigned seconds=argc==(effect?5:4)?unsigned(std::stoul(argv[effect?4:3])):(effect?5:30);
    if(!seconds||seconds>600)throw std::invalid_argument("Duration must be 1..600 seconds");
    std::vector<std::uint8_t> data;
    if(!effect){std::ifstream input(argv[1],std::ios::binary);if(!input)throw std::runtime_error("Cannot open sequence");data.assign(std::istreambuf_iterator<char>(input),{});}
    rolo::NativeMusicRender render(std::move(data));
    if(effect)render.effect(unsigned(std::stoul(argv[2])));
    const auto rate=render.sample_rate(),frames=rate*seconds;
    std::ofstream out(argv[effect?3:2],std::ios::binary);if(!out)throw std::runtime_error("Cannot create WAV");
    out.write("RIFF",4);le(out,36+frames*4,4);out.write("WAVEfmt ",8);le(out,16,4);le(out,1,2);le(out,2,2);
    le(out,rate,4);le(out,rate*4,4);le(out,4,2);le(out,16,2);out.write("data",4);le(out,frames*4,4);
    std::int64_t power=0;int peak=0;
    for(unsigned i=0;i<frames;++i){auto sample=render.sample();for(auto v:sample){le(out,std::uint16_t(v),2);peak=std::max(peak,std::abs(int(v)));power+=std::int64_t(v)*v;}}
    out.close();if(!out)throw std::runtime_error("WAV write failed");
    std::cout<<"Rendered "<<seconds<<"s stereo FM at "<<rate<<"Hz; peak="<<peak<<" RMS="<<std::sqrt(double(power)/(frames*2))<<" sequence_end="<<render.ended()<<'\n';
    if(peak<64)throw std::runtime_error("Unexpectedly silent FM render");
    return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
