#pragma once
#include "core/actor_state.hpp"
#include "core/score_award.hpp"
#include <span>
namespace rolo {
struct CampaignResetState{ScoreAwardState awards;std::uint32_t backup_a{},backup_b{};std::uint8_t lives{},gate{},sentinel{};};
inline void reset_score_threshold(ScoreAwardState&s){s.table_offset=0;s.next_threshold=1000000;}
inline void reset_campaign_score(CampaignResetState&s){s.lives=3;s.gate=0;s.sentinel=255;s.backup_a=s.backup_b=0xffffffffu;s.awards.total=0;reset_score_threshold(s.awards);}
struct CampaignNodeState{std::span<std::uint8_t>flags;std::uint16_t selector{};std::uint8_t reward{};};
struct CampaignNodeServices{virtual ~CampaignNodeServices()=default;virtual void scan(std::uint16_t type,bool reveal_callback)=0;};
inline void reveal_campaign_node(std::span<std::uint8_t>flags,std::uint16_t selector){if(selector&32768||selector>=flags.size())throw std::out_of_range("Campaign signed selector");flags[selector]|=1;}
inline void mark_campaign_node(CampaignNodeState&s){if(s.selector&32768||s.selector>=s.flags.size())throw std::out_of_range("Campaign current selector");s.flags[s.selector]|=10;reveal_campaign_node(s.flags,std::uint16_t((s.selector&0xff00)|s.reward));}
inline void complete_campaign_node(CampaignNodeState&s,CampaignNodeServices&v,bool alternate){mark_campaign_node(s);if(alternate)v.scan(11,true);v.scan(5,false);}
inline std::uint32_t place_campaign_actor(std::uint32_t code,std::uint32_t&x,std::uint16_t y,ActorState&actor){
 if((std::uint8_t(code)&0xfe)!=10)return 0;
 x=(x&0xffff0000u)|std::uint16_t(x-32);actor.word(12,std::uint16_t(x));actor.word(16,y);return 0xffffffffu;
}
}
