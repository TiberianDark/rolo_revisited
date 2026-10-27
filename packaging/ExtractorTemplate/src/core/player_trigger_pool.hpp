#pragma once
#include "core/player_trigger_scan.hpp"
namespace rolo {
struct TriggerMarkerServices {
    virtual ~TriggerMarkerServices()=default;
    virtual std::uint8_t marker_byte(std::uint32_t identity)=0;
    virtual void marker_byte(std::uint32_t identity,std::uint8_t value)=0;
};
struct TriggerRecord {
    std::array<std::uint8_t,16> fields{};
    std::uint8_t byte(unsigned offset)const{return fields.at(offset);}
    void byte(unsigned offset,std::uint8_t value){fields.at(offset)=value;}
    std::uint16_t word(unsigned offset)const{return static_cast<std::uint16_t>((byte(offset)<<8)|byte(offset+1));}
    void word(unsigned offset,std::uint16_t value){byte(offset,static_cast<std::uint8_t>(value>>8));byte(offset+1,static_cast<std::uint8_t>(value));}
};
// $2838: 16 records at6936, 17-entry free stack at68F2, sentinel6A36.
// Record contents remain stale on reset/free, as in the original.
struct PlayerTriggerPool {
    static constexpr std::uint16_t first=0x6936,sentinel=0x6a36,stack_base=0x68f2;
    std::array<TriggerRecord,16> records{};
    std::array<std::uint32_t,17> free_keys{};
    std::uint16_t head{};std::size_t cursor{};
    static constexpr std::uint16_t key(std::size_t i){return static_cast<std::uint16_t>(first+i*16);}
    TriggerRecord& record(std::uint16_t id){
        if(id<first||(id-first)%16||(id-first)/16>=records.size())throw std::out_of_range("Native trigger record identity");
        return records.at((id-first)/16);
    }
    void initialize(){head=0;cursor=0;for(std::size_t i=0;i<records.size();++i)free_keys[i]=0xffff0000u|key(i);free_keys.back()=0;}
    std::uint16_t word(std::uint16_t id,unsigned offset){
        if(id==sentinel){if(offset==0)return 0;if(offset==2)return head;throw std::out_of_range("Trigger sentinel field");}
        return record(id).word(offset);
    }
    void word(std::uint16_t id,unsigned offset,std::uint16_t value){
        if(id==sentinel){if(offset!=2)throw std::out_of_range("Trigger sentinel write");head=value;return;}
        record(id).word(offset,value);
    }
    // $4A84: marker identity is the original RAM low word, not a ROM offset.
    std::uint16_t allocate(std::uint16_t x,std::uint16_t row,std::uint16_t dispatch_offset,
            std::uint8_t parameter,std::uint8_t consume,std::uint16_t marker,TriggerMarkerServices& service){
        const auto identity=static_cast<std::uint16_t>(free_keys.at(cursor));if(!identity)return 0;
        ++cursor;auto& node=record(identity);const auto old=head;
        if(old)word(old,0,identity);
        node.word(2,old);node.word(0,sentinel);head=identity;
        node.word(4,x);node.word(6,static_cast<std::uint16_t>(row<<3));node.word(8,dispatch_offset);node.byte(10,parameter);
        node.word(12,marker);const auto full=0xffff0000u|marker;
        node.byte(14,service.marker_byte(full));service.marker_byte(full,0x17);node.byte(11,consume);
        return identity;
    }
    // $4B00 preserves the freed record's stale links; scanner reads them later.
    std::uint16_t unlink(std::uint16_t id){
        auto& node=record(id);const auto next=node.word(2),previous=node.word(0);
        if(next)word(next,0,previous);
        if(previous)word(previous,2,next);
        if(!cursor)throw std::out_of_range("Trigger free-stack underflow");
        free_keys.at(--cursor)=0xffff0000u|id;
        return static_cast<std::uint16_t>(stack_base+cursor*4);
    }
};
// The 18 native dispatch bodies remain required; this class never calls ROM code.
struct PooledPlayerTriggerServices:PlayerTriggerServices {
    PlayerTriggerPool& pool;TriggerMarkerServices& markers;
    PooledPlayerTriggerServices(PlayerTriggerPool& p,TriggerMarkerServices& m):pool(p),markers(m){}
    std::uint16_t trigger_word(std::uint16_t id,unsigned offset)override{return pool.word(id,offset);}
    std::uint8_t trigger_byte(std::uint16_t id,unsigned offset)override{return pool.record(id).byte(offset);}
    void release_trigger_restore_marker(std::uint16_t id)override{
        pool.unlink(id);auto& node=pool.record(id);markers.marker_byte(0xffff0000u|node.word(12),node.byte(14));
    }
    std::uint16_t consume_trigger(std::uint16_t id)override{return pool.unlink(id);}
};
}
