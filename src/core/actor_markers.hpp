#pragma once
#include "core/actor_state.hpp"
#include <stdexcept>
namespace rolo {
struct MarkerRestoreServices {
    virtual ~MarkerRestoreServices()=default;
    virtual void restore_marker(std::uint32_t key,std::uint16_t value)=0;
};
struct DeferredMarker {std::uint16_t next{},marker{},value{},x{},y{};};
struct DeferredMarkerPool {
    static constexpr std::uint16_t first_key=0x6aa2;
    std::array<DeferredMarker,24> records{};
    std::array<std::uint32_t,25> free_keys{};
    std::uint16_t head{};std::size_t cursor{};
    static constexpr std::uint16_t key(std::size_t index) {return static_cast<std::uint16_t>(first_key+index*10);}
    std::size_t index(std::uint16_t identity) const {
        if(identity<first_key||(identity-first_key)%10||(identity-first_key)/10>=records.size())throw std::out_of_range("Native deferred-marker identity");
        return (identity-first_key)/10;
    }
    void initialize() {
        cursor=0;head=0;
        for(std::size_t i=0;i<records.size();++i)free_keys[i]=0xffff0000u|key(i);
        free_keys.back()=0;
    }
};
inline bool marker_in_bounds(std::uint16_t x,std::uint16_t y,std::uint16_t lower_x,
        std::uint16_t upper_x,std::uint16_t lower_y,std::uint16_t upper_y) {
    return signed_word(lower_x)<=signed_word(x)&&signed_word(upper_x)>=signed_word(x)&&
           signed_word(lower_y)<=signed_word(y)&&signed_word(upper_y)>=signed_word(y);
}
// $2BCE..$2C4C: zero/empty/outside paths do not consume a deferred record.
inline void restore_or_defer_actor_marker(const ActorState& actor,DeferredMarkerPool& pool,
        std::uint16_t reference_x,std::uint16_t reference_y,MarkerRestoreServices& services) {
    if(!actor.longword(88))return;
    const auto lower_x=static_cast<std::uint16_t>(reference_x-80),upper_x=static_cast<std::uint16_t>(lower_x+480);
    const auto lower_y=static_cast<std::uint16_t>(reference_y-80),upper_y=static_cast<std::uint16_t>(lower_y+384);
    if(marker_in_bounds(actor.word(94),actor.word(96),lower_x,upper_x,lower_y,upper_y)) {
        const auto identity=pool.free_keys.at(pool.cursor);
        if(identity) {
            ++pool.cursor;const auto low=static_cast<std::uint16_t>(identity);
            pool.records.at(pool.index(low))={pool.head,actor.word(90),actor.word(92),actor.word(94),actor.word(96)};
            pool.head=low;return;
        }
    }
    services.restore_marker(actor.longword(88),actor.word(92));
}
// $2C4C..$2CBC. Preserve D0's marker-address overwrite after a removal:
// subsequent lower-X tests use the restored marker's low word.
inline void update_deferred_markers(DeferredMarkerPool& pool,std::uint16_t reference_x,
        std::uint16_t reference_y,MarkerRestoreServices& services) {
    auto lower_x=static_cast<std::uint16_t>(reference_x-80);
    const auto upper_x=static_cast<std::uint16_t>(lower_x+480);
    const auto lower_y=static_cast<std::uint16_t>(reference_y-80),upper_y=static_cast<std::uint16_t>(lower_y+384);
    int previous=-1;
    for(;;) {
        auto& link=previous==-1?pool.head:pool.records.at(previous).next;
        const auto current=link;if(!current)return;
        const auto index=pool.index(current);const auto& record=pool.records.at(index);
        if(marker_in_bounds(record.x,record.y,lower_x,upper_x,lower_y,upper_y)) {previous=static_cast<int>(index);continue;}
        lower_x=record.marker;
        services.restore_marker(0xffff0000u|lower_x,record.value);
        link=record.next;
        if(!pool.cursor)throw std::out_of_range("Native deferred-marker free-stack underflow");
        pool.free_keys.at(--pool.cursor)=0xffff0000u|current;
    }
}
}
