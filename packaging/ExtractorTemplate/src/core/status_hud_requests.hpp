#pragma once
#include "core/status_hud_templates.hpp"
#include <stdexcept>
namespace rolo {
struct HudTransferRequest {std::uint32_t source{},destination{},words{},command{0x40000000};bool operator==(const HudTransferRequest&)const=default;};
struct HudFillRequest {std::uint32_t value{},destination{},length{},command{0x40000000};bool operator==(const HudFillRequest&)const=default;};
struct StatusHudRequestState {
 std::array<std::uint8_t,640> sprites{};std::array<std::uint8_t,8> scratch_digits{},cached_digits{{255,255,255,255,255,255,255,255}};
 std::uint16_t reserved{};std::uint8_t initialized{},lives{3},previous_lives{255},key{},piece{};std::uint32_t score{};
 bool operator==(const StatusHudRequestState&)const=default;
};
struct StatusHudRequestServices {
 virtual ~StatusHudRequestServices()=default;
 virtual void transfer(const HudTransferRequest&)=0;
 virtual void fill(const HudFillRequest&)=0;
 virtual std::array<std::uint8_t,8> format_score(std::uint32_t)=0;
 virtual void sound(std::uint16_t)=0;
};
// 51D0: ordered original resource requests; queue/device completion is separate.
inline void publish_fixed_hud_resources(StatusHudRequestServices& s){s.transfer({0x1602a,0xac80,0xc0});s.transfer({0x27bc0,0xae00,0x20});s.fill({0,0xae40,63});}
// 7014: original zero-fill request; length is the raw count field.
inline void request_display_region_clear(StatusHudRequestServices& s){s.fill({0,0x0d40,0x7ff});}
// 5060: SAT reservation, cached lives/score and reward publication requests.
inline void publish_status_hud_requests(StatusHudRequestState& s,StatusHudRequestServices& services){
 if(s.reserved>75)throw std::out_of_range("Unproved five-sprite HUD capacity");
 const unsigned start=s.reserved; s.reserved=static_cast<std::uint16_t>(s.reserved+5);
 for(unsigned i=0;i<40;++i)s.sprites[start*8+i]=status_hud_templates[i];
 for(unsigned i=0;i<5;++i)s.sprites[start*8+i*8+3]=static_cast<std::uint8_t>(start+i+1);
 if(!s.initialized){s.initialized=255;publish_fixed_hud_resources(services);}
 const auto lives=s.lives;
 if(lives!=s.previous_lives){s.previous_lives=lives;if(!(lives&128)){services.transfer({0x27940u+(lives/10)*64,0xae80,32});services.transfer({0x27940u+(lives%10)*64,0xaec0,32});}}
 s.scratch_digits=services.format_score(s.score);
 for(unsigned i=0;i<8;++i)if(s.scratch_digits[i]!=s.cached_digits[i])services.transfer({0x27940u+unsigned(s.scratch_digits[i])*64,0xaf00u+i*64,32});
 for(unsigned i=4;i<8;++i)s.cached_digits[i]=s.scratch_digits[i];for(unsigned i=0;i<4;++i)s.cached_digits[i]=s.scratch_digits[i];
 auto reward=[&](std::uint8_t& latch,unsigned source,unsigned destination){if(latch&&!(latch&128)){latch=255;services.sound(37);services.transfer({source,destination,64});}};
 reward(s.key,0x2f1e0,0xb100);reward(s.piece,0x2eac0,0xb180);
}
}

