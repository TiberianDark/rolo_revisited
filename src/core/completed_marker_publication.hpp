#pragma once
#include "core/display_setup.hpp"
#include <array>
namespace rolo {
struct CompletedMapPoint{std::uint16_t x{},y{};};
struct CompletedMarkerPublication{std::uint8_t count{};std::array<std::uint16_t,7>dma{};};
struct CompletedMarkerPorts{virtual ~CompletedMarkerPorts()=default;virtual void artwork(GraphicsTransferRequest)=0;virtual void dma(std::span<const std::uint16_t>,std::uint32_t)=0;};
inline CompletedMarkerPublication publish_completed_map_markers(std::span<std::uint8_t>sat,std::uint8_t count,std::span<const CompletedMapPoint>points,std::uint16_t camera_x,std::uint16_t camera_y,CompletedMarkerPorts&p){
 if(!count||std::size_t(count)*8>sat.size())throw std::out_of_range("Completed marker SAT prefix domain");p.artwork({0x314e0,0xb200,0x40000000,64});std::size_t cursor=std::size_t(count)*8;std::uint16_t size_link=std::uint16_t(0x500|count);sat[cursor-5]=count;
 const auto left=std::uint16_t(camera_x-16),right=std::uint16_t(left+352),top=std::uint16_t(camera_y-16),bottom=std::uint16_t(top+256);
 auto word=[&](std::uint16_t value){if(cursor+2>sat.size())throw std::out_of_range("Completed marker SAT capacity");sat[cursor++]=std::uint8_t(value>>8);sat[cursor++]=std::uint8_t(value);};
 for(auto point:points){if(point.x&32768)break;if(signed_word(point.x)<signed_word(left)||signed_word(point.x)>signed_word(right)||signed_word(point.y)<signed_word(top)||signed_word(point.y)>signed_word(bottom))continue;const auto x=std::uint16_t(point.x-left+107),y=std::uint16_t(point.y-top+112);word(y);size_link=std::uint16_t(size_link+1);word(size_link);word(0x4590);word(x);}
 sat[cursor-5]=0;const auto total=std::uint8_t(size_link);const auto words=std::uint16_t(total*4);CompletedMarkerPublication result{total,{std::uint16_t(0x9300|(words&255)),std::uint16_t(0x9400|(words>>8)),0x95de,0x96e4,0x977f,0x7400,0x0083}};p.dma(result.dma,0);return result;
}
}
