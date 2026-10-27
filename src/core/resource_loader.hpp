#pragma once
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <bcrypt.h>
#include <array>
#include <bit>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <limits>
#include <span>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <vector>
#pragma comment(lib,"bcrypt.lib")
namespace rolo::resources {
inline std::string sha256(std::span<const std::uint8_t> bytes) {
    BCRYPT_ALG_HANDLE algorithm{};
    if(BCryptOpenAlgorithmProvider(&algorithm,BCRYPT_SHA256_ALGORITHM,nullptr,0)<0) throw std::runtime_error("SHA256 unavailable");
    std::array<unsigned char,32> digest{};
    const auto status=BCryptHash(algorithm,nullptr,0,const_cast<PUCHAR>(bytes.data()),static_cast<ULONG>(bytes.size()),digest.data(),32);
    BCryptCloseAlgorithmProvider(algorithm,0);
    if(status<0) throw std::runtime_error("SHA256 failed");
    std::string result; for(auto value:digest) {result+="0123456789abcdef"[value>>4];result+="0123456789abcdef"[value&15];} return result;
}
inline std::vector<std::uint8_t> checked_bytes(const std::filesystem::path& root,const char* relative,const char* digest,std::size_t expected) {
    const std::filesystem::path rel(relative);
    if(rel.is_absolute()||rel.has_root_name()) throw std::runtime_error("Absolute resource path rejected");
    for(const auto& part:rel) if(part==".."||part==".") throw std::runtime_error("Invalid resource path");
    const auto base=std::filesystem::canonical(root);
    const auto path=std::filesystem::canonical(base/rel);
    const auto inside=path.lexically_relative(base);
    if(inside.empty()||*inside.begin()=="..") throw std::runtime_error("Resource outside pack");
    if(expected>16*1024*1024||std::filesystem::file_size(path)!=expected) throw std::runtime_error(std::string("Resource size mismatch: ")+relative);
    std::ifstream input(path,std::ios::binary);
    std::vector<std::uint8_t> bytes(expected);
    if(!input.read(reinterpret_cast<char*>(bytes.data()),static_cast<std::streamsize>(expected))) throw std::runtime_error(std::string("Cannot read resource: ")+relative);
    if(sha256(bytes)!=digest) throw std::runtime_error(std::string("Resource hash mismatch: ")+relative);
    return bytes;
}
inline std::uint32_t u32(std::span<const std::uint8_t> bytes,std::size_t offset) {
    if(offset>bytes.size()||bytes.size()-offset<4) throw std::runtime_error("Truncated record");
    return std::uint32_t(bytes[offset])|(std::uint32_t(bytes[offset+1])<<8)|(std::uint32_t(bytes[offset+2])<<16)|(std::uint32_t(bytes[offset+3])<<24);
}
inline std::uint16_t u16(std::span<const std::uint8_t> bytes,std::size_t offset) {
    if(offset>bytes.size()||bytes.size()-offset<2) throw std::runtime_error("Truncated record");
    return std::uint16_t(bytes[offset])|(std::uint16_t(bytes[offset+1])<<8);
}
inline std::int16_t i16(std::span<const std::uint8_t> bytes,std::size_t offset) { return std::bit_cast<std::int16_t>(u16(bytes,offset)); }
template<class T,std::size_t N> void load_numeric(const std::filesystem::path& root,const char* path,const char* hash,std::array<T,N>& target) {
    static_assert(std::is_integral_v<T> && sizeof(T)<=4);
    auto bytes=checked_bytes(root,path,hash,N*sizeof(T));
    using U=std::make_unsigned_t<T>;
    for(std::size_t i=0;i<N;++i) {U value{};for(std::size_t j=0;j<sizeof(T);++j) value|=static_cast<U>(std::uint32_t(bytes[i*sizeof(T)+j])<<(8*j));target[i]=std::bit_cast<T>(value);}
}
template<class T,std::size_t N,std::size_t M> void load_macros(const std::filesystem::path& root,const char* path,const char* hash,std::array<T,N>& target,const std::array<std::uint16_t,M>& tiles) {
    auto bytes=checked_bytes(root,path,hash,N*10);
    for(std::size_t i=0;i<N;++i) {const auto pos=i*10;const auto offset=u32(bytes,pos+2),count=u32(bytes,pos+6);
        if(offset>M||count>M-offset||count!=std::uint32_t(bytes[pos])*bytes[pos+1]) throw std::runtime_error("Invalid terrain tile range");
        target[i]={bytes[pos],bytes[pos+1],std::span<const std::uint16_t>(tiles).subspan(offset,count)};
    }
}
template<class T,std::size_t N> void load_frames(const std::filesystem::path& root,const char* path,const char* hash,std::array<T,N>& target) {
    auto bytes=checked_bytes(root,path,hash,N*20);
    for(std::size_t i=0;i<N;++i) {auto p=i*20;target[i]={u32(bytes,p),u32(bytes,p+4),u32(bytes,p+8),u32(bytes,p+12),u32(bytes,p+16)};}
}
template<class T,std::size_t N> void load_sprites(const std::filesystem::path& root,const char* path,const char* hash,std::array<T,N>& target) {
    auto bytes=checked_bytes(root,path,hash,N*16);
    for(std::size_t i=0;i<N;++i) {auto p=i*16;target[i]={u32(bytes,p),u32(bytes,p+4),u32(bytes,p+8),u32(bytes,p+12)};}
}
template<class T,std::size_t N> void load_animation_frames(const std::filesystem::path& root,const char* path,const char* hash,std::array<T,N>& target) {
    auto bytes=checked_bytes(root,path,hash,N*22);
    for(std::size_t i=0;i<N;++i) {auto p=i*22;target[i]={u32(bytes,p),u32(bytes,p+4),u32(bytes,p+8),i16(bytes,p+12),i16(bytes,p+14),u16(bytes,p+16),u16(bytes,p+18),u16(bytes,p+20)};}
}
template<class T,std::size_t N> void load_animation_nodes(const std::filesystem::path& root,const char* path,const char* hash,std::array<T,N>& target) {
    auto bytes=checked_bytes(root,path,hash,N*22);
    using Op=decltype(T{}.op);
    for(std::size_t i=0;i<N;++i) {auto p=i*22;const auto op=u32(bytes,p);target[i]={static_cast<Op>(op),u16(bytes,p+4),static_cast<int>(static_cast<std::int32_t>(u32(bytes,p+6))),static_cast<int>(static_cast<std::int32_t>(u32(bytes,p+10))),static_cast<int>(static_cast<std::int32_t>(u32(bytes,p+14))),u32(bytes,p+18)};}
}
template<class T,std::size_t N> void load_animation_programs(const std::filesystem::path& root,const char* path,const char* hash,std::array<T,N>& target) {
    auto bytes=checked_bytes(root,path,hash,N*11);
    for(std::size_t i=0;i<N;++i) {auto p=i*11;target[i]={u32(bytes,p),u16(bytes,p+4),bytes[p+6],static_cast<int>(static_cast<std::int32_t>(u32(bytes,p+7)))};}
}
template<class T,std::size_t N> void load_tracks(const std::filesystem::path& root,const char* path,const char* hash,std::array<T,N>& target) {
    auto bytes=checked_bytes(root,path,hash,N*24);
    for(std::size_t i=0;i<N;++i) {auto p=i*24;target[i]={u32(bytes,p),u32(bytes,p+4),u32(bytes,p+8),u32(bytes,p+12),u32(bytes,p+16),u32(bytes,p+20)};}
}
template<class T,std::size_t N> void load_actor_definitions(const std::filesystem::path& root,const char* path,const char* hash,std::array<T,N>& target) {
    auto bytes=checked_bytes(root,path,hash,N*38);
    for(std::size_t i=0;i<N;++i) {auto p=i*38;target[i].key=u32(bytes,p);for(std::size_t b=0;b<34;++b)target[i].data[b]=bytes[p+4+b];}
}
template<class T,std::size_t N> void load_enemy_bursts(const std::filesystem::path& root,const char* path,const char* hash,std::array<T,N>& target) {
    auto bytes=checked_bytes(root,path,hash,N*8);
    for(std::size_t i=0;i<N;++i) {auto p=i*8;target[i].definition=u32(bytes,p);for(std::size_t b=0;b<4;++b)target[i].bytes[b]=bytes[p+4+b];}
}
template<class T,std::size_t N> void load_graphics(const std::filesystem::path& root,const char* path,const char* hash,std::array<T,N>& target) {
    auto bytes=checked_bytes(root,path,hash,N*20);
    for(std::size_t i=0;i<N;++i) {auto p=i*20;target[i]={u32(bytes,p),u32(bytes,p+4),u32(bytes,p+8),u32(bytes,p+12),u32(bytes,p+16)};}
}
template<class T,std::size_t N> void load_pieces(const std::filesystem::path& root,const char* path,const char* hash,std::array<T,N>& target) {
    auto bytes=checked_bytes(root,path,hash,N*11);
    for(std::size_t i=0;i<N;++i) {auto p=i*11;target[i].selector=bytes[p];target[i].group=bytes[p+1];target[i].row=bytes[p+2];target[i].column=bytes[p+3];target[i].stride=bytes[p+4];target[i].xbase=bytes[p+5];target[i].edges=bytes[p+6];for(std::size_t b=0;b<4;++b)target[i].neighbors[b]=bytes[p+7+b];}
}
template<class T,std::size_t N> void load_descriptors(const std::filesystem::path& root,const char* path,const char* hash,std::array<T,N>& target) {
    auto bytes=checked_bytes(root,path,hash,N*6);
    for(std::size_t i=0;i<N;++i) {auto p=i*6;target[i]={u32(bytes,p),bytes[p+4],bytes[p+5]};}
}
template<class T,std::size_t N> void load_streams(const std::filesystem::path& root,const char* path,const char* hash,std::array<T,N>& target) {
    auto bytes=checked_bytes(root,path,hash,N*10);
    for(std::size_t i=0;i<N;++i) {auto p=i*10;target[i]={u32(bytes,p),u32(bytes,p+4),u16(bytes,p+8)};}
}
}

