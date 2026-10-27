#pragma once
#include <array>
#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <optional>
#include <span>
#include <stdexcept>
#include <vector>
#ifdef _WIN32
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#endif
namespace rolo {
// Optional Windows demo feature. This is a map-entry campaign checkpoint,
// deliberately separate from original game logic and transient actor state.
struct DemoProgressSave{
 std::array<std::uint8_t,80>flags{};std::uint16_t x=280,y=472;
 std::uint32_t score=0,next_threshold=1000000;std::uint16_t award_offset=0;std::uint8_t lives=3;
 bool operator==(const DemoProgressSave&)const=default;
};
inline constexpr char progress_rom_hash[]="9478d47cc1883df42f3714ea485aedd71b541274eb45a3aa7c49f4a3518305e9";
inline std::uint32_t progress_checksum(std::span<const std::uint8_t>b){std::uint32_t h=2166136261u;for(auto v:b)h=(h^v)*16777619u;return h;}
inline bool valid_demo_progress(const DemoProgressSave&s){return s.x<1280&&s.y>=256&&s.y<1024&&s.lives<=99&&(s.award_offset==0||s.award_offset==4)&&s.next_threshold>s.score&&(s.flags[1]&1);}
inline std::vector<std::uint8_t> encode_demo_progress(const DemoProgressSave&s){
 if(!valid_demo_progress(s))throw std::invalid_argument("Invalid map progress checkpoint");
 std::vector<std::uint8_t>b{'R','O','L','O','M','A','P',1};b.insert(b.end(),progress_rom_hash,progress_rom_hash+64);b.insert(b.end(),s.flags.begin(),s.flags.end());
 auto put=[&](std::uint32_t v,unsigned bytes){for(unsigned n=bytes;n>0;--n)b.push_back(std::uint8_t(v>>((n-1)*8)));};
 put(s.x,2);put(s.y,2);put(s.score,4);put(s.next_threshold,4);put(s.award_offset,2);put(s.lives,1);put(progress_checksum(b),4);return b;
}
inline std::optional<DemoProgressSave> decode_demo_progress(std::span<const std::uint8_t>b){
 constexpr std::size_t size=171;if(b.size()!=size)return {};constexpr std::uint8_t magic[]{'R','O','L','O','M','A','P',1};for(unsigned i=0;i<8;++i)if(b[i]!=magic[i])return {};for(unsigned i=0;i<64;++i)if(b[8+i]!=progress_rom_hash[i])return {};
 std::size_t at=152;auto get=[&](unsigned bytes){std::uint32_t v=0;for(unsigned i=0;i<bytes;++i)v=(v<<8)|b[at++];return v;};
 DemoProgressSave s;std::copy_n(b.begin()+72,80,s.flags.begin());s.x=get(2);s.y=get(2);s.score=get(4);s.next_threshold=get(4);s.award_offset=get(2);s.lives=get(1);auto check=get(4);if(check!=progress_checksum(b.first(size-4))||!valid_demo_progress(s))return {};return s;
}
inline bool write_demo_progress(const std::filesystem::path&path,const DemoProgressSave&s){
 const auto bytes=encode_demo_progress(s);auto temporary=path;temporary+=".tmp";{std::ofstream f(temporary,std::ios::binary|std::ios::trunc);f.write(reinterpret_cast<const char*>(bytes.data()),bytes.size());f.flush();if(!f)return false;}
#ifdef _WIN32
 return MoveFileExW(temporary.c_str(),path.c_str(),MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH)!=0;
#else
 std::error_code ec;std::filesystem::rename(temporary,path,ec);return !ec;
#endif
}
inline std::optional<DemoProgressSave> read_demo_progress(const std::filesystem::path&path){
 std::ifstream f(path,std::ios::binary);std::array<std::uint8_t,172>bytes{};f.read(reinterpret_cast<char*>(bytes.data()),bytes.size());if(f.gcount()!=171)return {};return decode_demo_progress(std::span(bytes).first(171));
}
}
